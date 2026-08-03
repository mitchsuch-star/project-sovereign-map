# Ink & Iron: Current Status

> **Updated every session by Claude Code.**

## ▶ NEXT UP: RE-STAGED July 2, 2026 — the post-map / post-diplo queue

> ### ✅ THE NAVAL SECOND PASS — NV-4..NV-11 LANDED (August 2, 2026)
>
> **User direction: "do another pass on naval, make sure it works and the ux is
> fleshed out; does Normandy make sense for England to land at, how do we
> abstract them entering on Portugal irl? do we need buttons anywhere, better
> visual rep, a battle screen like for battles?"** Four decisions put back, all
> four taken at the recommended default. **Gate + landing record =
> `NAVAL_SPEC.md` §15, authoritative.**
>
> **Measured first** (16-turn ambient probe, historical seed, the `ai_v_sweep`
> idiom): Britain's Moore marched **30,000 men** ashore at Normandy on turn 1 —
> twice the transports' cap — and stood in **Berry by turn 2**; `naval_expedition`
> never fired for anyone because it was **strictly dominated**; a blockaded Spain
> laid a keel **every turn forever** (30 → 44 by turn 16, ~70 by turn 40) for
> +2.5 effective points; a turn-back was logged **every other turn**; the
> Continental System's headline 38.5% closure sat below its own 40% first notch
> and did nothing, with no way to tell; and the only interactive naval
> affordance in the whole game was one chip.
>
> - **NV-4 THE HOST RULE.** The crossing gate now reads the far SHORE as well as
>   the water: a sea link may not be MARCHED into a province held by a court you
>   are at war with while a hostile fleet still covers it. In the single-source
>   predicate, so ~25 seams inherit it; sited AFTER the ratio arm, so it can only
>   change the verdict for someone who already commands the sea. Both escape
>   hatches real and pinned — uncontested water is an administrative ferry (beat
>   the fleet and land unlimited), and a §5.3 window WAIVES it (drawing the enemy
>   off station is precisely when the army crosses; the Descent stays winnable).
>   It gates the FIRST landing, never the reinforcement of one that succeeded.
>   New `landing` verdict with an amber map tint and a **DEFENDED SHORE** line —
>   never "SHUT", because the water is not lost.
> - **NV-5 THE AI'S NAVAL LIFE.** `find_ai_expedition` sails for a shore that
>   will RECEIVE an army before it considers a beach; a **host** is an ally, a
>   vassal, or a friend at 25+ — and the shipped board reads exactly right
>   through that filter (**Portugal 40**, Naples 30 · Denmark/Hanover/Sardinia
>   0). `nation_is_penned_in` is land REACHABILITY, not adjacency (the first cut
>   called France penned too). **Measured: Britain lands at LISBON on turn 11**
>   and fights up through Galicia → Asturias → Bordelais; over 30 turns it runs
>   three expeditions and Paget reaches Limousin. Moore's 30,000 stay home, being
>   over the lift — where Britain's home army actually was until 1808. Plus the
>   establishment build ceiling (Spain halts at 45), the diversion rung, the
>   honest CS surface, and **three pre-existing AI bugs**: P4 attack, P4.25
>   garrison assault and P4.5 undefended capture all lacked the crossing gate.
>   **20+ turn-backs over 22 turns → ZERO over 30.**
> - **NV-6 THE ADMIRALTY'S CHIPS.** Posture and the Grand Diversion as honest-
>   availability chips in the ledger block (a withheld chip states why; every
>   chip command is pinned to actually parse); the **landing chip on the region
>   panel**, where a destination is chosen, quoting the same odds the resolver
>   rolls. The Diversion warns about the trap it cannot gate (a once-per-war card
>   spent with no army staged). **NV-P1 FIXED** — the ledger's RichTextLabel
>   defaulted to `MOUSE_FILTER_STOP` and ate the wheel before its own
>   ScrollContainer saw it.
> - **NV-7 THE NAVAL DIORAMA** (row **NV-D4 re-opened and CLOSED**). The same
>   tableau, same payload shape, same scene. The mapping is the model: §4.4
>   already bleeds every pooled fleet, so its loss dict IS the order of battle —
>   **Villeneuve 45, Gravina 30, Verhuell 12 against Nelson 100 and Senyavin
>   20**, the historical picture unprompted. The **ship is the fourth war-table
>   piece** from the same generator (24 → 32 sprites), diorama-only. Chart-blue
>   stage, SAIL LOST odometers, "45 → 20 sail", a sea vocabulary on the banner,
>   and the verdict spoken by **THE ADMIRALTY** — not Berthier, who has no
>   business reporting a fleet action. Evidence:
>   `docs/audits/NV7_NAVAL_DIORAMA_TRAFALGAR_2026_08_02.png`.
>
> **Pins flipped consciously:** three channel-gate pins (the ratio asserted
> UNCHANGED alongside, so the flip is provably the host rule and not a naval
> reversal); the square-thrash shape moved ashore after that file's own coverage
> guard caught its breaker going dead; the pieces drift guard 24 → 32; and
> **`BASELINE_SERIES` re-recorded ONCE**, divergence index 1 — **attribution
> verified by experiment**: with `HOST_RULE_ACTIVE` flipped False and everything
> else left in place, the series reproduces the prior record byte-identically.
> M1–M7 byte-identical without re-record. Suite **15,822/3**, ruff clean, Godot
> parse harness EXIT=0.
>
> **THE TIGHTENING REVIEW (same day, user-directed "look for bugs, no ham-fisted
> solutions") — record = `NAVAL_SPEC.md` §15.9.** Five defects found by hunting,
> ALL FIXED: **the neutrality bypass** (an expedition could land on ANY neutral's
> coast with zero diplomacy — closed with the consent gate, `is_expedition_host`
> made the ONE public predicate the executor, the chips and the AI all read;
> own soil = sealift, at-war = the verb's point, anyone else must RECEIVE us);
> **guns do not carry across a strait** (measured: with both Channel fleets sunk
> a London battery shelled Flanders, success=True — the crossing gate refuses
> covered water but uncontested water read "open"; the physical rule now lives at
> the single bombardment seam, both call sites, plus the P4 artillery skip);
> **counter-punch stays a land reflex** (the cautious rung offered Channel
> retaliations the executor refused every time); **the turn-back log names real
> water** ("the London–Castanos crossing" — a marshal name resolved to its
> region); **the enemy phase carries the sea** (the client stash scanned only
> `battle_diorama`, so an enemy-phase fleet action could never auto-play).
> Cleared: overwatch (same-region only), the enemy-phase passthrough, the
> probe's Piedmont landing (KoI had entered the war — an enemy beach). The AI
> build ceiling re-examined and KEPT: Spain halting at 45 is Cádiz's real
> establishment, and France 45 + Spain 45 + Holland 12 pooled at 0.8 vs the
> RN's 100+20 is exactly the arithmetic that made Trafalgar necessary. Zero
> turn-backs over 30 turns; `BASELINE_SERIES` byte-identical WITHOUT re-record;
> suite **15,837/3**.
>
> **THE ADVERSARIAL REVIEW + THE DRIVEN ARC (NV-9 / NV-10, same day)** —
> records `NAVAL_SPEC.md` §15.11–§15.12. A 6-lens find→refute fleet over the
> whole naval range returned 16 findings; **the refuters were cut short by a
> credit exhaustion, so "unrefuted" was treated as UNVERIFIED and every claim
> re-derived by hand.** Ten fixes, 7/7 targeted mutations caught.
> **THE P1 reproduced exactly:** Murat (cavalry, range 2) at Paris attacked
> Moore at London and **ended the turn standing in London** — the crossing gate
> reads the DIRECT pair, and the water was on the MIDDLE leg. Fixed as
> `crossing_check_reach` (the 2-tile MOVE seam's own model, made the single
> source) at the attack gate, the AI's P4 scan, and a new `_naval_advance_allowed`
> seam for every post-combat move. Also: the Glorious Charge had no gate at
> INITIATION; guns-across-a-strait were refused BELOW the war declaration (the
> player bought a war for an impossible order); the muster preview promised a
> corps Rule 2b withholds; `_decisive()` read the land grammar so every sea
> action was "decisive" and an indecisive win contradicted the Admiralty on the
> same screen; an ANNIHILATED pooled squadron vanished from the tableau; NV-8's
> enemy-phase fix was half a fix (the SERVER filter suppressed a fleet action the
> player FOUGHT); a pre-NV-8c save reloaded the dead edge walkable AND ungated;
> `nation_is_penned_in` went stale mid-turn. **FOUR TESTS WERE REPAIRED BECAUSE
> THEY WERE NOT TESTING ANYTHING** — each proven by deleting the code it claimed
> to pin and watching the suite stay green. **The save migration's first cut was
> itself a bug**: per-province, it pruned TEN edges out of the legacy fixture,
> because eleven legacy names also exist on the Europe map with different
> neighbours — name overlap is not identity; the test caught it, N1 preserved.
>
> **NV-10 — the A2 arc DRIVEN** (`tools/a2_strangulation_drive.py`, committed).
> A scripted France marched on **Portugal** — Junot 1807, the System's own
> founding act. Driving it found what reading could not: France took all four
> Portuguese provinces by turn 12 and the closure went **DOWN**, 38.5% → 23.1%.
> `closure_against` counted ports by NATION and read only who was AT WAR, so an
> overrun neutral still counted as open — the System could not express its own
> central move. A court whose CAPITAL is held by a power at war with the target
> now counts as closed. **Measured after: Soult takes Lisbon turn 9, closure
> 38.5% → 42.3%, `cs_tier_shift` fires to tier 1**; then turn 16 it falls back as
> Spain and the Kingdom of Italy make their own peace and their ports re-open —
> the arc working, fragility included. ~~**Recorded honestly:** Britain's weariness
> hits its 200 cap by turn 28 and still does not sue.~~ **← THAT CLAIM WAS FALSE
> and is corrected below (DP-1).** Suite **15,868/3**, `BASELINE_SERIES`
> byte-identical, M1–M7 green.
> Evidence: `docs/audits/NV9_NAVAL_DIORAMA_FINAL_2026_08_02.png`.
>
> **NV-8 — the user's visual pass answered** (record `NAVAL_SPEC.md` §15.10), from a
> screenshot of the naval tableau plus four asks. The ship art was rebuilt **under
> sail** (three mast columns, jib, gaff spanker, gun strakes) in the same offline
> generator as the land pieces, 24 → 32 sprites. The diorama learned a sea grammar:
> a sunk ship **founders** (heels 26°, settles, darkens) rather than toppling like an
> infantry block; no land heraldry standards at sea; STRUCK / SUNK rather than the
> land verdict words. **And the London↔Flanders sea link was CUT** — Britain had a
> 352px crossing onto one of the map's longest edges, the July-17 "Britain stood in
> Orleanais" shape; the registry drops to **18 sea links** and both adjacency folds
> go with it, with a save migration for worlds that stored the dead edge.
> `BASELINE_SERIES` re-recorded once, attributed. Ally-landing was assured in the
> same pass: the AI sails for a shore that will RECEIVE an army, which is how
> Britain lands at Lisbon rather than storming a beach.
>
> **NV-11 — the casualty spread, asked** (record `NAVAL_SPEC.md` §15.13), from the
> user's question *"did we address if the casualty spread made any sense?"* — which
> had never been asked. The **shape** checks out: a decisive action computes loser
> 55% / winner 3.9% against Trafalgar's real 66.7% / 0.0%, now pinned as a band. One
> thing did not: `_apply_side_losses` floored every loss at `max(1, …)`, so on the
> **winning** side a 1-sail ally was **annihilated every single time** (100%), a
> 2-sail ally lost half. Rounding alone is the honest rule and the historical one.
> The losing side is untouched **by arithmetic, not by a branch** — at 55% even a
> lone hull rounds to 1. Pinned as proportionality, not an exact figure, because the
> ±10% seeded jitter legitimately moves a squadron across a rounding line.
>
> **⚠ Open:** the **naval pillar score** (wants a human playing a campaign, not a
> scripted drive), the played **A2 sue-path** (§15.12 explicitly does NOT falsify the
> 80%-closure acceptance arm), the live wheel check for NV-P1, a visual sign-off on
> the new surfaces — the amber DEFENDED SHORE tint, the Admiralty chips, the
> region-panel landing chip, and the diorama in motion — and the **NV-V remainder**
> DEF-5 closes on (anchors A1–A5 in a played world, the NV-D7/NV-D8 verdicts, the Q7
> texture re-open check).
>
> **⚠ USER DECISION DUE** — its precondition (the visual pass) was met Aug 2: the
> **`Normandy↔Berry` (162px) / `Flanders↔Orleanais` (128px)** adjacency ruling
> (`NAVAL_SPEC.md` §15). The longest LAND edges out of their provinces, and the
> interior route a landed British army actually walks. Cutting them stops the walk
> inland; but adjacency here is derived from DRAWN shared borders, so cutting them
> makes the map visually lie.

> ### ✅ DP-1 — THE DEADLOCK CLOCK THAT COULD NEVER FINISH (August 3, 2026)
>
> **User direction: "fix diplomacy bug, be thorough."** Record =
> `NAVAL_SPEC.md` §15.14 (the A2 drive found it; the fix is in diplomacy).
>
> **First, a correction I owe the record.** The NV-10 entry above said *"Britain's
> weariness hits its 200 cap by turn 28 and still does not sue."* **That was
> false, and the fault was my probe, not the game** — the observer keyed on a
> proposal's `from_nation`, but an AI overture carries its source in
> `context.source_nation`, so it saw nothing and I reported nothing happening.
> Britain sued twice in that very run.
>
> **Instrumenting the real pipeline found a different and worse defect.**
> `ai_stalemate_counters` was keyed by NATION while meaning *"how many
> consecutive turns has this PAIR been deadlocked"*, and `cleanup_war_end` (R110)
> popped it for **both nations of any war that ended**. Britain fought France,
> Spain and Holland at once — so **every separate peace it signed with a minor
> reset its France clock**, and the P2 stalemate rung, which for a never-fought
> pair across the Channel needs `P2_NO_CONTACT_ESCAPE_TURNS`, could never
> finish. The reader was worse than the writer: `calculate_acceptance` looked the
> counter up under the **proposer's** name, so France asking Britain for terms
> priced France's deadlock.
>
> **Measured, same seed, 30 turns, the two runs differing in the key and nothing
> else:** legacy — the clock climbs to 14, is **wiped** at T15, climbs to 9, is
> **wiped** at T25, **and then sits at zero for the rest of the run**; pair-keyed
> — it climbs monotonically to 30 and Britain returns to the table at T15, T22
> and T29. The point is not "one more proposal": it is that **a court whose
> deadlock clock cannot accumulate stops coming to the table for the rest of the
> campaign**, and it gets worse the longer the war and the more fronts it has —
> exactly the strangled-Britain case the A2 arc exists to produce.
>
> One canonical key (`ai_diplomacy.stalemate_counter_key`) for writer, cleanup
> and reader alike. R110's intent preserved exactly — ending a war still clears
> *that* war's clock. Nothing else moved. Legacy saves' nation keys are **dropped,
> not migrated** (which war they counted is unknowable, and that ambiguity is the
> defect); cost is one clock restarting, ≤15 turns, self-healing. **Sibling scan
> clean** — `armistice_cooldowns`/`war_start_turns`/`cascade_triggered` are
> already pair-keyed and `war_exhaustion` is legitimately per-nation with R49's
> guard. `test_dp1_stalemate_counter_pair_keyed.py` (24), every assertion carrying
> a provocation control; a three-seam mutation fails 13 of 24. Suite
> **15,901/3**, M1–M7 and `BASELINE_SERIES` byte-identical without re-record.

> ### ✅ THE WOODEN WALL IS BUILT — NV-0..NV-3 LANDED IN ONE SESSION (August 2, 2026)
>
> **User direction: "start coding the navy — follow the spec, make sure nothing is
> gapped, add quality, commit and push."** That directive stands as the §12 GATE
> APPROVAL at recommended defaults (Q1 one-record model · Q2 all three arcs · Q3
> NV-D1 deferred · Q4 public counts · **Q5 naval v1 promoted into EA scope** · Q6
> numbers blessed · Q7 texture options OUT). **Landing record = `NAVAL_SPEC.md`
> §14, authoritative** — including the eight spec gaps found and closed in build
> (Amsterdam not "Holland" and East Anglia not inland-Wessex as dockyards; A4's
> worked math omitted Russia's POOLED Baltic squadron — the anchor's shape holds
> at measured 1.07/0.74/0.53; blockade requires authored naval presence; a
> conquered yard can found a ports-only court's navy; the N8 odds curve fixed and
> measured 64/12 vs anchors 55–65/≤15).
>
> - **The layer:** `backend/game_logic/naval.py` + `naval_executor.py` (four verbs
>   through the shared executor, GR5) + the authored `navies` block (15 rows, 26
>   continental ports) + validator + ONE serialized store `world.fleets` (beat
>   baselines under the `__naval__` dunder — the jealousy idiom) + the 12-step
>   checklist ×4 + 6 corpus rows + help's ADMIRALTY section.
> - **A5 THE HEADLINE, live:** Spain/France can NEVER walk Flanders→London (the
>   refusal names "the Royal Navy — 100 sail against our 54"); Britain's boot
>   descents still pass at 2.05×. The gate covers EVERY seam: moves, cavalry legs,
>   ATTACKS (an amphibious assault is refused), reinforcement musters, AI candidate
>   filters (18 sites origin-threaded — no AP thrash), charges, reckless cavalry,
>   forced retreats (demoted, with the **Corunna clause** sea-escape when cornered),
>   PF-8 `blocked_naval` stall arms, the `naval_turnback` log line.
> - **The blockade war:** Britain boots blockading (untargeted v1.0.3) — France/
>   Spain/Holland rot toward readiness 50, France bleeds the MEASURED −175 trade
>   ("Blockade") − 90 upkeep ("Admiralty") = **−265/turn, net 2,107→1,842, E1
>   absorption 0.555 still in-band (no retune)**; trade_dominance absorbs both
>   naval_income literals (Britain boots at 184 = 300 × (1−38% closure)); CS 2.0
>   closure boot fact 10/26 pinned, tiers +1/+2/+3 WE, island clause +2.
> - **Free Ireland:** the DEF-5 rider honored VERBATIM — expedition (boot odds 64
>   in the 55–65 band) → capture → clause flips → `create_client` → vassal republic
>   with the dormant `erin_free` deck that WAKES on independence; "The Irish
>   Question" grudge; once-only; GR5 predicate pinned nation-neutral; formables
>   count 5→6; Utils color measured over both perceptual floors; harp SVG imported.
> - **The Descent:** camp (staged at 2 → `boulogne_camp`) → Britain's DERIVED guard
>   flip (the blockade lapses — two-front tension, no scripting) → the Grand
>   Diversion (45% seeded, once per war; failure = fleet action at bad readiness =
>   **Trafalgar as it happened**, gutting Spain too via H6 pooled losses) → the
>   window (coverage halved, floor 0.9) → the London landing end-to-end.
> - **Conscious flips, all dated in-file:** campaign-log 142→156 (14 naval types);
>   5 economy identity mirrors gain the two components; the London-rush DEF-6 test
>   sinks the RN to keep owning the garrison layer; shape-parity exempts `fleets`;
>   **`BASELINE_SERIES` re-recorded ONCE — divergence index 5 IS the old run's
>   Channel walk**; the ambient non-player-threat liveness pin became a producer
>   probe (the ambient zero is honest — AI-3r discipline). **M1–M7 byte-identical
>   WITHOUT re-record.**
> - **Verification:** suite **15,748/3 → all green after flips** (140 naval tests
>   across 5 files); ruff clean (backend + tests); Godot import + parse harness
>   EXIT=0 (28 scripts incl. the three touched + map_connection_layer); live HTTP
>   on a fresh backend — the Admiralty block, the Blockade board naming France
>   −175, `build ships` laying a keel with the green-crew fold, the expedition's
>   honest yard refusal. Surfaces: THE ADMIRALTY ledger block (+ Blockade board +
>   Crossings verdicts + gate terms), map sea-link verdict tints + port anchor
>   glyphs (riding `naval_overlay` on the summary), the region-panel dockyard chip,
>   the war-room `naval_line`, 10 dispatch beat templates.
> - **THE NORMAN BEACH (user-directed, same session):** *"make it so British
>   land in Normandy if they do land, not in the middle of the country."*
>   MEASURED the defect first — Britain crossed at Flanders (352px, one of the
>   map's longest links) then walked Flanders→Orleanais→Nivernais→Burgundy→
>   Savoy into central France, the same shape as the July-17 "Britain stood in
>   Orleanais" defect. The registry gained **London↔Normandy** (111px — the
>   historic descent coast, well inside the map's 55–449px span range) with the
>   walkable adjacency DEF-7 requires, and Normandy now carries the SAME
>   12,000-man Channel depot as Flanders (DEF-6: a beachhead is never a free
>   walk-in — doubly so one march from Paris). **Measured after: Britain comes
>   ashore at NORMANDY on turn 1, grinding the depot down in two garrison
>   assaults before breaking out.** A5 holds on the new link (Britain 2.05×
>   passes, France 0.54 shut both ways). Left for a user ruling after the visual
>   pass: `Normandy↔Berry` (162px) and `Flanders↔Orleanais` (128px) are the
>   longest LAND edges out of their provinces and are the interior leaks a
>   landed army uses — but adjacency here is derived from DRAWN shared borders,
>   so cutting them would make the map visually lie. `BASELINE_SERIES`
>   re-recorded a second time (divergence index 9, attributed); M1–M7
>   byte-identical throughout.
> - **✅ NV-V LIVE VISUAL PASS: PASSED (August 2, 2026)** — driven in the real
>   client, fresh backend, turns 1–2. Confirmed on screen: the Channel's
>   **Y-fork of crimson SHUT links** from London (Flanders + the new Normandy
>   beach), red **anchor glyphs** on the blockaded dockyards, both 12k depot
>   markers; **THE ADMIRALTY** block complete (45 sail / readiness 70 / Adm.
>   Villeneuve, *Yards … 0/1 keels this turn* — the blockaded rate, shown =
>   applied — CS 38%, the **Blockade Board** naming France −175 / Holland /
>   Spain −100, **The Crossings** incl. *London–Normandy: SHUT — the Royal Navy
>   at 1.9×*, the Grand Diversion's three green gate terms); the signed
>   **Blockade −175g / Admiralty −90g** ledger lines with Net +1842g; the
>   region-panel **"Lay down ships (400g)"** chip on Brittany; the
>   `blockade_begins` beat in the campaign log; and `Normandy captured by
>   Britain` on turn 1 with the British red wedge sitting on the Channel coast
>   opposite England. Routed, neither caused by this phase: **NV-P1** the
>   Strategic Ledger panel ignores the mouse wheel (pre-existing — the same
>   family as the IGR terminal-wheel fix; it bites here because THE ADMIRALTY
>   renders below a long income list) and **NV-P2** recorded
>   working-as-designed (a blockading Britain stops tinting a crossing once it
>   owns both ends — §3.3's posture rule).
> - **⚠ STILL OPEN for the user:** the played-world A2 strangulation arc + the
>   naval pillar score — the rest of NV-V; DEF-5/DEF-6 close on those.
>
> **WHAT'S NEXT:** 1. **NV-V live half** (play session: visual pass + A2 arc +
> naval pillar score); 2. the long quiet-France campaign (living-balance/D1
> vehicle — can double as the naval live pass); 3. the ROADMAP spine: STEAM PAGE +
> LLC → Phase 9 (Advisors) → 10 → 11 (naval v1 now IN EA scope per Q5) → Pre-EA
> (Victory Pass) — routing = the user's call.

> ### ✅ SIGN-OFFS PASSED + THE NAVAL SPEC AUTHORED — August 1, 2026 (fourth session that day)
>
> **User direction: "mark gameplay test as passed; build naval spec — it can be
> abstracted; look into history; balance fun with lean design and usability."** Docs-only
> session: zero code, zero tests changed.
>
> - **The play-session visual sign-offs are ALL PASSED (user, August 1, 2026)** — the
>   standing UI sign-off convention has **no open items**: pin-20's Stage E+F visual half
>   (closed in `AI_INTENT_SPEC.md` header + §14 exit check + §20), the IGR-G before/after
>   pack (closed in `INGAME_REVIEW_FIXES_SPEC.md` §2/§6), the BD significance-gate feel
>   watch (closed in `BATTLE_DIORAMA_SPEC.md` — the gate ships as tuned), and the Aug-1
>   trio (forced-march line, muster committed figure, diorama refused/out-of-reach shelf).
> - **DEF-5 NAVAL: the spec is AUTHORED → `docs/NAVAL_SPEC.md` v1.0 "The Wooden Wall" —
>   USER GATE PENDING (spec §12, Q1–Q6 at recommended defaults).** The abstraction the
>   user directed: NO naval map layer — one serialized store (`world.fleets`: ships /
>   readiness / posture), two postures, four verbs, zero new screens. Four consequences:
>   the **crossing gate** (headline anchor A5 — Spain besieging London turn 5 becomes
>   structurally impossible while Britain's own boot descents still pass), the **blockade**
>   (trade ×0.5 + island-clause WE — and CS 2.0 closure gives France a **Britain sue-path
>   without invasion**, the win condition the game lacks), the **expedition** (Bantry-scale
>   evasion odds → **Free Ireland** rides the NA-6c carve machinery exactly per the DEF-5
>   rider's completion definition, deck `erin_free`, `test_naval_free_ireland.py`), and the
>   **fleet action** (Trafalgar resolver, no land-combat code touched). The §5.3 Descent
>   chain re-derives the actual 1805 math: Combined-Fleet pooling + a successful Grand
>   Diversion opens the Strait at 1.08× — and nothing less does. History table §1 (H1–H7:
>   Bantry 1796, the Boulogne window, blockade-rots-the-blockaded, Berlin Decree), numbers
>   N1–N11 + falsifiable anchors A1–A5, slices **NV-0 Admiralty → NV-1 Blockade War →
>   NV-2 Crossings & Free Ireland → NV-3 Descent → NV-V**. Deferrals all owned (§10
>   NV-D1..D8 — Copenhagen, Portugal coercion, privateers; DEF-8 explicitly NOT consumed).
>   Routing updates: MAP plan DEF-5 row, ROADMAP §Phase-11 + EA-scope note (gate Q5
>   recommends promoting naval v1 INTO EA scope), CLAUDE.md queue + Document Map.
>
> **WHAT'S NEXT:** 1. **the NAVAL GATE** (spec §12) → NV-0..NV-V build; 2. the long
> quiet-France campaign (living-balance/D1 vehicle — unchanged, can double as the first
> naval playtest once NV lands); 3. the spine: STEAM PAGE + LLC → Phase 9 (Advisors) →
> 10 → 11 (its Britain row consumes this spec) → Pre-EA. Routing = the user's call.
>
> ### ✅ THE RE-MEASURE FIX MENU — BUILT COMPLETE August 1, 2026 (third session that day)
>
> **User direction: "do the fixes from the audit but make the decision yourself to make
> the game as good as possible commit and push when done."** All six routed findings from
> the played-world re-measure (`AI_V_SWEEP_2026_08_01.md` §10) LANDED — the §Live-
> Playthrough section in `BUG_FIXES.md` is now **10/10 FIXED** and the four PT-D rows in
> `DESIGN_REFINEMENT.md` are struck with landing records. Two commits (PT-F6 isolated per
> its own harness discipline, then the rest), suite **15,572/3**, ruff clean, parse
> harness EXIT=0, boot smoke 0 SCRIPT ERROR.
>
> - **PT-F6 the AI square-thrash** (own commit): reproduced deterministically FIRST — the
>   neutered-latch control arm still walks `form → attack → form → attack → form`, the
>   exact live Moore farce — then cut to ≤1 formation per marshal per phase by an
>   execution-seam latch (`_squares_formed_this_turn`) + the in-square stance guard (the
>   S5-1 fortify guards' missing sibling, at the central candidate filter). Production
>   transcript: "forms square → counter-punches (square broken) → fortifies" — the break
>   is a choice now, not a fidget. **Harness verdict: M1–M7 + `BASELINE_SERIES`
>   byte-identical in isolation, 72/72 — no re-record for this slice.**
>   `tests/test_ai_square_thrash.py` (6).
> - **PT-F1 pursuit capture of neutral/allied soil — the delegated gate DECIDED as the
>   row recommended: (i) neutrals → the pin-15 War Purpose flow; (iii) allies/vassals →
>   pursuit ≠ conquest.** ONE predicate (`_pursuit_capture_guard`, keyed on the region's
>   controller at transfer time) guards all four capture doors (battle-advance,
>   auto-bombardment advance, glorious charge, and the reckless auto-charge's bare
>   assignment in world_state). Neutrals: the advance HALTS at the frontier and the
>   SAME `war_purpose_selection` dialogue the undefended-territory gate uses is staged
>   (closure core hoisted, shared verbatim); allies: the victor advances as LIBERATOR
>   and the province stays its owner's — the boot-Ulm strike now frees BAVARIAN Swabia
>   for Bavaria. GR5: same predicate both sides, the AI's answer is restraint (its wars
>   belong to the Stage-D machinery, never to a pursuit's momentum).
>   `tests/test_neutral_soil_pursuit_capture.py` (7, both live shapes + at-war control).
> - **⛏ `BASELINE_SERIES` RE-RECORDED CONSCIOUSLY ONCE (attributed to PT-F1, the IGR-X4
>   discipline):** a live spy on the guard found the OLD baseline world contained two
>   silent third-party annexations — **turn 5: Austria's Mack annexing BERLIN, Prussia's
>   CAPITAL, at peace with Austria; turn 6: Britain's Moore seizing Hanover's Brunswick**
>   (Hanover — in personal union with Britain). The standing baseline was built on the
>   exact absurdity the fix closes; Prussia keeping its capital is a structurally
>   different (and finally sensible) ambient Europe, series divergent from index 5.
>   Attribution clean: PT-F6 measured byte-identical in isolation first; every other fix
>   is presentation-only. Record at the constant.
> - **PT-D4 move-chains** → `main._collapse_enemy_move_chains`: 3+ hop-continuous moves
>   per marshal collapse into ONE `forced_march` entry at the view layer (after the fog
>   filter; stages = the destinations today's bullets already disclosed; origin named
>   only at FULL intel; attrition summed; conquest events preserved so a recapture chain
>   lists each fall under the one march line; own non-move action or discontinuity breaks
>   the chain; interleaved other marshals don't). + render arm in `enemy_phase_dialog.gd`.
> - **PT-D1 muster one-voice odds** → the header names the committed joint figure the
>   CO-2 verdict is priced on ("24,000; 41,000 with the muster committed"); the cautious
>   solo line says "at unfavorable odds **alone**" whenever reinforcers committed (the
>   −10% stays priced on the solo ratio — the blessed mechanic; the copy names its frame).
> - **PT-D2 diorama taxonomy** → statuses {refused, failed_arrive, out_of_reach} keyed on
>   the Session-61a trust-dock line (literal/crown = refusal BY CHOICE; low_score/fate =
>   honest failure) + **muster-promise parity** (`_inject_muster_promises`: every WILL
>   JOIN name renders with SOME status — the live Murat erasure closed); `.gd` predicates
>   read the absence family as a set so an unknown status can never render as a fighting
>   block. Spec vocabulary updated.
> - **PT-D3 letter-book coherence** → the row title follows the terms-derived display the
>   payload already carries (title always matches the lead clause); the STABLE context
>   label stays on `proposal_type` for the batching predicate.
> - Tests this session: `test_ai_square_thrash.py` (6) + `test_neutral_soil_pursuit_capture.py`
>   (7) + `test_enemy_phase_presentation.py` (13) + diorama +5/2 flipped + digest +2.
>
> ### WHAT'S NEXT — as of August 1, 2026 (a dated session record, NOT the live pointer)
>
> **[Superseded August 3, 2026. Items 1 and 3 are CLOSED — the user PASSED every visual
> sign-off on Aug 1, and DEF-5 was BUILT COMPLETE NV-0..NV-11 on Aug 2. The live forward
> pointer is the "NEXT SESSION STARTS HERE" banner in §Next Steps; this section is kept
> as the record of what the Aug-1 session handed forward.]**
>
> **THE AI INTENT PHASE IS CLOSED and the re-measure's fix menu is BUILT.** Remaining:
>
> 1. **⚠ open visual sign-offs for the next play session** (user eyes, all queued): the
>    IGR-G before/after pack (`docs/audits/IGR_G*_2026_07_31.png`); the BD
>    significance-gate FEEL watch; **pin 20's visual half for Stages E+F** (FOREIGN WARS,
>    casus-belli line, instrument chips, beats on screen); and NEW from this session —
>    the forced-march line, the muster committed figure, and the diorama's refused /
>    out-of-reach shelf in the running client.
> 2. **The long quiet-France campaign** (30+ turns, France passive mid-game) — the only
>    vehicle that can move living balance off 6.5 / measure the D1 band; can double as
>    the sign-off play session in item 1.
> 3. **DEF-5 (naval)** — the believability ceiling (Spain besieged London turn 5; the
>    Channel walks both ways). Owner row `MAP_IMPLEMENTATION_PLAN.md`; ROADMAP Phase 11
>    is its spine home.
> 4. **▶ the ROADMAP spine**: STEAM PAGE + LLC → Phase 9 (Advisors) → 10 (Character &
>    People) → 11 (Britain naval/subsidy) → Pre-EA (incl. the Victory & Objectives
>    Pass). Routing is the user's call at the next session.
>
> **Nothing is blocked on a user decision** — the PT-F1 gate was delegated and is
> decided + recorded (`BUG_FIXES.md` §Live-Playthrough).
>
> ### ✅ THE PLAYED-WORLD RE-MEASURE + FIX SESSION — August 1, 2026 (second session that day)
>
> **User direction: "do a live playthrough and add items to the most recent creative audit
> done at end of ai phase. fix any bugs found during playthrough and assess what the audit
> shows still needs improved commit and push when done."**
>
> **The addendum = `docs/audits/AI_V_SWEEP_2026_08_01.md` §10 (authoritative).** A 10-turn
> HTTP-driven 1805 campaign (`LLM_MODE=anthropic`, historical seed, active France: the Ulm
> strike → the plunder mistake → the failed march on Vienna → Kutuzov at the gates) — the
> first PLAYED re-measure the sweep asked for.
>
> - **The sweep's open evidence gaps CLOSED in play**: the autonomous glory-attack fired
>   organically (Murat vs John, fore-warned, mauled); emergent Revanche promoted BOTH ways
>   incl. **Britain-vs-Spain** (an AI-vs-AI grievance authored by play); the §3.5 mirror
>   inverted ("A great power in Austria's shadow", hegemon share 0.0) and the log's
>   hegemon read flipped to "Austrian-led alignment"; enemy courts endowed dukes on
>   conquered FRENCH soil (Charles→Languedoc, John→Piedmont, Moore→Lorraine); Britain
>   sponsored Sweden AND Russia against France; the war-score-aware offer arrived shaped
>   and directed correctly.
> - **The living balance HOLDS at 6.5** — `foreign_wars` stayed `[]` all 10 turns; no
>   standalone AI-AI instance, no council war (D3 compresses a France-centric war onto the
>   player, as designed). The re-measure that can move it = a 30+-turn campaign where
>   France goes quiet mid-game. **NEW measured pillar: the enemy phase as theater 5.5** —
>   square-thrash, move-chain teleportation, contradictory odds frames; the concrete
>   mechanism behind July-25's "narration 6.0".
> - **10 defects found, 8 FIXED in-session** (`tests/test_playthrough_fixes_2026_08_01.py`,
>   12): the fortify objection-then-failure hierarchy violation; "proceed"-during-objection
>   misrouted to the diplomatic channel; the capture hint recommending ALLY/VASSAL soil
>   (Bavaria's Franconia, Holland's Gelderland); "(Iron Marshal:" captioning every cautious
>   marshal (3 sites the July-9 sweep missed); the stale status-quo clause on the
>   `/pending_envoy` delivery surface (the July-25 activate fix, one surface over);
>   typed "reject the offer" unable to reach the on-screen offer (options live in
>   popup_payload + article-tolerant matching); **Mack's ghost** (a captured marshal is
>   held at the captor's capital at strength 0 BY DESIGN — the movement engaged-filter was
>   the one filter missing `strength > 0`, so the prisoner pinned Mortier inside Paris);
>   the self-contradicting surrounded-retreat note. M1–M7 + `BASELINE_SERIES` verified
>   byte-identical after the fixes (no re-record).
> - **2 ROUTED with owner rows** (`BUG_FIXES.md` §Live-Playthrough): **PT-F1** pursuit-battle
>   capture of neutral/ALLIED soil carries zero diplomatic consequence (Nassau taken from
>   at-peace Hesse → relation 0 + a non-aggression letter; retro-find: Swabia is BAVARIAN
>   at boot, so the Ulm capture took an ally's province) — needs the small pin-15-family
>   gate; **PT-F6** the AI square-thrash (forms/breaks square ×3 in one phase) —
>   harness-sensitive, own slice with the conscious-re-record discipline. Plus 4 design
>   rows PT-D1..D4 in `DESIGN_REFINEMENT.md` (muster one-voice odds, diorama
>   refused-vs-failed taxonomy, letter-book label coherence, move-chain presentation).
> - **Ranked "still needs improvement"** (addendum §10.5): 1. enemy-phase composition
>   (PT-F6 + PT-D4), 2. **DEF-5 naval urgency upgraded** — Spain besieged LONDON on turn 5;
>   the Channel walks both ways, 3. PT-F1, 4. the D1 conjunction (long-campaign vehicle),
>   5. diorama taxonomy, 6. letter-book labels.
> - The pin-20 E+F **visual** half stays on the user's open list (this session verified the
>   payloads over HTTP — foreign_wars shape, casus-belli field, instrument chips with live
>   prices, beats in the dispatch stream — not the pixels).
>
> *(The fix menu this session queued — PT-F6 + PT-D1/D2/D4, the PT-F1 gate, ranked in
> §10.5 — was BUILT COMPLETE the same day by the third session; see the top entry. The
> living WHAT'S NEXT is there.)*
>
> ### ✅ AI Intent Stage G — "The Reckoning" — RAN August 1, 2026 (the phase closes)
>
> **User direction: "code this commit and push." Landing record = `AI_INTENT_SPEC.md` §20
> (authoritative); evidence = `docs/audits/AI_V_SWEEP_2026_08_01.md`.** Suite **15,528/3**,
> ruff clean, zero production diffs, campaign-log pins untouched at 142, M1–M7 green,
> `BASELINE_SERIES` asserted verbatim by the new control-arm pin every suite run.
>
> - **`tools/ai_v_sweep.py`** — the committed three-arm + scripted-France driver (the
>   AI-3r probe was session-scratch; the acceptance harness is not allowed to be).
>   Read-only capture (the IGR-B event-log eviction trap handled by per-turn id-drain),
>   ambient idiom byte-compatible with the pin-16a baseline, subprocess-per-run
>   determinism, and the FranceScript arm whose seven run-N findings are documented at
>   their fix sites (a map of the engine's real seams: the pre-crisis guarantee deterring
>   its own receipt · the income phase repaying staged bankruptcy before the poll · the
>   busy-holder staging flipping the coveter into the BANDWAGON branch · the war_1 fold
>   window · the idle-mailbox dedup deadlock · `decision_reason` at context level).
> - **`tests/test_ai_intent_assurance.py` (43)** — Arm A control in-suite; Arm B variance
>   (spec triple + Tier-1 deck invariance); arm-(a) DoD pins (channel discrimination, Q3
>   shapes, cap-in-the-wild, both mirror directions, courting, soap-opera number, beat
>   texture, exhaustion-driven pair peaces, the machine-readable formation predicate, pin
>   21 run-level, the WARTIME homogeneity guard); arm-(b) scripted pins; the §13 **Q2
>   multi-front set** (fold semantics measured; peace/armistice isolation byte-pinned;
>   exhaustion survives a partial peace; settlement-track independence through the real
>   machinery; rear reserve max-not-sum pinned clamped AND unclamped); both-sides kits.
> - **One false alarm dissected, no production defect**: the reserve "growing" under a
>   second front is third-party relations cooling a band (two aggressive declarations
>   chill Russia 0.3→0.6) — max-not-sum intact.
>
> ### ✅ AI Intent Stage F — "The Stage" — LANDED August 1, 2026
>
> **User direction: "whats next commit push and assure status updated." Landing record =
> `docs/AI_INTENT_SPEC.md` §19 (authoritative).** Suite **15,485/3**, ruff clean, parse
> harness 25/0, headless boot 0 `SCRIPT ERROR`, new payloads live-verified over HTTP
> (a STALE backend answered first — killed per the hygiene memory, re-verified fresh).
> ONE new serialized field (`nation_intent_seen`); campaign-log count pins untouched
> at 142 (the routine lines are dispatch-only by design).
>
> - **AI-6**: `intent.process_intent_movements` — routine ladder movement as dispatch
>   news (`intent_hardens`/`intent_eases`), detected on the new seen-map (first
>   observation silent, want-changes silent — agenda_shift owns them, survival silent),
>   CAPPED at 2 lines per dispatch ranked by weight × proximity-to-French-interest
>   (2.0 concerns-France / 1.5 borders-the-bloc / 1.0 far), overflow collapsed into one
>   grammatical "other courts stir" tail. The cap lives in the PRODUCER so the beat
>   exemption is structural; `NARRATION_EXEMPT_EVENT_TYPES` enumerates the seven
>   dispatch beats + `design_promoted`/`volte_face` (the §18.1 handoff discharged).
>   `test_relevance_beats_raw_weight` pins §4.6's own sentence: a weight-90 Danube
>   quarrel loses both slots to weight-50/48 France-concerned designs.
> - **AI-6b**: the tempo pin written FRESH (nothing had asserted it): two LIVE crises →
>   exactly one foregrounded after the war-council promotion pass, the oldest first.
> - **AI-6c**: `build_active_wars` gains `foreign_wars` (sides leader-first with
>   formation-aware names, duration, the Stage D `stated_reason` stamp — court
>   knowledge, no fog — and leader exhaustion fogged PARTIAL+ like the France rows);
>   France's own rows carry `stated_reason`; `war_status_panel.gd` renders the dim
>   FOREIGN WARS section (panel stays alive when France is at peace — exactly when
>   Europe's wars matter) + `war_detail_popup.gd`'s "Casus belli:" line;
>   `diplomacy.py._instrument_actions` appends sponsor/buy-off/guarantee chips to the
>   wizard's action list with availability mirroring the executor's gates IN ORDER
>   (DP preflight first — the house "Insufficient DP" copy, aligned after the suite
>   caught the drift), live buy-off price in the label, deck-scoped design verbs
>   (recorded decision), vassal courts excluded by the early-return branch;
>   `diplomacy_wizard.gd` echoes the golden-corpus typed commands (the chip payload
>   carries the aim). End-to-end honesty pinned: an available chip's typed command
>   succeeds through the real executor.
> - Tests: `test_ai_intent_narration.py` (19) + `test_ai_intent_client_surfaces.py`
>   (19); one pre-existing pin (`test_insufficient_dp_grays_out`) caught the DP-copy
>   drift and the chips were aligned to it, not vice versa.

### ✅ AI Intent Stage E — "Consequence and Character" — LANDED July 31, 2026

**User direction: "do next step of project code and commit and push when done, feel free
to improve upon anything the spec is weak or unclear on." Landing record =
`docs/AI_INTENT_SPEC.md` §18 (authoritative).** The whole Stage E row shipped, both slip
candidates included — beat 5 fires under the harness, so the written-predicate fallback
was never needed. Suite **15,437/3 at `ddf7b05`, 15,447/3 after the §18.1 review round**, ruff clean, M1–M7 + `BASELINE_SERIES`
byte-identical (no re-record needed), zero new serialized fields, zero `.gd` diffs
(pin 20's live pass belongs to Stage F, as sited).

- **AI-5b(i) emergent designs** (`backend/game_logic/emergent_designs.py`): the
  humiliated court promotes its grievance into a REAL front-inserted `acquire_regions`
  entry ("Revanche") riding the serialized deck store — derived partition/capital-loss
  triggers + the new durable `punitive_settlement` memory written at ALL THREE ratify
  seams (multilateral, third-party, bilateral — from APPLIED clauses only) + the §3.3
  renege-grievance route; max one per nation ever; player + vassals excluded; survival
  override outranks then activation-on-clear (constraint (c), both halves pinned);
  announced as the `design_promoted` beat (town-crier visible).
  `get_agenda_grudge_nations` generalised to `(victim, author)` — player default
  byte-identical.
- **AI-5b(ii) the volte-face**: `volte_face_receptive` (beaten within 15 turns + defeat
  still showing + NEVER punitively stripped + courted to the alliance floor 40) → the
  beaten court PROPOSES the alliance itself (P-VolteFace, sited above P-Intent/P3 —
  at boot threat 85 a shelter-first ordering would silence the beat forever) → beat 5
  fires at the `_ratify_treaty` ALLIANCE chokepoint, and the deck-advance is FREE
  (in-bloc containment goes dormant → Russia turns to `gulf_and_straits`, §12.2's
  object; if the alliance breaks, containment wakes — Tilsit collapses into 1812
  unscripted).
- **AI-5c the Arbiter's Offer**: `process_mediation_offers` — a non-belligerent
  contain-design major (incl. a court that separate-peaced OUT of the very war — the
  Tilsit-Russia ruling) offers brokered terms over a weary French war (WE floor 60)
  through the EXISTING incoming-settlement machinery (a `mediator` provenance on the
  same offer/popup/accept/reject plumbing — no new dtype). Accept credits (+8
  relations); refusal is derived-only: the pin-8 refusal record + intent's new
  `WEIGHT_MEDIATION_REBUFFED` (+6, expires with the record's 12-turn window) — refusing
  mediation IS the coalition ramp, by machinery.
- **The wires**: NA-5 gated on the CLIMBED ladder (`against == player` + rung ≥ coerce;
  fixtures re-tuned to the real derivation — Potsdam's arithmetic; yield → descent
  pinned) · P1.75 commissions while PREPARING (coerce+ at peace — Blücher before Jena) ·
  jealousy's glory hunt prefers the nation's design frontier (deckless byte-identical) ·
  the bandwagon→vassalage on-ramp (`offer_vassalage` "Offer of Submission" at the
  exhausted ALLIANCE rung, relation ≥ 40, WPS-B cap pre-checked both sides — voluntary
  loyalty 80; the AI-hegemon mirror submits in place) · formations proven end-to-end
  through the Stage D settlement path (assurance, no new code) · economy verified
  landed (sponsor executor = AI-2b's record; paymaster stays the special case;
  WE→intent read pinned).
- Campaign-log types 140 → **142** (`design_promoted`, `volte_face`; five count pins
  flipped consciously); both beats HIGH dispatch templates + one-liners.
- **A four-lens adversarial review (correctness · pins/GR · falsifiability · design
  fidelity) then confirmed 1 P1 + 3 MED + 8 LOW — ALL FIXED pre-push (addendum §18.1)**:
  headline P1 — the mediation producer was structurally DEAD in production (the standard
  offer producer runs first and consumes every eligible war) and aimed at the wrong wars;
  re-gated so the per-war clock is transparent to the arbiter while a live offer still
  blocks — the arbiter now steps in exactly when the belligerents' own courier is spent
  (Prague 1813), regression-tested on the real pipeline sequence. Plus: the punitive
  record refined to HOMELAND-ONLY with the author charged over the same filtered set
  (surrendering conquests is the fortune of war, not a partition — a mis-charged durable
  author could have volte-face-foreclosed the wrong pair forever); the volte-face courier
  deck-gated (pin 18/N1) + never re-proposing to a standing ally; the on-ramp's two arms
  made floor-identical (band ≥2 both sides, release-cooldown pre-checks, AI cooldown only
  on a SEALED submission); bilateral wars pinned unmediatable as a recorded v1 bound; two
  masked negative controls closed (the NA-5 against-conjunct, the bandwagon-rung floor);
  the coerce-climb fixture arithmetic corrected in place (measured weight 80, not 74 —
  the allies-committed +6 also fires); and the Stage F handoff recorded — AI-6's cap
  pins MUST enumerate `design_promoted`/`volte_face` beside the seven beats.
- Tests: `test_ai_intent_emergent_designs.py` (43) + `test_ai_intent_system_wiring.py`
  (18) + `test_ai_intent_mediation.py` (14); ultimatum + phase-audit fixtures re-tuned.

### ✅ IGR-E — Plunder earns its prompt — LANDED July 26, 2026

**User direction: "code IGR-E ... commit and push when done", with the recorded dissent
explicitly carried forward.** Landing record = `docs/INGAME_REVIEW_FIXES_SPEC.md` §2 IGR-E
(authoritative). **Four commits, all pushed:** `c7e30b9` (the slice) + `88e2707` (the GR5
addendum) + `cec49f6` (docs) + `e6c0d42` (the post-landing adversarial review — 3 P2 +
10 P3, all fixed; see the review paragraph below). Final: suite **15,287/3**, ruff clean,
parser eval 461/461, M1–M7 and `BASELINE_SERIES` byte-identical, parse harness EXIT=0,
headless boot 0 `SCRIPT ERROR`. `tests/test_igr_e_plunder_prompt.py` (**38**).

**The number.** `PLUNDER_GOLD_MULTIPLIER = 1.75` → `PLUNDER_INCOME_MULTIPLIER = 4.0`,
renamed to the name gate Q4 actually blessed and kept a single source (a second constant
over the same base is the dual-source defect GR1 forbids).

**⚠ The gate's worked example is wrong, and the record corrects it rather than conforming
to it.** §5 Q4 illustrates option (a) as *"Nassau pays ~450–750g"*. **At ×4 Nassau pays
200g** — its `income_value` is 50, the **minimum** on the 126-province map (27 provinces
share it). The 450–750 band is `150 × 3–5`: the **median** province (41 of 126) labelled
with the poorest one's name. Measured ladder: 50→200 · 100→400 · 150→**600** · 200→800 ·
300→1,200. **Nothing was re-gated** — the gate's *shape* text ("~3–5 turns of its income")
is exactly what ×4 satisfies.

**The acceptance test passes in both directions**, as arithmetic over the production
formulas rather than judgement. Poor+early: the loot is ≥10% of the gate's 2,000g anchor
**and** exceeds the revenue it destroys over 5 turns (600 vs 315 at the median).
Rich+late: ≤6% of 20,000g **and** converges to within 15% of break-even over 30 turns.
The inversion is the point — the loot is one-time while forgone revenue keeps accruing
until it plateaus. A **negative control** re-runs arm A at the old ×1.75 and asserts it
**fails**, which is what makes the test evidence rather than decoration. One published
break-even model, in the test, derived from `Region`'s own methods with the **ES-2
occupation cost** included — the term that makes it honest.

**Quadrupling a number the player never sees changes no decision**, so the second half is
the prompt. Before this, *no* surface stated what Plunder would pay: the payload carried
three keys, none economic; the buttons were string literals; the terminal asked "How shall
they behave?"; and the Region Action Panel shows *effective* income, which for a
just-captured province is **0g**. Now one builder serves both capture routes, one
expression both quotes and pays (shown = applied), and the figure appears on the modal
button, the terminal sentence, the occupation message and both refusal restatements.
Stage 1 also mints a W6-0 `dialogue_id` it never had — the stale-answer guard was
structurally **inert** — with zero client wiring change.

**GR5 addendum, own commit: the AI could never plunder, on any board, ever.** Both AI
sites read a `personality_type` attribute `Marshal` does not have. (The second trap:
`Personality` has no `str` mixin, so reading the right attribute while still comparing to
the enum member leaves it just as dead — now pinned.) Measured on the pinned ambient run:
**41 capture choices, 100% `secure` → 39 secure / 2 plunder**, both by Britain's Paget.
`BASELINE_SERIES` stays byte-identical anyway, this time for a *design* reason: threat
accrues on the conquest, not on what the conqueror does afterwards. **Two of the three
tests that "proved" GR5 parity manufactured the missing attribute**, which is what let
them pass against dead code; one failed the instant the production fix landed. The guard
meant to catch exactly this was scoped to `enemy_ai.py` alone — now an **AST** check over
the whole backend, mutation-tested.

**Routed, not absorbed** (`BUG_FIXES.md` §IGR-E, each with owner/landing/done-when/test):
**IGR-X4 (P2)** the W6-8 estate confiscation windfall is **always exactly 0 gold** — it
reads effective income after stage 1 has left stability ≤ 25, so the player is asked to
pay relations and trust for nothing; this is IGR-E's own pathology one stage deeper, and
its fix is a *shape* change to a blessed W6-8/ES-7 number, so it escalates. **IGR-X5 (P3)**
a strategic-march capture never asks and never secures. **IGR-X6 (P3)** `region.plundered`
has no mechanical readers.

**⚠ The dissent survives the edit** and now lives in five places: the landing record, this
entry, the struck `DESIGN_REFINEMENT.md` IGR-D1 row, a comment at the constant, and the
acceptance test's docstring. **Attempts used: ONE of two.**

**Post-landing adversarial review (same session — 8 find lenses → per-lens refuters →
synthesis, 17 agents): no P1; 3 P2 + 10 in-scope P3 confirmed, ALL FIXED** (fourth
commit; spec §2 IGR-E carries the addendum). The P2s: **the newly-live AI branch would
sack its own recaptured homeland** — an aggressive commissioned marshal retaking his
nation's capital would burn its buildings and pay himself ×4 to loot himself; fixed
with an own-soil guard in the single source (starting-controller check; the player's
own-soil modal deliberately untouched; ambient tally unchanged at 39/2 — Paget sacks
Brabant and Ile-de-France, neither British — `BASELINE_SERIES` byte-identical).
**The published break-even model omitted the EC-U2 damaged-structure bill** — Secure
keeps enemy structures damaged (yielding nothing, billed 40g/turn) while Plunder
deletes bill and asset, so on a BUILT province razing wins at any multiplier
including ×0; the term is in the model now, the case published as a
multiplier-invariant test, and the design question homed as **IGR-X9** (it can never
touch the dissent counter — the acceptance test judges the multiplier and this term
is invariant to it). **And the record's "the inversion is the point" was false under
its own model** — garrisoned, the choice converges with a ≤4% permanent plunder
sliver; the true inversion is ungarrisoned (772 > 600 at the median); the record is
corrected in place and the test renamed. The P3s: one shared `apply_plunder_effects`
(the occupation branch's inlined copy dropped the per-building events), pre-IGR-E
saves backfilled at load (a live question was quoting "+0 gold" and paying 800; a
genuinely unresolvable one now omits the figure), the dead `region_income` key
deleted, one gold-formatting idiom everywhere, the single-source and negative-control
tests made falsifiable, exact-line `.gd` pins, and the band documented as
permission-to-try (the criteria admit exactly ×4). Pre-existing findings routed:
**IGR-X7** (capture responses drain the PopupQueue), **IGR-X8** (uneven capture
surfaces), **IGR-X9**. `test_igr_e_plunder_prompt.py` 30 → **38**.

### ✅ IGR-X3 — A beaten enemy signs; it does not have to like you first — LANDED July 26, 2026

**User direction after the recommendation was put to them: "Everything, incl. armistice
thaw".** Landing record = `docs/BUG_FIXES.md` §IGR-X3 (authoritative). Commit `0a62c54`.
Suite **15,234/3** at landing, `tests/test_igr_x3_peace_relation_floor.py` (33).

`STATE_RELATION_REQUIREMENTS["PEACE"]` is now `None`. Ending a war is not an act of
friendship — Pressburg and Tilsit were signed at the maximum of mutual hatred *because* of
how the war had gone. What prices a peace is war score, position and exhaustion, all of
which `calculate_acceptance` already weighs. **The rows above PEACE are untouched**:
`validate_transition` permits any upward jump, so they are the only thing preventing
`WAR → ALLIANCE`. Nobody has to like you to stop shooting; somebody does have to like you
to march beside you.

**The truce now actually cools tempers** — `_process_relation_decay` no longer lumps
ARMISTICE in with WAR. `ARMISTICE_THAW_PER_TURN = 3`; WAR still freezes. Measured:
Britain −90 → −75 over one five-turn truce, and a second carries it to −60 and
`armistice_expired_peace`.

**Plus the two P1s that were independent of the floor:** `_handle_accept_ai_proposal`
reported a *refused* ratification as an acceptance (measured verbatim: `success: true`
with *"You have accepted Britain's proposal. Relations with France are insufficient for
PEACE"* — offer consumed, cooldown applied, war carrying on); and the one place the game
taught the escape described a mechanism that did not exist.

**⚠ Three claims in the bug row were wrong, one of them mine.** "Can they recover? No" is
refuted — `mission_improve_relations` IS offered in the ARMISTICE branch, so the war was
endable by an undiscoverable ritual, not impossible. The IGR-D residual's −95/−100/−95
boot relations are wrong; −90/−80/−80 are right. And the floor was never gate-blessed: it
was authored as the armistice-EXPIRY branch condition and switched on when a cleanup
commit wired a function that had been dead for three days. **Option (b), war-score-aware
relief, was NOT built — it is inert**: `cleanup_war_end` pops the war score on any
WAR→non-WAR transition, so relief at ARMISTICE would always be 0.

**⚠ Byte-identity finding, reported not buried.** M1–M7 and the 40-turn `BASELINE_SERIES`
are unchanged — and the honest reason is that **the ambient harness never enters ARMISTICE
at all** (measured: 0 armistice turns in 40). The thaw is symmetric and WILL move AI-AI
relations in a played game; the harness cannot see it.

**Five tests consciously flipped or re-sited**, including
`test_conflict_alert_accept_anyway_ratifies` — which had been asserting a lie since it was
written: its fixture never cleared the ALLIANCE floor, so the treaty it claims to ratify
was refused and the handler reported success anyway. It only went red once the swallow was
closed.

### ✅ IGR-F — The small courts write one letter, not five — LANDED July 26, 2026

**User direction: "build IGR-F per spec §2. No gate."** Landing record = spec §2 IGR-F
(authoritative). Commits `7b91928` (build) + `0d14db7` (the live pass). Suite **15,201/3**,
ruff clean, parser eval 461/461 mock, M1–M7 and the 40-turn `BASELINE_SERIES`
byte-identical, Godot parse harness EXIT=0, headless boot 0 `SCRIPT ERROR`,
`tests/test_igr_f_envoy_digest.py` (83), **20-mutation sweep 20/20**.

Routine asks from the lesser courts (`open_borders` / `non_aggression` / `friendly_gift`
from a non-major tier) stop arriving as N sequential blocking modals and ride one derived
**letter-book** instead — the existing mailbox panel, with per-row Accept/Decline and each
court's own spoken line given room. **No PopupQueue slot** (the 11-key pin holds), **no
campaign-log type** (140 holds), **no new dialogue dtype**. One new endpoint,
`POST /mailbox/respond`, activates and answers atomically.

**A 37-agent seam-verification fleet ran before any code was written and corrected the
spec twice:**

- **`tier == "minor"` is the wrong predicate.** Reis Efendi is the **Ottoman** diplomat and
  the Ottoman is authored `secondary` — a minor-only test would have left untouched one of
  the two voice lines the review named as being flattened. It is `!= "major"`. And tier
  alone is not enough at all: **a minor court suing for peace arrives on the identical
  `incoming_proposal` dtype**, so the predicate is a conjunction with a positive type
  allowlist keyed on the *stable* `context["proposal_type"]` — `terms["type"]` is
  rewritten downstream, and keying there would batch a `design_purchase` province cession
  as routine mail.
- **"3–5 per turn" is not what the board does.** Measured over 20–25 ambient turns on two
  independent harnesses: the maximum routine small-court deliveries in any single turn is
  **2**, in every run — `MAX_BANDWAGON_PER_TURN` binds. The real shape is a **relentless
  2-per-turn drip from the same seven courts on 9–16 of 20 turns**, with 11 of 41
  generated proposals silently discarded by the throttle, 100% minor-tier.

**A pre-existing P1 fixed in passing, reproduced by hand before it was accepted:** the
popup slot was written unconditionally while `push` makes only the FIRST arrival current,
so on any multi-proposal turn the client rendered the LAST letter and its id-bound answer
hit the W6-0 stale guard. Measured — three letters delivered, the response carried
PapalStates (dialogue_id 3), the active dialogue was Bavaria (dialogue_id 1), Accept came
back *"another matter has arrived since"*. **The multi-court surface this slice exists to
fix was already unanswerable.**

**The seam that produces the storm is the safety valve** (`main.py:837-854`), which
re-derives a modal from the active dialogue on *every* response cycle — literally
"interrupts a command in flight". `pop()`/`_promote()` deliberately untouched.

**The digest is NOT a route-table entry, and that is the whole reason it works.** Every
`_post_hud_response_routes` entry returns from `_on_command_result` before
`_display_result`, so routing it would have swallowed the output of whatever command the
player had just typed — replacing a storm of modals with a surface that eats your orders.
It follows the NA-6b discipline: stashed on arrival, raised from the control-return tail
behind the Proclamation, latched per turn, blanked on the `enemy_phase` response.

**✅ VERIFIED LIVE** — `docs/audits/IGR_F_LETTER_BOOK_2026_07_26.png`. Prussia's
great-power modal fired first and alone; the command's own output was not swallowed;
*THE SMALL COURTS WRITE (2)* rendered Reis Efendi and Araujo in full with their own
Accept/Decline; one inline click signed PEACE → OPEN_BORDERS and dropped the badge 2 → 1
with no result modal; the row body still opened the full popup with its Counter arm; and
dismissing then typing another command did **not** re-raise the panel. **One defect found
by playing it, fixed in-slice:** the panel's authored rect is a *ceiling* for
`clamp_centered_panel`, so at 600×400 the taller letter rows clipped the second letter —
raised to 960×720.

**Two of my own tests were inert and both are fixed** (proven by mutation), plus a drive-by:
`test_nation_agendas_formables.py:1310` scraped a fixed 200 characters after
`_on_proclamation_dismissed` and de-bound the moment another control-returning branch was
added ahead of the re-enable — the same false-satisfy shape IGR-B's review found in the
NA-6 dead-name pin. Now bounded by the next function.

---

### ✅ IGR-D — The carve becomes completable — LANDED July 25, 2026

**User direction: "Build IGR-D per spec §2", gate Q2 already decided as a SPLIT (spec §5),
plus "make the payoff for forming duchy good as well". Landing record = spec §2 IGR-D
(authoritative).** Suite **15,107/3**, ruff clean, parser eval 461/461 mock, M1–M7 and the
40-turn `BASELINE_SERIES` byte-identical, Godot parse harness EXIT=0, headless boot
0 `SCRIPT ERROR`, `tests/test_igr_d_carve_completable.py` (49).

A 12-reader + 3-refuter verification fleet ran before any code was written, and it earned
its keep: it found that the carve must ride `demands` (`_ratify_treaty` reads
`proposal["clauses"]` exactly once, as a bare string test), that the counter-offer strikes
the carve first every time, and that `main.py` keeps a module-level `world` **separate**
from `game_state["world"]` — the executor reads the dict, the response layers read the
global, and setting only one runs the command on one world and builds the response from
another. That last one is why the first delivery test failed while every unit test passed.

- **Arm A — `create_client` carries into the pair-substitute bilateral peace.** The apply
  body was **extracted** into `formations.apply_create_client_clause` and both routes call
  it, so the whole NA-6c §20.1 review (live re-read, active-tag refusal, the
  four-condition elimination gate) is inherited rather than re-earned. The settlement path
  is byte-identical. Eligibility is re-validated on the new route through the *same*
  `evaluate_create_client_eligibility` — never a forked predicate — and it earns its place:
  in live probing it correctly refused twice, once when Prussia retook Posen during the
  transit turn and once when **Russia** walked into it.
- **Four defects found in passing, none named by the spec:** the counter-offer amputated
  the client state and never said so; `applied_treaty_clauses` omitted it, so the
  ratification summary did not mention what was signed; a carve-only Tilsit logged as a
  **`white_peace`**; and a **third** harshness dialect scored it 0.0, so Talleyrand judged
  a dismemberment "too generous" and bolted an unauthored 50 g/turn tribute onto it.
- **⚠ The price was retuned after measurement.** The real defect was *saturation* — on any
  realistic package the carve moved acceptance by **exactly zero**, because harshness
  clamps. My first number (the ×50 harshness mirror) fixed that but measured **40 against
  the bar of 50 for a victor holding ALL of Prussia** — it would have shipped the same
  defect wearing a different hat. Re-derived from the table's own territory rate: a victor
  holding all of Prussia now lands at **54**, one holding only Posen at **34**.
- **Arm B** reads the same carried-types set as arm A, so the split cannot drift, and needs
  **zero** new refusal codes and **zero** new Godot machinery. Scoped to the PEACE arm;
  G4F-15 governs the truce and disabling it too would leave a blocked player no exit.
- **The carry promise had three producers and only one was honest** — the `.gd` body text
  hardcoded the flat guarantee, so the July-25 R5 fix only ever reached a hover tooltip.
- **Payoff (user-directed):** the client was born at loyalty **30**, five below the
  disaffected line, with **no patron relation seeded at all** — it refused every call to
  arms, was bribable on day one, and rebelled in ~15 turns. `CARVE_LOYALTY` 30 → **60** and
  a new `CARVE_PATRON_RELATION = 40` (which exactly cancels the satellite drift) make it
  stable, loyal, and useful — using the drift system's own levers rather than exempting the
  carve from them. The relation outlives vassalage, so a Warsaw later freed to proclaim
  Poland stays France's friend.
- **✅ Must-see #4 CLOSED — the Proclamation was sighted in-client** (screenshot
  `docs/audits/IGR_D_PROCLAMATION_2026_07_25.png`): real client, real backend, the carve
  carried into a peace with Prussia alone. *"it answers to France as a satellite (loyalty
  60) · it marches when France calls, and pays tribute … By your hand."*
- **Post-landing review (8 lenses x 2 refuters, 39 agents): 5 production + 10 test defects
  fixed; a 10-mutation sweep now catches 10/10.** The headline is that the slice
  **re-committed its own defect one surface downstream** — `terms_ratified` was annotated
  from the SUBMITTED proposal, so a carve the new gate correctly refused still told the
  player the Duchy had been erected. Not hypothetical: my own live probing hit that refusal
  twice (Prussia retook Posen; then **Russia walked into it**). Also fixed: `subjugation`
  was in neither the carried set nor the labels (silently dropped, and the guard test
  iterated the very dict it was missing from); the split left an *ally-beneficiary* carve
  as the one clause dropped with no word; the armistice arm stopped naming what it
  abandons — the arm arm-B funnels blocked players onto; and Talleyrand still called a
  dismemberment "too generous" on the slice's own blessed package.
- **Ten of my own tests were vacuous**, each proven by reverting the production fix and
  watching the test stay green — the counter-offer fix had **zero** coverage, and arm B's
  entire coverage was source-string matching that already passed on master.
- **Residual, stated not hidden:** bilateral peace with a **boot** enemy is unreachable
  (the pre-existing −60 relation floor vs −95/−100 boot war relations, decay skips
  WAR/ARMISTICE). The reviewed Prussia case — and Tilsit — measures −40 and works.

### ✅ IGR-B — The campaign log becomes readable — LANDED July 25, 2026

**User direction: "Build IGR-B per spec §2", gate Q1 already decided (spec §5, option (a)).**
**Landing record = spec §2 IGR-B (authoritative).** Suite **15,057**, ruff clean, parser eval
461/461 mock, M1–M7 green, the 40-turn `BASELINE_SERIES` byte-identical,
`tests/test_igr_b_campaign_log_readable.py` (46). **No `.gd` diff.**

One pure `campaign_log.collapse_refusal_family(events)`, called from `GET /campaign_log`
*after* `filter_campaign_log` (never inside it — 51 test call sites own that contract),
bucketing by `(turn, proposal_type)` **within the refusal family only**. A bucket of one
passes through as the same object; a bucket of N is one shallow copy of its first member
carrying display-only `collapsed_count` / `collapsed_pairs`, which `format_event_oneliner`
renders as an adaptive sentence. **The producer is untouched by design** — both emission
sites are gated on `record_diplomatic_refusal`, the writer of `world.diplomatic_refusals`
that AI-3's ladder gate reads.

- **The acceptance case moved: the burst is turn 3, not turn 9.** The spec's raw table was
  read off a `world.event_log` already truncated by `MAX_EVENT_LOG_SIZE=500`, so it never saw
  turn 3's **69** emissions — 3.3× the wave it named — and **turn 9's 21 refusals are 100%
  fog-filtered**, which would have made the "≤5 events" test pass on a 1-event page. Turn 3 is
  what reproduces the live review's 24/25: 26 visible rows, 23 refusals.
- **Measured result on turn 3: 26 rows → 5, refusals 23 → 2, and the buried `agenda_shift`
  rises from index 25 of 26 to index 4 of 5** — visible without scrolling, which was the whole
  point. Turns 2/5/6/12/13 collapse proportionally.
- **Two P1 hazards, both found by verifying the spec against master and reproduced by hand
  before any code was written.** (1) The bare `(turn, proposal_type)` key is *not* unique to
  refusals — `diplomatic_proposal_sent` (the player's own), `proposal_arrived` and
  `offer_lapsed` share the vocabulary and all take an "always show" branch; a bucket of two
  non-refusals collapsed and **deleted one**, and `offer_lapsed` lands on turn 3 itself. The
  function gates on `type` first. (2) `filter_campaign_log` returns *originals, not copies* —
  the very dicts `world.to_dict` serializes — so stamping `collapsed_count` in place would
  have baked view state into every save from that moment on.
- **Pinned unchanged across a real `GET /campaign_log`:** `world.diplomatic_refusals`,
  `len(world.event_log)`, AI-3's `_ladder_climbed` (×30 court pairs), event-log element
  identity, and the absence of any `collapsed_*` key from the serialized save.
- **`CAMPAIGN_LOG_TYPES == 140`** still holds — no new event type, no schema change.
- **The residual is stated, not hidden:** the 500-event eviction is producer-side and worse
  than the spec said (**342 of 842 events, 41%, evicted by turn 21 on a zero-action run**).
  Not folded in — the honest lever changes `get_refused_asks` cardinality and therefore AI-3.
- **A 59-agent find→refute review then took 8 more fixes**, four of them against my *own*
  tests, each reproduced by hand first: the save-corruption gate ran over a bucket the fog
  filter had already reduced to one (so nothing collapsed); both AI-3 pins compared
  all-False to all-False on an empty refusal record; the "fresh list" test appended to a
  list and asserted a *key* was absent; and nothing pinned that the collapse runs AFTER the
  fog filter. Headline behaviour fix: **the sentence branched on how many courts there were
  and not on which ones mattered**, so a measured live burst of `{Prussia 10, Austria 4,
  Denmark 1, Bavaria 1}` rendered as "16 approaches rebuffed among the courts" — two minors
  asking once each deleted the fact that Prussia was turned away ten times. It now ranks by
  frequency, and a short bucket loses no names at all.
- **Drive-by, pre-existing: 4 of the 7 arms of the NA-6 dead-name pin were non-binding.**
  `test_get_endpoints_carry_the_overrides_too` sliced a fixed 2,400 characters after each
  route decorator, overshooting four of the seven bodies into the *next* endpoint, whose own
  call satisfied the assertion — deleting the overrides from `/campaign_log`, `/dispatch`,
  `/marshal_overview` or `/status` left it green. Bounded to the real body; mutation-tested
  3/7 → **7/7** binding.
- **DECIDED and recorded rather than fixed silently:** the turn header now counts *collapsed*
  rows ("Turn 3 — 5 events" where 26 happened). It stays: the header has always meant rows in
  this block, expanding shows exactly that many, the collapsed row states the true number one
  line below, and gate Q1(a) bought "no Godot diff" with this behaviour. Reversing it is a
  ~4-line `.gd` change.

### ✅ IGR-A — Honest copy — LANDED July 25, 2026 (the first slice of row IGR)

**User direction: "do bug fixes A".** The four gate-free items of
`docs/INGAME_REVIEW_FIXES_SPEC.md` §2 IGR-A, plus the P1 the spec routed ahead of it.
**Landing record = spec §2 IGR-A (authoritative)** — it records every place the spec's own
claims turned out wrong, because a 4-agent seam-verification pass re-measured all of them
against master before a line was edited.

- **A1 the hard-block copy** — `Spain cannot join against Prussia: no_participation_path.`
  became a whole sentence. One helper (`display_names.ally_entry_block_line`), prefix-aware for
  the three keys with a dynamic nation suffix, chancery third-person because the same line feeds
  the campaign log. **The second surface was dead**: `filter_campaign_log` had no
  `hard_block_surfaced` branch, so the chronicle line the spec asked to fix had never once
  reached the overlay. It does now.
- **A2 the duplicated "Political Context:"** — the confirm popup printed each line inline in
  Talleyrand's prose *and* again as a bullet, then announced "+2 more diplomatic concerns" about
  lines already on screen. The inline append is gone at both confirm sites; the cap rose 2→4 at
  **all three** render sites (break-treaty goes through a different builder). The paradox
  inline **stays** — its popup renders `message` and nothing else, so dropping it would have
  deleted the reliability preview from the game.
- **A3 a nation typed where a province belongs** — `move to Austria` marched Ney eight provinces
  to the Spanish coast, and **`Britain → Brittany` was a second case the spec missed**. New
  single-source predicate `backend/ai/nation_names.py`, deliberately *not* a widening of the
  shared demonym list, running after the exact-region check (the collision set is **three** —
  Hanover, Naples, Normandy) and before the demonym null. It never nulls the target; the
  executor's one region chokepoint answers with the court's own provinces, on every verb
  including attack.
- **A4 the silent vassal release** — "Kingdom of Italy has been released from vassalage." now
  names the 375 g/turn tribute, the real threat delta (85 → 77, read from `reduce_threat`'s
  return because it clamps), the 5-turn cooldown, the lost call to arms, **and the woken deck
  with its formation watcher** — releasing Kingdom of Italy is precisely what un-blocks
  `→ forms: Italy`, and the game had been performing its own best causal link in silence.
- **Bonus P1 — IGR-X1**: `del marshal._recovery_destination` removed an attribute `to_dict`
  reads directly, so any save or autosave after an AI marshal finished recovering raised
  `AttributeError`. Its own row said "take before IGR-A".

**A post-landing adversarial review (38 agents, 6 lenses → 2 refuters each) found 16, of which
4 survived and were fixed** — headline: **A3's first cut was half a fix, and the refuters were
wrong to downgrade it.** Only the bare `move to` phrasing reached the guarded ladder; `march to`,
`advance to`, `head to`, `proceed to`, `make for`, `travel to`, `push to`, `deploy to`,
`relocate to` and `journey to` all run through the *strategic* target pass, which had no guard —
**ten of eleven phrasings still built a real MOVE_TO order to Asturias.** Reproduced by hand
before accepting. Also fixed: `Ottoman`/`PapalStates` (tags that are their own demonym) classified
as a generic army and marched at the nearest Austrian; retreat told the player a real court "is
not known to the staff"; A1 **dead-named a formed nation** (composing finished prose defeats the
client's raw-tag formation override — a regression, since the pre-A1 line passed the raw tag);
and A1 made a *repeatable* event visible, a new source of the very log spam IGR-B exists to cure.

Suite **15,011/3** · ruff clean · parser eval **461/461** mock (+4 corpus rows) · Godot parse
harness EXIT=0 (17/17 scripts, both scenes instantiate) · headless boot **0 `SCRIPT ERROR`** ·
M1–M7 and the 40-turn `BASELINE_SERIES` byte-identical. `tests/test_igr_a_honest_copy.py` (71).
**Next per spec §6: the pause for review, then IGR-B (gate Q1).**


### 🎮 THE QUEUED IN-GAME REVIEW ✅ HELD July 25, 2026 — NA-6c/6d + AI-3r, widened cross-element

**User direction: "Play the game for real and give me a full in-game review … widened to a
cross-element pass."** Played in the real Godot client against the real backend
(`LLM_MODE=anthropic`, default `europe_1805.json`): France, seed `historical`, turns 1–9, then a
5-turn `SOVEREIGN_SEED=austerlitz` variance pass. **Record =
`docs/audits/INGAME_REVIEW_2026_07_25.md` (authoritative).** Backend commit `bdeb17c`.

**Scores (overall ≈7.4):** agendas/formables **8.5** · marshal drama **8.5** · combat legibility
**8.0** · parsing **7.5** · economy **7.5** · AI aliveness **7.5** · diplomacy/settlements **7.0** ·
vassals **6.5** · UI/UX **6.5** · **narration 6.0** (the weak pillar, and the #1 gap).

**5 defects found by play, ALL FIXED in-session** (`tests/test_ingame_review_fixes_2026_07_25.py`, 29):
- **P1 the declare-war soft-lock** — declaring war on a treaty partner looped forever (war purpose
  → treaty warning → Talleyrand objection → war purpose → …), three cycles observed, only Cancel
  escaped. `_include_popup_passthroughs` POPS the objection popup when it delivers it, so the
  objective and treaty resolution were unreadable at answer time and each path dropped the other's
  bypass flag. Fixed with a transient context that survives the pop; re-verified live.
- **P1 every AP-priced marshal-petition arm arrived dead** — `turn_manager` runs the jealousy pass
  BEFORE `advance_turn` refills AP, so `enabled: ap >= cost` was baked at zero and shown to a
  player holding 4/4. Confirmed twice live (Promise Glory at 4/4, Force Reconciliation at 3/4 — no
  HTTP on click). The paid half of the Jealousy channel was unreachable in ordinary play.
  Affordability now re-derived at the delivery seam; disabled arms state their reason.
- **P2 beat-7 copy lied** — `exposed`/`outmatched`/`penniless` rendered as "the moment passed",
  the exact §0.3 defect AI-3r was written to kill. Single-sourced on `war_council.crisis_cause_phrase()`.
- **P2 the terminal swallowed the mouse wheel** — `OutputDisplay` is a `fit_content` RichTextLabel
  inside a ScrollContainer; drag worked, wheel did not. `scroll_active = false`, matching every
  sibling ledger. Verified live.
- **P2 the separate-peace promise was not kept** — "Your drafted terms for X carry into the talks"
  while identity clauses are dropped by design. Copy now names what will not travel, with a drift
  guard tying it to the seed function.

**Must-see checklist:** Formables button **PASS** (gate terms flipped `•`→green `✓` live the turn I
took Posen, and the negotiate button appeared) · create_client carve authored in a settlement
**PASS** · "→ forms:" watcher **PASS** · per-court Exposure + The Emperor's Own Exposure **PASS** ·
Stage B/C/D mirror / intent / weariness / paymaster / `agenda_pursuit` **ALL PASS** · **The
Proclamation NOT REACHED** (the carve sits on a whole-war settlement needing all four courts at
50; the bilateral route the game offers drops the clause — stays on the must-see list) ·
"The Polish Question" NOT REACHED (needs the Duchy to exist) · beats 2/3/7 did not fire, **as
expected and NOT filed as a regression** (spec §8.2: 0 crises / 40 turns × 8 seeds).

**Routed:** `BUG_FIXES.md` §In-Game Review July 25 — **IGR-1 the campaign log is drowned in AI-AI
refusal spam** (turn 9: 24 of 25 events were `X rebuffs Y`, burying Russia adopting *The Gulf and
the Straits*), IGR-2 raw `no_participation_path` in player copy, IGR-3 identity clauses dropped by
the bilateral substitution, IGR-4 Talleyrand's "designs held in check" rung has no reachable
trigger (GR9). `DESIGN_REFINEMENT.md` §In-Game Review — IGR-D1 plunder yields 87g against 3,085
income so the Plunder/Secure choice has no tension, IGR-D2 minor-court envoy spam, IGR-D3 the
identity-clause gate.

**Variance pass:** the D7 contract held exactly — Tier 1 identical (exposure 159,000/189,000,
Austria 104,000/126,000, deck content), Tier 2 banded (alarm 85→84, Britain relation −85→−90,
Russia weight 89→90). Headline: **Austria opened on `Primacy in Germany` (→ Bavaria) instead of
`Redeem Italy`** — the authored AI-0c deck-order band producing a materially different war — and
the variance propagated into the drama (Ney crowned + Bernadotte↔Davout feuding, where
`historical` gave Davout the crown and Murat↔Lannes the feud).

**Also confirmed live** (evidence gaps closed): Murat's **autonomous glory-attack executed**
("hungry for glory, has attacked Brunswick on his own initiative" — Sweep 2 had this unfilled);
decks advance in play (Britain *The Low Countries → The Paymaster of Coalitions* on taking
Flanders; Austria retargeted onto Kingdom of Italy the turn I released it; Russia took up *The
Gulf and the Straits* at T9); the Fontainebleau petition's rentes moved the ledger from
`+1817g` to `+740g` net.

Suite **14,936/3**, ruff clean, Godot parse harness EXIT=0.

**▶ QUEUED SAME DAY — row IGR, `docs/INGAME_REVIEW_FIXES_SPEC.md` (v1.0, ✅ GATE BLESSED — build may proceed).**
Everything the review routed rather than fixed is now a spec'd, ordered pass rather than loose
backlog: **IGR-A** honest copy (4 items, gate-free) · **IGR-B** the campaign log becomes readable
(Q1) · **IGR-G** settlement viewport +
map-stack legibility (gate-free) · **IGR-D** the carve becomes completable (Q2 — the big one; ends
with the in-client Proclamation sighting this review could not deliver) · **IGR-F** the
minor-court envoy digest (gate-free) · ~~**IGR-E** plunder earns its prompt (Q4, blessed number)~~ ✅ **LANDED July 26, 2026**.
Build order **A → pause for review → B → D → F → E → G**; the two gate-free slices land first
per the project's slice-review cadence. **✅ GATE BLESSED July 25, 2026 (spec §5, authoritative):** Q1 **(a)** aggregate the log at the view layer keyed `(turn, proposal_type)` · Q2 **(a) scoped to `create_client` + (b) for the rest** — the carve CARRIES into a separate peace (Tilsit), while vassalage/liberation stay settlement-tier and the bilateral route is DISABLED with a stated reason rather than dropping them silently; the G4F-15 armistice ruling stands · ~~Q3~~ struck pre-gate (IGR-C withdrawn) · Q4 **(a)** `PLUNDER_INCOME_MULTIPLIER = 4`, blessed and in-band tunable, with a falsifiable acceptance test (a poor early player plausibly plunders; a rich late one does not) and a recorded dissent that option (b) — stability-vs-authority — is the better design if the number fails twice.

Nothing in the spec is deferred without an
owner; the four items deliberately not taken (beats 2/3/7, the Polish Question label, Congress
beat 6, the unreproduced modal stacking) each name theirs in §4.

**v0.2 → v0.3 — the spec's own verification + refutation pass (same day).** Before trusting the spec, every routed row
was re-measured against master by a find→refute fleet. **Four v0.1 claims were wrong and are
corrected in place, marked "⚠ v0.1 SAID"** so the reasoning stays auditable: (1) the log
aggregation key `(proposer, proposal_type)` was **measured insufficient** — a burst turn carries
~10 distinct proposers, so 21 lines become ~10; the working key is `(turn, proposal_type)`, and a
**per-category filter is outright wrong** because the buried `agenda_shift` payload shares
category "diplomacy" with the noise; (2) "broaden Talleyrand's rung to France's own designs" is
**not buildable** — France has no agenda deck, so there is no French design to hold in check; the
correct fix is to name any live restraint (measured 0 → ~34 rendered rows); (3) Austria does not
"short-circuit on busy" — its design targets the player and is dropped by the player-target
filter; (4) releasing a vassal does **not** end shared wars, so that copy must be forward-looking.
Then the refuters went after those corrections and **overturned two more of mine**: (5) the
`move to Austria` → **Asturias** case is **P3, not the P1 I had escalated it to** — it is not
silent, `movement_executor.py:186-203` names the substituted province three times and flags it
(*"Our maps read Asturias as the province nearest your order, Sire"*), and the attack arm refuses
outright; the real seam is `parser.py:99 _is_nation_demonym` (whose own docstring already names
this bug class) generalised to bare nation names, **not** the executor, which never sees the word
"Austria"; and (6) **the whole IGR-C slice is WITHDRAWN** — Talleyrand's "designs held in check"
rung is not a GR9 orphan (it is the *third* surface of the exposure mechanic, and the other two
render at boot and were verified PASS in this very review; the AI-vs-AI silence already has an
owner in `AI_WAR_DECISION_SPEC.md` §8.2-1 = AI-V arm (a)), the proposed broadening renders **0
rows while France remains the hegemon**, and it would have shown Sweden's authored anti-Napoleon
design as held in check *against Britain*. **The gate is therefore 3 questions, not 4, and the
spec is smaller than v0.1 — which is the point of running the refuters.** **Two unrelated
defects were found in passing and routed:** IGR-X1 (**P1 crash** — `enemy_ai.py:2039`
`del marshal._recovery_destination` makes every later save/autosave raise `AttributeError`) and
IGR-X2 (`get_region_intel` mutates `world.intel` on read, so `GET /campaign_log` perturbs the
world). The log-spam producer measures at **171 pairs scanned per turn** with the refusal family
**excluded from the anti-spam counter**, and the wave **repeats on the ~6-turn dedupe period** —
it is standing, not a one-off.


### ⚔️ AI-3r ✅ GATED + BUILT COMPLETE July 25, 2026 — "What It Leaves Undefended" (all five slices, one session)

**User direction: "do the next phase commit and push making ai wars work better assure its done
well spec wise and didnt miss any key elements."** The gate was held under that delegated grant —
**gate record = `AI_WAR_DECISION_SPEC.md` §6.1 (Q1–Q5 at the spec's recommendations; Q6 overridden
by the user's own request — AI-3r ran NOW, the Battle Diorama stays queued next), five
implementation rulings in §6.2, landing record = §8 (authoritative).**

- **.0 The Probe** (`docs/audits/AI_3R_PROBE_2026_07_25.md`): 8 seeds × 40 ambient turns — **0
  crises, 0 council wars everywhere; §0.2 confirmed measured** (Prussia never left `align` while
  openable; Britain/Russia sat AT the fight rung 10–15 turns blocked by nothing but the acquire-only
  type filter). N7 kept at 85 from projection data. **Unexpected finding recorded:** the
  pre-existing combat-seam auto-declaration already ignites un-counselled AI-AI wars in ambient
  worlds (Prussia→Austria turn 5) — outside AI-3r's D1-only mandate, noted for AI-V.
- **.1 Exposure** — the HOI4-inspired rear-security reserve: `world.get_neighbouring_nations` (ONE
  region pass, per-turn cached, cleared through the standard invalidation chain) +
  `get_exposure_view`/`get_rear_reserve`/`get_free_strength` in `war_council.py`; the restraint
  force gate now weighs **FREE strength** (standing − the reserve held against the worst armed
  neighbour, max-not-sum per Q2, capped at 60%); `_restraint_block_reason` is ONE seam that both
  gates and names causes. Ledger: per-court **Exposure** rows (fogged PARTIAL+, Europe-only) +
  **"The Emperor's Own Exposure"** (un-fogged, "Advisory only, Sire" — Q5's pinned asymmetry: the
  player is TOLD, never gated; executor-source negative pin). **Live-verified over HTTP**: France
  159,000/189,000 free with the rest held against Britain; Austria/Prussia/Bavaria rows fog-gated.
- **.2 The Moment** — four opportunity terms that can actually climb (all per-turn readings, never
  latches): holder's-allies-committed +6, holder-recently-beaten +8 (ruling R3's zero-new-fields
  derivation), holder-exhausted +5 (finally consumes AI-4c), own-rear-quiet +6.
  `WEIGHT_AT_WAR_WITH_HOLDER` DELETED (ruling R5 — dead for war-opening by construction, cosmetic
  elsewhere). The opener widened to deny/contain designs (Q3) with the D3 guard pinned
  (player-hegemon containment stays the coalition's business). Emergent interplay pinned: **a
  guarantor at war is a hollow pledge** (−8 deterrent + 6 allies-committed = −2 net).
- **.3 The Cap** — **`MAX_SIMULTANEOUS_AI_WARS` DELETED** (Q1); the runaway guard moved to the
  suite (`SWEEP_WAR_ALARM=6`/40 turns, enforced by a seeded subprocess run); **beat 7 never lies
  again**: causes `exposed` (threat NAMED in the copy) / `outmatched` / `penniless` (ruling R2)
  join the taxonomy, the soft-stall cooling maps the LAST blocking reason to its own cause, and the
  `crisis_passed` event carries `last_soft_block` for falsifiability. **Authored `wary_of`** landed
  per ruling R1: scenario key `statecraft` (Prussia fears Austria 1.25/Russia 1.4 · Austria fears
  Prussia 1.25 · Ottoman fears Russia 1.5 · Sweden fears Russia 1.4), ONE serialized world field,
  validator block + `MODDING_FORMAT.md` row. Talleyrand's war room gains the **designs-held-in-check
  rung** ("Berlin is not free to move, Sire…").
- **.V measured honestly (spec §8.2, the E1-anchor precedent):** ambient re-measure = **0 council
  wars per 40 turns on every seed** — within the alarm, below D1's band, and the blocking predicate
  is now WRITTEN (every warlike 1805 design targets the player-hegemon → D3 routes it to the
  coalition; the lone AI-vs-AI case needs a moment conjunction the passive ambient world never
  assembles). **Reachability proven deterministically**: the fixture crisis declares its fore-warned
  war on schedule with the cap gone; a widened contain design opens, coerces and declares. The D1
  band transfers to **AI-V arm (a)**, where a played France assembles the moments.

Conscious pin flips recorded in spec §8.3 (boot weights 85/84/89 with prices unmoved where it
matters — Prussia's 59/align byte-identical; Sweden coerce→fight is behaviourally inert; the D5-3
deterrent fixtures re-anchored on PEACETIME guarantors). `tests/test_ai_war_decision_ai3r.py` (56);
suite **14,907/3**, ruff clean, **M1–M7 byte-identical AND the 40-turn threat `BASELINE_SERIES`
held byte-identical** (no re-record — coerce and fight are treated alike by every price consumer),
parse harness EXIT=0, headless boot 0 `SCRIPT ERROR`, exposure rows live over HTTP. The beat-7
`exposed` moment on a live screen rides the queued user in-game review (NA-6c/6d).

**▶ NEXT: the user in-game review (NA-6c/6d + the AI-3r exposure surfaces) + Battle Diorama (row
BD) → §11 Stage E (AI-5 wires · AI-5b(i) emergent designs Core · AI-5c) → F → G (AI-V, now
carrying the D1 band measurement).**

### 🖥️ THE PIN-20 LIVE IN-GAME PASS ✅ HELD July 25, 2026 — Stages B/C/D on screen, 8 defects fixed

**User direction: "do in game pass and make any fixes found commit and push when done, give a
review of the game after."** The AI-Intent phase had shipped Stages A–D across three build sessions
with **no Godot-side verification at all** — pin 20's standing debt. This session drove the real
1805 campaign through the real client (two worlds: a 38-turn HTTP-driven sweep for reachability,
then a fresh hand-played campaign for the surfaces), and every Stage B/C/D surface was confirmed
rendering — or fixed.

**Verified live on screen (pin 20 CLEARED for Stages B and C, partially for D):**

- **Stage B** — the Diplomatic Ledger's NATIONS tab opens with **"How Europe Reads France"**
  (`Read as: The hegemon of Europe — 40% of the continent's weight. / The courts believe he will go
  as far as war (alarm 85). / They think he is coming for Hesse`), and every court carries its
  **Design** and **Intent** rows (Britain `The Low Countries` / "prepared to go as far as war —
  France stands in the way (weight 88)"; Prussia `The Hanoverian Prize` at weight **59**, the pinned
  boot value). The **Weariness** row renders where fog allows (Austria: "National exhaustion across
  all wars: 0 (stable) — at war with Bavaria, France, Kingdom of Italy").
- **Stage C** — **THE PAYMASTER'S PURSE** block live in the THREAT & COALITION tab
  ("Britain pays Austria 300g/turn to keep the field" + the counterplay line); **Compacts** rows live
  ("Britain sponsors Russia against France (200g/turn)"); the **allegiance auction** fired twice
  unprompted (`THE FLIP IS IN PLAY: Sweden weighs its allegiance` → `THE FLIP: Sweden signs with
  Britain`); an envoy arrived speaking the NA-2 `agenda_pursuit` register ("My master's design is
  known to all Europe; Denmark sends this offer in its pursuit").
- **Stage D** — **beat 6 (The Congress) fired twice in the wild**: `THE CONGRESS: Austria and
  Bavaria make peace without France` (turn 14) and `Britain and Spain` (turn 16), campaign log AND
  dispatch. `threat_by_target` carried five populated non-France slots (AI-4a steps 5–6 live).
  **Beats 2/3/7 did NOT fire in 38 turns and `war_intents` stayed empty** — recorded honestly:
  that run collapsed France to 9 provinces with six powers pinned at the exhaustion cap, which is
  exactly the state AI-3's restraints suppress. **The D1 acceptance band (1–4 AI-initiated wars /
  40 turns) is therefore still unmeasured in a healthy campaign and belongs to AI-V.**
- Also live: CR-5 delegation ("Davout, deal with Mack" → the cautious scout + "Davout, cautious as
  ever, wants to see the ground before he commits"), W6-2 dynamic battle naming ("The Great Battle
  of Swabia", "Second Battle of Swabia"), Crowned with Glory, an autonomous jealousy glory-attack
  (Murat took Swabia unordered), the marshal-petition channel, `/formables` with honest gate terms.

**Eight defects found and FIXED (`test_live_pass_fixes_2026_07_25.py`, 20 tests):**

1. **Map labels drew straight across the Imperial Command window** (P2, every frame of every
   session): the label layer only dodged WORLD-space map furniture, so `FRANCE` / `SPAIN` /
   `PORTUGAL` / `KINGDOM OF ITALY` rendered over the terminal's own text, and the nation tier
   dodged *nothing at all*. Fixed with a screen-space avoid channel — `main.gd`
   `_push_map_label_avoid_rects()` → `map_renderer_base.set_ui_avoid_rects()` →
   `map_label_layer.set_ui_avoid_rects()` — pushed on every layout pass and on minimize/restore,
   applied to BOTH tiers. Verified: `FRANCE` now nudges clear and the panel is clean.
2. **A re-opened settlement offer described the map of the turn it ARRIVED** (P2): the status-quo
   clause is *derived* from current controllers, but `/mailbox/activate` replayed a cached
   `popup_payload` — a turn-3 offer read "Austria retains … Swabia" on turn 8, after France had
   retaken Swabia, on the surface where peace is accepted or refused. Now rebuilt every activation,
   exactly like the proposal arm beside it.
3. **The ledger stated a coalition-dissolution rule that does not exist** (P2): "any member's war
   exhaustion exceeds 80" is nowhere in `coalition.check_dissolution` (which tests threat < 20 and
   fewer than 2 members at war, full stop). Live proof: Austria pinned at WE **200** with the Third
   Coalition standing. The clause is retired; the payload now derives from
   `DISSOLUTION_THREAT_THRESHOLD` + the member floor so it cannot drift again.
4. **"WE: 200/100"** (P3): the member bars hardcoded a denominator of 100 against
   `WAR_EXHAUSTION_MAX = 200`. Backend publishes `war_exhaustion_max`; the bar scales off it.
5. **Berthier's coordination line was ungrammatical** (P2): `" and ".join()` produced "aided Ney and
   Lannes and Murat and Bernadotte, however, **was** conspicuously absent." New `_join_names()`
   ("A, B and C") + a `{failed_was}` number token.
6. **The enemy-phase popup stuttered every battle** (P3): "- Mack attacks Ney" was immediately
   followed by "Mack attacks Ney" inside the battle block. `_format_battle` now takes the action
   line's pair and drops the restatement when it duplicates.
7. **The purse and the dispatch quoted different sums in the same breath** (P3): the dispatch said
   "the subsidy stands at 200 this season" (delivered) while the ledger said "pays 300g/turn" (the
   tier at the treasury *after* income). The purse now names the delivered sum when the two differ,
   keeping the prospective rate beside it — read from the transfer's own event, zero new state.
8. **The mailbox subtitle lied** (P3): "Current-turn envoys only." above rows from turns 3 and 7.

**Not defects, checked and cleared:** the campaign log DOES humanize camelCase nation keys at render
(`PapalStates` → `Papal States`); the log's per-turn page was complete (battles, captures, jealousy,
`glory_crowned`); ESC not dismissing a hard-stop settlement dialogue is by design; `end turn` while
blocked returns an honest reason every time. **Recorded as an observation, not fixed:**
`ai_ai_proposal_refused` can be the ENTIRE campaign-log page for a turn (six identical-shaped
rebuffs) — pin 13's soap-opera risk lives in the log, not just the dispatch.

Suite **14,851/3** (+20), ruff clean, parse harness EXIT=0, boot smoke 0 `SCRIPT ERROR` ×3.

**Then the same session's post-pass question — "do nations fight each other?" — opened row AI-3r
(below), which was GATED AND BUILT the same day (see the top entry).**

### ⚠️ AI-3r SPEC'D July 25, 2026 (same session) — "What It Leaves Undefended" — ✅ GATE HELD + BUILT same day (top entry; gate record spec §6.1)

**The question that opened it, in the user's words:** *"do nations fight each other?"* → *"doesn't
just 2 at war seem overly gamey… there should be relationships and opportunities"* → *"why should
there be a max"* → *"they don't want to leave themselves exposed to a strong enemy — take
inspiration from Hearts of Iron."* **Spec = `docs/AI_WAR_DECISION_SPEC.md` v0.1 (PROPOSED, not
blessed); ROADMAP row AI-3r; amends `AI_INTENT_SPEC.md` §6 D1 ONLY (D2–D7 untouched).**

**The finding, measured then read.** The live pass produced **0 AI-initiated wars in 38 turns** with
`war_intents` empty throughout. That is not bad luck — the `fight` rung needs weight **85**, and the
reachable ceiling for an `acquire_regions` design against a holder the court is **not already at war
with** is **76** on the default seed (55 base + 8 cold relation + 10 holder-busy + 3 bankrupt).
`WEIGHT_AT_WAR_WITH_HOLDER` (+10) is a **dead term** — the state it needs disqualifies the crisis.
Maximum seeded jitter reaches 84, one short. The only corridor is a reneged bargain (+15).
**D1's own acceptance band (1–4 AI wars / 40 turns, `AI_INTENT_SPEC.md` §7) is therefore unmeetable
by construction**, which makes reachability a **defect against the phase's DoD, not a redesign.**
Two companions: the crisis opener filters `want_type == "acquire_regions"`, so `deny_regions` (60)
and `contain_hegemon` (65) — the historically warlike designs — can never open a war at all; and
when D1's cap DOES bind, the crisis dies on beat 7 with cause `starved` — *"the moment passed,
opportunism decayed"* — which is **false**, and is the same defect class as the coalition-dissolution
rule retired hours earlier the same day.

**The design shift:** replace the global quota with an **exposure calculus**. A court's *free* field
army = standing strength − a **rear-security reserve** held against its worst armed neighbour
(`menace = their strength × relation band × authored posture`, **max not sum**, capped at 60% of its
own army); only free strength counts toward the 1.25× force ratio. Diegetic (*"Berlin will not strip
the Silesian frontier while Vienna stands armed"*), playable (France can manufacture or prevent
another power's war), and self-limiting with no number to set. HOI4 borrows: the held-back-divisions
idea, authored per-pair `wary_of` posture on the existing `NATION_STATECRAFT` (D7's "authored
content, not a formula"), and the recognition that **justify-war-goal already exists here** as the
Stage D fore-warning and **world tension already exists** as AI-4a step 5 accruing threat to the
aggressor's own slot — wired, and idle, because no AI has ever expanded.

Slices: **AI-3r.0 the probe (8 seeds × 40 turns, harness-only, runs FIRST — every §3 number is
otherwise guesswork)** → .1 exposure + the ledger row → .2 the moment (opportunity terms + design
widening) → .3 cap deletion + beat-7 cause honesty (`exposed` / `outmatched`) + authored posture →
.V re-measure into AI-V arm (a). **Slices .1/.2 need no gate (defect side); .3 and the widening do.**
Six questions in spec §6 with recommendations: delete the cap outright · max-not-sum reserve · widen
the designs · authored posture · **player display-only** (Napoleon may strip the Rhine; the game's
job is to tell him what he leaves open) · sequence after BD.

### ⚔️ AI INTENT ⛩ RE-CHECK HELD + STAGE D ✅ BUILT July 24, 2026 (third session that day) — War and Peace

**User direction: "do next phase of intent commit and push."** The phase's only remaining gate —
the D6 ⛩ re-check — was **held from the Stage C evidence pack under the standing delegation**
(gate record = `AI_INTENT_SPEC.md` §16, authoritative): **D1's cap CONFIRMED at 2** (band 1–4,
re-measure at AI-V), **AI-3b slipped out of Stage D** (not cut — exit review owns it; pin 24 and
§7a scene 7's seal half carry the predicate), **AI-5c keeps its Stage E slot**, **pin 17(b)
re-sited to the landing record and BLESSED there with measured data**, AI-3c stayed in-stage, and
the **§4.4b arbitration ruled EXCLUSIVE** (one coalition world-wide; anti-France always wins —
an eclipse coalition dissolves for France, cooldown zeroed). **Then Stage D was BUILT in the same
session — landing record = spec §17 (authoritative)**, the stage's indivisibility honoured: under
the harness an AI-initiated war both **starts** (Prussia on Hanover for the Hanoverian Prize —
fore-warned beat 2 with honestly-gated instruments, the refused coercive demand beat 3 on the
serialized record, declaration at 2 foregrounded turns through `declare_war` at the announcement)
**and ends** (the exhausted loser sues through `effective_peace_threshold` — P1's formula
extracted to ONE seam, pin 19b — the winner takes the surrender through the standing scorer seam,
the design province cedes, the war instance closes headlessly with the player's mounted dialogue
untouched).

- **`war_council.py` (AI-3 + AI-3c):** the crisis lifecycle over ONE new serialized field
  (`war_intents`); ladder gate (2 refusals / renege skips rungs); restraints + D1 cap 2 (a capped
  crisis WAITS); `can_declare_war` shared preview; the treaty-break-first step; pin 21's stall
  guarantee (a dead predicate starves the crisis ON SCREEN); one foregrounded crisis world-wide;
  AI-vs-AI only in v1 (player-targeted designs coerce via NA-5, fight via the coalition — pins
  stand); AI producers on the crisis (folds-holder buys off; one protector/turn guarantees); AI
  guarantors JOIN at the declaration, France's pledge pleads (never auto-conscripts); the P7
  frontier bias masses corps on the border via the existing movement gates (deckless-neutral).
- **§4.3a at the combat seams:** both refusal-discards are now ABORTS and the OPEN_MOVEMENT
  capture hole is CLOSED (pin 15 — no undeclared conquest, either side; the player's silent
  open-borders capture now stages War Purpose instead). `exit_shared_wars_for_defection` lifted
  from the VS-6 idiom, pinned executable against the boot coalition.
- **AI-4a steps 5–6 + §4.4b:** every threat producer passes its ACTOR as target (the discarded
  non-player hegemony increment WIRED — D3's fuel); written stays-France-only decisions on the
  four standing contributors; per-target decay; the eclipse pass (share-gated, brewing-only —
  pin 16c structural); the player never enrolled; all nine coalition anchors target-keyed with
  legacy defaults byte-identical; **pin 16(a) VERIFIED TWICE — France's 40-turn series
  byte-identical in isolation AND with AI-4c live; `BASELINE_SERIES` stands unedited**; the
  Stage-C no-accrual invariant consciously INVERTED (Britain peaked 55/decayed, four slots
  returned to 0 organically — pin 16b live).
- **AI-4c:** the tick keys on `get_nations_at_war_with` on Europe (legacy verbatim, pin 17c);
  explicit third-party loser-bears-its-dead arms in BOTH combat copies; pin 17(a) green (the pin
  that failed against master); **17(b) blessed with data** (boot third-party belligerents Spain
  24we/28g · Holland 26/5 · Bavaria 40/4 · KingdomOfItaly 24/10 by turn 4 — an order below their
  treasuries); the labelled nations-tab weariness line + its `.gd` render.
- **AI-4b (`settlement_third_party.py`) + AI-2d join/broker:** headless third-party peace (scorer
  hard-stops veto; the victor's-consent arm; D2's capital ruling — a minor's capital may cede and
  eliminate, a great power's never); `_settlement_offer_build_terms`'s `player` param RENAMED
  `accepter` (nation-pair-general); beat 6 names consequences incl. the French-frontier read; the
  broker ask on the existing proposal transport (Accept convenes at the broker margin, result as
  popup — PL-14 rule, no new dtype; +10 relations both courts).
- **Beats 2/3/6/7 live end-to-end:** 6 campaign-log types (count pins 134→140 ×2, conscious),
  town-crier visibility (DPF-1), dispatch templates + priorities (beats exempt from the routine
  cap), and the headline's first non-France arms (`europe_at_war` with the stated reason /
  `europe_crisis` / `europe_congress` / `europe_crisis_passed`, all weighted below France-centric
  — pin 13) with Berthier closing notes.
- **Conscious pin flips:** the inverted no-accrual invariant · log counts 134→140 · the W6
  "AI-vs-AI war is no headline" pin re-pointed at the CLASS boundary (never `war_touches_us`,
  weight below it) · the ultimatum-yield threat pin re-scoped to the player's slot (the AI
  beneficiary now accrues its own) · 5 formables-test renames · preserved warts on the record
  (the mirror copy's missing decisive-victory arm; France-gated coalition shock) → exit review.
- **The 9-lens review fleet then confirmed 2 HIGH + 12 findings, ALL FIXED same session
  (addendum = spec §17.1)** — headline [r5 HIGH]: the seven boot wars fold into ONE instance
  CONTAINING France, so the four satellite sub-pairs (Spain|Britain, Holland|Britain,
  Bavaria|Austria, KingdomOfItaly|Austria) had NO exit and would have ratcheted to exhaustion
  200 forever → **the exhausted-pair exit** (a spent, stagnant, non-vassal sub-pair white-peaces
  out of a player-containing instance; vassals stay bound to the lord's war; one exit/turn);
  [r2 HIGH]: a design war won by ELIMINATION never gets ended_turn → the D1 cap counted it
  forever (two conquests would have ended AI war-making) → live-for-the-cap = two standing
  sides; plus the eclipse reader/copy de-anchoring sweep (notifications, top-bar flag, dispatch
  section, war-room attribution, oneliners, convergence bias, the 6a oscillation gate, the
  France coalition panel), the broker ask naming its war, the last-region cession honesty, the
  force-arm winner-pays hole closed by shape, R7 humanization, and 6 test-falsifiability
  hardenings. The 40-turn threat baseline was re-recorded consciously ONCE (the pair-exit
  legitimately ends the minors' side-wars ~turn 17).
- Suite **14,831/3** (was 14,772/3; `test_ai_intent_war_decision.py` +
  `test_ai_intent_third_party.py` = 47 + the flipped pins), ruff clean, M1–M7 byte-identical
  in-suite, parse harness EXIT=0 (`diplomatic_ledger.gd` the one `.gd` touch). **▶ NEXT: the
  pin-20 live in-game pass (Stage B/C surfaces + the new Stage D beats/headlines/weariness row)
  + the user in-game review (NA-6c/6d) + Battle Diorama (row BD) → §11 Stage E (consequence &
  character: AI-5 wires · AI-5b(i) emergent designs Core · AI-5c kept · volte-face may slip)
  → F → G (AI-V).**

### ⚙️ AI INTENT STAGE C ✅ BUILT July 24, 2026 (second session that day) — The Bargaining Table

**User direction: "do next phase of intent, commit and push."** Landed **Stage C in full per
`AI_INTENT_SPEC.md` §11.1** — **AI-2** intent-driven rungs (P-Intent BEFORE P3: the design
purchase / sell-neutrality / alignment asks; AI-AI trigger 0 design+alignment asks; P-Bandwagon
widened to any hegemon; the §4.2c `INTENT_ASK_BUDGET_PER_TURN=2` lane + opportunism valve),
**AI-2b** the D5 counter-instruments (`instruments.py` — the ONE directed record for
sponsorship/licence/sell-neutrality, compensation bargains that SUSPEND designs at the agenda
chokepoint, guarantees with the −8 intent deterrent + `guarantee_abandoned` enforcement; player
verbs `sponsor_design`/`buy_off_design`/`guarantee_nation` at 1 DP with honest refusals; 4 new
serialized stores; beat 4 The Broken Bargain on the PL-14 popup), **AI-2c** statecraft
(`NATION_STATECRAFT`, honor-bias idiom — Austria hardens/align-first, Prussia folds/gold-first,
Russia honour/sponsor-first, Britain's −40 subsidy wall DERIVED from hostile-army-on-home-soil;
the AI-AI haggle arm; ask-order partitions under the NA-2 design-front rule), **AI-2d** the §12.6
allegiance auction (announced flips, D5-record bidding, refusable player wins) + the AI sponsor
branch (Russia funds Austria turn 1), **AI-2e** the paymaster duel (subsidy visible on campaign
log/dispatch/THE PAYMASTER'S PURSE + per-nation Compacts `.gd` rows; the outbid over the directed
record; bought clients not worth funding), and the parallel **AI-4a steps 1-4** (`threat_by_target`
+ the `threat_level` property — the step-4 pin verified BYTE-IDENTICAL against `d1be956` before any
behaviour landed, then re-recorded consciously). **Landing record = spec §15 (authoritative)**;
**re-check evidence pack = `docs/audits/STAGE_C_EVIDENCE_2026_07_24.md`.** An 8-lens find→2-refuter
review (56 agents; 27 verifiers lost to the session cap were adjudicated by hand) confirmed **16
findings, ALL FIXED** — headline P1: renege attribution was DIRECTION-BLIND (the attacked party was
branded the breaker; fixed as aggressor-attributed via the war_instances attackers side, with
unattributable wars lapsing on the new `instrument_lapsed` event). Suite **14,772/3** (+159); parse
harness EXIT=0; boot 0 `SCRIPT ERROR`. **▶ NEXT: THE ⛩ RE-CHECK (the phase's only remaining gate —
user decides from the evidence pack: D1's cap, the §11.2 cut list, AI-5c keep/slip) + the pin-20
live in-game pass (Stage B ledger rows + Stage C compacts/purse/courier surfaces); Stage D (War
and Peace) may not build before it. BD (Battle Diorama) still queued by its ROADMAP row.**

### ⚙️ AI INTENT STAGES A + B ✅ BUILT July 24, 2026 — the dice, the bounds, and Europe's hand

**User direction: commit the spec, then "do as many phases as you think are comfortable to do at
once" (committing deferred to session end); mid-session addendum: record the standing AI review
questions at the spec's end.** Landed **Stage A (AI-0b campaign seed · AI-0c historical bands ·
AI-0d the second design)** and **Stage B (AI-1 intent layer · AI-1b the mirror · AI-2a
diplomacy-path convergence)** per `AI_INTENT_SPEC.md` §11.1 — **landing record = spec §14
(authoritative)**; the spec also gained **§13 (v1.4.1)**, the user's six standing review questions
routed to owners (border massing → NEW row **AI-3c** "The army agrees with the ledger", Stage D;
multi-front conduct + recruit/commission budgeting → AI-V assertions + the §8 economy re-measure;
AI-vs-AI wars = Stage D; the non-France hegemon = D3 + pin 16d). **BD (Battle Diorama) re-sequenced
BEHIND the AI stages by user direction — row BD stands.**

- **AI-0b:** serialized `WorldState.campaign_seed` (env `SOVEREIGN_SEED` in-model; `from_dict`
  restores exactly, pin 14c), `from_scenario(seed=…)`, sha256 module-RNG-free derivation helpers
  (`campaign_variance.py` — jitter ramps 0→full by turn 12, 0 forever on historical), boot banner,
  seed in strategic-ledger Intel tab (bbcode-sanitised) + save metadata, conftest suite-wide
  `SOVEREIGN_SEED=historical` pin.
- **AI-0c/0d:** ten authored relation bands (France|Prussia [-25,5] the Haugwitz contingency; the
  grudge pairs Austria|Prussia + Hanover|Prussia NEW at behaviour-neutral 0), `threat_level_band
  [80,90]`, Austria's `order_group` (seed `ulm` opens Germany-first — Mack's deployment), Russia's
  `gulf_and_straits` behind arbiter (pin 22 every seed); validator band schema (contains-value,
  war-pair < −60 clamp, order_group contiguity, formable-deck rejection); the **six-clause
  historian test** across a 7-seed sweep (`test_ai_intent_historical_envelope.py`).
- **AI-1/1b:** `intent.py` — {want, against, weight, price} derived + per-turn cached on the
  bloc-cache chokepoint; staleness DECIDED turn-granular; boot pins measured (Prussia **`align` 59
  over Hanover** — the Potsdam winter; Austria/Britain/Russia `fight`; Sweden `coerce`); ledger
  nations-tab `intent` row + **"How Europe Reads France"** mirror block (restraint drifts the
  perceived rung down; boot target = Hesse, §3.5's misreading by design); Talleyrand war-room
  prices.
- **AI-2a:** recipient-explicit envelope/transport, **the refusal record both paths** (serialized
  `diplomatic_refusals`, ordered keys, + the `ai_ai_proposal_refused` public event — fog-filter
  visible), cooldown re-key with legacy-format-as-player-arm migration (zero churn), counter-offer
  asymmetry decided in writing. The AI-AI refusal moment did not exist before this slice — it is
  AI-3's ladder-gate substrate (§5 pin 8).
- **Review:** 60-agent find→2-refuter workflow, **11 distinct findings ALL FIXED** — headline P1:
  the refusal event was invisible in-game (no fog-filter branch + excluded from the phase return).
  Conscious pin flips: campaign-log count 122→123 (×2 files), relations matrix +2 pairs, war-room
  keys +`intents`, Russia contain-in-bloc → gulf_and_straits (the Tilsit route).
- Suite **14,409 → 14,613/3** (207 new across 4 `test_ai_intent_*.py` files), ruff clean, M1–M7
  byte-identical, parse harness EXIT=0, headless boot 0 `SCRIPT ERROR` ×2. **⚠ open: pin-20 live
  in-game visual pass** on the two new ledger surfaces (intent rows + the mirror block + the seed
  line) — headless-verified only. **▶ NEXT: user in-game review (NA-6c/6d + the new AI surfaces) →
  Battle Diorama (row BD) → §11 Stage C (the bargaining table) → ⛩ THE RE-CHECK.**

**[Historical — the July 2, 2026 re-staging snapshot. Every gate named below has since been held; see Quick Stats for live state.]** **THE REAL-MAP CUTOVER IS COMPLETE** (Slices 1–9 + 7.5 + the DEF-7 registry mini-pass all LANDED — full record below) **and the Phase 8 Peace Deals arc is functionally complete**: the Gate 4 end-of-queue smoke RAN July 2, 2026 (11 findings fixed at `7635229`; **gate passage recordable once the user confirms the residual eyes-only visual checklist** — see the July 2 Gate-4 entry below); **✅ SLICE G1 LANDED July 2, 2026 at `1a9da53`** (Request Terms lifecycle — SC-30 closed — + the D-G1-1(a) armistice-paradox exemption); **✅ SC-32 / Slice G2 closure bookkeeping DONE July 2, 2026** (this re-staging session — ledger rows updated, spec masthead bumped; SC-32 is formally CLOSED). **Routing authority: `docs/ROADMAP.md` §Current Phase Queue** (re-staged July 2) + the Next Steps section below. Immediate user gates: Gate 4 visual half · Slice H design gate (`docs/SETTLEMENT_SLICE_H_ALLY_PETITIONS_SPEC.md`) · Command Robustness scope ✅ BLESSED (CR-5 detailed scope blessed July 5, 2026 — `COMMAND_ROBUSTNESS_SPEC.md` §6) · Economy Revisit decisions (`docs/ECONOMY_REVISIT_SPEC.md`) · Marshal Content Pass gate (`docs/MARSHAL_CONTENT_PASS_SPEC.md`).

### 🧠 AI INTENT SPEC v1.4 ✅ July 24, 2026 — the structure & creative pass (docs-only)

**Docs-only session** (user: *"review with a fresh mind… feel free to add ideas, refine it, assure it
makes for good gameplay… creatively, use history… I want an easy to follow and phased spec"*).
`AI_INTENT_SPEC.md` bumped **v1.3 → v1.4**; **§6 (D1–D7) untouched, no v1.3 correction reopened.**
Two deliverables:

**1. Structure — §11 is now the phased build plan and the document's front door.** After four review
passes, build scope had to be collated from five places (D6, three §8 owner tables, §9a's cut list,
the acceptance sections). §11 restates the whole phase as **Stages A–G** — A the dice & bounds
(AI-0b/0c/0d) → B Europe shows its hand (AI-1/1b ∥ AI-2a) → C the bargaining table (AI-2 family ∥
AI-4a steps 1–4) → ⛩ the D6 re-check → **D war & peace, ruled INDIVISIBLE** (AI-3 + AI-4a-c +
AI-3b — a war that can start must be able to end; nothing user-facing lands mid-stage) → E
consequence & character (AI-5 family) → F the stage (AI-6 family) → G the reckoning (AI-V) — each
stage with rows, what-the-player-has, and exit criteria; beat-to-stage ownership mapped; **the
living cut list moved to §11.2** (§9a's copy marked as the v1.3 record); a turn-14 player vignette
states what the phase feels like when done. The 69-line version-archaeology header was rebuilt as a
reading map + version table (narratives live on in §9/§9a/§10). **All existing §-numbers stable —
zero cross-reference churn.**

**2. Creative — §12, six additions, each with history/mechanic/price/owner (record table §12.8):**
(1) **the deterrence receipt** — beat 7 "The Crisis Passes" + pin 21 + a DoD line: a foregrounded
crisis must END on screen, cause named and instrument credited — D5's success case was invisible
(the guarantee that works produced *nothing*), and every-crisis-becomes-war would have collapsed D4's
"only timing is uncertain" into scheduling (Ochakov 1791; Haugwitz after Austerlitz); (2) **Russia's
second design** `gulf_and_straits` (`acquire_regions` [Finland, Rumelia], authored BEHIND
`arbiter_of_europe`; row **AI-0d**, pin 22 = inactive at boot on EVERY seed) — found: **§7a scene 4
(Tilsit) was structurally unsatisfiable**, a volte-faced Russia had nothing to advance to since its
deck ends at arbiter, so "aimed at a third party" had no object; the entry also gives AI-3 its
natural far-from-France war (the Finnish War / Russo-Turkish 1806 — both targets non-capital, so
D2-safe by construction), and the AI-5b(ii) row gains the retire-the-contain-design clause; deck-
order variance re-pointed at **Austria's existing pair** (Italy-first vs Germany-first — the actual
Vienna war-council debate); (3) **the licence** — D5-2's own word, now defined: a directed
sponsorship at `amount_per_turn: 0` whose consideration is committed non-interference, pin 23 (a
licence is a bond both directions; ONE record shared with sell-neutrality; Tilsit's green-lights, and
their unwinding is the road to 1812); (4) **the purchased dispatch + the player's own seal** —
AI-3b's principle-7 half, pin 24: an active, priced, deterministic discovery verb (the cabinet noir;
Talleyrand's trade run in reverse), and France may seal its own licence-class articles for a premium
— masking defers third-party reads at the intent-derivation chokepoint (one site), discovery fires
the deferred reaction IN FULL, dispositions never sealable; (5) **the Arbiter's Offer** (row
**AI-5c**, may slip — cut list #2): armed mediation gives `arbiter_of_europe` its missing behaviour;
refusal consequence derived-only, and the weight rise feeding the existing ladder + statecraft IS
Prague 1813 by machinery, no bespoke wire; (6) **the allegiance auction** (inside AI-2d): a minor's
flip announced as in-play and biddable by both sides before it resolves (Bavaria, September 1805 —
courted by both empires, signed in secret at Bogenhausen; a sealed-article natural). Beats now
**seven**; pins **21–24**; §12.7 records what was deliberately NOT added (no espionage system, no
mediation auto-join, no further second designs).

**Files:** `AI_INTENT_SPEC.md` (v1.4), CLAUDE.md AI row, ROADMAP row AI, this entry. **No code, no
tests, suite untouched.** Build order unchanged: BD → Stage A. **▶ NEXT: user in-game review of
NA-6c+NA-6d, then Battle Diorama (row BD), then §11 Stage A.**

### 🧠 AI INTENT DESIGN GATE ✅ HELD July 20, 2026 — `AI_INTENT_SPEC.md` **v1.2**, §6 authoritative

**Docs-only session.** The v0.1 spec's six open questions were decided under the user's delegated
gate ("make decisions — we want this to play fun and historically"), and the spec's code claims were
**re-verified against master `12636a6`** by two read-only mapping passes. Four claims did not survive
and each one changes the build — recorded in §0.1 rather than quietly edited.

**Decisions (§6):** **D1** cap 2 simultaneous AI-initiated wars, 40-turn acceptance band 1–4 (1805–15
opened ~one non-French war every 18–24 months; three parallel AI wars is a different century) ·
**D2** AI wars may eliminate minors but a great power's last capital never falls to one — Venice and
the HRE died in this period, Prussia and Austria survived *because the hegemon chose to keep them*,
and here the hegemon is the player · **D3** France stays the gravitational centre: the machinery
generalises, but a coalition forms against a non-player hegemon only once that power's hegemony share
exceeds France's — the player can genuinely be eclipsed, but ambient AI noise cannot dilute the
campaign's central pressure · **D4** the ladder is fully open (this project's diplomacy has no fog, and
v0.1's own "soften the rung by relations" would have introduced it); only *timing* is uncertain ·
**D5** three counter-instruments ship **with** AI-2, not after it — compensation (Schönbrunn 1805),
sponsorship (Tilsit 1807; Britain's whole foreign policy), guarantee — and per §3.3 a bought-off
design becomes a **standing expectation** in the ES-7 idiom whose breach is the strongest casus belli
in the game, which is the road from Schönbrunn to Jena · **D6** build order **BD → AI-0/1/2 → user
re-check → AI-3 → AI-4 → AI-5/6 → AI-V**; the re-check is the phase's only remaining gate.

**The four corrections (§0.1):**

| | v0.1 said | Verified | Consequence |
|---|---|---|---|
| A | the AI-vs-AI `war_objective` branch is dead, no caller | `combat_executor.py:3482`/`:3532` and the `meta_executor.py:2108` cheat reach it; no *production AI* caller exists because `enemy_ai.py` targeting is `is_at_war`-gated end to end | **AI-3 shrinks a lot.** It decides and announces; the declaration seam already works. **No new PEACE→WAR edge is created** — now a DoD line |
| B | generalising threat is a "small wire" | `add_threat` has **no target param**; one serialized clamped int read in **16 backend modules (73 refs) + 10 `.gd`** | AI-4 gets an **additive migration contract** (§4.4a): `threat_by_target` map + `threat_level` as a property over the player's slot, byte-identical pin green *before* any non-player target is passed. The phase's long pole |
| C | build a bandwagon rung; generalise proposals to AI-vs-AI | **both already exist** — P-Bandwagon `ai_diplomacy.py:1094`; `process_ai_ai_diplomatic_phase:1954`, whose ladder can never return a war and which had **never ratified a treaty** until a July 2026 fix | Generalise, don't invent — and budget for bugs in a near-unexercised path |
| D | ~~cache intent "on the agenda idiom"~~ | **⚠ WITHDRAWN by the v1.3 verification pass (July 21, 2026) — the defect does not exist.** `_agenda_cache` IS cleared: it is the last statement of `invalidate_bloc_members_cache` (`world_state.py:1695`, the NA-0 fix), `invalidate_active_nations_cache:1619` chains into it, `set_diplomatic_state` (`diplomacy.py:2634`) reaches it directly, and there are **two** direct clears (`world_state.py:1695` + `formations.py:488`). Pinned twice in `test_nation_agendas.py::TestCacheAndSerialization` | **Row AI-0 DELETED.** Following the original instruction — "move the flush to `invalidate_active_nations_cache`" — would have **re-opened the P1 NA-0 closed**. The one real residual (intent also reads relations/force/treasury, none of which reaches that seam) is a decision *inside* AI-1. See spec §10 row 1 |

**v1.1 amendment (same day, user-directed — "assure major powers feel alive and goal-oriented and
engage in politics like IRL"):** added §3.4, the **great-power aliveness contract**. Each major gets a
distinct *derived* `statecraft` style — **Austria** the patient aggrieved coalition-builder (hardens
under coercion), **Prussia** the hesitant bandwagoner who sells neutrality and goes to war only over a
reneged bargain (Schönbrunn→Jena), **Russia** the distant honour-driven arbiter who intervenes far
from home then reverses (Tilsit), **Britain** the paymaster behind the moat who funds everyone and
never marches. It generalises `NATION_DESIRE_PROFILES` + the live Russia 1.1 honour bias into a
per-nation weighting over the *same* ladder — **no LLM (GR6), no new serialized personality object**,
and it must not perturb the 1805 boot. The contract's teeth are in AI-V: an **in-character** assertion
(each major exhibits its signature move ≥1×), a **homogeneity guard** (no two majors share a
first-instrument distribution — identical AIs fail), a **legible-from-ledger** assertion (the player
can name each *style*, not just its target), and §5 pin 10 (the majors stay in character under stress,
not just at peace). New owner row AI-2c; two new DoD lines (distinct statesmen + politics-with-each-
other witnessed). Docs-only; principle 8 added to §2. **Correction folded same day (user: "britain is
in reach"):** the Britain cell's "never coerced / unreachable" overstated it and would have broken
principle 7 (a paymaster with no counter-play). Britain is hard, not impossible — its field armies and
continental holdings are beatable on land, and its *core* behind the Channel is reached by **cutting
its trade (the Continental System, already modelled)** now and by **Ireland/invasion once DEF-5 naval
lands**. It answers a land ultimatum with gold precisely to teach that the front door is the wrong
door; the reward for the economic lever is the gold stops.

**v1.2 amendment (same day, user-directed — "creative spec review… think of gameflow, fun,
historical, with room for surprises"): the gameflow pass.** A creative read of v1.1 asking the one
question the first two revisions did not — *what does the player actually do, turn to turn, once this
ships, and what can still astonish them?* Verdict: v1.1 is a correct **simulation** spec and an
incomplete **game** spec, with two structural gaps. **(1) Pin 3 is a limit, not a mechanic.** "The
player is never a spectator" was guarded by the D1 cap, the D2 floor and the fore-warning — three
*bounds*, none of them participation; the player's verb for an AI-vs-AI war was *reading*. **(2) Total
legibility left no room for surprise** — fully open ladder + fore-warning always + every reason
rendered had traded the diorama for a timetable. Five additions, all additive, **§6 untouched — every
D1–D6 decision survived the read intact**:

- **§4.2b The participation surface** — when an AI-vs-AI war brews, **both sides court France**: join
  A / join B / **sell neutrality** (Prussia 1795–1806 played from the other side) / sponsor without
  joining / **broker** for a price / refuse everyone *having been asked*, which is the whole
  difference. Every arm routes through an existing seam (call-to-arms, paymaster, settlement). Plus
  the third-party **war-exhaustion display** (`world.war_exhaustion` already exists per-nation) so
  "let them bleed while France rearms" — a §1 core fantasy — is a timeable strategy, not a guess.
  *Highest fun-per-line item in the phase.*
- **§3.6 Where the surprises live** — the fog boundary re-drawn from "no fog" to **no fog on
  *dispositions*, fog on *agreements* and *timing***. A court's want/target/rung/war-reason is never
  hidden (D4 intact); but France is not a party to every bilateral treaty in Europe, so the **sealed
  article** (Tilsit's secret articles, the partition conventions) is the historically correct place
  for fog — and pin 12 requires every sealed bargain to be **discoverable before it bites**. Plus
  **emergent designs** (a humiliated or reneged-upon nation promotes a grievance into a *new deck
  design* — Prussia after Jena; this is what makes the DoD's "≥1 agenda shift" a system rather than a
  deck-order tick) and the **volte-face** (a beaten-then-*courted* great power reverses into a partner
  — Tilsit; the reward for generosity, an option the game gives no reason to consider today).
- **§4.6a The beats + tempo** — every system this project shipped *well* named its moment (the
  Proclamation, the petition channel, the muster preview); every flat one emitted lines. Six beats on
  existing transports: **The Courier** (a named envoy through the `incoming_proposal` idiom, not a
  dispatch line), **The Brewing Crisis** (fore-warning with the defusing instruments listed and
  honestly gated — the `/formables` contract applied to diplomacy), **The Ultimatum** (NA-5, re-homed
  as the `coerce` rung), **The Broken Bargain**, **The Volte-Face**, **The Congress**. Tempo rule: one
  foregrounded crisis world-wide — the phase's failure mode is not too few wars but four simultaneous
  crises reading as noise, which is exactly how jealousy failed in *both* prior audits.
- **§3.7 Britain is an auction, not a wall** — the v1.1 correction explained Britain; it did not make
  her *playable* for the fifty turns before the Continental System bites. Make the subsidy **visible**,
  **contestable** (France may outbid for a recipient's alignment), and its clients **removable** by
  peace/compensation/vassalage/defeat. Three-quarters built already (`get_british_subsidy_recipient`
  `coalition.py:1084`, `get_paymaster_nation` `agendas.py:778`).
- **§3.5 The mirror** — intent was entirely outward-facing. France's own ledger row now shows
  **Europe's derived reading of France** from observable deeds only (GR6-safe): what the courts believe
  Napoleon wants, and where they place him on the ladder. The player **can be wrong about how they are
  seen** — a defensive massing reads as a threat whether or not it was meant as one, which is a
  surprise engine costing one derived row and is the road to the Third Coalition, exactly.

**v1.2 self-correction, same session (user: "will this assure the same thing doesn't happen every
time"): §3.8 VARIANCE + the N-seed acceptance sweep.** The first v1.2 draft answered *"can this
surprise me?"* and mistook it for *"will this differ next time?"* — two different properties.
Measured against master: **`agendas.py`, `ai_diplomacy.py` and `coalition.py` contain ZERO `random`
calls between them** (`enemy_ai.py`: 3, in ~4,600 lines), `get_active_agenda` is "first predicate that
holds wins" over an authored deck, and **no campaign seed exists anywhere in the project**. Intent, as
a pure function of world state, inherits that exactly — so combined with pin 1 (byte-identical boot)
**every campaign opens identically and diverges only as the player forks it**: Prussia reaches for
Hanover on the same turn, Britain pays the same client, the same crisis brews at the same moment. The
second campaign teaches you the timings; the third is a script. → **§3.8**: a **serialized campaign
seed** (determinism is load-bearing here — M1–M7, the boot pin, §4.4a's threat series and pin 8's
save/load all need reproducibility, so `random()` at the decision is not available). It perturbs **the
bars, not the choices**: `weight`, opportunism triggers, ladder dwell and cooldowns within a band;
tie-breaks where deck order is quietly acting as destiny; **weighted late** so turn 1 of 1805 still
looks like 1805. Character stays fixed (§3.4) — Prussia still wants Hanover, only *when* moves — and
because the system compounds, a few turns' difference forks the mid-game entirely. **It never makes
intent unreadable** (D4 intact): the jitter moves a number and the ledger shows the number it moved
to, so the seed invalidates **memorisation**, never **understanding**. **Sequencing: AI-0b must land
at the front** with AI-0/AI-1, or every pin written against "the" deterministic trace is revisited.
**Second finding, methodological:** every §7 acceptance number was specified against a **single**
40-turn trace — against a deterministic layer that is not a sample, it is one point of an unsampled
function, and D1's cap would have been tuned against an anecdote. AI-V now runs an **N-seed sweep
(start at 10)** and states the band as a distribution (no run over the ceiling, median in band, no
seed at zero) — the same sweep that **falsifies §3.8**: if every seed produces the same wars on the
same turns, the variance slice failed. New pin 14 (turn-0 intent byte-identical across seeds;
save/load reproduces its own campaign; all existing byte-identical pins green with the seed fixed),
new DoD line, new row **AI-0b**.

**✅ D7 DECIDED same session (user: "yes this should be seeded but within bounds of history") — the
1805 OPENING is seeded too.** The question §3.8 raised and declined to answer is now a gate decision:
**`AI_INTENT_SPEC.md` §6 D7 (authoritative) + §3.8.1 (the historical envelope)**. Without it the phase
would still have shipped a script — Tier-3 divergence only begins once the player has forked the
world, so the first ~10 turns of every campaign would have been identical. **The governing structural
choice: the bounds are AUTHORED CONTENT, NOT A FORMULA** — every varying value carries an authored
range beside it in `europe_1805.json` (the file already holds `nation_relations` ×29,
`diplomatic_states`, `starting_wars`, `agendas`, `threat_level`), and **no authored band → no
variance**. That makes historical fidelity *reviewable by reading the scenario file*, enforceable in
`modding/validator.py` like any other block, free for modders, and it makes ahistorical drift
**structurally impossible** rather than merely unlikely: the engine cannot invent a range it was not
given, so no future slice widens the opening by accident. **Tier 1 — FIXED on every seed:** province
ownership, roster, capitals, `starting_wars` (the Third Coalition *is* the scenario), **deck
CONTENT**, the marshals with their MC-2/3/4 skills+personalities+relationships, treasury/manpower/
force (the blessed E1 band), and the §3.4 statecraft profiles — Austria is Austria. **Tier 2 —
BANDED** (what was genuinely contingent): `nation_relations` per pair (Prussia's disposition is *the*
definitional contingency of 1805 — Haugwitz carried something near an ultimatum to Vienna and arrived
to congratulate Napoleon after Austerlitz), deck **ORDER** among equally-live designs, initial ladder
readiness, small grudges **drawn from real ones** (Austria–Prussia over Germany, Russia–Ottoman over
the straits), **the minors' lean** (Bavaria/Baden/Württemberg were genuinely up for grabs, and §3.4
says a minor's aliveness *is* its timing — the band that matters most), Britain's first subsidy
client, and `threat_level` narrowly (blessed number; **widening escalates**). **Tier 3 — derived**
(intent, coalition posture, advisories, the §3.5 mirror). **The historian test = the pin that makes it
falsifiable:** on EVERY seed the Third Coalition exists, France is at war with Austria/Britain/Russia
and **at peace with Prussia** (Prussia's entry is a thing that *happens*, never a boot state), every
turn-0 active design comes from that nation's own authored deck, nobody boots eliminated or holding a
province it did not hold in 1805, no minor boots at war. **Migration = zero test churn:**
`SOVEREIGN_SEED` joins the documented `main.py` boot-precedence chain; **unset or `=historical`
reproduces today's boot byte-for-byte** (every band collapses to its authored centre) and `conftest`
pins it suite-wide exactly as it already pins `SOVEREIGN_SCENARIO=none` — so all **14,409** existing
tests, the E1 band, M1–M7 and §4.4a's threat series keep their numbers unedited. **§5 pin 1 is
NARROWED, not deleted** ("the historical seed is byte-identical"), and its original intent is actually
*strengthened*: an appetite must now be written into the scenario file to exist at all. Pin 14
amended (its first draft asserted turn-0 intent identical across seeds — D7 overturns that) into a
three-part pin: historical-seed byte-identity · the historian test on every seed · save/load
reproducing its own campaign. The seed is **shown and shareable** (ledger + save) so a good opening
can be replayed or reported against. New row **AI-0c** (authoring + validator schema + `MODDING_FORMAT`
row + the historian test), **order-constrained to the front with AI-0b**.

**Also folded:** the §4.6 narration cap **amended** — it governs *routine ladder movement only*; the
beats are events and are exempt (as written it could have suppressed the phase's best content, the
precise way jealousy buried its own); line selection weighted by `weight` **× proximity to French
interest** (a Danube quarrel and a Prussian design on Hanover are not worth the same two lines); the
minors get a paragraph saying their aliveness is **timing, not character** (Bavaria 1805, Saxony 1806,
Bernadotte 1812 — the flip, not the style); three new pins (**11** surprise is never a lie, **12**
every sealed article is discoverable, **13** guard the *inverse* failure — a living Europe must not
become a soap opera where France's own war reads as incidental, **measured** as dispatch share);
**§7a the seven scenes** — the decade's characteristic events (Confederation of the Rhine, Schönbrunn,
Jena, Tilsit, Pitt's subsidy, the Continental System biting, a partition) as a falsifiable
reachability list, ≥5 of 7 or a written blocking predicate; and four new AI-V assertions. Six new
owner rows (AI-1b/2d/2e/3b/5b/6b) with **honest scope triage in §8** — AI-2d + AI-6b are core, AI-1b +
AI-2e are cheap, AI-3b + AI-5b may slip to the phase exit review with §7a scenes 4 and 7 failing as
their written blocker. Review record + the 11-finding disposition table = **spec §9**. Docs-only.

**Also added (v1.0):** the price ladder gains `bandwagon` and a `sponsor` *branch* (a nation with weight but
not force hires a proxy) plus an **opportunism term** so AI wars land while France is committed
elsewhere rather than at random; three new pins in §5 (derived-intent save/load determinism — the
ladder's *history* must be serialized or "no cold-open wars" becomes a lie on load; and "the AI must
not solve the player's problems"); a concrete narration budget (**2 intent lines per dispatch**,
fore-warnings exempt); and AI-5 finally gets its own test file instead of "folded into the above".

### 🎭 CREATIVE AUDIT (post-NA-6d) ✅ HELD July 19, 2026 — 9 defects fixed; 2 items escalated to gates

**Memo = `docs/audits/CREATIVE_AUDIT_2026_07_19.md`, authoritative** (§9 = the landing record).
Method: a live 10-turn France campaign (`LLM_MODE=anthropic`) + a 40-turn AI-only run through the
real `TurnManager.end_turn` + an agenda/war-status probe. Suite **14,374 → 14,409/3**, ruff clean,
M1–M7 byte-identical 11/11, live-verified on a restarted backend.

- **The headline answer to "do nations act differently now": YES for belligerents, NO for everyone
  else.** Turn 1 alone, Britain drove straight at the Low Countries (`low_countries`) and Austria
  massed Charles+John on Milan (`redeem_italy`); by turn 3 Britain sent a **status-quo settlement
  offer to bank its design**. But **an agenda can only influence a nation already at war** — every
  reference in `enemy_ai.py` is target-*choice* biasing downstream of the ratio/threshold gates, and
  there are **zero `declare_war` call sites** in `enemy_ai.py` / `ai_diplomacy.py`. Five of ten
  nations with decks boot at war with nobody; two hold *acquisitive* designs (Prussia
  `hanoverian_prize`, Sardinia `house_of_savoy_restored`) with no path to pursue them.
- **"Do any formables happen": NO.** 40 turns of real AI: `formations/creations: NONE`, no deck ever
  advanced. `/formables` itself is honest and well-built — it is reporting on a chain whose first
  link is missing for the neutral half of Europe.
- **Milan was severed from Italy** — its only land neighbours were Munich and Tyrol, both across the
  Alps. Italy's `risorgimento` was unreachable by conquest and a retreat from Milan toward Piedmont
  was redirected to Munich, *deeper into Austria*. Fixed: symmetric **Milan ↔ Piedmont** edge; all
  five claimed provinces now form a connected sub-graph.
- **9 defects fixed** (memo §9 table): the pending-decision discard at `main.py:1240` (guard inverted
  from a drifted type allow-list to a derived "offers options = is a decision" rule); the dispatch
  reporting a halted marshal as `en_route` (new `awaiting_decision` status); the purpose clause
  swallowed into an order target (`Milan To Reinforce Massena`); camelCase marshal keys leaking via
  `_name_tag` **and** the outcome clause that bypassed it; `"he has restless for glory"`; the
  duplicate `jealousy_target_notice` line; verbatim headline repeats across turns; a missing space in
  the mild-concern prefix; and the Milan adjacency.
- **Escalated, NOT built** (GR9): agenda-driven war entry for neutral acquisitive designs (a new AI
  mechanic) and the war-economy constants (measured treasury 800 → 20,131 while the army fell
  189,000 → 143,089 — but from a *passive* run, so re-measure from an actively-spending one first).
- **One correction recorded in place:** the first pass of this audit claimed the re-raised interrupt
  was "never surfaced". It is surfaced (`requires_input: True`, queued by `main.gd`); the harness
  simply never printed `strategic_reports`. The memo shows the correction rather than hiding it.

### 🧭 AI INTENT — next-phase spec DRAFTED July 19, 2026 ⏸ AWAITING A USER DESIGN GATE

**Spec = `docs/AI_INTENT_SPEC.md` v0.1 (intent-focused), ROADMAP row AI.** Written straight out of
the creative audit, after mapping the AI decision architecture at `b4b6326`. The finding that
motivates the whole phase is larger than the one the audit went looking for:

> **No AI nation can decide to go to war. About anything. Ever.**

Every `PEACE → WAR` edge is a cascade, a vassal auto-join, a negotiated entry, an armistice expiry, a
rebellion — or `coalition.form_coalition()`, which is a **global anti-France threat scalar**, not a
decision any nation makes. `enemy_ai.py` never imports `declare_war`; agendas bias target *choice*
only, downstream of the ratio/threshold gates (`enemy_ai.py:2669`); `ai_diplomacy.py:1070-1073`
states the absence as deliberate ("the coalition system remains the war-maker"); and `declare_war`
already pre-provisions the AI-vs-AI `"conquest"` objective (`diplomacy.py:7577`) with **no caller** —
the seam was built and never connected. The France-centricity is explicit too: the war-declaration
threat bump fires only when `aggressor == world.player_nation` (`diplomacy.py:7659`) and
`hegemony_passive` skips when the hegemon is not the player (`coalition.py:1738`).

**Scope:** a derived **Intent layer** (want / against / weight / **price**) whose spine is a ladder —
`ask → buy → align → coerce → fight` — so war is the *bottom* of a ladder rather than a dice roll,
and every rung is something the player can counter. Then peacetime pursuit (five idle courts become
active with no new wars), the war decision itself with a **stated reason** and fore-warning,
de-France-centering threat/coalitions/settlements so wars can happen *and end* between third parties,
wiring into NA formations / vassals / econ / jealousy proxy / NA-5 ultimatums (which become the
`coerce` rung), and legibility as the deliverable rather than the polish.

**Six open gate questions (§6)** — headline: how much world-motion is wanted, and whether France
stays the gravitational centre. Recommended sequencing in §6.6: **Battle Diorama (row BD) first** as
a contained slice, then AI-1/AI-2 as a playable increment before committing to AI-3. The phase's
acceptance test is the audit's own falsifying run — the 40-turn AI-only campaign must stop being
static, with the 1805 opening and M1–M7 unmoved.

### 🏛 NA-6d — THE POLAND CHAIN + THE FORMABLES BUTTON ✅ LANDED July 19, 2026 — THE NA-6 ARC IS BUILD-COMPLETE

**Landing record = `NATION_AGENDAS_SPEC.md` §21, authoritative.** Suite green
(`test_nation_agendas_formables.py` 196 → **225**), ruff clean, M1–M7 byte-identical 11/11, Godot
parse harness EXIT=0, headless boot 0 `SCRIPT ERROR`, `GET /formables` live-verified over HTTP.

- **The structural finding: a created client could never proclaim.** `process_formations` skipped
  ANY nation with a `nation_formations` record, and NA-6c's creation writes one at birth — the C→T
  chain was structurally dead, and the same latch blinded the §11.6-5 watcher for created clients.
  Fixed as a QUARTET in `formations.py` keyed on new `_is_creation_record` (birth ≠ formation):
  the poll skips only FORMED records; `_proclaim` preserves the record's `template` key (the
  `from_dict` capital re-derivation depends on it); `_forms_block_for_record` resolves the
  deck-entry arm FIRST (a template-first read would resolve formed Poland back to "Duchy of
  Warsaw"); `get_formation_watch` retires only on FORMED records. `_resolve_sponsor`'s
  prior-record arm went live: **Berlin blames Paris** — Prussia+Russia take the −30 blow vs BOTH
  Poland and sponsor France, exactly once.
- **"The Polish Question" lands on the threat panel** (the NA-6a deferred row): authored
  `grudge_label` on the forms block/template ("The Polish Question", "The Roman Question");
  `get_formation_grudge_contributions` emits per-formation source keys
  (`formation_grudge:<tag>`, court-deduped inside the shared `AGENDA_GRUDGE_CAP` remainder —
  conscious source-key flip, merged-key emission pinned dead); label arm
  `diplomatic_ledger._threat_source_label` shared with the advisory.
- **The Formables button** (§11.6-8): `GET /formables` → `build_formables_payload` — every Class C
  template + Class T watcher, `gate_terms [{text, met}]`, availability = the REAL settlement
  predicate per active war (drift-pinned against `_carve_templates_for_court`), deep_link into the
  qualifying court; never hidden, never dead. The player's own-soil Normandy row renders the
  MIRROR term ("a clause only a victorious enemy may put before you") — found in the live HTTP
  check. `diplomacy_wizard.gd` step-1 gains "Formable Nations — states that could yet exist" →
  step 3 chip rows; deep link lands on the court's action list (`_on_nation_selected`).
- **The watcher's `.gd` consumer** (the NA-6b deferred row): the ledger Design line appends
  "→ forms: Poland (1 of 2 provinces held)"; the war-room per-belligerent design lines carry the
  same marker backend-side.
- **§11.7 final sweep:** the risorgimento-block pin added (a standing Roman Republic holding Rome
  keeps Italy unformed, watcher honestly 4 of 5); one-province watcher copy fixed. Remaining
  live-verify note (§20.1): the AI's treatment of a carved client beyond turn 1 — next played
  session, no code owed.

**▶ NEXT: user in-game review of NA-6c + NA-6d (the §11.10 cadence), then Battle Diorama (Tier A) per ROADMAP row BD.**

### 🏛 NATION AGENDAS BUILD — NA-6c CLASS C CARVE-OUT CREATION ✅ LANDED July 19, 2026 — ▶ NEXT: NA-6d

**A conquering side can now carve a NEW client state out of the defeated party's soil at the peace
table** — the player erecting the Duchy of Warsaw out of Prussia, and (GR5, and the point) a coalition
victor erecting the Duchy of Normandy out of the player's own homeland. Landing record =
**`NATION_AGENDAS_SPEC.md` §20, authoritative**; commit `6e87654`. Suite **14,218 → 14,293/3**, ruff
clean, M1–M7 byte-identical 11/11, Godot parse harness EXIT=0, headless boot 0 `SCRIPT ERROR`,
live-verified over HTTP.

- **Two structural facts shaped the whole slice.** (1) `process_formations` can NEVER announce a
  creation — it skips every vassal, and a carved client is one from its first instant — so the carve
  emits its own Proclamation. (2) `_forms_block_for_record` resolves identity by scanning the nation's
  DECK, and two of the three templates are deckless; without the new template arm, Normandy and the
  Roman Republic would have had no name, no flag and no standing grudge, and every one of those
  failures is a silent `None`.
- **Authored catalogue** (`formable_nations`, serialized like `agendas` because it is read at runtime):
  DuchyOfWarsaw [Posen] carrying the dormant `commonwealth_restored` deck that forms **Poland**
  (aggrieved Prussia + Russia — the C→T chain NA-6d completes); Normandy [Normandy]; RomanRepublic
  [Rome] (aggrieved Austria + Spain). Four heraldry SVGs authored + imported.
- **One predicate carries the whole §11.4 rule**: every template province held by the carver's bloc AND
  its registry `starting_controller` equal to the court being carved — which is simultaneously "carve
  the defeated", "never an ally's soil" and "never your own homeland".
- **The Papal pin holds**: carving Rome eliminates the Papal States and creates the Republic in ONE
  ratification, both events logged — gated on a decisive war score, refused OUT LOUD at the authoring
  seam rather than silently dropped at ratification the way `territory_cede` does it.
- **§11.6 honest availability arrives on the settlement surface for the first time**: the carve row is
  SHOWN when unavailable with its gate terms ("requires Posen"), rendered as inert text rather than a
  link. That surface's own rule had been "ineligible options simply do not appear" — wrong for a
  standing campaign ambition, which then reads as "this game has no such thing".
- **Fixed in passing:** the region double-promise check could not see a carve's template-resolved soil
  (a carve + a cession of the same province both validated); `agenda_settlement_mod` scored a
  carved-away design province as a white peace; `_MATERIAL_LOSS_TYPES` was missing VS-5's
  `vassal_transfer`; the literal 90 in `settlement_ratify` became the shared
  `TOTAL_ANNEXATION_WAR_SCORE`.
- **A 12-lens adversarial review then ran against the commit — 136 agents, 41 candidates, 24
  refuted, 17 survivors merged to 12 distinct defects, ALL FIXED** (addendum `NATION_AGENDAS_SPEC.md`
  §20.1). **No lens came back clean**, and the slice's own tests plus a live HTTP drive had both
  passed — which is the argument for running it. Headline P1: **a carved capital had no garrison,
  forever** (both garrison seams key off `region.is_capital`, the carve set only the world map, so
  the newborn client was an undefended province the enemy retakes for free). Then: a carved Duchy of
  Normandy **rewrote history prose** ("Ney was broken at Normandy" → "...at Duchy of Normandy",
  permanently — Godot had the guard since NA-6b, the backend twin did not); the first end turn
  **announced the new nation as eliminated**; duplicate elimination announcements — and the §11.2
  Papal pin turned out **untestable in play**, passing only because its helper bypassed
  `capture_region`; a carve **stripped a marshal's estate with no ES-7 warning on any surface**;
  `_MATERIAL_LOSS_TYPES` was **a no-op** (the frozenset is only the early-out gate); a **bankrupt
  loser could never be carved** (the empty-purse arm returned above the carve gate, so the most
  beaten France was the one immune); and **the player's actual click path had zero coverage**.
  Falsifiability verified by reverting four fixes — exactly the four matching tests fail.
- **✅ Visual check HELD July 19, 2026 (spec §20.2) — both sign-off rows CLOSED.** Three flags passed
  first look; **Normandy FAILED and took five drafts** — centipede, cartoon cub (with a *smile*),
  spiky-sun mane, housecat, then the shipped lean maneless leopard. All five were then **discarded**: user-directed
  same day, `Normandy.svg` now adapts the **public-domain "Flag of Normandie.svg"** (Wikimedia,
  Saebhiar, PD-self — licence verified against the live source page), exactly as `Hanover.svg` adapts
  the PD Saxon Steed, re-fitted to 500×300 and recoloured to the game palette with the azure tongue
  and dark outline kept. Real heraldry at last — manes, claws, tongues, correct passant guardant —
  and still clean at 44px. **Lesson:** when an asset class already has a sourcing precedent in
  `THIRD_PARTY_LICENSES.md`, reach for it before the fifth redraw, not after. The greyed carve row was rendered from the live payload
  through the exact BBCode the client builds: it carries the gate ("requires Posen"), names what is
  missing, and contains **no `[url=`** — un-clickable by construction, not a dead button.
- **Session hazard worth remembering:** a review subagent ran `git stash` to "compare against baseline"
  and destroyed the entire uncommitted tree (23 files, 2,167 insertions). Recovered intact from
  `stash@{0}`. Standing lessons: commit a large slice BEFORE handing it to a review fleet, and hand
  review agents a pre-snapshotted diff plus an explicit read-only prohibition.

### 🔍 WHY "give them hell" FAILED IN LLM MODE — the `generic` sentinel ✅ FIXED July 19, 2026

**User pushback: "my concern was why give them hell was failing in llm and if similar fails exist".** Fair — the July 18 fix made the FAST parser handle the idiom, which *bypasses* the LLM. That fixed the symptom and never answered the question. Probing the live model directly (bypassing the 0.7 gate) gave the real answer.

**The LLM was never wrong.** On `"Ney, give them hell"` it returned `action=attack, target="generic", ambiguity=65` — correctly saying *"attack, but you named no foe I can resolve"*. It invented nothing. (Same for `"give Charles hell"`: Charles is FOGGED at boot, so refusing to name him was right.)

**The break was a three-layer contract failure downstream:**
- `prompt_builder` **instructs** the model to emit it — *"If you cannot determine the specific region, set target to `generic` and ambiguity to 60+"*, plus the `pursue the enemy` / `support whoever needs it` examples.
- `PARSE_TOOL` **advertises** it (*"Enemy commander, region name, or 'generic'"*) and `_extract_valid_targets` puts it in the valid-target list, so validation **blesses** it.
- The tactical executor **rejected** it: `attack` → *"Unknown target: generic"*, `move`/`scout` → *"Region 'generic' not found. Nearby: Guyenne, Nivernais, Balearics"*.

Three layers agreeing to produce a value the fourth refuses. And since **vagueness is precisely what sends a command to the LLM**, every vague live command shared the fault — this was systemic, not one idiom. The STRATEGIC executor had carried the correct sentinel set privately all along (`generic`/`the enemy`/`them`/`whoever`/`nearest`…); the tactical path never learned.

**Fix:** hoisted that set into one shared source (`backend/ai/generic_targets.py`), consumed by the strategic path and by a new normalization at the parser seam that collapses the sentinels to `None` — where the executor's existing, well-exercised auto-resolve path takes over. Plus a defence-in-depth normalization at `executor.execute`, deliberately: the original defect *was* one layer assuming another had handled it.

**"Do similar fails exist?" — measured, not assumed.** A live sweep of 10 vague phrasings that genuinely reach the LLM found 2 more hard failures beyond the reported one:
- **`"Ney, take up a better position"` / `"Ney, reposition"`** → *"Move order requires a destination"*. Same shape, one action over: an attack with no target auto-resolves to the nearest enemy, but a move **cannot** — there is no nearest destination. Now raises a `move_destination` clarification offering the marshal's adjacent regions, each reissuing a fully-formed `"<marshal>, move to <region>"`. Stands down for automated strategic hops (nobody is at the keyboard).
- **`"Ney, we need more troops"` → "treasury cannot support this"** — investigated and **NOT a defect**: France boots with 800 gold and a recruit costs 1003; an explicit `"Ney, recruit infantry"` gets the identical refusal. My probe's crude pass/fail had miscounted a correct in-game answer as a failure.

Post-fix live re-run: **6/6 clean** — the idiom musters, the vague attacks muster, the vague moves ask where, the scouts scout.

**Residual, noted not fixed:** the LLM occasionally returns a marshal name as a `recruit` target (observed `target=Moore`). Functionally inert — `_execute_recruit` uses `marshal.location` and ignores the target — but it is a wrong value passing validation.

Suite 14,206 → **14,218/3**, corpus 453/453, ruff clean, live-verified in `LLM_MODE=anthropic`.


### 🤖 LLM LAYER HEALTH PASS ✅ HELD July 18, 2026 — SDK migration + 7 confirmed fixes

**User direction: "make sue llm is in good shape commi and push".** A 28-agent audit of the whole LLM integration (4 lenses → skeptic refuters) plus a hands-on review against the current Anthropic API reference. **24 raw findings → 7 confirmed**, all fixed. Suite **14,204 → 14,206/3**, corpus 453/453, ruff clean, live-verified in `LLM_MODE=anthropic`.

**Headline: the integration was hand-rolling raw HTTP against an SDK it already depended on.** `anthropic==0.75.0` has been in `requirements.txt` and installed all along, while `providers.py` POSTed to the endpoint with `httpx` — paying for the dependency and using none of it. Migrated to `client.messages.create`, keeping the `_post_messages(body) -> (response_json, error)` seam byte-compatible so all 235 existing LLM tests and their mocks pass untouched (`message.to_dict()` converts the typed response back to the wire shape the callers read).

- **RETRIES — the real win.** There were none: one 429, one 529 overload, one dropped connection and the command degraded straight to the sub-0.7 fast-parser guess, which then EXECUTED and spent AP. Same words, different order, depending on an invisible rate limit. `max_retries=1` with the SDK's exponential backoff and `retry-after` handling. Deliberately ONE — the parse sits inside the player's command round-trip, so the ceiling is a latency budget (~11s), not just a cost.
- **The "5s" ceiling was a fiction.** A bare timeout applies PER OPERATION, so a flaky network could block ~15–20s while the code and its comments asserted 5s. Now `anthropic.Timeout(5.0, connect=2.0, pool=1.0)`.
- **Typed exception chain** (auth / permission / not-found / bad-request / rate-limit / timeout / connection / status), so the log names WHICH failure instead of a status-code ladder we maintain. Plus the `request_id`, the one value Anthropic support needs to trace a failure and which was previously unrecoverable.
- **Truncation was undetectable.** A forced tool call cut off at `max_tokens` still arrives as a well-formed `tool_use` block — the SDK reconstructs the partial JSON — so a truncated parse was indistinguishable from a complete one and would sail through as a confident order with fields silently half-written. `stop_reason` is now checked BEFORE the tool input is read (`max_tokens` and `refusal` both discard).

#### The two P1s the audit found

- **The async middleware was blocking the entire event loop.** `serialize_state_mutations` is `async def` and took a `threading.Lock` with a plain `with`, holding it across `await call_next` — so while one POST was in flight NOTHING else on the server could progress. Invisible while handlers are fast (they are plain `def`, so FastAPI threadpools them), and very visible the moment a POST blocks on a live LLM parse: a stalled call could freeze the server for the whole timeout, and the client double-send the UI-6 chip latch exists to defend against is exactly what produces a second POST in that window. Now `asyncio.Lock` + `async with` — same mutual exclusion, yields the loop. Pin consciously flipped (`test_state_lock_exists` asserted `threading.Lock`, which WAS the defect) and paired with a new test that the middleware acquires it with `async with`.
- **`repudiate_bargain` was dead end-to-end, in mock AND live.** The parser routed it, validation passed it, and `diplomatic_executor` had dispatched it all along — but `executor.py`'s diplomatic action tuple never listed it, so every "repudiate the bargain with Austria" fell through to the unknown-action tail and died as "Unknown command". One line; now answers in character ("There are no active bargains to repudiate, Sire.").

#### The rest

- **A dropped API-failure signal.** `reparse_with_llm` stamped `llm_error` on a local `ParseResult` the caller never saw, so when the CR-2 forced retry itself timed out, nothing downstream knew — and Berthier recovery could fire a THIRD blocking call on a request whose first two had already failed. Return contract widened to `(dict_or_None, llm_error)`; returned as an explicit tuple rather than mutating the input dict, since an argument that quietly becomes an output is the same implicit seam that let the signal go missing.
- **`requested_type` was structurally unreachable on the live path.** PARSE_TOOL has no such property and the prompt never asks for one, so the field `_execute_recruit` reads for its soft-correction message ("Ney commands no cavalry, Sire") could only ever be None there — any recruit phrasing the fast parser failed to classify silently lost the arm. Now derived DETERMINISTICALLY from the raw text (new single source `backend/ai/recruit_arm.py`, consumed by both the mock branch and the parser seam) rather than adding a schema field: the arm is a fact about the words typed, not a judgement call, so this is GR6-purer AND repairs the case where a live re-parse discarded a fast-parsed arm.
- **The META_ACTIONS validation bypass was too wide.** It returned above the score clamp and above the Sweep-5 invented-marshal guard — so a META parse could carry an out-of-range score into downstream arithmetic, and could name a marshal the player never uttered. Both hoisted above the bypass; the marshal-membership, multi-marshal and VALID_ACTIONS checks correctly stay below it (META actions are nation-level and deliberately absent from VALID_ACTIONS).
- **Six phantom schema fields removed** from `json_to_parse_result` — `standing_order`, `condition`, `dialogue`, `requested_type`, `cheat_type`, `cheat_args`. None is a PARSE_TOOL property, so reading them advertised an input contract the schema does not offer and (the schema being deliberately non-strict) invited an extra property the pipeline would carry. Each disposition is documented inline.

#### Verified clean — worth recording

- **GR6 holds.** Traced every mechanically-dangerous field: cheats are unreachable (`cheat` is in neither META_ACTIONS nor VALID_ACTIONS, so validation discards the whole result); `debug` is hard-gated on `debug_mode`; the `diplomatic_data` allowlist + field-strip correctly runs BEFORE the META bypass; hallucinated marshals are set-checked and the invented-marshal guard strips them. No LLM output reaches a mechanical effect without a deterministic gate.
- Model pin `claude-haiku-4-5` is current and correctly aliased; no deprecated parameters (`output_format`, `budget_tokens`, assistant prefill) anywhere; `temperature: 0` is valid on this model.
- **Prompt caching assessed and REJECTED, with the reason recorded** so it is not re-litigated: tools+system is ~700 tokens, below Haiku 4.5's 2048-token minimum cacheable prefix, and the volatile game state sits at the TOP of the ~3.7K-token user prompt. Making it cacheable needs a prompt restructure whose regression risk outweighs the saving on a call that only fires for sub-0.7 parses.

**Live-verified** on the real API: `"Ney, deal with Mack"` → 2.7s, correct delegation parse with a flavor line; `"Ney, make it so"` → Berthier recovery in character. Both log `request_id` and token usage.


**Two corrections I had to make to my own fixes, caught by the suite and by a test I wrote:**
- The first cut of the lock fix used a single module-level `asyncio.Lock`. That binds to the first loop that awaits it, and every `TestClient` spins up a fresh loop — **21 endpoint tests failed**. Now per-loop.
- The second cut keyed those locks by `id(loop)`. CPython reuses addresses, so a new loop could inherit a collected loop's lock and raise the exact error the indirection exists to prevent — caught by `test_state_lock_is_per_event_loop`, which I had written for precisely that hazard. Now a `WeakKeyDictionary` on the loop object, so entries also retire with their loop.
- I also over-reached by deleting six phantom field reads from `json_to_parse_result`; a pin (`TestParseResultIncludesFields`) correctly encodes it as a faithful mapper. Reverted to reading them, with the reachability analysis recorded in the docstring instead. The fix that mattered — deterministic `requested_type` — stands on its own.


### 🎯 JULY-18 PLAYTEST SWEEP — the "give them hell" command family + the viewport-overflow sweep ✅ BOTH LANDED July 18, 2026

**User report (verbatim):** *"few issues found, when is ay ney give them hell he doesnt do anything it just give options then i said ney gives charlkes hell and a popup appeared. also the dplo window is too big for the screen when in settle a war. look for similar issues fix them commit and push"*

Both reports were real, both had a family behind them, and the sweep found them with a 34-agent find→adversarially-verify workflow (28 confirmed of 30 raw) followed by a 50-agent pre-commit review of the fix itself (15 confirmed of 23, each double-refuted). Suite **14,017 → 14,201/3**, corpus **433 → 451/451**, ruff clean, parse harness EXIT=0, headless boot **0 `SCRIPT ERROR`**, all 34 scenes instantiate.

#### Track 1 — the command family (backend, commit `06a2f1e`)

- **The two halves of the report were ONE defect seen from two angles.** "give … hell" was unrecognized by every parse layer — absent from the fast parser's keyword chain, the CR-5 delegation verb allowlist, and the golden corpus — so it fell to the live LLM to freelance a lethal order. The two phrasings then diverged at the **ESP-EV-4 guessed-target guard, which sat AFTER the range-check block**. That block returns early with a strategic PURSUE, so an out-of-range guess marched off unguarded and opened a bad-odds popup over an enemy the player never named, while a target that grounded nothing hit the guard and got a flat terminal refusal offering nothing to answer. *Same intent, two surfaces, one of them a dead end.*
- **The vocabulary had drifted three ways.** Three seams carried three independent copies of "what counts as an attack word", and `_TARGETING_ANCHORS` had drifted WIDER than the parser could route: it listed smash/crush/destroy/engage/assault/storm/rout with no parser branch, so *"Ney, attack Mack"* then *"Ney, crush him"* resolved the pronoun perfectly and **still shrugged**. New single source `backend/ai/attack_vocabulary.py`; the anchor set is now a superset **by construction**.
- **Landed vocabulary:** colloquial idioms (give them hell, crush/smash/destroy/engage/assault/storm/rout/defeat/ambush, no quarter, put them to the sword, wipe them out, have at them, fall upon, finish him, **give battle** — copy the game itself prints), capture verbs capture/seize beside occupy, and `observe` on the scout branch. **Deliberate exclusions, each pinned:** `take` (stamps conf 0.95, would short-circuit the live LLM and silently degrade the CR-5 personality arms), `secure` (HOLD family), `march`/`advance` (move family), bare `watch` (would swallow "build a watchtower" and the corpus's negative pin "the warden watches").
- **Silently WRONG actions killed — worse than a shrug.** `cover/screen the retreat` ordered the marshal *himself* to retreat and spent the AP; `fix bayonets` and `restore order in Vienna` executed masonry repairs. All at confidence 0.9, i.e. **above the LLM-fallback gate, so live mode could never correct them**.
- **`head FOR Vienna` shrugged while `head TO Vienna` marched** — a one-word difference the player cannot see is significant. Destination-bearing and possessive-object forms added, anchored so they cannot shadow the SUPPORT family.
- **No more fabricated provinces.** `"hell"` auto-corrected into the province **Algiers**, which rode into Berthier's live recovery prompt *as a fact the Emperor had stated*, so his suggested rephrasing could name a province 1,500km from the marshal. The extraction scan is now gated on a resolvable action and idiom filler is skip-listed.
- **Delegation last names:** *"Ney, deal with Charles"* lost the delegation entirely while *"deal with ArchdukeCharles"* produced the correct CR-5 ASK. Last-name tokens resolve now, **uniqueness-gated** so an ambiguous token ("archduke", owned by two Archdukes) is declined rather than silently guessed.
- **Berthier stopped reciting internal ids** ("break_square, change_autonomy"). The live prompt had been fixed for this in the F5 pass; the mock template had not.

#### Track 2 — the viewport sweep (Godot)

- **The settle-a-war window is `proposal_confirm_popup`, not the wizard** — `_on_action_selected` closes the wizard before the settlement opens. Its `FooterLabel` was `fit_content=true` / `scroll_active=false` with no minimum, as a direct VBox child **outside any ScrollContainer**: the one unbounded contributor. Since the panel is centre-anchored with `grow_vertical=2`, the overflow split across BOTH edges and carried the action buttons off the bottom — **with no ESC handler and no overlay click-to-close, an unrecoverable soft-lock**.
- **`Utils.clamp_centered_panel` already existed and was already correct — it just reached 5 of ~30 surfaces** (the layer-50 ledger screens). None of the ~20 modals called it. **But adding the call alone would have fixed nothing:** Godot clamps a Container's size UP to `get_combined_minimum_size()`, so rewriting offsets is inert until the content is bounded. Both halves were required everywhere, and that is the sweep's organising fact.
- Landed: footer + tier-2 affordance rail bounded (uncapped Press/Ease buttons no longer share the primary rail, so Submit/Back Out cannot be pushed away); viewport-derived per-court floor; option-derived ESC hatch (`dismiss` is a *proposal*-family action with no settlement arm — hard-coding it would desync the dialogue); proclamation body scrolled with the flag and [Acknowledge] pinned outside; reward-dialog explainer bounded; wizard floors lowered so its own chain no longer exceeds its authored box; `war_detail_popup`'s button row **HBox → HFlowContainer** (an HBox's minimum width is the SUM of its children, and that panel is right-anchored with `grow_horizontal=0`, so a Third-Coalition-sized bloc grew it LEFT off the viewport); keyboard dismissal for both report dialogs (`main.gd`'s ESC ladder refuses to act while a modal is open, so a clipped [Continue] cost the player the turn); clamp rolled out to all 27 centre-anchored surfaces.
- **The helper itself was hardened** with an anchor guard (it writes symmetric offsets, so an edge-anchored panel would be teleported — guarded structurally, not by trusting callers), a degenerate-rect guard, and a second pass that relaxes descendant minimums so the clamp can actually bite.

#### What the pre-commit review caught (and why it mattered)

- **P1, a regression that never shipped.** The first cut of the guard rewrite refused *any* order whose descriptive words grounded nothing — so **"attack the weakest enemy", "attack the enemy vanguard", "attack the British army"** would all have bounced to a popup. **The set of words a player may use to describe a foe is not enumerable**, so a guard keyed on a filler denylist is the wrong instrument. Resolved by splitting on **who chose the target**: a PARSER substitution of one real foe for another still ASKS (the original ESP-EV-4 case, unchanged), while an ENGINE pick **proceeds and DISCLOSES** — *"Your words named no foe our maps know, Sire — Ney marches on Mack at Swabia, the nearest in sight. Name another and he will turn."* No legitimate order is blocked; no substitution is silent.
- **P1, a one-way ratchet.** `_relax_child_minimums` measured against the already-shrunk minimums it had left last time and never wrote anything back — open the settlement once at Interface Scale 2.0 and the per-court table stayed pinned near the floor **for the rest of the session**, on a full-size screen. Now restore-then-measure (a pure function of viewport and content) and iterated, because one proportional pass systematically under-delivers when a share lands on a control whose real minimum is text-derived.
- **The clamp cache had to learn to follow its caller** — `proposal_confirm_popup` re-derives its per-court floor from the live viewport every open, and a write-once cache would have clobbered that fresh value with a stale one, silently undoing the scene-level half of the fix.
- Plus: six modals that received the clamp call while keeping an unbounded `fit_content` label (covered-looking but not covered), the settlement preamble laying out at height **zero** once the relax pass ran, and an R7 camelCase leak (`"ArchdukeJohn at Tyrol"`) into the clarification's player-facing labels.
- **Three of the new tests were vacuous and the review proved it by mutation** — deleting the relax call site left all three green. Rewritten to pin the WIRING (scoped to the function body, not the file), and the whole set re-mutation-tested: **all 14 mutants now caught**, including `range(_RELAX_ROUNDS)` → `range(1)` and a neutered anchor guard. The hand-written clamp list (12 of the 22 touched scripts) was replaced by one **derived** from the scenes, with a paired negative pinning the two deliberately-excluded edge-anchored panels.

**Follow-up the same day — "will it work with the LLM?"** Verified live in `LLM_MODE=anthropic`, and the answer is **yes, and it no longer needs the LLM at all**: the idiom now scores 0.9 in the fast parser, which is above the 0.7 fallback gate, so it resolves **deterministically** and behaves identically in mock and live (GR6). That property exposed one more gap, since a phrasing that never reaches the LLM must resolve its own names: **"Ney, attack Charles" resolved to NOTHING even with ArchdukeCharles fully visible** — the full-name patterns only cover "archdukecharles" / "archduke charles", and fixing the delegation path alone had left the ordinary attack verb behind. Both seams now draw from ONE uniqueness map (`llm_client.unique_name_tokens`, consumed by `delegation._resolve_target`). **The golden corpus immediately caught the first cut of it:** ArchdukeCharles is FOGGED at the 1805 boot, which left "archduke" uniquely owned by ArchdukeJohn among the VISIBLE enemies, so `"attack archduke charles"` resolved to the *wrong Archduke*. Restricted to SURNAMES — a title identifies a rank, a surname identifies a man. Corpus 453/453, suite 14,201/3.

**Live-verified on fresh worlds:** *"give them hell"* → clean muster against Mack · *"give Charles hell"* → muster **with disclosure** · *"attack the weakest enemy"* → engages, never blocked · *"attack Venetia"* with a resolved target → the answerable clarification, clickable and typeable · *"crush Mack"* → clean named attack.

**One pin consciously flipped:** `TestGuessedTargetGuard::test_substituted_target_is_refused` asserted the dead-end shape; it now pins the clarification, keeping the load-bearing invariants (no battle fought, no interrupt staged) and adding the new one (it is answerable).


### 🔎 NATION AGENDAS — FIFTH REVIEW (whole-arc AUDIT) ✅ HELD + ALL FINDINGS FIXED July 18, 2026 — → NA-6c → NA-6d

**User direction: "fix all make decision and inform me … sensitive to the golden rule and history and fun. commit and push after all fixes in."** A 112-agent adversarial audit of the whole arc NA-0..NA-6b at `57dbde7`: 29 raw findings → **8 survived** triple refutation (2-of-3, default-REFUTED). Memo `docs/audits/NATION_AGENDAS_PHASE_AUDIT_2026_07_18.md` (authoritative); fix record **`NATION_AGENDAS_SPEC.md` §19**. Suite **14,018 → 14,047/3**, ruff clean.

- **P1 — deny satisfaction was anchored on bloc membership, and a coalition is not a bloc.** §18's court-relative hegemon fix was necessary but not sufficient: its stated justification — *"Coalition formation produces real `ALLIANCE` states"* — is **factually false**. `form_coalition` writes `active_coalition`, declares war, nudges relations +10, and writes **no diplomatic states at all**; the boot Third Coalition is allied only because the scenario authors those rows. A coalition formed in play left the denier in a bloc of one and its design read SATISFIED while the enemy held every listed province (+10 resolve, early separate peace, invisible to the player). **Ruling: satisfaction is a statement about the PROVINCES.** Denied ⇔ held by self/own client, or by a below-major power outside the hegemon's bloc. §11.2 (a free Dutch buffer satisfies), D68 (allying in is dormancy) and guard 2 (a beaten great power is still a great power) all preserved; **D70 closed**. Boot byte-unchanged. `TestCoalitionIsNotABloc` pins the false premise so it cannot silently become true.
- **Coherence — a WON design could not be priced at ENTRENCH.** Both acceptance scorers gated on the ACTIVE view, which is `None` once an acquire satisfies — or is a *different, later* deck entry (Austria holding Milan flies `primacy_germany`, so a demand for Milan matched nothing). More success bought less defence of the province just won. New `_satisfied_view`; both ENTRENCH-strip arms price the live design AND the won one. ADVANCE deliberately still fires only from the live design.
- **P3 — an armistice is a pause, not a restoration of neutrality.** It both WOKE the paused opponent's guard design and STRIPPED the war exemption from the army standing there because of that war (−25, and −70 relation resumes the war instead of maturing it to peace). New `_belligerent`/`_has_belligerency`; §5.9's written predicate amended — the code matched the spec, so this was a shared gap.
- **P2 — a demand overtaken by war is not a bargain.** Yielding after the pair fell to WAR still ceded the province, wrote a perpetual tribute treaty and reported *"The peace holds"*; yielding to an issuer eliminated that turn **resurrected** it. Reachable with zero player action via an ally cascade. `_ultimatum_void_reason` gates both arms; defying a void demand plants no pressure marker. New log type `ai_ultimatum_void` (pins 121→**122**).
- **Also landed (`e44c5db`):** three §11.8-stage-3 dead-name surfaces the §17.1 sweep missed (the diplomatic nation-picker — the surface used to *talk to* the nation just created; the NA-5 proposal/ultimatum notification, unrepairable client-side for single-token tags like `Holland`; the pre-proposal objection summary) + `ENEMY_AI_REFERENCE`'s P4 row citing `get_agenda_covets` where the code calls `get_agenda_military_targets`.
- **Empirical firsts:** a formation occurred **organically** for the first time — United Netherlands, driven through `release_vassal` → real garrison combat → `_attempt_region_capture`, no `region.controller` ever assigned (closes half of D65(a)). Over 40 turns of unattended AI play, **4 of 6 §0 G2 coupling pillars are observable**; the target bias is near-inert by construction (150 picks, 103 multi-candidate, **0** exact-ratio ties). §11.9's sponsor machinery is unreachable but assessed **GR9-compliant** — owner, landing slice, completion definition, STATUS line and behavior tests all exist. Typing "Italy" still gets nothing (D65(b), NA-6c).
- **Probe trap worth keeping:** `power_score` reads `get_nation_regions`, cached behind `invalidate_active_nations_cache()` — **not** `invalidate_bloc_members_cache()`. A probe that mutates `region.controller` and flushes only the bloc cache sees a stale bloc share and wrongly concludes the geometry is unreachable. That is very likely why three prior slice reviews missed the P1.

### 🏛 NATION AGENDAS BUILD — NA-6a + NA-6b ✅ LANDED July 18, 2026 · in-game review + 2nd adversarial sweep ✅ HELD same day (1 P1 + 5 P2 FIXED) · WHOLE-PHASE review ✅ HELD (1 more P1 + 2 FIXED) → NA-6c → NA-6d

**User direction: "do a and b then your own visual check commit and push when done."** Both phase-1 formable slices landed in one session per the §11.10 plan of record, which pauses here for review before the Class C carve work. **Landing record = `NATION_AGENDAS_SPEC.md` §17 (authoritative).** Suite **13,890 → 13,997/3**, ruff clean, parse harness EXIT=0, headless boot **0 `SCRIPT ERROR`**, M1–M7 byte-identical 11/11 before AND after. NA-6a at `9a559f8`.

- **The structural fact:** `get_active_agenda` cannot be the formation predicate — an `acquire_regions` entry is ACTIVE only while UNMET, so on the tick it satisfies the chokepoint already returns the NEXT deck entry (that IS §11.1-4's "post-formation goals for free"). `process_formations` scans the RAW deck via a new public `agendas.entry_satisfied`, and walks the whole deck, not just `deck[0]`. Both pinned.
- **NA-6a:** new `backend/game_logic/formations.py`; ONE serialized key `nation_formations {tag: {id, sponsor, turn}}` (`turn` = a conscious §11.10-1 extension); both call sites wired + pinned (tick BEFORE the shift poll; ratify AFTER the cache invalidations); `risorgimento`→**Italy** and `the_seventeen_provinces`→**United Netherlands** authored — **both decks were single-entry, so `guard_the_peninsula` / `merchants_peace` had to be authored too** or the post-formation mechanism had nothing to fall through to; the Britain-deny mirror pinned and fully derived; §11.9 relation blow + `formation_grudge`; validator `forms` block (a `forms` on a POSTURE type is an ERROR — a formable that can never fire is the dead promise GR9 forbids).
- **Conscious deviation from §11.10-8:** the shared `AGENDA_GRUDGE_CAP` is a deterministic **budget split**, not a joint clamp — one merged `add_threat` would have destroyed §11.9's "the threat panel NAMES the grievance", and this keeps `_calculate_agenda_grudge_threat` byte-identical so both NA-3 pins stay put.
- **NA-6b:** `proclamation_popup.tscn/.gd` on **CanvasLayer 117** (re-measured, spec claim holds), PopupQueue slot + `nation_proclamation` key, choice-less with no response endpoint; the two Godot R7 chokepoints (`Utils.formation_overrides`, consulted before the static map AND the camelCase split) with the **`_flag_path_cache` flush** it had never had; adoption at `api_client`'s single 200-OK chokepoint, before the callback; `_is_prose_safe_nation_key` (Normandy/Rome are PROVINCE names — NA-6c walks straight into that trap); `Italy.svg` + `UnitedNetherlands.svg` + `.import` sidecars.
- **The live visual check earned its keep — SIX defects found by looking, all fixed in-session:** the flag silently not rendering (no `.import` sibling); dead space on a fixed-height card; **a dead-name leak on the ledger** ("while **Kingdom of Italy** holds Milan" survived the proclamation — the backend bakes the already-humanized name, so Godot cannot repair it downstream; fixed at the agenda + war-room prose seams via `formed_display_name`); **P1 the entire end-turn report swallowed**; **P1 the terminal soft-locked**; and a rump state able to proclaim a triumph then take up "Survival" on the same card (the raw-deck scan bypasses the survival override — it had to be re-applied).
- **The architecture changed as a result:** the Proclamation is deliberately **NOT** a pre-empting route. Every `_post_hud_response_routes` entry returns from `_on_command_result` before the enemy-phase dialog / turn text / dispatch AND without re-enabling input — and a formation fires inside `advance_turn`, i.e. on exactly the `enemy_phase` response. The card is now STASHED ahead of all routing (so a higher-precedence modal cannot destroy it either) and shown when control returns, after the dispatch. The command-tail seam is guarded on `enemy_phase` — a residual caught on the SECOND live pass, where unguarded it swallowed the very tail it was added to preserve.
- **Pre-ship adversarial review:** 8 lenses → 2 independent refuters each (17 agents, ~2.7M tokens). It found both P1s and the survival-gate hole; the live drive independently confirmed them. Final live sequence verified end to end: **enemy-phase report → Morning Dispatch → The Proclamation → Acknowledge → terminal accepts commands.**
- Conscious pin flips: `CAMPAIGN_LOG_TYPES` 120→**121** (×2 files), `PopupQueue` slots 10→**11**. Deferred with owners: the per-formation threat label + the §11.6-5 watcher's `.gd` consumer → **NA-6d**; the five other mid-turn region-transfer paths → **NA-6c**.

- **In-game review + second adversarial sweep (same day, delegated): 1 P1 and 5 P2s found and FIXED — record `NATION_AGENDAS_SPEC.md` §17.1.** Headline **P1: the Proclamation was 100% undeliverable on the settlement-ratify path** — the PL-14 response REBUILD in `_respond_to_dialogue_sync` discarded a popup that `_include_popup_passthroughs` had already POPPED off the queue and cleared from the world; the formation latch then guaranteed it could never re-fire. Fixed generically (`_capture_popup_passthroughs` / `_restore_popup_passthroughs`) — the defect silently ate ANY popup type, not just this one.
- Plus: **two formations on one tick lost the second card** (found by driving a staged double formation — both nations formed for real while the single queue slot swallowed the second landmark; overflow now rides `nation_proclamation_popups`, the `vassal_rebellion_imminent_popups` precedent, and the dismissal handler chains); **the card was stranded whenever the tick produced strategic reports** (the DOMINANT case, not an edge case — formations come from conquest, i.e. marshals under standing orders, which is exactly what populates `strategic_reports`; the tail is now ONE `_return_control_to_player()` called from all four control-returning seams); **the command-tail seam swallowed the whole response** (ratify → card → Acknowledge → never learn the settlement was ratified, ended war still in the HUD; the card now comes LAST); **five more dead-name seams** (the battle Materiel line, two dispatch beats, and the always-on-screen coalition war-HUD row — `humanize_entity_name` was also mangling it to "Kingdom Of Italy"); and **the campaign log rendering post-formation events under the dead name** — fixed history-respectfully, so pre-formation entries keep the contemporaneous name and "Kingdom of Italy is no more — Italy is proclaimed" stays coherent.
- **Live dead-name sweep three turns past the formation across `/status`, `/ledger`, `/diplomatic_ledger`, `/marshal_overview`, `/dispatch`, `/campaign_log`: NO present-tense dead names remain** — the only surviving mention is the proclamation line that is supposed to carry it. (An earlier pass read a STALE backend that had outlived a failed restart and briefly showed an already-fixed leak — a live-verification trap worth remembering: check the server's start time, not just that it answers.) Sequence re-verified end to end in the client: enemy-phase report → Morning Dispatch → The Proclamation → Acknowledge → terminal accepts commands. Suite **14,011/3**, ruff clean, M1–M7 byte-identical, parse harness EXIT=0, boot 0 `SCRIPT ERROR`.
- **Working as designed, confirmed by the review:** Britain retook Flanders and Amsterdam during the enemy phase of the double-formation run, so Holland lost both its target province and its capital and correctly did NOT form — organically exercising the survival-override gate the first sweep added.
- **Residual risk stated in §17.1:** no formation has yet happened *organically* through played conquest (every exercise staged the provinces); the formed nation cannot yet be addressed by its new name (the name→tag resolver is unpatched, homed to NA-6c with the carve tags); `deny_regions`/`contain_hegemon` formables are validator-blessed and documented but never authored or run.

- **WHOLE-PHASE review (NA-0 → NA-6b) ✅ HELD July 18, 2026 — record `NATION_AGENDAS_SPEC.md` §18.** A 21-agent arc-level sweep (10 lenses → refuters → synthesis) scoped to cross-slice interaction rather than any one slice. It found **ONE P1 that all three previous slice-scoped reviews had missed**, precisely because it lives in a geometry no single slice owns.
- **The P1: the anti-hegemon designs deleted themselves at the moment they succeeded.** `agendas._hegemon` consumed `coalition._identify_max_bloc_share` RAW — "who is biggest" — which is the wrong question for an ANTI-hegemon design. Coalition formation makes real `ALLIANCE` states, so once the anti-France bloc out-massed France the raw answer became **Britain's own ally**, and every predicate keyed on it inverted: Britain's `low_countries` and Russia's `arbiter_of_europe` went INACTIVE for the rest of the war they were being fought over (ledger row, war-room line, rung-1.5 counsel, acceptance mod, covets, `agenda_pursuit` voicing — all silent with them); **the paymaster stopped paying exactly when the coalition it funds existed** (a regression against the NA-3 Britain literal it replaced); and worst, the deny SATISFACTION check read **TRUE while France still held the Scheldt**, handing Britain +10 resolve and an early separate peace *for France winning the thing Britain denies*.
- **Fixed in two contained parts:** `coalition.identify_ranked_bloc_shares` (the ranked form of `_identify_max_bloc_share`, which becomes its `[0]` — the two non-agenda consumers stay byte-identical), and **court-relative** `agendas._hegemon(world, nation)` = the largest bloc that court is NOT in, threaded through all 14 anti-hegemon call sites. Boot-identical on the shipped scenario; the forms only diverge once the geometry inverts. Plus a satisfaction correction with two guards, each earned from a defect: sitting inside the DOMINANT bloc is dormancy and never satisfaction (this preserves the existing "allying in does not fulfil the design" pin AND covers the inversion), and **the share floor gates ACTIVATION, never SATISFACTION** — the old "hegemon fell → satisfied" arm was false while the cut-down power still held the targets.
- **P2 — the war room advised a cession the player could not make.** `agenda_satisfiable_by_player` gated on BLOC control while `generate_suggested_terms` filters to the player's DIRECT holdings; with every target in a VASSAL's hands the counsel still fired, cost an action, opened talks, offered an unrelated province and scored the design term at ENTRENCH — strictly worse than ignoring it. Now direct-gated, mirroring the narrowing §16 already applied to NA-5's ultimatum trigger. Textbook cross-slice drift: a lesson learned in one slice and never carried back. **P3** — `generate_ultimatum_terms` was the one AI proposal builder not stamping `proposer_nation`, so the fallback prose read *"Unknown demands 300 gold per turn"*.
- **What the review did NOT find, worth recording:** GR8 is clean (measured on the real 126-province world — `advance_turn` 9–24 ms/turn, agenda work ≈1 ms of it, cache 837 hits / 179 misses over 10 turns, no thrash); serialization is clean across all six phase fields incl. cross-save contamination on both the backend and the Godot static stores; no duplicated-with-divergent-semantics defect and no constant defined twice; and all six §0 G2 "full coupling" pillars have real production call sites reachable in the shipped campaign.
- **Known limitation recorded rather than papered over:** a court INSIDE the dominant bloc reads its deny design as not-satisfied even when it holds the targets itself. This is **pre-existing and unchanged** by the fix (the old code counted those targets as "in hegemon bloc hands" for the same reason). Correcting it means deciding what deny satisfaction means when the denier and the hegemon are allies — an authoring decision, not a defect. **Homed to NA-6c**, which touches the same predicates for the carve tags. Suite **14,017/3**.

### 🏛 NATION AGENDAS BUILD — NA-5 ULTIMATUMS ✅ LANDED July 18, 2026 — ~~▶ NEXT: NA-6~~ ✅ NA-6a + NA-6b LANDED July 18 (entry above)

**User direction: "na-5 code commit push."** The §8 gate answers built as specced — no further gate was needed by design. **Landing record = `NATION_AGENDAS_SPEC.md` §16 (authoritative).** Suite **13,890/3** (+35 `test_nation_agendas_ultimatums.py`, 2 campaign-log count pins consciously flipped 118→120), ruff clean; XR-1 honored for the `.gd` touch (parse harness EXIT=0 + report regenerated; headless main-scene boot **0 `SCRIPT ERROR`**).

- **The rung:** `ai_diplomacy._generate_agenda_ultimatum` between P7 and P8 — at peace · relation < 0 · active ACQUIRE design with a player-DIRECT-held unmet target · outside the player's bloc · fog-free strength ≥ 1.25× (ledger marshal-sum basis) · 15-turn per-nation cooldown **set at ISSUE** (an ignored demand doesn't return next turn) · max ONE live world-wide. Two conscious tightenings recorded in §16: player-DIRECT-held targets only (the cession arms can't sign away vassal soil — no dishonest bargains) and the player's capital never demandable. Exempt from the F8 bandwagon throttle (a deferral would silently eat the court's one ultimatum).
- **Building Blocks:** the player's own `generate_ultimatum_terms` gained `issuer`/`demand_regions` params (both omitted = byte-compatible player path) — the design target IS the territory demand; `_force_send` bypasses the player-side score filter. Yield applies demands player→issuer through the SAME `_apply_ultimatum_demands` arms (new `beneficiary` param, GR5; player-threat adds fire only for a player beneficiary).
- **Surface:** new dtype `incoming_ultimatum` (CURRENT_TURN_OFFER_TYPES — lapse ≠ rejection, pinned; mailbox priority 2, "Ultimatum" row), the incoming-proposal popup's crimson **ULTIMATUM** register (Demands:, Counter hidden, **Yield/Defy**), "Ultimatum from X" notification, dtype routed in `main.gd` ×2 + `main.py` /pending_envoy + /mailbox/activate + the popup safety valve. Typed yield/defy/accept/reject resolve through the existing dialogue-response path — **no new typed commands, corpus untouched** (pinned).
- **Consequences:** Yield transfers the demands (region + tribute clause player→issuer) and the issuer's design derives as satisfied for free; Defy plants the DD8-idiom marker (`ultimatum_rejection_pressure` serialized: 8 turns / +2 / cap 4, threat panel "Defied an ultimatum" — the FIFTH standing contributor; drive-by: the DD8 source got its missing label too) and floors the cooldowns (`apply_ultimatum_rejection_cooldowns` — the overwrite trap inverted); **no unilateral AI declare-war** (the coalition remains the war-maker, pinned) and issuing never lowers the player's threat (pinned). Campaign-log `ai_ultimatum_accepted`/`ai_ultimatum_rejected` (types 118→120).
- **July 18 follow-up (docs-only): the spec is v1.3 — §11.10 "NA-6 build plan of record" added** so the NA-6 session executes §11 with zero design judgment calls: sub-slices **NA-6a formation core → NA-6b Proclamation/identity → user-review PAUSE → NA-6c carve creation → NA-6d Poland chain + Formables button**, with 9 pinned decisions (formation record carries `{id, sponsor}` — a conscious §11.1 amendment §11.9 needs; the poll's two call sites; the two-chokepoint identity-override mechanism incl. the Godot flag-cache flush trap; the Proclamation as a PopupQueue popup NOT a dialogue, **layer 117** measured free; the roster-addition **shape-parity test** vs boot KingdomOfItaly; the carve eligibility predicate + the deliberate no-capital-guard asymmetry; the §11.9 sponsor definition + France-scoped-scalar caveat; GET `/formables`). Plus the §7 numbering note: **there is no NA-4** — the §15 live-verify step occupies that sequence slot; identifiers frozen.

### 🏛 NATION AGENDAS — NA-0..3 LIVE VERIFICATION ✅ PASSED July 17, 2026 — ~~▶ NEXT: NA-5 ultimatums (§8)~~ ✅ NA-5 LANDED July 18 (entry above) → NA-6 Formable Dreams

**User direction: "do the playtest."** Mock-mode live drive of the default 1805 campaign over HTTP (Nation Agendas is code-owned, so mock is the deterministic correctness mode). France boots at war with the Third Coalition — every war-gated seam exercisable turn 1. **Verdict: PASS, 0 defects.** Full record = `NATION_AGENDAS_SPEC.md` §15. No production code changed (verification-only); docs-only commit.

- **NA-0** dynamic activation confirmed *organically* — the survival override fired unprompted on turn 3 ("The court of Bavaria takes up a new design: its own survival"; Bavaria at war with Austria crossed the threshold).
- **NA-1** all four legibility surfaces live: `/diplomatic_ledger` Design rows persisted 8 turns byte-stable; the war room named all three coalition designs; the rung-1.5 "offer it at the table and their reason to fight goes with it" counsel; the shift beat printed exactly once on the genuine flip (no turn-1 spam). Denmark voiced an agenda-consistent `non_aggression` proposal.
- **NA-2** acceptance-mod battery via `/debug/acceptance_preview`: +12 acquire-advance (cede Milan→Austria), −8 entrench (bare peace), **0 AUD-b-safe** (bare armistice), deny both directions (Britain −8 / +12), contain gated on hegemon share (Russia −8, flips to 0 below the 0.33 floor).
- **NA-3 + covets** pinned green, not live-triggered this session (an emergent hard-stop dialogue queue — petition → proposal → settlement offer → capture choice — made a clean campaign impractical): `test_nation_agendas.py` + M1–M7 harness = **188/188 on master**; wiring confirmed live where reachable.
- Stability: 0 server errors across 8 turns. Non-NA notes (no defect): console-only em-dash mojibake; a candidate frontend UX observation — hard-stop dialogues can stack and freeze turn-advance, worth feeling in real Godot pacing before judging fun.

### 🏛 NATION AGENDAS BUILD — NA-3 WAR COUPLING ✅ LANDED July 17, 2026 (M1–M7 harness-checked first) — live verify ✅ PASSED July 17 (block above) → ▶ NEXT: NA-5 → NA-6

**User direction: "do na 3, commit and push, assure no logical gaps (from this whole spec) arose from this mechanic or regression errors."** All five §5.5–§5.9 seams + BOTH §7 riders landed backend-only; **landing record = `NATION_AGENDAS_SPEC.md` §14 (authoritative)**. The §7 completion bar was honored in order: the M1–M7 sweep harness ran green BEFORE the first edit and after the last (11/11 byte-identical — the harness recon confirmed M1–M6 boot no world and M7's jealousy loop touches no agenda path). Seam-mapping = an 8-reader recon workflow; **the mandated whole-spec gap check = a 46-agent 6-lens find → 2-refuter adversarial-verify workflow — 20 raw findings, 10 confirmed (several by live mutation experiment), ALL FIXED pre-commit, 10 refuted.** Headline P1: the grudge's first cut read `side_by_nation` on ended instances, which the REAL war-end path strips empty — structurally dead in production, invisible to the synthetic fixtures; re-derived from `participant_meta` and pinned through the real resolver. Suite **13,851/3**, ruff clean, no `.gd` touched.

- **§5.5 resolve deltas WIRED:** `get_agenda_resolve_delta(nation, player, world)` joins `effective_p1_threshold` beside the WPS-D ticking term — advancing Austria at −45 fights on (−48) while the deck-stripped control sues; **satisfied Austria at −35 sues THROUGH the boot coalition** (the +10 delta opens the P1 gate the same turn the NA-2 Pressburg arm unlocks loyalty — the "completed by NA-3" note closed). Survival arm deck-independent by design; every legacy P1 pin green untouched. (Review fix: the negative control asserted a key that never exists — now a real discriminator on `proposal_type`.)
- **§5.6 target bias:** `_agenda_covet_set`/`_agenda_biased_distance`/`_pick_personality_target` on `EnemyAI`, reading **`get_agenda_military_targets` — ACQUIRE-ONLY** (review fix honoring §3.1's deny row: "never self-conquest" — Britain's corps get no pull toward conquering Flanders; diplomacy keeps the full covets): strategic-region list orders design targets first, P4 aggressive equal-ratio ties break toward a covet + the cautious nearest-pick credits 2 hops, P7 target CHOICE credits 2 hops while the hop loop's must-reduce gate reads real distance; covets memoized per (nation, turn) (GR8). Gates/ratios untouched; deckless worlds byte-identical (pinned); **both call-sites spy-pinned** (review fix — a revert to the inline picks now fails the flow tests). **`ENEMY_AI_REFERENCE.md` patched in-slice:** P2.5/P3.8/P3.9 rows added, P4.78→P7.4 relabel + footer, admin-chain rows 1.5/1.6/1.75/6.5 + the stale +75g→+25g fix, and a NEW "Diplomatic proposal triggers (separate P-namespace)" section documenting the P1 threshold composition + Pressburg + hawk cadence.
- **§5.7 paymaster generalized (GR5):** `get_paymaster_nation` + tiers — any coalition member with a live authored `paymaster` POSTURE pays (posture read independently of deck priority, documented: Pitt's gold flowed while `low_countries` stayed Britain's announced design); 200 / 300 (>4k) / 400 (>8k) cap 400; survival-override courts keep their purse shut; non-Britain paymaster pinned; **the attribution resolver generalized too** (review fix — `resolve_british_subsidy_war_id` gains `supporter`, killing the last Britain literal that silently dropped a non-Britain paymaster's `war_support_delivered` accrual; attribution pinned). **Deckless legacy worlds keep the Britain literal byte-identically** (500-gold gate, flat 200 — every legacy subsidy pin green). **One conscious re-bless:** Britain boots at EXACTLY its 2,000 floor (exclusive per the NA-0 pin) → the boot turn pays nothing, the first gold above the floor opens the purse (`test_british_subsidy_flows_to_austria` re-pinned both arms).
- **§5.8 the post-peace grudge:** `agenda_grudge` joins step 2 as the fourth standing contributor (+1/turn per at-peace court whose acquire/deny design stays denied by France's bloc within 10 turns of ITS OWN war-end; cap 2; threat panel names it "Denied national designs"). **Derived per-nation from `participant_meta`** (the review's headline P1 — see above): a separate-peace court (the Pressburg exiter) grudges from its own `exited_turn` while the coalition war burns on; everyone else from the instance end. Fully derived, zero new fields; retention window covers every per-nation horizon by construction. Pinned through the REAL `resolve_pair_to_resolved` path on the boot Third-Coalition instance both ways; dissolves the turn the targets come home (Sardinia pin — the R156 payoff); armistice-shaped (unended) wars never grudge.
- **§5.9 the Ansbach trap:** `process_agenda_violations` — one marshal-pass beside the NA-1 shift poll: a belligerent's ≥1,000-man column in an ACTIVE guard region fires one-time −25 (per pair per 10 turns, event-log latch, zero new fields) + HIGH dispatch beat + `agenda_violation` campaign-log event (type count 117→118). GR5 pinned both directions (France in Jutland AND Britain in Jutland); ally/at-war/peaceful/courier exemptions pinned; **own-soil exemption** (review fix: a garrison on a legally-held treaty-ceded province is no transit — Denmark's reactivated guard can't bleed a French Jutland forever); **rolling-cap fail-safe** (review fix: an event log that rolled inside the window suppresses rather than re-fires); **the `advance_turn` wiring itself pinned** (review fix); the latent-guard negative pinned (Berlin under Prussia's deck-latent `armed_neutrality` prices nothing — deck priority stays the chokepoint).
- **Rider (a) — the settlement per-court term:** `agenda_settlement_mod` (settlement term vocabulary, shared ±12/−8 constants, first-match-wins ADVANCE → demand-strip → the-peace-that-returns-nothing) is the scorer's **11th component** with `ACCEPTANCE_COMPONENT_DISPLAY` "National design" — the per-court breakdown renders it with zero extra wiring; a clause ceding Savoy prices Austria's satisfaction at +12 (the §7 pin). Deckless fixtures 0 by construction; the 10-key set pins consciously became 11 (3 files).
- **Rider (b) — the preview positive row:** peace-class R17d previews now score `generate_suggested_terms` output (bare mock retired for peace-class only) through ONE memo shared with the BPH-B snapshot loop — **pinned with a counting wrapper** (review fix: clause identity is call-invariant, so only a call-count pin catches a memo revert). Live pin: the armistice-first route puts **"+12 Advances their design"** in the preview positives — the row NA-2 documented as unreachable.
- **Tests:** `test_nation_agendas.py` 134 → **177** (+43). Conscious pin flips all dated in-test: campaign-log 117→118 ×2, settlement component set 10→11 ×3, the boot-subsidy floor re-bless. Docs: spec §14, SYSTEMS_REFERENCE **§28 Nation Agendas** (new), ENEMY_AI_REFERENCE, ROADMAP row NA, CLAUDE.md queue. **▶ NEXT per §7: live verify NA-0..3 in a playtest → NA-5 ultimatums (§8) → NA-6 Formable Dreams (§11).**

### 🏛 NATION AGENDAS BUILD — NA-2 DIPLOMACY TEETH ✅ LANDED July 17, 2026 (after the in-game §7-cadence review PASSED) — ~~▶ NEXT: NA-3 war coupling~~ ✅ NA-3 LANDED same day (entry above)

**User direction: "look in game then do na-2 then commit and push."** The paused-for-review NA-0/NA-1 surfaces were verified LIVE first (Godot at ≥2560 against the running backend): the Nations-tab gold "Design:" lines, the war room naming every coalition belligerent's design, and the rung-1.5 **"Satisfy their design (Britain)"** executable counsel all render as contracted; ONE copy wart found — "Their court will not rest while **Hanover holds Hanover**" — and fixed in-slice (eponymous holder==region arm, pinned + re-verified live over HTTP). Then NA-2 was built per spec §5.2–§5.4. **Landing record = `NATION_AGENDAS_SPEC.md` §13 (authoritative).** Suite **13,806/3**, ruff clean, no `.gd` touched.

- **§5.2 the acceptance term:** `agendas.agenda_acceptance_mod` — +12 when the offer's territorial content advances the target's active design (acquire: target ceded to them; deny: a listed region ceded out of the hegemon's bloc), −8 when it entrenches the denial (a demand stripping a HELD design region — priced on ANY type, incl. armistice, pinned deliberate — or a formal peace from WAR **or ARMISTICE** state ending a design-advancing conflict empty-handed); bare armistice NEVER entrenches (AUD-b protected). Wired on the respected-estate recipe: outside the composite floor, `components["agenda_mod"]`, feedback trackable + `FEEDBACK_STRINGS`, sign-aware R17d label ("Advances their design"/"Entrenches their denial"), AND direction-aware confirm-popup labels in `build_war_context_snapshot` (killed the raw "Agenda Mod" leak). Score-coupling pinned at the SCORE level. Legacy/deckless worlds 0 by construction — full suite green on the first run.
- **Covets unification:** `get_agenda_covets` is the authoritative first source in `generate_suggested_terms` stage 2a + `_has_bargain_strategic_interest` (profile fallback intact); the 2 dead `NATION_DESIRES` territory rows DELETED (8.EVAL AUD-d) + negative pin; **stage-4 Talleyrand commentary made region-accurate for agenda-sourced tags** (was praising ceding "Bavaria" while the terms ceded Savoy, and advising conquer-Saxony when the live covet was Hanover — the review's headline P2, both directions fixed + pinned; profile-sourced tags keep the authored voice).
- **§5.3 R155 cadence:** hawk check-time type-cooldown reduction (−2 turns, rejection AND lapse paths, dove/loyalist untouched, boundary pinned); `_hegemony_ask_candidates` leads with the design ask (Prussia's armed neutrality asks non-aggression FIRST); design-advancing asks voice `agenda_pursuit` (conscious flip of the NA-1 Denmark control).
- **§5.4 Pressburg + courting:** P1 coalition-loyalty gains `pressburg_ready` (survival OR deck[0] satisfied, `war_score < −30`) — pin pair: satisfied Austria at −49 sues a separate `armistice_losing` where denied boot Austria stays loyal; **deckless survival is DELIBERATE** (the Knife at the Throat is universal — pinned); courting stable-sort bias via `vassal_holds_agenda_target` on the unified covets (Austria courts the Kingdom of Italy that holds Milan; eligibility/cost/caps untouched, GR5).
- **Adversarial review:** 6-lens find → 2-refuter verify workflow (28 agents; 13 verifiers lost to a session usage limit — their raw findings hand-verified in the main loop); 11 raw → 8 acted on, 1 accepted+pinned, **2 homed as owned NA-3 riders (spec §7): (a) the settlement scorer's per-court agenda term** (the §5.4 "buy-them-out" lever is bilateral-only today) **and (b) preview positive-row reachability** (the R17d mock is bare — +12 legible today as the score delta + snapshot copy).
- **Tests:** `test_nation_agendas.py` 90 → **134**. **▶ NEXT: NA-3 (war coupling + the 2 riders; M1–M7 harness check FIRST) → live verify → NA-5 → NA-6.**

### 🏛 NATION AGENDAS BUILD — NA-0 + NA-1 ✅ LANDED July 17, 2026 — review PASSED July 17 (see the NA-2 entry above)

**User direction: "code nation intent; assure Warsaw becoming Poland has political implications as well; make Rome formable as well; assure there is a button for France — if those aren't in phase 1 of coding just document, follow the phasing laid out by plan, commit and push."** Phase 1 per the §7 cadence = NA-0 substrate + NA-1 legibility, then PAUSE — both LANDED this session (**landing record = `NATION_AGENDAS_SPEC.md` §12**, authoritative); the three formable asks are ALL NA-6 scope and were **DOCUMENTED into the spec as the v1.2 amendment** (not built, per the user's phasing instruction). Seam-mapping = an 8-reader workflow; pre-ship = a 6-lens find→adversarial-verify workflow. Suite green, ruff clean, boot smoke 0 `SCRIPT ERROR`, parse harness EXIT=0, live `/diplomatic_ledger` curl verified.

- **NA-0 substrate:** `backend/game_logic/agendas.py` — the five §3.1 predicate types + `AgendaView` + per-turn-cached `get_active_agenda(nation, world)` (`_agenda_cache` flushed from `invalidate_active_nations_cache`) + the survival override ("The Knife at the Throat", territorial for every nation incl. player-France) + §6 blessed constants + the pure NA-2/NA-3 feeders (`get_agenda_resolve_delta`, `agenda_concerns_player_bloc`, `agenda_satisfiable_by_player`) — deliberately unconsumed (NA-0 "no consumer changes" bar). The §4 decks authored into `europe_1805.json` **incl. the dormant KingdomOfItaly/Holland satellite decks**; **boot pins measured live:** Austria=`redeem_italy`, Prussia=`hanoverian_prize`, Britain=`low_countries`, Russia=`arbiter_of_europe`, France hegemon 0.396 share, satellites dormant → wake on independence. Validator `agendas` block (type-enum/duplicate-id/region-cross-check hard-fails, unknown-nation WARN); `MODDING_FORMAT.md` + `SAVE_FORMAT_REFERENCE.md` rows. **Conscious deviation from §3.4's "ONE field": TWO serialized keys** — `world.agendas` (the deck store; decks must survive save/load, the marshal_pool precedent) + `world.nation_agenda_seen` (the shift-beat dedup state).
- **NA-1 legibility (§5.1 in full):** Nations-tab `agenda: {id, title, stance_line}` beside `bloc_stamp` (single source `build_agenda_payload`, null-omit, DPF-1 un-fogged) + the `diplomatic_ledger.gd` gold "Design:" line; **war room names EVERY belligerent's design** (coalition rows via `opponents` — beyond the spec's line, the R156 payoff: "Austria's design: Redeem Italy — their court will not rest while Kingdom of Italy holds Milan") + the **rung-1.5 "Satisfy their design" recommendation** (below losing-war; leader-with-terms-route → `request_terms`, any satisfiable member → `open_proposal` — satisfying a NON-leader member is the Pressburg crack); `agenda_pursuit` motive reason (all 5 registers pinned as a hard-KeyError contract + Metternich/Hardenberg/Castlereagh named overrides + `DECISION_REASON_DISPLAY` "national design") with the `determine_ai_offer_decision_reason` arm below `war_overload` / above the generic fallbacks; the **dispatch shift beat** — `process_agenda_shifts` polled once per turn late in `_advance_turn_internal` (first observation SILENT — boot would spam 9 lines; deactivation silent; genuine shifts queue ONE `fog_rule="always"` line + `agenda_shift` campaign-log event; seen-map dedup survives save/load). Campaign-log count pins consciously flipped 116→117; `test_w6_assessment_verb` wars-shape + invest-rung pins flipped (the boot coalition war legitimately draws the satisfy-their-design counsel first).
- **The v1.2 spec amendment (docs-only, the user's three asks — all NA-6):** (1) **Warsaw→POLAND** — `commonwealth_restored` gains `forms` → Poland (the C→T chain) **with political implications = NEW §11.9 "The Partitions Avenged"**: authored `aggrieved: [Prussia, Russia]`, one-time −30 relation blow to the formed nation AND its sponsor at the Proclamation, + the derived standing **"Polish Question"** threat contributor (+1/turn, §5.8 sibling, shared cap, zero new fields, GR5 both directions); post-formation deck `guard_the_vistula`. (2) **Roman Republic formable** — Class C carve [Rome] from the defeated Papal States (1798 precedent), with the **one-province elimination-and-creation pin** and the **risorgimento-block interplay** (a standing Roman Republic keeps Italy unformed — an anti-Italy lever both sides can play); aggrieved [Austria, Spain]. (3) **The Formables button for France = §11.6-8** — an assured F1-wizard top-level "Formable Nations" browser, every template + watcher with U6 honest-availability gate terms + live progress, no hidden/dead rows (the discoverability half of reactive-but-discoverable). §11.7 completion + §7 NA-6 row extended to match.
- **Tests:** `tests/test_nation_agendas.py` (90 — boot/dormancy/priority/predicates/survival-both-arms/elimination/cache-incl-production-seam/round-trip/validator-incl-floor-bounds + all NA-1 surfaces); 3 existing pins consciously flipped. **The 32-agent 6-lens pre-ship review confirmed 25 findings — ALL FIXED** (spec §12 records them): headline P1s = the `_agenda_cache` flush relocated to `invalidate_bloc_members_cache` (declared wars now update agenda surfaces same-turn — `set_diplomatic_state` never reached the old seam) and the F8 bandwagon throttle extended to count `agenda_pursuit` (it outranks `hegemony_pressure` in the reason ladder and would have bypassed the 2/turn cap); the deny-arm semantics re-anchored on the hegemon's bloc, satisfaction split from dormancy, resolve feeders vassal-gated, deck deep-copy, the None-floor `.get()` trap closed validator+runtime, and the survival/shift-beat/stance copy polished. **▶ NEXT: user reviews NA-0+NA-1 in-game, then NA-2 (diplomacy teeth) → NA-3 (war coupling, M1–M7 harness check) → live verify → NA-5 → NA-6.**

### 🇮🇹 FORMABLE DREAMS — Nation Agendas spec v1.1 amendment ✅ RECORDED July 17, 2026 (same day as the gate; docs-only, committed + pushed)

**User direction: "add more formables that have rewards for forming and their own goals when formed; and a possibility for a free Ireland — defer this to the naval phase; just spec and STATUS/ROADMAP work."** No code was touched; every claim was grounded against the live registry first (Ireland = **Ulster + Munster**, both British at boot; Polish partition provinces = Posen/Prussia + Russia's western belt — **the map's Galicia is SPANISH Galicia**, so Warsaw's post-formation dream targets Lithuania/Volhynia, the 1812 "Second Polish War" shape; Holland holds Amsterdam/Brabant/Friesland/Gelderland; no Irish or Polish nation tag exists → those are new-tag CREATION, not transformation). Changes of record:

- **`NATION_AGENDAS_SPEC.md` → v1.1 (authoritative):** new **§11 "NA-6 — Formable Dreams"** owned follow-on slice (after NA-5): the `forms` deck-entry key; formation = identity transform (internal tag NEVER changes — display name + flag via the R7 chokepoints; ONE new serialized field `world.nation_formations`) + one-time rewards (`FORMATION_GOLD` +2,000 / `FORMATION_STABILITY_BONUS` +2 all regions, in-band tunable) + **post-formation goals for free via deck order** (entries authored after the forming entry activate natively — zero new goal machinery); deliberately NO new popup surface. **Class T transforms:** KingdomOfItaly→**Italy**, Holland→**United Netherlands**. **Class C creation pathfinder:** **Duchy of Warsaw** carved from Posen by settlement clause (VS-5 `transfer_vassal` precedent; dynamic roster + `NATION_DESIRE_PROFILES`/`TALLEYRAND_COMMENTARY` rows per the Don't-Do rule) — the machinery Ireland reuses. Boot-zero pinned; completion §11.7 + `tests/test_nation_agendas_formables.py`.
- **Same-day follow-up (user-directed: "assure the UX is good for creating these; vassals can be created in wars under a conquering country, i.e. Normandy, Warsaw"):** **§11.4 GENERALIZED** — Class C carve-out creation is symmetric for ANY conquering side in a war (carve the *defeated* party's soil only, never an ally's, never your own): v1 templates Warsaw ([Posen], France's carve from Prussia) + **Duchy of Normandy** ([Normandy], the coalition-side mirror carved from FRENCH home soil — proves GR5 against the player's homeland; deck-less pure client) + Ireland (DEF-5). **NEW §11.6 UX contract** (binding on the NA-6 build): wizard-first `create_client` clause with the U6 honest-availability chip idiom ("Erect the Duchy of Warsaw — requires Posen"), full-bargain preview (provinces/loyalty-seed-30/tribute + the ES-7 estate-cession warnings), legible incoming AI carve offers through the R7 display chokepoints (the Normandy mirror reaches the player as a normal incoming settlement, Accept/Reject), immediate flag/VASSALS-ledger/dispatch on ratification, and a **"forms: Italy" live progress marker** ("3 of 5 provinces held") on Class T forming entries. Completion (§11.7) gained the matching pins.
- **Third same-day follow-up (user: "what would forming a new country look like in UX?"):** NEW **§11.8 formation-moment walkthrough** — the full stage 0–4 arc on named surfaces, worked example = the freed Kingdom of Italy taking **Rome** and proclaiming **Italy**: stage 0 the watchable dream (progress marker + Talleyrand stakes line), stage 1 the dispatch-leading tipping event ("The tricolore rises over Rome"), **stage 2 "The Proclamation"** — ONE ceremonial popup card (new flag over the struck-through old, engraved proclamation line from the `forms` blurb, rewards + new agenda stated plainly, single [Acknowledge], perspective-aware witness/author subtitle) — **a conscious amendment retiring §11.1-3's "no new popup" caution**, with the full standing dialogue-wiring checklist PINNED in §11.7 (dtype whitelist, dialog_manager registration, PopupQueue slot, XR-1 boot-smoke); stage 3 the same-turn world change (map/ledger/diplomacy re-title via R7, tag unchanged so relations/wars/grudges carry over); stage 4 no modal debt. Creation (Warsaw/Normandy/Ireland) shares stages 2–4 identically. Never-do pins: no double-fire, no boot-fire, no dead name anywhere, no queue-jumping, never blocks the turn.
- **§4 decks:** two **dormant satellite decks authored at NA-0** — KingdomOfItaly `risorgimento` (acquire Milan/Piedmont/Savoy/Naples/Rome) + Holland `the_seventeen_provinces` (acquire Flanders), latent while vassalized (§3.2 rule), WAKING on independence — a freed vassal marches with a national dream even before NA-6's formation layer exists. Deliberate interplay: an independent Netherlands holding Flanders **satisfies Britain's `low_countries` deny agenda** — freeing Holland becomes a diplomatic lever against London. NA-0's completion definition gained the dormancy pins.
- **Free Ireland → DEF-5 rider** (`MAP_IMPLEMENTATION_PLAN.md` DEF-5 row updated): naval expedition into Ulster/Munster at war with Britain creates the `Ireland` client tag (deck `erin_free`); unreachable pre-naval — the whole deferral reason; completion + `test_naval_free_ireland.py` named in the row. Grounding: Bantry Bay 1796, the 1798 expedition, Emmet 1803.
- **§9 homes:** player-France two-path goals seeded to the **Pre-Ship Victory & Objectives Pass** ON the agenda substrate (two CHAINED paths ride deck-priority for free; the new machinery is **branching** — a player choice between mutually-exclusive paths — plus player rewards; the anti-Britain path is unauthorable pre-naval, mirroring the Britain naval-agenda cut); **"Unite Germany" formable REJECTED** (post-period — the Confederation of the Rhine is clientage, already modeled by vassalage).
- **ROADMAP row NA + Phase 8.5 "National Goals" row + CLAUDE.md queue line updated** to the NA-0..3 → NA-5 → NA-6 shape.

### 🏛 NATION AGENDAS DESIGN GATE ✅ HELD July 17, 2026 — the Phase 8.5 centerpiece is SPECCED; BUILD NEXT

**User direction: "decide how we will do nation intent — consider history, gameplay value, if it's dynamic, etc.; stop with any questions but always have a recommended path, then push and commit spec."** The gate was held this session: two substrate-mapping agents verified every consumption seam against master (enemy-AI rung tree + targeting, acceptance-formula components, motive-line register bank, war-objective machinery, validator precedents, cached derived-state idiom), three questions were put to the user with recommendations, and **all three were answered at the recommended defaults**. **Gate record + build contract = `docs/NATION_AGENDAS_SPEC.md` (v1.0, authoritative — §0 gate record):**

- **G1 Architecture = authored decks + dynamic activation:** 1–3 hand-authored historical agendas per nation (scenario `agendas` key, validator-checked, region names verified against the live registry — Milan/Piedmont/Savoy, no "Lombardy"); the ACTIVE agenda is derived per-turn from live state (war score, territory, bloc share, treasury) via the `get_authority_proxy` + cached-helper idioms; ONE new serialized field (`nation_agenda_seen`, shift-beat dedup). Five code-owned agenda types (`acquire_regions` / `deny_regions` / `contain_hegemon` / `paymaster` / `guard_neutrality`) + the built-in survival override ("The Knife at the Throat"). Decks: Austria Redeem Italy + Primacy in Germany, Prussia The Hanoverian Prize + Armed Neutrality (the Ansbach violation trap), Britain The Low Countries + Paymaster, Russia Arbiter of Europe, Sweden/Ottoman/Sardinia/Denmark one each; France/vassals/minors none (survival only — player goals stay with the Victory & Objectives Pass).
- **G2 Teeth = full coupling in pass 1:** acceptance `agenda_mod` +12/−8 outside the composite floor (respected-estate precedent, R17d preview-visible), war resolve on `effective_p1_threshold` (advancing −8 fights longer / satisfied +10 sues to lock gains / irrelevant 0 — AUD-b protected), enemy target bias in the strategic-region scorer + P4/P7 picks (bias not a new rung — survival tree inviolate), paymaster subsidy generalized off the Britain literal + treasury tiers 200/300/400, the Pressburg separate-peace arm (satisfied coalition members sue at −30), the DERIVED post-peace grudge (+1 threat/turn cap +2, zero new fields — 1809 in machinery), and the Ansbach neutrality-violation trap (−25, GR5 both directions). This consumes the whole promoted core: R123, R124, A3, R155-residual, R156.
- **G3 R162 ultimatums = owned follow-on slice NA-5** with its gate questions ANSWERED in spec §8 (trigger rung between P7/P8, terms from agenda targets via the player's own `generate_ultimatum_terms`, rejection → bounded expiring coalition-pressure marker NOT a free war, existing mailbox transport + dtype whitelist rule) — built only after NA-0..3 are verified live. No further gate.
- **Build order (spec §7): NA-0 substrate → NA-1 legibility, THEN PAUSE for user review** (standing slice cadence) **→ NA-2 diplomacy teeth → NA-3 war coupling → live verification → NA-5.** NA-3 must check the M1–M7 sweep harness for agenda exposure before landing. Blessed numbers spec §6 (in-band tunable). Deferrals all homed (spec §9): Eastern Question + AI-AI declaration → 8c, naval agendas → DEF-5, trade pressure → EC-8, dead `NATION_DESIRES` territory rows deleted at NA-2.
- **After the agendas build: Battle Diorama (Tier A)** per the queued row BD (user-sequenced July 17).

### 🔬 ECON WAR-COUPLING (EC-W) ✅ RESEARCHED + GATED + BUILT July 17, 2026 — the third economy pass LANDED

**User direction: "do it, you have approval to make decisions; consider history, other games, new ideas, balance numbers, all avenues — losing soldiers costing less at large makes sense, because salaries, but there are maybe expenses or balances missing."** The gate was exercised under that delegation; **gate record = `docs/audits/ECON_WAR_COUPLING_RESEARCH_2026_07_17.md` §3 (authoritative)**. Research = an 11-agent grounded workflow (7 code verifiers + history/games/ideas designers + synthesis, ~1.29M tokens), every load-bearing claim re-verified firsthand; two synthesis errors caught (the Britain-60/Prussia-35 "boot WE" is a settlement-SMOKE-preset seed, not the campaign boot; the flat `WE×5` drain is incompatible with Austria's binding +18 boot margin — redesigned as a treasury-fraction). Upkeep stays on fielded strength per the user steer; the build added the MISSING expenses, **all boot-zero by construction** (presence-/WE-/battle-/settlement-gated), zero new serialized fields, GR5-symmetric:

- **EC-W1 "Contributions of War":** an enemy army (≥1,000 men, at-war, not captured) standing on a province suspends its income to the owner — new signed **"Contributions"** Net component (`WorldState.get_disrupted_regions()`, one marshal pass GR8, consumed in `calculate_turn_income`); a disrupted ESTATE feeds nobody (the marshal's satisfaction falls with his lands — `get_estate_income`); ES-2 occupation + infrastructure still bill; the region bleeds −2 stability/turn instead of growing. Suspension only — occupier-side extraction deferred as **EWC-D1**. Boot case pinned: Mack@Swabia disrupts Bavaria (the real Sept-1805 occupation; Bavaria stays solvent), every other boot anchor byte-identical.
- **EC-W2 "The War Effort":** France finally enters the WE system — +8/turn at war with anyone / −5 decay (coalition §10a France arm) + the missing battle arm (France loses as DEFENDER → casualty WE; executor pipeline + auto-charge copy — the exact playtest shape had accrued NOTHING). Every nation pays `int(max(0,treasury) × WE // 2500)`/turn — new signed **"War Effort"** Net component, single-source `calculate_war_effort_cost` (WE 200 → 8%/turn of the chest). Treasury-fraction so it attacks the passive hoard, costs a poor nation ~nothing, and can never push a treasury negative by itself. R49 already guarded partial peace.
- **EC-W3 "The Butcher's Bill":** every resolved non-bombardment battle charges each side `int(casualties × 0.05)` at once (50g/1k, below the 60g/1k war recruit price — hierarchy pinned); one-time flow outside Net (plunder precedent); "[Materiel]" line on the battle message (pipeline step 13b + auto-charge).
- **EC-W4 "Peace with Teeth":** AI settlement indemnities price to the payer's PURSE — `min(500 + 50×age + |score|×40 + 0.15×treasury, 0.40×treasury)`, empty chest → white peace (was `min(2000, 500+50×age)` — the playtest's absurd 600g vs a 61k hoard); player-ask baseline scales too (`max(300, 0.25×court_balance)`, still capacity-capped + `_stays_acceptable`-gated). Exact-amount pins consciously re-blessed.
- **EC-W5 fixes:** AI personality auto-plunder now pays the player's ×1.75 (was ×1.0 — GR5; single source `world_state.PLUNDER_GOLD_MULTIPLIER`) and the treasury report's net includes infrastructure (was silently omitted → the projection lied whenever structures existed).
- **Ledger/UI:** both new components threaded the full EC-U2 recipe — `calculate_turn_income` → `process_income_phase` → `ledger._build_economy` → `NET_GOLD_COMPONENTS` guard → treasury report (disrupted provinces named) → morning-dispatch projection → turn-end message + `turn_end` event → `strategic_ledger.gd` render lines (the session's ONE `.gd` touch).
- **Numbers check (memo §4):** the playtest counterfactual inverts — net declines as the war worsens (+3,369 → ≈+780 at turn 17), the hoard plateaus ~29k instead of 61k, and the settlement demand against it lands ≈6.5k not 600g; a short decisive winning war stays profitable (the Napoleonic shape). Deferrals homed with owners: **DESIGN_REFINEMENT §Econ War-Coupling EWC-D1/D2/D3** + named cuts.
- **Pre-push adversarial review (6-area find→verify, 7 agents / ~1.01M tokens) initially returned NO-SHIP with 10 confirmed findings — ALL resolved before commit** (memo §6.1): the HIGH was an N1 breach (the France WE tick + both new battle arms lacked the Europe gate — the LEGACY fixture world boots at war, so legacy France accrued WE and its pinned infantry regen drifted; three gates added + legacy pin), plus elimination-path WE lingering (R49 mirrored into `_eliminate_nation`), silent materiel billing on garrison/auto-kill messages (shown=applied restored at 3 sites), the auto-advance banner + `main.gd` banner omitting the new components (both fixed + pinned), vassal tribute ignoring disruption (processor + ledger mirror fixed), and the player-ask all-or-nothing regression (floor retry). **Recorded as intended + pinned: France now inherits the pre-existing WE→infantry-regen penalty** (200 WE → the 1,000/turn floor — the manpower half of war-weariness, part of EWC-D2's spirit via an existing dial). 2 rows routed OPEN = `BUG_FIXES.md` §EC-W (EWC-F1 un-ratifiable winning offers — pre-existing saturation; EWC-F2 rente face vs disruption).
- Suite **13,670/3** (+43: `test_econ_war_coupling.py` 40 + re-blessed offer pins), ruff clean; boot smoke = headless load-check on `strategic_ledger.gd` (`parse_ok can_instantiate`) + the committed Godot parse harness re-run exit 0 (report regenerated, covers the `main.gd` touch).

### ~~🔬 NEXT — FABLE RESEARCH ECON (economy realism, THIRD attempt)~~ ✅ DONE July 17, 2026 (see the EC-W entry above)

**This is our THIRD pass at the economy** (pass 1 = the July-9 Economy Revisit / EC build; pass 2 = the July-14 Combat-Overhaul Phase 4 econ slices EC-U1/U2/U3 + the EC-U1 reversal). It still isn't right. **Task: `fable research econ`** — a Fable-led research pass (memo → gate → build, do NOT autonomously build) into WHY France's treasury is decoupled from military fortune, and what fixes it.

**Core defect (found in the July 17 playtest — fresh `new_game`, ~20 turns, mixed passive/active play):** France's treasury snowballs monotonically and net income *rises* even while the army is destroyed, marshals are lost, and the enemy occupies core home soil. Because upkeep bills on *live* fielded strength ("you pay for the soldiers you have," the reversed EC-U1), **a shrinking/losing army lowers costs — so losing the war makes France richer.** A player is never under economic pressure; gold is effectively free.

| Turn | Treasury | Net/turn | Gross income | Upkeep | Army | Marshals | Note |
|-----:|---------:|---------:|-------------:|-------:|-----:|:--------:|------|
| 1  | 800    | +2,107 | 4,687 | 2,630 | 189,000 | 7 | boot; 56.1% upkeep absorption (in EC-2 band) |
| 6  | 14,793 | +2,590 | 4,186 | 1,594 | 155,554 | 7 | Swabia taken from Austria; occupation −52g fires |
| 12 | 33,816 | +3,461 | 4,322 | 896   | 115,593 | 7 | army bleeding, **net still climbing** |
| 14 | 40,747 | +3,487 | 4,181 | 744   | 96,610  | 5 | 2 marshals lost (Bernadotte **captured**) |
| 17 | 51,266 | +3,369 | 3,895 | 576   | 75,534  | 5 | Britain (Moore) occupying **Orleanais** (core France) |
| 20 | **61,099** | **+3,300** | 3,746 | 496 | **64,568** | 5 | army −66% from boot, treasury +7,500% — Britain war-score **+24 vs France** |

**Why it happens (hypotheses for Fable to verify):** (1) upkeep keys off live strength, so attrition = savings; (2) home income is nearly inelastic to invasion — a British army *sitting in Orleanais* barely dented income (no occupied-home income suspension / war-damage applied to the player's own contested province); (3) peace penalties are trivial at scale — winning Britain's settlement demanded a **600g** indemnity against a 61k treasury (~1%); (4) no war-weariness / deficit-pressure term couples treasury to being invaded. Manpower pools also fully regen to max regardless, so there is no reserve pressure either.

**Prior context Fable must reconcile (don't re-break these):** the EC-2 gate blessed 55–70% turn-1 absorption (`ECONOMY_REVISIT_SPEC.md` §0.6.7); the measured anchors 36.9% boot / 84.2% fresh-conquest / 54.5% steady-state were accepted (turn-1 aspirational anchor retired, S7 note); the economy is deliberately a **sandbox** (no hard win/lose — do not "fix" victory code back); EC-U1 upkeep-on-establishment was tried and **reversed** by user direction (fielded strength is the intended base). Austria's +18 boot solvency is the fragile constraint any absorption retune must respect. **Everything above is verified-live signal, not a code read — Fable should re-derive against master before proposing numbers.**

**Everything else in the July-17 review was realistic and working** (accurate Third Coalition boot; layered legible combat modifiers; war-score-aware AI peace offers; glory ladder + crown + captured-marshal recovery; vassal loyalty incl. Switzerland 53; recruitment friction with the 3,000 field-levy cap + morale dilution; zero runtime errors over 20+ turns). The economy↔war decoupling is the one thing that reads as unrealistic.

### 🪖 BATTLE DIORAMA (TIER A) — ✅ EVAL HELD + QUEUE DECISION July 17, 2026: SLOTTED AFTER NATION AGENDAS

**Idea from the July 17, 2026 design conversation:** when a battle resolves, show it as a **framed popup tableau of mini soldiers** — two (or more) crowds scaled to committed strength, casualties toppling as the report reads out, an outcome banner, a casualty tally, and the Berthier line — instead of / alongside the text-only report. **Spec: `docs/BATTLE_DIORAMA_SPEC.md`** (corrected in place by the eval — where they disagree the memo wins). **The Fable review ✅ RAN July 17, 2026** (eval bullet below) **and the queue decision ✅ was made the same day** (final bullet below): **BUILD IT, sequenced AFTER Nation Agendas** — now a queued Tier-A slice (ROADMAP §Current Phase Queue row **BD**), no longer "review only."

- **Why it's on the table:** directly targets the Creative Audit's two weakest pillars — **combat legibility 4.5 / narration 3.5**, verdict *"great stories, untold"* (`docs/audits/CREATIVE_AUDIT_2026_07_10.md`). It's the only surface that can *show* a coordination failure (the Davout–Bernadotte −2 no-show) as a visible hole in the line rather than one buried sentence.
- **Cheaper than it sounds — two of three hard parts already paid for:** the piece-sprite tint/facing pipeline (`assets/ui/pieces/`, `scenes/war_table_piece.gd`), the battle-report data (`battle_report.py` — outcome/casualties/original strength/modifier snapshot), and the multi-marshal coordination/reinforcement breakdown (`combat_executor.py`) all exist. New work = a `battle_diorama.tscn/.gd` scene that lays out N pieces per contingent + a scripted sequence.
- **Effort tiers (the real decision):** **Tier A — static tableau** (recolored/base-stripped figures, casualties faked by topple-tween, no frame-animation; ~1 slice, RECOMMENDED first) → **Tier B — scripted skirmish** (needs fire/fall poses; 2–3 slices, only after A proves the format) → **Tier C — live sim** (NO, GR8 scaling category error). The two rendered mockups proved **Tier A reads as a battle with static art alone**.
- **Multiple armies = the argument FOR building it:** Sovereign battles resolve primary + reinforcing corps, and coalition wars put two nations' corps on one tile. The tableau **scales on contingents (banners), not raw soldiers** — per-corps labeled blocks capped ~8–10 figures, **mixed coat colors for coalitions** (Austrian off-white + Russian gold), tail-summary beyond ~4 corps, and the greyed **failed-to-arrive / routed / withdrew** block as the drama surface. Multi-army is **nearly free in Tier A**, expensive in Tier B — another point for static-first.
- **Jumping-off mockups (in the spec):** Mock 1 = single engagement (Ney vs Mack at Ulm); Mock 2 = coalition multi-army (Austerlitz: Ney/Lannes/Soult **+ a greyed off-line Bernadotte "failed to arrive"** vs Mack-Austria shattered + Kutuzov-Russia withdrawn intact, "coordination bonus ×1.25" surfaced). Visual language: navy `#141b2e` + gold `#b8912f` frame, serif battle-name/outcome/Berthier, faction color on coats only, `⚔` clash glyph, per-corps `⚑` standard.
- **Asset reality (verified July 17):** there is **no CC0 pack of animated Napoleonic line infantry** — CC0 gets you static ([Pixel Art Top Down Soldiers](https://opengameart.org/content/pixel-art-top-down-soldiers)) or modern; period-correct + animated lives only in [LPC](https://liberatedpixelcup.github.io/Universal-LPC-Spritesheet-Character-Generator/) (CC-BY-SA) or the own Pillow pipeline. This is why static-first needs no animated art and carries no ShareAlike obligation.
- **Open questions for Fable/the gate:** replace vs augment vs toggle the text report; does static actually lift the pillar in live play or does it need fall/fire poses; fixed cap vs proportional figure count; accept LPC ShareAlike or stay CC0/own-pipeline; and the GR9 boundary (one bounded Tier-A slice with a named landing, or not started).
- **✅ CREATIVE EVALUATION HELD July 17, 2026 → `docs/audits/BATTLE_DIORAMA_EVAL_2026_07_17.md`** (18-agent grounded + adversarially-verified pass; spec §13 = pointer, §6/§7/§12 corrected inline). **Verdict: BUILD IT, fun 7/10**, but as a *significance-gated, honestly-costed* slice = Godot tableau **+ a modest backend `contingents[]` slice** (NOT the "near-zero" freebie §7 advertised — the identifier `contingents` exists nowhere, per-corps committed strength doesn't exist, `casualty_distribution` is written-but-never-read). Fun is **bimodal** (peak on decisive/coalition, net-negative on routine skirmishes) → **significance-gate = a DoD item, not polish**. Three spec claims corrected by the code review: §12.3 causality (grudge→no-show, not reverse), §6 "coats-only" color (art is carved wood; color rides the standard), §7 backend cost. **Cut for the real slice:** Kutuzov "withdrew in good order" (unmodeled), proportional counts, per-corps cascade v1, raw-JPG portraits, Battle Gallery, Tier B/C. ~~Weigh at the gate against Nation Agendas~~ (superseded — see the queue-decision bullet below; Wave 6 already lifted legibility→7 / narration→7.5, so this is a delight-multiplier, not a pillar rescue). **▶ Live interactive hero mockup** (Austerlitz coalition frame) published: `https://claude.ai/code/artifact/f49581da-b77c-4d42-b9d0-a9836ba00ed4`.
- **✅ QUEUE DECISION July 17, 2026 (user-directed — "slot this in docs after Nation Agendas"):** the eval verdict is ACCEPTED and the **Battle Diorama (Tier A) is IN the queue, sequenced AFTER the 8.5 Nation Agendas design gate** — it no longer competes for the centerpiece slot. Rationale (Fable recommendation, user-agreed): agendas deepen the every-turn strategic loop — the genuinely thinner remaining gap (enemy motivation) — and will *generate* the coalition battles the diorama exists to render; the diorama is the reward slice after. **Scope of record = eval §6** (ONE bounded slice: the medium backend `contingents[]` builder — per-corps nation/arm/pre-mutation committed strength, dead `casualty_distribution` wired, four statuses only, fog-filtered enemy side, `main.py` whitelist-registered — + the significance-gated Godot tableau with instant-repeat-final-frame; the §5 cuts stand; Tier B/C held until Tier A is measured live). Completion = eval §6 DoD + `tests/test_battle_diorama.py`. **Named landing: ROADMAP §Current Phase Queue row BD + this line** (the eval's missing-landing note is satisfied).

### 🎯 CR-6 MINI-GATE — S5-D1 BARE-ATTACK GATING ✅ BLESSED + LANDED July 16, 2026 (sixth session)

**User direction: "CR-6 mini-gate (USER GATE — ask me the gate questions first, don't build unprompted)."** The gate was held (four questions answered over two rounds), then built the same session. Backend + tests only (**no `.gd`** — reuses the existing clarification popup / muster interrupt / objection popup surfaces); suite **13,627/3**, ruff clean.

**Gate record (authoritative — also in `COMMAND_ROBUSTNESS_SPEC.md` §7):** S5-D1 = a bare `attack` with no marshal named auto-picked a marshal into a real battle, skipping CR-2 clarification, the W6-4 muster gate, and objections — the most ambiguous lethal order had the fewest safeguards. Blessed decisions: **(a)** multi-contact bare `attack` → the "Which marshal shall lead the attack, Sire?" clarification (single-contact keeps the instant pick); **(b)** arm the W6-4 muster gate on the bare-attack paths (silent on favorable odds, Berthier warning on bad odds — the personality "who-musters" surface now shows on lazy commands too); **(c)** route objections for the auto-picked marshal (a cautious/hostile marshal can still object); **(d)** E-CA-4 closed as subsumed by (b) — no always-on odds line (the staff only speaks when the odds are questionable; there is no pause before a clearly-winning attack).

- **Architecture — resolve-and-rewrite at the dispatch seam.** A new `CombatExecutor.resolve_auto_attack` runs in `executor.execute` *after* the AP pre-check and *before* the objection block. For a PLAYER `general_attack`/`auto_assign_attack` it resolves the marshal and either (clarify) returns the marshal-choice question for >1 commandable marshal in enemy contact, (named) **rewrites the command in place to a specific `attack`** so the pick flows through the *entire* named-attack pipeline (objection + muster gate + AP + autonomous/fortified checks — zero lines changed in the 170-line objection block), or (passthrough) leaves the command for the existing `_execute_general_attack`/`_execute_auto_assign_attack` (move-toward / no-enemies / error cases, byte-unchanged). GR5: `not is_ai_command and not is_strategic_execution and not _autonomous_execution` — AI/strategic/autonomous callers never issue these types and are guarded out regardless.
- **Single-sourcing (avoids a new S5-D3 mirror):** extracted `_scan_general_attack_candidates` (shared by `_execute_general_attack` + the resolver) and `_resolve_auto_assign_attacker` (shared by `_execute_auto_assign_attack` + the resolver). The resolver prefers a commandable marshal over an autonomous one when both are in contact. New clarification builder `build_contact_attack_clarification` (each option reissues a fully-formed `"<marshal>, attack <enemy>"`, resolving through the ordinary named pipeline; registered via the existing `main.py:1738` seam so the typed-answer channel + popup both work).
- **No pins flipped:** the gating lives at the dispatch seam, so the direct-call unit tests in `test_auto_assign_attack.py` (24) stay green (they call the executor methods directly, bypassing the resolver) — the new behavior is pinned by `tests/test_cr6_bare_attack_gating.py` (13: resolver verdicts + full-pipeline muster/objection/clarification/passthrough/GR5). Full suite green with zero regressions.
- **Pre-ship adversarial find→verify (6 agents):** caught ONE real regression, FIXED before commit — threading `command` (with its raw text) into the rewritten attack armed the ESP-EV-4 **guessed-target guard**, so `attack them all` / `attack <typo-region>` got falsely refused ("names no foe or province"). Fix: the guard stands down for a `_auto_assigned` command (the target was resolved deterministically, not typed by the player) — the guard's own "delegated → let it fly" principle; regression test added. One cosmetic fix folded (the "attacks!" note no longer prepends onto a pre-battle glorious-charge prompt). Findings 3a/3b (a clarification could list a retreating marshal; provenance drops on the objection round-trip) accepted as minor/pre-existing.
- **Next (user-directed):** the **`fable research econ`** pass — economy realism, third attempt (see the top "🔬 NEXT — FABLE RESEARCH ECON" section: France's treasury snowballs while the army is destroyed) — then the 8.5 design gate proper (Nation Agendas).

### 🏁 PHASE 8.5 — BATCH Q "Quick Wins & Honest Counsel" (Chunk 2) + 🗺️ MAP SERIF LABEL FONTS ✅ LANDED July 16, 2026 (fifth session)

**User direction: "better serif font for CITY and COUNTRY map labels (Task 1, do first) + continue Batch Q — VS-5 live ratify, AUD-b, AUD-c, E7, Metternich. run a pre-push adversarial find→verify Workflow, commit and push."** The balance-sensitive AI-diplomacy trio + the two design builds + the VS-5 live exercise — the second, harder Batch Q chunk that Chunk 1 deliberately left for a focused pass. Backend + docs + ONE `.gd` (the map labels); suite **13,614/3**, ruff clean, engine boot 0 SCRIPT ERROR, parse harness EXIT=0.

- **🗺️ Task 1 — map CITY/COUNTRY labels now render in period serifs (was the plain Open Sans fallback):** `map_label_layer.gd` drew ALL labels with `ThemeDB.fallback_font`. Now the nation tier loads **Marcellus SC** (a Roman small-caps serif — the classic antique-atlas country face; nation display names are Title Case so the small-cap two-height effect renders) and the province/city tier loads **Spectral** (a lighter serif drawn for small-size screen legibility), via a guarded `_load_label_font()` that falls back to the ThemeDB face if an asset is missing. Zoom-LOD sizing / outline / occupied-rect avoidance UNCHANGED. Both faces already on disk + OFL-credited. Verified headless: nation=Marcellus SC, province=Spectral, both distinct from the old fallback (Open Sans SemiBold). Pin tests `test_ui_visual_foundation.py` (+2: assets-present + non-fallback-tier assertions). ⚠ open: live in-game visual sign-off at a couple zoom levels (the map booted clean; the self-served screenshot pass was skipped because the user was actively using the machine for another app — deferred, not blocking).
- **AUD-b (balance-critical) — the P2 "stalemate" armistice no longer fires with ZERO combat:** the stalemate counter incremented from war START with no battle requirement, so the whole Third Coalition sued for peace by turn ~5-7 having never fought. The P2 exit now requires the pair to have actually FOUGHT (`world.battle_records[diplo_key]` non-empty = ≥1 war-score battle); a genuinely contactless war still gets an exit, but only after a much longer `P2_NO_CONTACT_ESCAPE_TURNS=15` window. Uninvolved coalition members (declared war, never engaged) correctly hold — the battle-record gate is per-pair. Tests re-anchored to the corrected contract (`test_session4_diplomacy.py` +2 no-contact cases, `test_da1_ai_intelligence.py` `_setup_stalemate` records a battle).
- **AUD-c + AI-P3-P6 carve-out — incoming settlement offers are now war-score-aware:** `_settlement_offer_build_terms` hard-coded the indemnity direction (player ALWAYS pays), so a WINNING player still got dunned for reparations. Now, from the player's perspective vs the opposing leader: winning by ≥ `SETTLEMENT_OFFER_DECISIVE_WAR_SCORE=20` → the losing AI PAYS the player (concession); losing by ≥ the band → player pays reparations (historical framing, unchanged); inside the band → a clean WHITE PEACE (no indemnity). Score threaded via `get_war_score_for(world, player, proposer_nation)`. `test_settlement_incoming_offers.py` +3 direction tests; the presence/amount pins default the staged war to player-losing.
- **E7 — Talleyrand's defiance floor is authority-BANDED (the sabotage arc is no longer near-dead content):** at boot authority 100 the base curve collapses to 0.00 and the flat 2% `SCHEMER_FLOOR` WAS the effective rate — the whole sabotage/discovery/confrontation/redemption arc + two shipped popups fired barely 1-in-50. The floor is now banded (`_defiance_floor_for_authority`): **5% at authority ≥70**, easing to the ordinary 2% below (where the base curve already dominates). Applied in BOTH the variance and deterministic curves; loyalist→0.0 and cooldown→0.0 early returns untouched. Spec-drift fixed in the same slice: `DIPLOMACY_SPEC.md §3a` still documented the PL-23-retired `trust_mod` term — removed, examples re-derived. `test_session6_diplomacy.py` re-anchored (auth 85/100 → 0.05; +1 sub-band test).
- **Metternich (DD8) — "Armed Mediation" BUILT small (the never-built §5c "+5 coalition bonus" re-specced onto the threat substrate):** rejecting a **Schemer**-authored **peace-family** proposal (armistice/peace only — never a subsidy/trade/alliance ask) plants a **once-per-rejection, 5-turn-expiring war-pressure marker** for that nation on the coalition-threat scalar (`record_schemer_peace_rejection` at the reject seam → `_calculate_schemer_peace_rejection_threat` in `process_coalition_turn`, +2/marker capped +4). Anti-stacking (dict keyed by nation; a repeat rejection refreshes, never stacks); AI-only; new serialized `WorldState.schemer_rejection_pressure`. Closes the consequence-free-rejection gap AND the `DIPLOMACY_SPEC.md §5c` doc debt (spec updated to the landed mechanic). `test_batch_q_metternich_dd8.py` (12).
- **VS5-LIVE-RATIFY exercise — ran, found NO production defects:** added the debug-gated `lord` param to cheat `create_vassal` (`meta_executor.py` — a 2nd arg overrides the default France lord, so an ENEMY-held vassal can be staged; 1805 boots zero). Drove the recipe end-to-end via the executor + the real `_apply_settlement_terms` seam: Austria-lord Bavaria staged → winning France-vs-Austria war → `vassal_transfer` ratified → verified lord re-key to France, loyalty reset to 30, tribute/autonomy carried over, `vassal_transferred` event + `diplomatic_vassal_transferred` morning-dispatch line, no exceptions. `test_settlement_vassalage.py` +4 (the live-exercise class).
- **Pre-push adversarial review:** a 6-area find→verify Workflow (7 agents, ~666K tokens, 44 tool-uses) — **ALL SIX areas (fonts / AUD-b / AUD-c / E7 / Metternich / VS-5) returned ZERO findings**; the clean verdict was spot-checked against the agent transcripts (each agent demonstrably read its target files — the AUD-b reviewer alone referenced `battle_records` 61×).
- **Remaining Batch Q → next chunk:** the CR-6 mini-gate (S5-D1 bare-attack gating, a user gate) and then the 8.5 design gate proper (Nation Agendas core). AUD-g/S5-1/2/3/5/S5-D2/AUD-e already landed in Chunk 1. `UI-2d-1` (decision-modal off-screen exit control) remains open in `BUG_FIXES.md` — not taken this session.

### 🏁 PHASE 8.5 — BATCH Q "Quick Wins & Honest Counsel" (Chunk 1) ✅ LANDED July 16, 2026 (fourth session)

**User direction: "code commit and push chunk off as much as you think is fair."** The first, cleanest chunk of the 8.EVAL-routed Batch Q (gate record `docs/audits/EVAL_8_2026_07_16.md` §1/§3) — the low-risk backend bug-fixes + doc reconciliations, landed together; the balance-sensitive AI-diplomacy trio (AUD-b/AUD-c/AUD-g-of-that-family), the E7/Metternich design builds, and the VS-5 live exercise are the **next chunk**. Backend + docs only (no `.gd`); suite **13,590/3**, ruff clean; `tests/test_batch_q_fixes.py` (20).

- **S5-1 — enemy-AI square↔fortify self-cancelling loop KILLED:** a `square_formation` guard added to all THREE fortify decision sites (`_check_threats`, `_consider_fortify` early-return, the P8 fallback) so an AI marshal holding a valid square (P2.5's choice vs adjacent cavalry) is never ALSO handed a fortify order — fortifying auto-breaks the square, then P2.5 re-forms it next turn, the loop that burned Moore's nation-turns (`TACTICAL_TRIANGLE_SPEC §239-240`). Enemy-only, no player/serialization surface.
- **S5-2 — raw camelCase marshal keys no longer leak into rejection copy:** the three engaged/blocked-move seams (`combat_executor` attack-while-engaged, `strategic_executor` march-while-engaged, `movement_executor` move-into-visible-enemy) route names through `display_names.humanize_entity_name` ("ArchdukeCharles" → "Archduke Charles") in both message and suggestion; the `engaged_with`/`enemies_at_destination` DATA fields keep raw keys.
- **S5-3 — the reward-expectation rail notice stays LIVE:** the `DOTATION_EXPECTATION` notice (created once at shortfall-open with frozen numbers + a static "holds 2 turns") now refreshes every pre-erosion turn via a single `_post_expectation_notice` closure — live expectation/satisfaction + a real grace countdown — is DISMISSED when grace elapses (the HIGH `DOTATION_EROSION` notice owns the "fraying" narrative), **and — per the pre-push adversarial review — is dismissed on pay-back-to-met** so it never contradicts the grant confirmation. Fixes the live "rail says 80g/2 turns while dispatch says 160g/fraying" contradiction.
- **S5-5 — bombard no-guns guard single-sourced + fixed-corps copy corrected:** a `not marshal.artillery` guard at the TOP of `_execute_bombardment` protects EVERY caller (the post-objection `meta_executor` route bypassed the old parse-seam guard); and the PF-7 "drafted in fixed corps of N" note now cites the TRUE batch (`full_corps_size`, captured before the CO-4 field cap) instead of the capped delivery (a field-levied infantry corps no longer misreports itself as 3,000).
- **S5-D2 — MOVE_TO/HOLD issuance-time passability honesty:** if a player march's only routes cross a neutral we cannot enter (no passable corridor to the destination), the order is REJECTED at issuance with an honest message naming the closed frontier and **charges 0 AP** — the player learns now, not after paying 2 AP and stalling at the border. PF-8's per-turn stall reroute/break is unchanged for reachable/partial routes; diplomacy is un-fogged so this is safe.
- **AUD-g — Talleyrand military-advantage bands realigned:** the shifted 5-band ladder (dead "even" tier at ratio 0.5–0.75, true parity mislabelled "slight", ungrammatical "…is disadvantage relative to ours") replaced by a symmetric ladder centred on parity — overwhelming / superior / **comparable** (real parity) / inferior / overmatched — every word grammatical in both sentence templates.
- **AUD-e (docs-only) + S5-4 (docstring):** `_select_next_marshal_action`'s docstring + `ENEMY_AI_REFERENCE.md` (:127 sort claim, :211 P4.78→P7.4 relabel, :616-630 round-robin) reconciled to the SHIPPED sort (paid/free tier → round-robin → marshal_priority → name; `action_priority` is NOT the sort key); `DialogueManager.preempt`'s docstring refreshed (no longer hard-stop-only; the QUEUE_CAP overflow-drop named with its Pre-EA Dialogue Robustness owner — the fix itself stays deferred).
- **Pre-push adversarial review:** a 7-fix find→verify workflow (9 agents, ~1.07M tokens) — 6 fixes CONFIRMED clean, ONE confirmed medium defect in S5-3 (the pay-back-to-met asymmetry above), FIXED + regression-tested before commit.

### 🏛️ 8.EVAL HELD + CLOSED and 🖱️ REGION-PANEL & MAP-INTERACTION UX PASS ✅ BOTH July 16, 2026 (third session)

**User direction: "make the decisions for it [8.EVAL] knowing i want a good game; side note — when i click on region its popup UIs happening under the command box, fix this! make hover/clicking on regions have better UX + any other quick UX wins."**

**Track 1 — 8.EVAL (gate record = `docs/audits/EVAL_8_2026_07_16.md`, authoritative):** a 13-agent workflow re-verified all 25 docket items against TODAY's master (several rows dated July 3; much had landed/rotted since), then the keep/defer/drop calls were made under the delegated mandate. Headlines: **AUD-b confirmed balance-critical and still fully live** (the Third Coalition still sues for armistice by turn ~5-7 with zero combat — P2 counts battle-free turns from war start, no coalition gate); **E7 confirmed DORMANT** (at boot authority 100 the 2% floor IS the defiance rate — the whole sabotage arc + two shipped popups are near-dead content) → **DECIDED: authority-banded floor**; **Metternich DECIDED: build small** (rejected Schemer peace → expiring war-pressure on the threat substrate); **Nation Agendas re-scoped + PROMOTED to the Phase-8.5 design-gate centerpiece** (its legibility half landed piecemeal via W6-9/W6-10/UI-6/DEF-1; `nation_concerns` obsolete); **Talleyrand Desk CLOSED as landed** (~6/7 items shipped; R159 re-homed); **AI P3-P6 opportunism closed as substantially handled** (landed piecemeal across W6-10/VS-R/VS-6/P4.5 — the surviving fragment, war-score-aware multi-party offer terms, merged into the AUD-c slice); DW-2 SPLIT (convergence retired as intentional architecture; calibration → Pre-EA Balance Pass); AUD-e code-canonized (Enemy AI 8.0 held under the shipped sort — docs reconciled instead of reordering 19 nations); AUD-a/arch-#23/R32/power_score/R24/R33/R36/narration-toggle DROPPED with reasons. **Phase 8.5 opens with Batch Q (12 S-items, VS-5 live ratification exercise first) → the CR-6 mini-gate (S5-D1) → the 8.5 design gate.** All routing docs updated (ROADMAP queue+Quick-Status, DESIGN_REFINEMENT §8.EVAL Dispositions with 8 named pre-EA rows + queue items 5/6 + Wave-4/5 rows, BUG_FIXES §Sweep-5 dispositions incl. the S5-5 inverted-copy re-verify note, the preflight-audit DW-2/DW-4 rows, the E7/Metternich DWL ledger rows, CLAUDE.md).

**Track 2 — Region-Panel & Map-Interaction UX pass (user-flagged defect FIXED):** root cause of "popup under the command box" = the panel anchored center-left growing downward into the expandable terminal's corner (and at CanvasLayer 26 it *covered* the input box). Fixes, all landed:
- **Panel re-docked TOP-LEFT under the top bar** (`region_panel.tscn`), content in a ScrollContainer whose height is fitted per render and **clamped above the terminal's LIVE top edge** (`avoid_control` = BottomLeftUI, wired from main.gd; refits on the terminal's own `item_rect_changed`/`visibility_changed` — grip drags, reset, minimize/restore — plus viewport resize; retarget resets scroll, chip re-render preserves it).
- **Hover highlight moved to the GPU** (`map_renderer_base.gd` `HIGHLIGHT_SHADER` over the province lookup mask — same exact-palette-match discipline as the owner fill, NEAREST): the TRUE province silhouette lights with fill + 2-texel rim; the old path CPU-allocated a full map-canvas RGBA image per hover change and drew a **circle**. Hover is now one uniform write (G4 budget shape). Legacy circle-fixture map keeps the CPU path.
- **Click feedback:** `set_selected_region` keeps the clicked province lit (distinct gold tint) while the panel is open, with a 0.45s decaying pulse on click; selection survives layer rebuilds; cleared on every close path. Pointing-hand cursor over wired provinces.
- **Dismiss ladder:** ESC (before pause opens — and modal-gated so it never closes an invisible panel UNDER the pause menu), right-click, open-water click, and re-clicking the open province all close the panel; `map_dismiss_requested` signal + main.gd wiring.
- **Pre-commit adversarial review (3 lenses → per-finding refutation, 13 agents): 4 CONFIRMED findings, ALL FIXED** — (1) stale height clamp on terminal drag/minimize/restore (→ the reactive `avoid_control` setter), (2) ESC-under-pause swallowed (→ modal gate on the rung), (3) world-swap `hide_all()` stranded the old campaign's selection glow (→ `close_panel()` first in `_reset_frontend_state_for_world_swap`), (4) mid-pan clicks selected/dismissed through overlying UI (→ `is_panning` early-returns on both pressed branches).
- Tests: `test_ui_region_panel_ux_2026_07_16.py` (18 pins incl. the 4 review fixes); full suite green pre-fix run + targeted re-runs; boot smoke ×2 CLEAN (0 SCRIPT ERROR); parse harness regenerated EXIT=0.

### 🎨 UI BEAUTY PASS ✅ LANDED July 16, 2026 (second session) — war-bar fill root-caused, sea-floating nation labels snapped ashore, the Saxon Steed upgraded, + a 13-finding verified UI-defect sweep ALL FIXED

**User direction: "look at the war bar how it fills in, look where Naples is labeled, see any other ui issues, make it beautiful, feel free to use assets from online, see any fixes I failed to make, better Hanover's horse in the flag, commit and push."** Live-driven (screenshots at the native 5120×1440) + a 23-agent find→adversarial-verify workflow over the UI .gd/.tscn files; every fix below was re-verified in-game (boot smoke 0 `SCRIPT ERROR`).

- **War-bar fill ROOT-CAUSED and fixed (the U5 anchor fix hadn't cured it):** the fill TextureRect lacked `expand_mode = EXPAND_IGNORE_SIZE`, so `warbar_fill.png`'s natural 72×22 px became the control's MINIMUM size — at UI scale/short bars the anchored span is smaller, so the pill overflowed PAST the centre gem (a −44 losing score read like a partial win) and bulged out of the track vertically. Fixed in BOTH builders (`war_status_panel.gd` + `war_detail_popup.gd`) + a proportional `BAR_RIM_INSET` so a ±100 fill tucks inside the gold rim caps; the popup bar (which has no gem) gained a slim gold **centre tick** so fill direction stays readable under the score label; the HUD gem got the same `EXPAND_IGNORE_SIZE` (26×26 texture vs 20×20 rect — it rendered oversized and off-centre, the sweep's find). Verified live at −44: fill inside the track, ending exactly at the centred gem/tick.
- **"Naples" (and any multi-blob nation) no longer prints its name in open sea:** the nation-label tier's radius²-weighted centroid stays ONLY when it falls inside an owned province circle; otherwise it snaps to the nearest owned blob's hand-authored `label_anchor` (`_snap_label_to_owned_land`, `map_renderer_base.gd`). Naples (mainland+Sicily averaged into the Tyrrhenian) verified snapped onto the mainland; same rule covers Sardinia/Piedmont-class splits. Centroid-weighting pins (`test_map_slice75_presentation.py`) untouched.
- **Hanover's Saxon Steed UPGRADED from the hand-drawn horse** to the detailed heraldic steed adapted from Wikimedia Commons **"Flag_of_Twente.svg" (public domain, same Saxon-Steed lineage)** — rescaled to fill 90% of the game-red field; verified crisp at ledger thumbnail size; credit recorded in `THIRD_PARTY_LICENSES.md`.
- **UI-defect sweep (find→verify workflow, 13 CONFIRMED findings, ALL FIXED):** (1) `Utils.bb_flag` hard-stretched every flag into 3:2 — Union Jack squashed 25%, Papal banner stretched 50%; now derives width from the texture's real aspect (cached) — verified live in the ledger. (2) The enemy-phase battle-outcome color LIED: it keyed on a hardcoded legacy roster (`Ney/Davout/Grouchy/Drouot`) AND on "defender is player" rather than who WON — Soult/Murat/Lannes victories rendered red, a Ney defeat rendered green; nations now ride the battle events (`combat_executor.py` both emitters) and the dialog colors by the VICTOR's side (`_victor_is_player`). (3) `_get_nation_color` knew 3 of 20 nations in private constants → central `Utils.NATION_COLORS` with a luminance floor for near-black fills. (4) Morning-dispatch marshal/intel "tables" were space-padded to character stops under the proportional EB Garamond — ragged staircases + field-fusion at exactly-full stops; both copies (`main.gd` + `dispatch_view.gd`) now render separator-based lines. (5) `main.gd._format_number` counted the '-' sign as a digit ("-,500" on a deficit treasury) → delegates to `Utils.format_number` (enemy_phase_dialog's copy deduped too). (6) Unbounded `fit_content` modals could grow past the screen and strand their buttons (unanswerable): `proposal_confirm_popup.tscn` + `incoming_proposal_popup.tscn` ContentLabels now scroll inside the fixed panel; the wizard's `AssessmentPanel` capped at 150px scrolling. (7) The five fixed-rect layer-50 screens (840×620 etc.) clipped their header/close-X off-screen at Interface Scale ≥1.5 on small windows → shared display-only `Utils.clamp_centered_panel` on every open (authored rect stays the ceiling; no-op on viewports that fit). (8) Notification detail panel's inverted type hierarchy (12px title under a 16px body, 10px buttons) → 17px title, theme-size buttons. (9) The terminal's full-height drag could wedge its resize grip under the top bar (`TOP_BAR_RESERVED_PX` now reserved in `_relayout_terminal`).
- Suite green + ruff clean; backend surface = the two battle-event nation fields only (display-only, fog-safe — events already rode the visible enemy phase).

**Second wave (same session, user follow-up "did Naples really own Africa? can nation colors be more accurate based on like Europa etc? are nations right?"):**
- **Naples really did own Africa — THREE mis-authored map regions fixed in `europe.json`** (bitmap-verified by overlaying each region's lookup-color extent on the visual art): the region named "Sicily" painted a strip of the **African coast** (→ renamed **Tripoli**, controller Naples→**Ottoman** — the Ottoman regency that actually sat there; the island of Sicily is the region named "Naples", kept as the kingdom's seat); "Algarve" painted **Morocco** (→ renamed **Morocco**, Portugal→**Spain** — the Ceuta/Melilla presidios rationale); "Andalusia" painted the **Algerian coast** (→ renamed **Oran**, Spain→**Ottoman** — Algiers held Oran from 1792). Plus the pure rename "Bessarabia"→**"New Russia"** (the painted region is the north-Black-Sea steppe, Russian in 1805; actual Bessarabia stayed Ottoman until 1812). Scenario fix: Castanos (Campo de Gibraltar) restationed Andalusia→La Mancha; Portugal's `covets_regions` Algarve→Morocco. Ownership deltas touch only periphery nations (Ottoman 12→14, Portugal 5→4, Naples 2→1 regions) — France/Austria untouched, E1 blessed numbers safe.
- **NATION_COLORS re-authored to Paradox/EU4 conventions** (user-directed): **Austria WHITE** (was gold), **Spain GOLD** (was plum), **Russia dark forest green**, **Ottoman vivid green**, **Prussia anthracite blue-black**, **Portugal teal** (was purple), **Hanover pale yellow** (was brown), **Sardinia Savoy dark red-brown** (was gray), **PapalStates cardinal purple** (was near-white — Austria took white), Sweden/Bavaria/Holland/Naples/Denmark/Hesse/Saxony/Switzerland/KoI kept. The DEF-10 SET discipline held: measured min pairwise blended deltaE **13.4** (floor 12) / fogged **7.8** (floor 7) / fallback 53.6 (floor 30) via the same Lab math as `test_map_slice75_presentation.py`; the contrast-rule exemplar lists updated (PapalStates moved to the white-text side). Verified live — the political map now reads instantly as an EU4-style Europe.
- **Nations-audit findings REPORTED, not changed** (deliberate design compressions whose ownership feeds blessed econ numbers): Piedmont under KingdomOfItaly (historically annexed to France 1802 — moving it re-tunes France's E1 absorption anchors, user's call), East Frisia/Westphalia/Oldenburg/Brunswick grouped under Hanover (E. Frisia was Prussian), Swabia under Bavaria (Württemberg/Baden were separate French allies), Karelia under Sweden (Old Finland was Russian). One test re-anchored: the ES-7 dispatch-rollup test's `_conquer` first-safe-pick shifted from Algarve (city 150) to Piedmont (major_city 200), exactly meeting its 200 expectation — expectation raised to 240 (above any non-capital income) so the unmet-marshal intent survives future map edits. Suite **13,551/3** green, ruff clean.

### ⚔️ COMBAT OVERHAUL PROGRAM ✅ **CLOSED July 16, 2026** — Sweep 5 (Parsing/UX) MET + EXIT SWEEP passed; flag date-accuracy pass; visual sign-offs RECORDED

**User direction: "do combat overhaul and if you see anything else that will improve it do it … some flags are wrong … make sure vassals have flags too. do visual check yourself for sign off."** Second-session record; full detail in the three audit docs.

- **Sweep 5 (Parsing/UX) ✅ RAN + MET** — `docs/audits/SWEEP_5_2026_07_16.md` + `SWEEP_5_LIVE_EVIDENCE_2026_07_16.md`. Half A: PF/AI/metric tests 87 green, M1–M7 byte-identical, corpus mock 433/433 + **live 432/432** (NEW `mock_only` harness arm). Live evidence: three fresh 6-turn anthropic playthroughs whose first two rounds **live-found five real defects — ALL FIXED in-session**: (1) the typed-answer channel died behind ANY soft-stop dialogue (`register_pending_clarification` now PREEMPTS non-hard-stops — the ASK's "give battle" mis-parse killed; CR-2 pin consciously flipped), (2) "press on"/"continue" now resolves `attack_anyway` at interrupts, (3) an invented-marshal guard at the validation seam (live LLM picked never-mentioned Bernadotte for bare "attack", breaking his HOLD — live now rejoins the CR-4-focus/CR-2-clarification flow), (4) movement-target passthrough on BOTH parse paths ("move to Venetia" now yields "Region 'Venetia' not found. Nearby: …" instead of "requires a destination"), (5) `mock_only` corpus rows. Half B: 12-component adversarial review (28 agents, ~3.7M tokens) — **Parsing 7.0→7.5 MET, UX 7.0 / Narration 8.0 / Diplomacy 8.5 held-or-raised, +1.0 Vassals (7.5), ZERO regressions**; both Sweep-2 WAD drama gaps confirmed CLOSED live (autonomous glory attack + crown lit).
- **P0 (synthesis exit condition) ✅ FIXED same session** — the end-turn HTTP 500: `_build_result_response` forwarded `enemy_phase` RAW (per-action `new_state` WorldStates → tuple-keyed caches crash `jsonable_encoder` AFTER the turn advanced; also a fog leak). Now routed through `_build_visible_enemy_phase`; poison reproduced-then-killed; `test_sweep5_end_turn_500.py` (4); exit re-drive = 6 end turns with pending captures, **zero 500s**.
- **EXIT SWEEP ✅ — THE PROGRAM IS CLOSED** — `docs/audits/COMBAT_OVERHAUL_EXIT_SWEEP_2026_07_16.md`: every §1 target MET or EXCEEDED (Combat 5.0→7.5, Economy 5.0→6.5, Drama 6.0→7.5, Vassals 6.0→**7.5**, Parsing 7.0→7.5, UX 6.5→7.0, Narration 7.0→8.0, Marshal System 6.5→8.0, Diplomacy 8.0→8.5, Settlement 7.0→7.5, Architecture 7.0→8.0, Enemy AI held 8.0; **overall 6.4→≈7.6** vs ≥7.3), zero regressions across all six sweeps. Exit scenarios scripted per the synthesis: reward-economy transaction **FULL** (Duchy of Swabia endowment → live "Dotations: −96g" ledger component; rente at honest 1.5× → "Rentes: −96g"), low-loyalty vassal arc **LIVE** (`vassal_rebellion` fired turn 2 from staged loyalty 30), settlement flow OPENED (full wizard-path ratification w/ `vassal_transfer` → routed to 8.EVAL). Routed forward: `BUG_FIXES.md` §Sweep-5 (S5-1..5; Moore AI loop, camelCase R7 leaks, stale dotation rail, preempt overflow, PF-7 lows) + `DESIGN_REFINEMENT.md` §Sweep-5 (S5-D1 bare-"attack" gate inversion → CR-6 gate candidate; S5-D2 PF-8 issuance honesty; S5-D3 hygiene).
- **Flag date-accuracy pass (user-directed) ✅** — all 20 heraldry SVGs audited for 1805: **Hanover REDRAWN** (white Saxon Steed on red — the old white/yellow bicolor is the post-1814 Kingdom flag), **Ottoman star → 8-point** (Selim III's 1793 naval ensign; 5-point is 1844 Tanzimat), **Saxony REDRAWN** (Electorate banner-of-arms: barry sable/or + green crancelin — white/green is 1815+). Kept-as-authored judgment calls documented in `THIRD_PARTY_LICENSES.md` (Switzerland's cross = medieval confederate war sign, the 1803–13 Mediation era had no flag; Naples = the Angevin azure-semé-de-lis banner, the Bourbon plain-white is illegible at thumbnail). The other 15 verified period-correct (Prussia's file is literally the 1803–92 flag; Papal States already the pre-1808 red-gold). **Vassal flag coverage verified structural** (backend sends raw nation keys; every vassal-capable key has an asset) **and visual** (all three client-state cards render flags).
- **Visual sign-off pass ✅ RECORDED (self-served per user direction)** — engine booted clean (headless import 0 errors; the 3 edited SVGs re-imported), then screenshot-verified in-game at the native 5120-wide display: **UI-6 surfaces** (Region Action Panel with flag + honest chips on allied soil; VASSALS tab cards with flags/loyalty bars/tribute-cut legibility/call-to-arms/garrison hints; Nations-tab flags crisp at 14px incl. the new 8-point Ottoman; gear button honoring the UI6-GD-1 invariant per code; Generals screen with the Laurels ladder — Lannes CROWNED live, Murat's "» envious of Bernadotte" arrow, Commission bench, portraits + `█░` skill bars), **U2 map crispness at ≥2560 ✓**, **U3 leather/filigree/icons ✓**, **U5 pieces ✓** (two-rank spread, tin-flat sprites, contact shadows; nit: arms hard to distinguish at min zoom — resolves on zoom, acceptable). **The U2/U3/U5/UI-6 ⚠ sign-off rows are CLOSED.**
- Suite **13,551 passed / 3 skipped** (+30 this session), ruff clean per commit; stray `warn_probe_tmp.gd.uid` orphan removed.
- **▶ NEXT: 8.EVAL** (war-LLM/diplomacy triage + the routed settlement-ratification live exercise) **→ Phase 8.5.**

### 🖱️ UI-6 INTERACTION & HERALDRY SWEEP ✅ LANDED July 16, 2026 — vassal buttons, clickable map, flags, glyphs — `docs/UI_VISUAL_FOUNDATION_SPEC.md` §8-U6

**User direction: "add buttons for vassal interactions and do another review of the ui … streamline systems, add clickable items when possible, commit and push."** A 7-reader understanding workflow mapped every seam first; built in 8 slices; a 23-agent 5-lens find→verify review confirmed 15 findings (9 distinct) — ALL FIXED pre-commit; then a live user review round added the full province verb set, the 4 missing flags, and the Blender-sprite check.

- **VASSALS tab (diplomatic ledger tab 6 / KEY_6):** per-vassal cards — flag, loyalty bar, autonomy + provenance ("scenario"-seeded boot vassals labeled client states, not conquests), tribute (+rate), VS-4 contribution tier, warning band + grip-aware recovery hint, garrison/subsidy lever lines, granted provinces — plus **honest-availability action chips** (Invest / Loosen Rein / Tighten Rein / Cede Province… / Release) riding the wizard's own `get_available_diplomatic_actions` rows; chip terms render backend-derived, **grip-effective** gains (`invest_gain`/`autonomy_up_gain` mirror the executor's `int(gain*mult)` — never a promise the VS-R spiral blunts) + the executor's own blunted-disclosure phrase. Cede hands off to the wizard's VS-3 province picker. Backend `_build_vassals` in `diplomatic_ledger.py`.
- **NEW single-source `vassal.forecast_vassal_loyalty`:** the knowable steady-state next-turn delta (drift + garrison + **subsidy clauses** + shared enemy + relations + grip; battle term excluded) — consumed by the ledger tab AND the wizard preview trend (review fix: the old wizard arrow read autonomy drift alone and could contradict both the ledger and the actual tick; a drift-lock test now binds helper == pipeline on a battle-free turn).
- **Region Action Panel (`region_panel.gd/.tscn`, layer 26):** the map's `region_clicked` seam — dead since the cutover — now opens a fog-honest panel from the map node's own filtered stores. Context chips: **Recruit Infantry/Cavalry/Artillery**, **Build Depot/Fort/Training Ground/Market/Stables** (canonical `BUILDING_TYPES` keys, hidden when built/no slots) + **Watchtower** (slot-exempt) + **Repair** (damage-gated); foreign province → **Negotiate** (wizard handoff); per-marshal **Fortify/Unfortify/Drill/Scout** + **Attack <enemy>** (FULL-vis enemies only). Same never-over-a-screen/modal rule as the war HUD.
- **Heraldry:** 20 nation flags wired (untinted) into ledger nation rows + vassal cards, wizard step-1 buttons + step-2 header, war HUD cards + armistice rows, war-detail header (`Utils.nation_flag_path/bb_flag/apply_flag_icon`, cached). The 4 missing flags (Hanover/Hesse/KingdomOfItaly/Switzerland) authored in the set's flat style; licenses manifest updated.
- **Notification rail glyphs:** phosphor silhouettes replace the 3-letter codes (sword/scales/handshake/eye/castle-turret/…), white on the priority pill, legacy text fallback for unmapped types; glyph existence pinned.
- **Top-bar gear button** (pause was ESC-only) honoring the ESC invariant (closes screens first — review fix); **Generals card order chips** (Fortify/Unfortify/Drill); Talleyrand-tab **[Assess the Situation]** chip (W6-9 verb).
- **Streamlining:** `Utils.bb_icon/bb_button_chip` single-source the chip idiom; `_format_number` 5 copies → `Utils.format_number`; stale Generals-placeholder guard retired; nav hover style-jump fixed; **shared `_chip_command_in_flight` latch** (review fix — a chip double-click double-spent); **`_on_objection_response` refreshes open info screens** (review fix — chip-raised objections resolved after the chip's callback left stale cards); U5 clustering residual CLOSED (`_marshal_slot_offset_2d` two-rank spread, shared by pieces/labels/hitboxes).
- **Blender check:** NOT installed (PATH/Program Files/winget) — the §8-U4 3D pipeline stays unavailable; the 2D carved-wood set was composite-inspected (3 tints × 3 arms) and verdicted KEEP.
- **Gates:** boot smoke 0 `SCRIPT ERROR` ×3 (build / post-review / post-follow-up + import pass); parse-harness report regenerated (settlement-critical .gd touched); ruff clean; `tests/test_ui6_interaction_sweep.py` (44); suite **13,521 passed / 3 skipped**. **⚠ open: user visual sign-off** on the new surfaces (vassal cards, region panel, flags incl. the 4 new, glyphs, gear, two-rank piece spread) — one-line tunes, same gate family as U2/U3/U5.

---

### 🏰 VASSAL DEPTH QUEUE ✅ **BUILT COMPLETE July 16, 2026 — ALL SIX SLICES LANDED** — `docs/VASSAL_DEEPENING_SPEC.md` §8 (build record)

**User direction: "do vassal updates and be thorough — the ones that are queued, I approve all before starting; see if they all make sense or if we need anything else."** A pre-build **seam-verification workflow** (6 parallel readers + synthesis, ~1.2M tokens) checked every queued slice against the actual code BEFORE building — verdict: **all six SOUND, none needed redesign, every one needed amendments** (the spec's wizard seam was wrong for VS-3; `CommandRequest` would have silently dropped the wizard's region pick; VS-4's "shared-war path" substrate was actually the war-cascade + assimilated marshals; `change_vassal_autonomy` had NO lord gate and would drain the *player's* DP on any AI call). It also **promoted a Slice 0** (nation-neutral substrate) that three later slices depended on. Landed in order, each commit suite-gated:

- **Slice 0 (`1082382`) — nation-neutral vassal substrate + VP-D1 garrison wire:** actor param + `_charge_dp` DP split on invest/change-autonomy (AI lords pay from `nation_dp`/`nation_gold`); the missing `change_vassal_autonomy` lord gate closed; coalition threat player-scoped (AI vassalizations add none; AI rebellions relieve none); `_acting_nation` + structured `new_level` executor wiring. **VP-D1 WIRED**: presence-based flat +2 (`lord_garrison_present` single source, debug endpoint mirrored) — the authored +5..+8 ladder deliberately discarded (economy-breaking vs −2 drift); full value in the VS-R spiral band; healthy recovery hint re-advertises it; 5 F1c pins consciously flipped. `test_vassal_slice0_substrate.py` (26).
- **VS-3 (`e2f72ad`) — Land Grants via the F1 diplomacy wizard** (spec §1.3 landing record): `grant_region_to_vassal` — worth-scaled `min(25, 10+income//200)` loyalty, NEVER spiral-blunted; conquered-land-only + no capitals + ES-7-estate-excluded + contiguity (waived for landless vassals + homeland returns); `granted_regions` provenance → WAR-branch reclaim-on-rebellion; 1 DP + 0 AP (family convention), 3-turn per-vassal cooldown; the wizard option rides `diplomacy.py get_available_diplomatic_actions` with a **positive-path province picker** in `diplomacy_wizard.gd` (every pick states income/loyalty/tribute terms); `CommandRequest.region` + overlay added; typed "cede X to Y" path + 3 corpus rows; recovery hints (both bands) now name the grant. Boot smoke clean. `test_vassal_land_grant.py` (32).
- **VS-4 (`02bd773`) — Loyalty-gated call-to-arms** (spec §5 landing record): single-source `vassal_military_contribution` (loyal ≥60 / wavering 35–59 / disaffected <35). Disaffected **refuses NEW war-cascade auto-joins** (both arms; `vassal_refuses_call` cascade entry + ledger row + declare-war copy + HIGH notification + dispatch + campaign log; **no retroactive mid-war exit**, pinned). Wavering **withholds assimilated ex-vassal marshals** (`original_nation`) from auto-reinforce + muster (`vassal_wavering` reason) — UNLESS under an explicit SUPPORT order (A-D4 pattern; direct orders stay obeyed, pinned). GR5-symmetric; marshal-teeth latent at the 1805 boot (satellites have no marshals). `test_vassal_call_to_arms.py` (20).
- **VS-5 (`5cdf354`) — Settlement vassalage: creation ASSURED + `vassal_transfer` clause** (spec §6 landing record): creation/liberation confirmed already guided-surface-reachable (pins). NEW transfer clause `{from: from_lord, to: to_lord, vassal}` across the full lifecycle (schema, validator `evaluate_vassal_transfer_eligibility`, guided suggestion + Talleyrand line, demand-only add verb, package-level ratify handler) + shared `transfer_vassal` domain helper (loyalty reset 30, marshal re-key, **VS-3 provenance cleared**, pair re-homing, no release cooldown). **Two pre-existing hegemony-projection bugs fixed** (liberation's unread `vassal_nation` key; vassalage's REVERSED from/to) — both fed AI acceptance pricing. AI parity scoped to accept-side pricing (deferral row VP-D8). `test_settlement_vassalage.py` (29).
- **VS-6 (`6e2bd53`) — The Defection: coalition-flip as a BRIBE** (spec §7 landing record): `attempt_vassal_bribe` right after courting, **resolving immediately** (structural double-fire guard, zero new serialized fields). Gate: briber at WAR with the lord + solvent; vassal loyalty <35 (**deliberately the VS-4 disaffected line**) or <50 in the lord's grip spiral (Ried window); probabilistic, grip-scaled. Outcomes: **transfer** (600g + WPS-B cap, VS-5 machinery) or **free + GUARANTEED WAR** with the former lord (300g; VS-3 reclaim, sibling shock, armistice/F8b fallbacks kept). No `coalition.members` mutation (recorded deviation); player-side bribe verb deferred (VP-D9). Spec §7's wrong F8b-baseline paragraph corrected. `test_vassal_defection.py` (18).
- **VP-D6 (`1f48642`) — Enemy-AI grip-awareness:** P1.6 `_find_vassal_shore_up` rung (invest → **VS-3 grant** → autonomy-up, escalating desperation; "subsidize" dropped — not an action) through the shared executor at player prices; command builder carries structured `region`/`new_level`. Latent until an AI lord holds a satellite. Rows VP-D1 + VP-D6 CLOSED in `DESIGN_REFINEMENT.md`; NEW deferral rows **VP-D8** (AI-authored dependency clauses) + **VP-D9** (player bribe verb). `test_vpd6_ai_vassal_shore_up.py` (12).

**A post-build 5-lens find→verify adversarial review (11 agents, ~1.07M tokens) confirmed 10 findings — ALL FIXED pre-push (`dd304ab`):** 2 HIGH **reproduced live** (the VS-6 bribe against a *cascaded-in* satellite — the slice's core scenario — force-flipped WAR→VASSAL stranding the pair in the war instance forever, and the free outcome silently fell back to PEACE on the instance side-conflict, inverting the guaranteed-WAR contract; both now settle the old war pairs FIRST via `cleanup_war_end`, +2 real-war-instance integration tests from the reviewer's live repro), 4 MEDIUM (the refusal dispatch event was invisible under the `player_vassal` fog rule; Rule 1b now accepts PURSUE-into-region as the written word, mirroring the muster; liberation×transfer same-vassal packages rejected + the liberation apply-guard requires the LIVE lord; the VS-3 typed region scan no longer matches the recipient's name — Hanover/Naples), 4 LOW (defection popup cleanup, transfer threat relief, AI-lord `threat_delta_for_lord` preview honesty — one pin flipped, mock-parser "grant independence" exclusion); 1 claim refuted. **Suite 13,323 → 13,477/3 (+154), ruff clean every commit, Godot boot smoke + parse-report regen for the .gd slice.** **▶ NEXT: Combat Overhaul Sweep 5 (Parsing/UX) → program exit sweep → 8.EVAL** — the vassal track is CLOSED pending a live playtest re-score (Vassals 6.5 → 7+ candidates all landed: the positive grip lever, military teeth, settlement re-homing, The Defection, both-boards AI).

---

### 🏰 VASSAL FIXES + DEPTH QUEUE — July 15, 2026 (post-Sweep-4) — ~~▶ NEXT VASSAL BUILD = VS-3 land grants (BLESSED)~~ ✅ **superseded: BUILT July 16 (see above)**

**User direction: "how does autonomy work, fix the issue(s) found, see if we did vassal diplo items and how we can raise score more … make all of this next in status, assure we build diplo stuff, docs only, commit and push."**

**Two Sweep-4 issues FIXED (backend + tests; suite 13,323/3, ruff clean):**
- **The "grant X *more* autonomy" parse shrug** — root cause: `change_autonomy` targets a *nation* (the executor resolves it from `raw_command`, F6), but `_apply_fuzzy_matching` still hunted for a *marshal* in the leftover words and matched the direction word **"more" → "Murat"** by edit-distance, failing the command; `grant Holland autonomy` (no direction word) worked while `grant Holland more/less autonomy` shrugged. **Fix (`parser.py`):** skip marshal fuzzy-matching for the four vassal-family actions (`change_autonomy`/`invest_vassal`/`release_vassal`/`make_vassal`), same as `recruit_marshal` already does — they carry a nation target, not a marshal. Also killed a related mis-resolve (`make Holland autonomous` → target `Mack`). The F6 tests only covered the mock parser + executor, never the full `CommandParser.parse` pipeline — which is why it slipped; new pins test the full path.
- **VP-D5 — autonomy-up hid its permanent tribute cut** — `change_vassal_autonomy` now shows the tribute DELTA directionally: up = "Tribute rate: 75% → 50% (a permanent income cut)", down = "50% → 75% (you collect more of their income)". A player following the "grant autonomy" recovery hint now sees the recurring cost at the decision point.
- Tests: `test_playtest_fixes_2026_07_14.py` `TestSweep4AutonomyDirectionParse` + `TestAutonomyTributeLegibility` (+9). Both live-verified over HTTP. Marked resolved in `DESIGN_REFINEMENT.md`.

**How autonomy works (for reference):** three levels — **Puppet** (drift −4/turn, tribute 100%), **Satellite** (−2, 75%, default), **Autonomous** (+1, 50%). `change_vassal_autonomy` costs 1 DP: UP = +10 loyalty (blunted ×0.4 in the VS-R spiral) **and flips a bleeding satellite's drift −2 → +1**, at the price of a permanent 25pp tribute cut; DOWN = −15 loyalty, tribute restored. This is why "grant autonomy" is a taught recovery lever alongside invest.

**▶ VASSAL DEPTH QUEUE — the path from Vassals 6.5 → 7+ (dependency-ordered; full design in `VASSAL_DEEPENING_SPEC.md` §1, §5–§8):**
1. **VS-3 — Land Grants via the F1 Diplomacy Wizard ✅ BLESSED July 15, 2026 (the "diplo stuff" — BUILD NEXT).** Cede a controlled province to a vassal → worth-scaled loyalty, lord forfeits income / vassal tributes it at its autonomy rate; the *positive* grip lever the spiral hint lacks. Spec `§1`; reuses the `settlement_ratify` transfer seam + the wizard's sub-picker; GR5 AI parity. `test_vassal_land_grant.py`.
2. **VS-4 — Loyalty-gated call-to-arms (NEW July 15).** Loyalty gains *military teeth*: a **disaffected vassal (loyalty < ~35) refuses to send troops to your wars**, a wavering one (~35–60) drags its feet, a loyal one contributes fully — single-source `vassal_military_contribution`, GR5-symmetric, surfaced in the dispatch/muster. Independent; the soft precursor to defection (withhold troops → then flip). Spec `§5`; `test_vassal_call_to_arms.py`.
3. **VS-5 — Vassal creation & transfer in peace deals (NEW July 15).** Settlement *already* creates vassals (`vassalage`/`subjugation`) + frees them (`liberation`); assure those are reachable on the **guided peace surface + F1 wizard**, and ADD **transfer** (`vassal_transfer` clause → change a vassal's lord, re-key marshals/tribute, reset loyalty toward the new lord). This is the machinery VS-6's "become someone else's vassal" outcome reuses. Spec `§6`; `test_settlement_vassalage.py`.
4. **VS-6 — The Defection: coalition-flip as a BRIBE (REFINED July 15; supersedes the §2.7 stub).** A flip is *transactional* — a coalition must **offer the wavering vassal a concession it wants** (sovereignty/land/subsidy/frontier guarantee); no willing briber → it stays. When the bribe lands, **two outcomes**: (a) **becomes FREE → guaranteed at WAR with the former lord** (a *hostile* break, not today's graceful PEACE), or (b) **becomes someone else's vassal** (transfers to the bribing coalition member — reuses VS-5). Driven by what the coalition offered; GR5 (your coalition can bribe enemy satellites too). Depends on VS-5. Spec `§7`; `test_vassal_defection.py`.
5. **Cleanup/enablers:** **garrison lever wire-or-remove** (VP-D1, P0 — `vassal.py` reads an unassigned `garrison_troops`) + **enemy-AI grip-awareness** (VP-D6 — lets a spiralling AI lord shore up its satellites AND *pay* defection bribes / defend against them, so VS-4/VS-6 are alive on both boards). `DESIGN_REFINEMENT.md`.

Rationale (spec §8): VS-4 + VS-5 are independent floor-raisers; VS-6 depends on VS-5's transfer and VS-4's "wavering→withholding" precursor. Runs alongside the Combat Overhaul program's remaining **Sweep 5 → exit sweep**; interleave-vs-after is the user's call at build time. Per-slice numbers escalate to each build gate.

---

### ⚔️ COMBAT OVERHAUL — SWEEP 4 (Vassals, Half B) ✅ RAN July 15, 2026 — `docs/audits/SWEEP_4_2026_07_15.md` — ▶ **Sweep 5 NEXT**

**The Phase-5 (Vassals) Half-B measurement.** The 12-component adversarial review (25 agents / ~2.45M tokens) over a deterministic engine probe (`scratchpad/vassal_probe.py`) + a live-HTTP surface prong (`LLM_MODE=mock`, clean boot).

- **Half A (hard gate) — PASSED.** Phase 5 touches no combat code, so M1–M7 held byte-identical vs Sweep 3 (M1 `…→0.818`, M2 `0.613/1.000`, M3 `−2749`, M4 `100%`, M5 `+0.240`, M6 GUARD `0.000`, M7 `turn 1`); the vassal gate `test_vassal_recovery_lever` (9) + `test_vassal_authority_coupling` (42) + `test_playtest_fixes_2026_07_14` (19) = **70 green**; full suite **13,314/3**.
- **Half B — Vassals 6.0 → 6.5, target MET (at the floor); UX 6.5 → 7.0; ten pillars held; ZERO regressions.** The July-14 playtest scored the pillar exactly **6.0**, dragged down by VS-1 teaching *broken* levers; the 10 fixes (`016bf71`) removed that drag and VS-R added the real content. **The crux, live:** a strained court (`authority=65 "Respected"`) loses Paris and the raw `authority_tracker` **stays 65** while derived `get_imperial_grip` correctly spirals to **25** → −2 drift, invest blunted ×0.4 ("the Emperor's faltering grip blunts the gesture"), spiral hint pivots to "win a decisive battle or release them." The teach-it loop closes end-to-end over HTTP (invest 94→100; the Autonomous flip drops a satellite out of the bleed). GR5-symmetric, one-way, **zero serialized fields**.
- **Held short of 7 (all CONFIRMED, none regressions):** coalition-defection unbuilt (the marquee "Coalition Dynamics" beat, GR9); VS-R is collapse-only (grip floor from healthy authority is 45, never spirals unless pre-depressed); the garrison-in-capital lever still inert dead code (VP-D1).
- **Findings routed:** P0 wire-or-remove garrison (`DESIGN_REFINEMENT.md` **VP-D1**); P1 coalition-defection (`VASSAL_DEEPENING_SPEC.md` §2.7 GR9) + VS-3 land grants (§1); P2 the "grant X **more** autonomy" pre-parse gap → **Sweep 5**, tribute-cut legibility (**VP-D5**), enemy-AI grip-awareness (**VP-D6**); P3 dual authority-derivation reconcile (**VP-D7**).
- **Combat Overhaul Phases 0–5 COMPLETE; every phase's Half-B target met, zero program regressions.** **▶ NEXT: Sweep 5** (Phase 6 already landed at `3c0246a`) → program exit sweep → 8.EVAL.

---

### ⚔️ COMBAT OVERHAUL — PHASE 6 (Parser & Play-Friction Cleanup) ✅ LANDED July 15, 2026 — `docs/COMBAT_OVERHAUL_SPEC.md` §4 Phase 6 — ▶ **Sweep 5 (Half B) NEXT**

**User direction: "code next phase of fixes be extra thorough."** The next coding phase in the Combat Overhaul program. All **ten** spec §4.7 live-found bugs fixed, backend-only (**no `.gd` touched** — every display rides an existing passthrough); suite **13,314/3**, ruff clean.

- **PF-1** bare leading preposition stripped in `strategic_parser._clean_target_text` ("march on Tyrol" → region Tyrol, not the phantom "On Tyrol"). **PF-2** delegation ASK options declare answer `aliases` (incl. the target-qualified "observe Mack"/"attack Mack" the question prints) so answering in the question's own words resolves instead of mis-parsing. **PF-3** an uncontested MOVE onto an empty/unfortified/ungarrisoned at-war enemy province now captures via the single `_attempt_region_capture` pipeline (GR5-symmetric); a **direct** move pops the plunder/secure popup, a **strategic-march hop auto-secures** (like the AI) — save-and-restore of the shared single-slot `pending_capture_choice` so a march never clobbers an earlier marshal's pending choice. **PF-4** an out-of-range `attack` skips the wasted trust-costing tactical objection (new `_attack_target_beyond_range` probe reusing the existing range primitive) — the order becomes a strategic PURSUE with its own objection; in-range attacks still object. **PF-5** notification-rail dedup: `dismiss_by_type`-before-add for `TREATY_SIGNED` (by counterpart), `DIPLOMATIC_PROPOSAL_RESULT` (by target), `DOTATION_EXPECTATION` (by marshal). **PF-6** a non-literal 2-AP strategic HOLD announces the upgrade inline + names the 1-AP `defend` alternative. **PF-7** the mock parser recognizes the `artillery` arm (word-boundary regex so "gun" ≠ "Burgundy"; feeds the soft-correction), a requested recruit count is *noted* (fixed batch unchanged), and a `bombard` from a no-guns marshal is rejected before melee. **PF-8** `find_path`/`find_weighted_path` gain optional `passable_for` (skip non-destination regions a nation can't enter); a player strategic march prefers passable corridors (terrain-only fallback), and a stall on a diplomatic block **reroutes once, else BREAKS the order with a reason** (mirrored into PURSUE) — no more silent re-stall. **PF-9** the Nations-tab treaty display scoped to the player↔nation pair key and hidden while at WAR (no third-party leak). **AI-1** behavior-preserving relabel of the mislabeled `P4.78` defensive-reinforcement rung → `P7.4` (matches its true post-P7 evaluation position; returned score 7 unchanged).
- **Adversarial verification (4 rounds, ~30 agents):** the review caught **8 real defects** that were all fixed before landing — round 1 found 5 (PF-2 printed-phrase alias gap, PF-3 strategic-guard block, PF-5 weak production tests, PF-7 "gun"/Burgundy substring collision, PF-8 PURSUE silent re-stall); rounds 2–3 found the PF-3 multi/cross-marshal capture-choice clobber (fixed with save-restore auto-secure) + a PF-5 GR9 unowned-`changed`-flag (removed) + refuted a false-positive PF-4 "charge" gap (charge isn't in `objection_actions`, so it never objected — the dead-code extension was reverted). Final convergence check: **CONVERGED, zero residual defects**.
- **Tests:** `test_pf1_march_on.py`, `test_pf2_delegation_ask.py`, `test_pf3_uncontested_occupation.py`, `test_pf4_unreachable_attack_no_objection.py`, `test_pf5_notification_dedup.py`, `test_pf6_hold_ap_announce.py`, `test_pf7_recruit_arm_amount_bombard.py`, `test_pf8_hostile_route.py`, `test_pf9_nations_treaty_scope.py`, `test_ai1_priority_order.py` (each with falsifiable negatives; PF-5's two production-path guards mutation-verified to fail on a revert).
- **▶ NEXT: Sweep 5 (Half B)** — Parsing ≥7.5, UX ≥7.0, Narration ≥7.5, Diplomacy held ≥8.0. (Sweep 4 for Phase 5 Vassals ✅ RAN July 15 — target MET; see the Sweep 4 section above.) Then the program exit sweep + 8.EVAL.

---

### 🏰 VASSAL DEEPENING — VS-R AUTHORITY ↔ LOYALTY COUPLING ✅ BUILT July 14, 2026 — `docs/VASSAL_DEEPENING_SPEC.md` §2 (landing record §2.7)

**User direction: "code the recommendations from the vassal spec commit and push — leave anything that touched the diplo screen for next session."** Built **VS-R** (backend-only — the memo's recommendation on all six §2.6 open questions, at the §2.5 default numbers). **VS-3 land grants DEFERRED to next session** because that slice routes through the **F1 Diplomacy Wizard** (a diplo-screen surface). Suite **13,219/3**, ruff clean, **no `.gd` touched**; a 5-lens adversarial review returned **zero confirmed findings**.

- **The derived signal — `get_imperial_grip` (new, `backend/models/authority.py`, "one grip = one module"):** blends the lord's court standing (the player's `authority_tracker`; a flat **75** baseline for enemies — jealousy-proxy parity) with a territorial-collapse term (capital lost −40 / homeland-minority −25, **mutually exclusive**; worst active war_score < −50 → −15, < −30 → −8). **The crux fix:** the raw `authority_tracker` does NOT fall when Paris / the homeland / the war is lost — the derived grip does, so the *player's* collapse is finally legible. Keys off the lord ⇒ symmetric for enemy lords for free (GR5). Boot: player full-empire → **100** (dormant); enemy intact → 75; enemy floor **20** (never sub-15). **Zero new serialized fields** (pure derived read).
- **The banded coupling (`process_vassal_loyalty` step 7, per-lord memoized GR8):** grip ≥ 30 → **0** (byte-identical — `_contribute` skips zero); grip < 30 → **−2**/turn, additive to autonomy drift, capped at −4, **never a multiplier**. Negative-only, spiral-band only, keys off the LORD's grip (not vassal loyalty). The optional sub-15 **−4 floor (memo §Q4) is HELD** for post-playtest tuning (owner: spec §2.6-Q4).
- **"No cheap recovery" (`get_authority_lever_multiplier`):** **1.0** at healthy grip (byte-identical) / **0.40** in the <30 band — blunts ONLY the cheap one-shots (invest +10→+4, autonomy-up +10→+4; **full cost still paid**). **The per-turn subsidy is left full-strength** (a *large* subsidy stays existential; §2.6-Q2); VS-3 land grant / full release / autonomy-DOWN are never softened.
- **Enemy courting scales with player weakness (`attempt_vassal_courting`):** the loyalty<50 unlock **widens** (→ <65 at grip 0) and each success **bites harder** (×1.0 → ×1.5) as the player's grip falls — the Treaty-of-Ried dynamic. **0/×1.0 at healthy grip** (byte-identical). Bounded by the existing cooldown + one-per-turn cap.
- **Legibility:** a spiral-band `recovery_hint` variant names the levers that still work ("Grant autonomy, pay a large subsidy, release them, or win a decisive battle"); the healthy-band "Invest, garrison, autonomy" hint is byte-preserved. The grip term names itself ("the Emperor's faltering grip") in the drift event. (Land grant joins the spiral copy when VS-3 lands.)
- **One-way (memo Q4):** VS-R is **read-only** on authority — never writes it back, so jealousy co-fires (two casualties of one cause) without a brakeless loop; recovery flows through **winning** (grip rises → coupling relaxes; the Saxony-after-Lützen property). Reversible / latch-free.
- **Layering (recorded deviation from §Q5):** relocated ONLY the two shared breakpoints (`AUTHORITY_SUPPRESS_ABOVE`/`ACCELERATE_BELOW`) to `authority.py` (jealousy re-imports; `J.get_authority_proxy`/`J.AUTHORITY_*` pins stay green). `get_authority_proxy`/`is_capital_threatened` **stay in `jealousy.py`** (jealousy-internal, VS-R never reads them). No circular import (authority.py stays a leaf; the diplomacy war-score import is function-local).
- **Coalition-defection ("The Defection") NOT built (§Q7):** v1 = grip-accelerated *independent* rebellion (reuses `check_vassal_rebellion` unchanged). Coalition-join is a separately-gated GR9 follow-on (spec §2.7).
- **Tests:** `test_vassal_authority_coupling.py` (**42**) — banded curve, grip math + edge cases, boot-dormancy/byte-identical pins, lever blunting (invest/autonomy-up only; subsidy/release/autonomy-down unsoftened), courting-scales-with-weakness, one-way/no-writeback, no-new-fields, recoverability (winning arrests the spiral; full-3-satellite collapse ≥ 8 turns), GR5 enemy-lord symmetry. All prior vassal/jealousy pins (`test_vassal_recovery_lever`, `test_session5_diplomacy::TestLoyaltyTicks`, `test_jealousy_v32`) green.
- **▶ NEXT (next session): VS-3 land grants — the F1 diplomacy-wizard slice** (spec §1, buildable after a bless). The Combat Overhaul **Sweep 4** remains queued independently.

---

### 🏰 VASSAL DEEPENING SPEC — July 14, 2026 (VS-R research → **now BUILT**, see above; VS-3 deferred) — `docs/VASSAL_DEEPENING_SPEC.md`

**User direction (this session): "add the next phase of spec the ability to give land to vassals, this should fit into our diplo wizard! but have next session research also tying authority to their loyalty — meaning if Napoleon spirals he may lose them without huge concessions."** Authored `docs/VASSAL_DEEPENING_SPEC.md` (design only — **no code**):
- **VS-3 — Land Grants to Vassals (via the F1 Diplomacy Wizard)** — spec-complete, buildable after a bless. New `grant_region_to_vassal` action: cede a lord-controlled province to a vassal → `region.controller = vassal` (reuses the `settlement_ratify.py:267` transfer seam), **worth-scaled loyalty** bonus (rich province binds harder), the lord **forfeits the income** while the vassal **tributes it** at its autonomy rate (the historical point — Napoleon enlarged Bavaria/Saxony/Württemberg with conquered land). Rides the wizard's existing Vassals category + war_id sub-picker pattern for a province picker; GR5 AI parity (same executor + an enemy_ai rescue rung); cooldown + reclaim-on-rebellion anti-abuse. Numbers escalate to the gate.
- **VS-R — Authority ↔ Vassal-Loyalty Coupling — ✅ RESEARCH COMPLETE July 14, 2026** — memo [`docs/audits/VASSAL_AUTHORITY_COUPLING_RESEARCH_2026_07_14.md`](audits/VASSAL_AUTHORITY_COUPLING_RESEARCH_2026_07_14.md) (9-agent adversarially-verified: history / authority-code / vassal-code / jealousy-coherence; historical timeline independently fact-checked). Spec §2 is now **gate-ready** with recommended numbers. **Headline verdict: it WOULD play like Napoleon losing his vassals IRL on every axis but one.** Key findings the gate must know: **(1)** the raw `authority_tracker` does **NOT** spiral on military collapse (its only military movers are ±5 nudges gated on *outnumbering*; a capital lost to an enemy garrison assault docks **zero**) and `nation_authority[player]` is **inert dead code** → recommend a new derived **`get_imperial_grip`** blending the tracker's court component with the jealousy proxy's territorial-collapse term (symmetric for AI lords for free, GR5); **(2)** the draft's `≥70 → +1` band **must become `0`** — it's a hard boot-dormancy pin against ~10 test files; coupling is **negative-only, spiral-band only**, anchored on jealousy's **70/30** lines; **(3)** "no cheap recovery" = a 0.40 lever multiplier on invest/autonomy-up only (VS-3/release/winning never softened — **winning battles is the strongest arrestor**, Saxony-after-Lützen); **(4)** **one-way** (authority→loyalty) — a two-way loop opens the first brakeless authority sink; **(5)** jealousy co-fires but VS-R stays **ACTIVE during capital-threat** (opposite polarity — the de-compounding lever); **(6)** **zero new serialized fields** for v1, boot-dormant at authority 100; **(7)** the one unfaithful element — real satellites **switched sides / joined the coalition**, the game only models *independent rebellion* → v1 ships grip-accelerated independent rebellion, **"The Defection" (coalition-join) homed as a separate GR9 slice**. → **user gate** decides spec §2.6 + sets §2.5 numbers **before any code**.
- **Open questions for the gate (spec §3):** VS-3 — sequencing (standalone after Sweep 4 vs. hold for program exit), contiguity, `granted_regions` provenance, region-worth floor, numbers. VS-R — the six §2.6 decisions (signal choice, subsidy softening, coalition-defection now/later, optional −4 floor, layering relocation, copy bless), memo recommends each.
- **▶ This does NOT change the Combat Overhaul queue** — ~~Sweep 4 is the immediate next step~~ (✅ Sweep 4 RAN July 15, Vassals target MET — see the Sweep 4 section at top); Vassal Deepening (VS-3 land grants) is queued after the program or interleaved at the user's call.

---

### ⚔️ COMBAT OVERHAUL — PHASE 5 (Vassals) ✅ COMPLETE (Half A July 14 + Sweep 4 July 15, 2026) — `docs/COMBAT_OVERHAUL_SPEC.md` §4 Phase 5 — ✅ **Sweep 4: Vassals 6.0→6.5 target MET**

**User direction: "run next step of fixes commit and push."** The next queued step was Combat Overhaul Phase 5 (Vassals). Backend-only; suite **13,177/3**, ruff clean, no `.gd` touched.

- **VS-1 loyalty recovery lever + teach it** — the passive satellite bleed (-2/turn) was HIDDEN behind an `abs(delta) ≥ 3` event gate until loyalty crossed 20, so the player never saw a healthy-band vassal slipping nor learned how to arrest it. Fix (`vassal.py`): (1) gate lowered `≥ 3 → ≥ 2` so the steady drift surfaces every turn; (2) a **recovery hint** ("Invest, garrison their capital, or grant autonomy to steady them.") rides the `vassal_loyalty` event — new `recovery_hint` field, folded into the dispatch `message` — whenever a vassal is falling while still in the healthy band (`delta < 0 and new_loyalty ≥ 40`); (3) Talleyrand's `< 35` dispatch advisory (`dispatch.py`) now names the same three levers. The arresting actions already existed (invest +10, garrison +5..8, grant-autonomy flips drift to +1) — VS-1 makes them *visible and taught*. **Exit met: a falling vassal can be arrested by a surfaced action, on the turn the slide first shows.**
- **VS-2 dead-code cleanup** — the "war weariness" contribution called `get_coalition_loyalty_penalty(vassal)`, which is always 0 for a lord's own satellite (never a coalition member AGAINST its lord) — genuinely dead. **Deleted**; loyalty drift is now independent of coalition state (coalition membership is a diplomatic-acceptance concept, not a loyalty one). The prior `test_deep_audit_session2.py::TestFix17...` pin, which had asserted the penalty applied, was flipped to assert the removal.
- **Tests:** new `test_vassal_recovery_lever.py` (9 — event gate, hint present/absent by band & direction, VS-2 removal, invest & autonomy arrest the fall); Fix17 re-blessed.
- **✅ Sweep 4 (Half B) RAN July 15, 2026** — Vassals 6.0→**6.5 (target MET)**, UX 6.5→7.0, ten pillars held, **0 regressions**; `docs/audits/SWEEP_4_2026_07_15.md`. See the Sweep 4 section at the top.

---

### 💰 ECONOMY PLAYTHROUGH + EC-U1 REVERSAL — July 14, 2026 (later session)

**User direction: "economy got re-sweeped, do a full play again testing economy" → then "you should pay for how many soldiers you have, update economy so it's balanced based on findings, commit and push."**

- **Live 8-turn economy-focused playthrough (anthropic mode) — the Sweep-3 mechanics all verified working:** EC-U3 Grande Armée surcharge (boot absorption 55.5% ✓), EC-U2 infrastructure sink (built a depot → −40g/turn "Infrastructure" line ✓), Intendance MC-2b (Davout's −15% recruit cost, labeled ✓), admin_bonus (unused AP → gold ✓), ledger reconciles to the gold every turn ✓. The economy now has real teeth: net fell +2107 → +845 as France lost ~750g of income regions, then **stabilized positive** (no death spiral). Investigated a scare — France silently lost 6 interior provinces to Britain — and proved it **working-as-designed** (the AI's 4-action economy lets an unopposed army chain-capture undefended regions; I'd marched all 7 marshals east, stripping the interior). Zero true bugs; a standalone repro (`scratchpad/repro2.py`) confirmed no ghost flips.
- **⏪ EC-U1 REVERSED (this session's change):** the playthrough flagged the establishment high-water-mark as a permanent tax with no demobilization relief, and the ledger's army total showed the phantom peak, not the men in the field. Per the user's steer, upkeep now bills on **ACTUAL fielded strength** — `(marshal.strength // 1000) × rate`. Removed `Marshal.establishment`, `get_upkeep_strength()`, and `_reconcile_establishments()` entirely; the over-limit + Grande Armée surcharges and the ledger army total now key off the live fielded total (a shrinking army sheds its surcharge; the display shows real strength). **Boot is byte-identical** (billed == strength at turn 1), so the E1 band, ES-3, and EC-U3 numbers are untouched — attrition simply now lowers the bill. Old save with a stale `establishment` key still loads (ignored). Docs updated (COMBAT_OVERHAUL_SPEC EC-U1 marked REVERSED with history preserved, SAVE_FORMAT field removed, CLAUDE.md Phase-4 banner). **Test:** `test_economy_upkeep_fielded_strength.py` replaces `test_economy_upkeep_not_regressive.py`; suite 13,168/3, ruff clean; committed + pushed at `1af60e7`.
- **▶ NEXT: Combat Overhaul Phase 5 (Vassals)** — ✅ **Half A LANDED July 14, 2026 (this session's next-step)**: VS-1 + VS-2 in; see the Phase 5 entry at the top. Next = Sweep 4. (Optional follow-up from this playthrough: a loud "your homeland is being overrun" dispatch/notification when an undefended interior is being eaten — legibility gap, not a bug; unfiled.)

---

### ⚔️ COMBAT OVERHAUL — PHASE 4 (Economy) ✅ COMPLETE July 14, 2026 (Economy 5.0 → **6.5**, target MET) — `docs/COMBAT_OVERHAUL_SPEC.md` §4 Phase 4 — ▶ **Phase 5 (Vassals) NEXT**

**User direction: "code and commit phase 4 of fixes be thorough look at economy of the era" → then "commit push then do sweep."** Both slices in, grounded in the period's fiscal reality (the state maintained corps at establishment and paid to garrison its fortress/depot network); backend + one `.gd`; suite **13,167/3**, ruff clean, Godot parse-clean.

- **✅ Sweep 3 (Half B) RAN — `docs/audits/SWEEP_3_2026_07_14.md`** (12-component LLM review, 13 agents / ~1.18M tokens; live evidence `SWEEP_3_LIVE_EVIDENCE_2026_07_14.md`). **Economy 5.0 → 6.0 (+1.0), ZERO regressions, 11 pillars held.** The "losing pays" bug is reproduced-and-closed (engine probe: −85k men → net flat +1652 WITH the fix vs +2584 WITHOUT) and the first conquest-free sink is live and transparent — but **Economy is 0.5 SHORT of the ≥6.5 target**: the loose-gold surplus is structural (homeland income ~+3,400 ≫ upkeep ~+1,748), which the two scoped levers can't force to scarcity. **Refinement `2ce1f1d`:** Sweep 3 caught EC-U1's turn-1 window and seeded the boot peak in `from_scenario` (boot-safe).
- **✅ EC-U3 Grande Armée surcharge `9d57597`** (the user-steered gated upkeep-baseline revisit — "revisit, let's get the score higher"): a premium rate (`GRANDE_ARMEE_RATE=18` above the absolute `GRANDE_ARMEE_THRESHOLD=140000`) modelling a supermassive standing army's diseconomies of scale. At boot it touches **ONLY France** (189k; next largest Prussia 78k), so Austria's binding +18 and every other nation are byte-unchanged — the one lever that bites the hegemon without breaking the E1 boot band. Lifts France's turn-1 stacked absorption **36.9% → 55.5%** (into the EC-2 aspirational 55–70% band that rate-8 alone couldn't reach), cuts the homeland surplus **−29%** (net 2989→2107; idle 7-turn banking 21,723→15,549), and makes a fully-doubled 378k army the edge of sustainability with **no death-spiral**. Ledger + turn-summary split the surcharge into over-limit + Grande Armée (`.gd` Godot parse-clean); E1 + ES-3 tests re-blessed to the measured values. **Re-score (2-agent adversarial — Economy reviewer + full-surface regression hunter): Economy 6.0 → 6.5, target MET, ZERO regressions** across six empirical checks (boot solvency, GR5 symmetry/non-farmable, ledger reconciliation exact even under bankruptcy halving, doubled-army sustainability, re-blessed-test honesty, no serialization/Godot/scale break). **Phase 4 COMPLETE; all four Combat-Overhaul phases met their Half-B targets with zero program regressions. Overall directional ~6.9–7.0.**

- **EC-U1 non-regressive upkeep** — the review's "losing pays" bug: upkeep was `(strength // 1000) × rate`, purely proportional to SURVIVING strength, so grinding a corps down LOWERED its bill while region income held → net ROSE while losing. Fix = bill on the corps' **establishment**, a per-turn high-water-mark of strength (new serialized `Marshal.establishment`, reconciled in `WorldState._reconcile_establishments`; `marshal.get_upkeep_strength()` = `max(strength, establishment)`, single source). Europe-only (N1 legacy keeps strength-proportional). **Establishment is 0 until the first reconcile**, so a fresh / directly-set marshal bills on current strength — every pre-existing direct-call upkeep test AND the E1 boot band (Austria +18) are byte-unchanged; the fix only bites after a turn of play. Era: losses obliged paid replacements (recruit gold), never a rebate. Ledger stays transparent (`billed_strength` per marshal).
- **EC-U2 conquest-free gold sink** — every recurring sink was conquest-gated, so a homeland-only France banked its surplus (treasury 800→17,623 over 6 turns in the Sweep-2 run). Fix = **infrastructure upkeep**: `EUROPE_INFRASTRUCTURE_UPKEEP = 40` g/turn per built structure (depots, forts, training grounds, markets, stables, active/damaged watchtowers), riding the existing per-region income loop (GR8, no new scan), bankruptcy-mercy halved like occupation, its own signed **"Infrastructure"** Net component (threaded through `process_income_phase`, `ledger.py`, `meta_executor`, `dispatch`, `strategic_ledger.gd`, and the `NET_GOLD_COMPONENTS` guard). **Boot-safe**: the 1805 scenario authors no buildings → 0 at turn 1 for every nation, so it cannot break the boot-solvency band (that ruled out ally-subsidy / army-size recurring drains, which would hit Austria +18 at boot). Symmetric player/AI (GR5). A homeland-only France now decides whether to invest surplus in infrastructure and carry the bill, or hoard.
- **Regression:** new `test_economy_upkeep_not_regressive.py` (13, incl. a falsifiable counterfactual that the bug reproduces with the fix removed) + `test_economy_sink_reachable.py` (10); `NET_GOLD_COMPONENTS` extended; serialization/save-load/ledger/dispatch/foundations/AI-economy/ES-2/ES-7/E1-band + combat-sweep M1–M7 all green.
- **▶ NEXT: Phase 5 (Vassals)** — VS-1 surface a loyalty-recovery lever in the healthy 100→40 band + VS-2 wire-or-delete the dead "war weariness" term, then Sweep 4.

---

### ⚔️ COMBAT OVERHAUL — PHASE 3 (Un-starve Marshal Drama — break the triple lock) ✅ COMPLETE July 14, 2026 (Half A + Half B) — `docs/COMBAT_OVERHAUL_SPEC.md` §4 Phase 3 — ✅ **Phase 4 Half-A landed**

**User direction: "Next in the program is Phase 3 — un-starve Marshal Drama (break the triple lock; target M7 ≤ 8)... commit and push."** All three verified locks broken in `jealousy.py` (in-band tunable single sources); **M7 flipped `never → turn 1`**, M1–M6 held.

- **DR-1 glory from attrition/occupation** — new `STALEMATE_GLORY = 1`: an **inconclusive** battle (no decisive victor) where one side **out-bleeds the other ≥2:1** — new `_out_bled(own, enemy)` predicate; a flawless exchange counts — **or takes a province** now scores partial glory for the dominant commander. **Symmetric player/enemy (GR5).** A hard-fought grind feeds the ladder before a clean rout. Clean-win `_victory_points` unchanged (regression-pinned `test_decisive_win_still_uses_victory_points`).
- **DR-2 slow glory decay** — `GLORY_WINDOW 5 → 8` (the sole decay lever), so occasional deeds accrete into a ladder gap instead of evaporating at turn 6.
- **DR-3 authority-dampening rework** — chose **"exempt the first rung"**: the `authority > 70 ⇒ +1 threshold` calm now applies only to **rung ≥ 2 (neutral/friendly professionals)**; a marshal who already resents the celebrated man (Rival −1 / Hostile −2, relationship-base threshold 1) keeps his hair-trigger edge even at the height of empire. Keyed on the *relationship* base (before idle acceleration), so an idle-accelerated professional is still calmed while winning. `authority < 30` death-spiral acceleration untouched (pinned). The existing rung-2 professional-dampening test is unchanged-green.
- **M7 harness re-framed (honest flip):** the Phase-0 `measure_m7` scenario modeled a *losing* 1:1 assault (the attacker out-BLED every turn — zero glory is correct for losing), which never reproduced the triple lock the spec describes (a player *winning* the attrition earning no glory). Phase 3 re-frames it to the review's **winnable ~3:1 massed assault** into a dug-in defender — the attacker out-damages but the fort resists a clean rout — dormant under baseline jealousy constants, lively under Phase 3. Documented in the test docstring.
- **Regression:** suite **13,146/3**, ruff clean, no `.gd` touched. New tests: `test_drama_glory_from_attrition.py` (15) + `test_drama_ladder_liveness.py` (10); the 106 existing `test_jealousy_v32.py` tests unchanged-green. **Drive-by:** seeded the pre-existing pytest-randomly-flaky `test_deep_audit_session1.py::test_war_score_accumulates_across_battles` (a rout-flee → pending-capture-choice popup blocked the 2nd battle; Phase 1-2 decisiveness widened the flake — test-only, no product change).
- **✅ Sweep 2 (Half B) RAN July 14, 2026** — `docs/audits/SWEEP_2_2026_07_14.md`: the 12-component LLM review (13 agents / ~1.43M tokens) on a fresh 6-turn `LLM_MODE=anthropic` France/1805 playthrough (`docs/audits/SWEEP_2_LIVE_EVIDENCE_2026_07_14.md`). **Marshal Drama 6.0 → 7.5 (met, +1.5)**; Narration 7.5→8.0, Marshal System 7.0→7.5, Architecture 7.5→8.0 (+0.5 each); 8 pillars held, **0 regressions**; overall ≈7.15–7.25. **An organic petition fired FOUR times across three kinds + the Fontainebleau collective beat** (M7 in the wild = turn 2); DR-1/DR-2/DR-3 confirmed live; Jealousy↔ES-7 rente economy interlocked. Two WAD evidence gaps for a differently-driven session (no autonomous glory-attack executed; crown never lit on a top tie) — not defects. **Phase 3 EXITS; Combat Overhaul Phases 0–3 COMPLETE.**
- **▶ NEXT: Phase 4 (Economy)** — EC-U1 non-regressive upkeep + EC-U2 a conquest-free gold sink (the live run reconfirmed the loose-gold problem: treasury 800→17,623 over 6 turns despite ~1,900g/turn of conceded rentes). Then Sweep 3.

---

### ⚔️ COMBAT OVERHAUL — PHASE 2 (Decisiveness, regen cap, legibility, Iron Resolve) LANDED July 13, 2026 — `docs/COMBAT_OVERHAUL_SPEC.md` §4 Phase 2 — ✅ **Phase 3 Half-A landed**

**Counter-pressure & decisiveness.** All four Phase-2 slices landed; **Sweep 1** Half-A (`docs/audits/SWEEP_1_2026_07_13.md`) flipped M2/M3/M5 to target with M6 held.

- **CO-3 decisiveness → capture** — new single-source helper `combat.decisiveness_morale_penalty(loser_casualties, winner_casualties)`: extra morale loss for the side losing a lopsided casualty EXCHANGE (out-bled ÷ other, keyed on the RATIO not absolute size — an equal-strength defender who trades evenly is untouched, M6). Wired into BOTH morale paths (immediate `resolve_battle` + deferred coordinated `_calculate_casualties`) on the out-bled side of every decisive/tactical outcome; symmetric (GR5). `defender_bonus` stays 0.2 flat. Blessed (sweep-tuned): pivot 1.75 / slope 22 / cap 55. → **M2 `0.61 @2:1 / 1.00 @3:1`**.
- **CO-4 cap regeneration (SYMMETRIC)** — `economy_executor.AI_CORPS_REGEN_CAP = 3000` + `region_has_friendly_supply(region)` (capital or supply_depot exempt). ANY corps reinforcing in the field recruits a capped levy — ONE rule in the shared `_execute_recruit` keyed on the recruit region's supply, identical for player and enemy (GR5; the enemy AI needs no special wiring). Applies to troop `recruit` only — commissioning a NEW marshal (`_execute_recruit_marshal`, "The Marshalate") is a separate executor and untouched (new marshals still hire at the capital). Caps troops (manpower/morale follow); gold stays batch price (throughput cap, not price penalty); an explicit `reinforcement_cap` may only lower further. Harness knob mirrors the constant (`test_regen_cap_matches_production`). → **M3 `−2749`** (cas 5749 vs capped regen 3000). *(User-directed symmetry pass, July 13 — the initial land was enemy-only; GR5 favoured one region-keyed rule.)*
- **CO-6 reinforcement legibility** — coordinated battles print `Massed effective strength: <lead> (lead) + <committed> committed (<names>) = <total>.` (a rival reinforcer, CO-1b ×0.0, correctly prints no line).
- **CO-7 Iron Resolve stance** — releasing the coil exempts the fortify-mandated ×0.90 defensive-stance attack penalty in `get_attack_modifier` (personality mods untouched; read-only when `consume=False`). The 3-stack release lands full +24%. → **M5 `+0.24`**.
- **Regression:** suite **13,121/3**, ruff clean, no `.gd` touched. Tests: `test_combat_overhaul_phase2.py` (20) + flipped M2/M3/M5 harness assertions; 3 MC-band fixtures re-tuned for the deeper decisiveness hit (Charles solo 40→48 / coordinated 40→72; enemy Charles 40→48; the artillery-reinforcer scenario Wellington 50k→42k so the assault still fails but the gun holds).
- **Sweep 1 Half B RAN** (July 13, 2026 — 12-component LLM review, 13 agents/~1.1M tokens, grounded in code + Half-A deltas + a live probe): **Combat 5.0→7.5 (+2.5, met)**, Narration 7.0→7.5, Marshal System 6.5→7.0, Architecture 7.0→7.5 (all +0.5); 8 held, **0 regressions** (Enemy AI held 8.0 — the symmetric cap is not farmable, R2 cleared). Overall directional ≈6.9–7.0 (short of 7.3 *by design* — later phases own the flat pillars). Recorded in `docs/audits/SWEEP_1_2026_07_13.md` §Half B.
- **▶ NEXT: Phase 3** — un-starve Marshal Drama (break the verified triple lock: DR-1 glory-from-attrition/occupation, DR-2 slow glory decay `GLORY_WINDOW` 5→8, DR-3 authority-dampening rework; target **M7 ≤ 8**). Then **Sweep 2**.

---

### ⚔️ COMBAT OVERHAUL — PHASE 1 (Combat core: additive strength) LANDED July 13, 2026 — `docs/COMBAT_OVERHAUL_SPEC.md` §4 Phase 1

**The keystone slice.** CO-1 additive committed strength + CO-1b personality/relationship scaling + CO-2 odds band + CO-5 single-source survivor count. **Sweep 1a** (`docs/audits/SWEEP_1a_2026_07_13.md`, Half A only per §2.3): α tuned to `COMMITTED_ALPHA = 0.6` (single source `combat_executor.CombatExecutor.COMMITTED_ALPHA`, harness-guarded).

- **CO-1/CO-1b** — `resolve_battle` gains `committed_attacker`/`committed_defender` (default 0.0 → every solo battle byte-identical); `_calculate_effective_strength` adds the already-effective committed mass. `_committed_reinforcement_strength` scores each reinforcer `α · strength · effectiveness · get_attack_modifier(consume=False) · rel_factor` (MC-3 ×0.0…×1.5, Jealousy-v3.2 withholding). New `consume=False` read path on `Marshal.get_attack_modifier` (GR1 — no one-time bonus spent scoring a reinforcer). Symmetric both sides (GR5).
- **CO-2** — muster odds band folds the WILL-JOIN committed strength (`inferred_attack_effective_ratio(committed_attacker=…)`); CR-5 gate's lead-only read untouched.
- **CO-5** — `_reconcile_report_survivors` single-sources the post-battle strength so the report's `casualty_summary` and the event agree (the two-truths bug).
- **Metrics FLIPPED:** M1 flat→`0.82` @5 corps (monotonic), M1b `0/0/0`→`41400/36000/0`, M4 `0%`→`100%`; **M6 GUARD held** `0.000`; M2/M3/M5/M7 correctly unchanged (Phase 2/3). Suite **13,100/3**, ruff clean, no `.gd` touched. Tests: `test_combat_overhaul_co1_additive.py` (11) + `..._co5_report_consistency.py` (4); 5 fixtures re-tuned (all confirmed intended — each passes with α=0.0).
- **▶ NEXT: Phase 2** — CO-3 decisiveness→capture (M2), CO-4 enemy regen cap (M3), CO-6 reinforcement legibility, CO-7 Iron Resolve stance (M5). Then **Sweep 1** (Half A + first Half-B LLM review).

### ⚔️ COMBAT OVERHAUL — PHASE 0 (Baseline & Harness) LANDED July 13, 2026 — `docs/COMBAT_OVERHAUL_SPEC.md` §4 Phase 0

**User direction: "do next phase the fixes from playtest, code, commit and push initial phase of this."** Phase 0 of the Combat Overhaul & Score-Raising Program — the measurement foundation the whole build-and-measure program is judged against. **No balance change; pure measurement.**

- **The Sweep harness (`tests/test_combat_sweep_metrics.py`, P0-1)** — a deterministic Monte-Carlo (400 fixed seeds; `random.seed` before every `resolve_battle`) over the REAL combat resolution (`combat.py`), the REAL report/distribution seam (`battle_report.generate_battle_report` + `combat_executor._distribute_casualties`), and the REAL jealousy engine (`jealousy.process_turn` / `record_battle_glory`). Measures M1–M7, prints a scoreboard, and **asserts the current BASELINE** so each later slice must consciously flip its paired assertion. 9 tests green.
- **Sweep 0 baselines (P0-2, `docs/audits/SWEEP_0_2026_07_13.md`)** — every Field-Review keystone is now a falsifiable metric: **M1** `0.000×5` (concentration inert) · **M1b** `0/0/0` (no personality expression in mass) · **M2** `0.000/0.000` (defenders near-unbreakable) · **M3** `+4251` net (the defender GAINS ground under sustained 2:1 — frontal attrition unwinnable) · **M4** `0.0%` (survivor two-truths bug) · **M5** `+0.116` (Iron Resolve stance-trapped) · **M6** `0.000` (defender edge intact — the anti-over-nerf GUARD that must hold every phase) · **M7** `never` (drama dormant — the triple lock). **Half B** = the same-day ⚔️ Field Review scoreboard (the fresh live evidence Sweep 0 anchors to; §2.2 re-runs Half B from Sweep 1).
- **Two modelled knobs** are the only forward-looking constants (both at baseline in the harness, read by the metrics): `COMMITTED_ALPHA = 0.0` (CO-1/Phase 1 flips M1/M1b) and `AI_CORPS_REGEN_PER_TURN = 10000` (CO-4/Phase 2 flips M3). Everything else is measured from real resolution.
- **▶ NEXT: Phase 1** — CO-1 additive committed strength + CO-1b personality/relationship scaling + CO-2 odds band + CO-5 single-source survivor count. Set the tuned α, flip the M1/M1b/M4 assertions, run Sweep 1a (Half A).

### ⚔️ FIELD REVIEW + COMBAT OVERHAUL SPEC — LANDED July 13, 2026 — `docs/COMBAT_OVERHAUL_SPEC.md`

**User direction: "play the game, use all elements, review every component with scores" → then "make this a spec so we can run sweeps to raise problematic scores and improve combat as a whole ... include all fixes ... reinforcement still uses personalities ... do the econ fix ... include the parser and other issues found during play ... phase it for new sessions ... discover why jealousy was dormant."** A 7-turn live 1805 France playthrough (`LLM_MODE=anthropic`, vs the Third Coalition) + a 25-agent adversarially-verified component code audit produced the ⚔️ Field Review (overall **6.4/10**) and this build-and-measure spec.

- **Keystone finding:** combat is load-bearing. Non-additive reinforcement (`combat.py:_calculate_effective_strength` uses the LEAD marshal only) + flat defender dominance + **the AI out-regenerating the player** (Mack reinforced +10k in one turn vs ~5k of damage) make frontal attrition **unwinnable** — which starves Marshal Drama (glory 0 all game), Economy (conquest-gated sinks read 0; treasury 800→15,058 unspent), and Vassals (loyalty needs wins).
- **Why Jealousy was DORMANT = a verified TRIPLE LOCK** (spec §3.2): (1) a stalemate awards **0 glory to everyone** (`jealousy.py:154`), (2) `GLORY_WINDOW = 5` decays the occasional point before it accretes, (3) `authority > 70` adds **+1 to every jealousy threshold** while the player **boots at authority 100** (`jealousy.py:381`). Phase 3 breaks all three.
- Spec is **phased 0–6 for fresh sessions**; **reinforcement stays personality- & relationship-scaled** (CO-1b + metric M1b — an aggressive reinforcer pushes harder than a cautious one; a resentful one contributes ≈0); the **econ fix** is Phase 4; **the parser + every live-found play-friction bug** is Phase 6 (PF-1…PF-9 + AI-1). Balance numbers are **sweep-tuned**, not separately gated, via a new deterministic combat-metric suite (M1–M7). Committed docs-only at `15fa202` (suite 13,075/3, ruff clean).
- ~~**▶ NEXT: Phase 0**~~ ✅ **LANDED July 13, 2026** — the sweep harness + Sweep 0 baselines (see the Phase 0 section above). **Next = Phase 1** (CO-1 additive personality-scaled reinforcement + CO-5 survivor-count bug).

### ✅ ARTILLERY ARM — filling the gap LANDED July 13, 2026 — `docs/ARTILLERY_GAP_SPEC.md`

**User direction: "all nations and bench, artillery more scarce, majors have more available; check that recruiting a marshal requires manpower; make the starting state favor France a bit and realistic; commit and push."** The artillery arm was unreachable in 1805 (0 marshals carried it; the commission factory read only `cavalry`; every nation's authored artillery manpower pool sat stranded) — this makes it reachable, scarce, and France-first.

- **Arm-aware manpower commission** (the "check required manpower" ask). `recruitment.candidate_arm`/`corps_requirement` route a commission to its ARM pool: infantry→infantry (5,000), cavalry→**cavalry** pool (5,000 — fixes the pre-existing cavalry-from-infantry draw), artillery→**artillery** pool (`RECRUIT_ARTILLERY_CORPS=3000`). `check_commission` gates on that pool + `commission_marshal` draws from it; payload carries `arm`/`artillery`/per-arm `pools`; validator gained an `artillery` bool + cavalry/artillery mutual-exclusivity.
- **A gunner on every commissioning bench:** France **Marmont** (reflagged — the "artillery savant" bio is now true) **+ Senarmont**; Austria **Smola**; Russia **Kutaisov**; Prussia **Holtzendorff**; Britain **Shrapnel**. Named historical artillerists, artillery-weighted skills (high tactical / low shock).
- **Scarcity = the authored pools** (France 10k, majors 5–6k, minors 500–2k) × a 3,000 battery → majors raise guns readily, thin pools shut a battery out. No new mechanic.
- **France favoured (realistic):** fields artillery **first** (10k pool, 2× any major), **most** (two gunners), **cheapest** (4,500 vs 5,000–5,500).
- **Two conscious divergences (spec Landing note):** (1) "all nations" = the 5 bench powers (the 15 minors have no bench — historically right + a separate expansion); (2) France's edge is on the **bench**, not an active starting battery, to avoid rewriting the **blessed ES-3 turn-1 upkeep anchor** (236g→252g) as a side effect — offered as a one-line follow-up.
- Tests: `tests/test_artillery_arm.py` (14) + `test_marshal_recruitment.py` extended; the MC-2 skill-balance frame left intact (Senarmont is outside it by design). Suite **13,075 passed / 3 skipped**, ruff clean. No `.gd` touched (the Commission card can show the arm from the new payload fields — GR9-homed follow-up).

### ✅ DEF-1 ROSTER VOICES — the loyalist register class + 15 bespoke Europe-court voices LANDED July 13, 2026

**User direction: "do roster voices ... full bespoke pass."** Display-only (GR6): diplomat copy banks + the Voice Bible; no executor/serialization/balance change. No `.gd` touched.

- **The `loyalist` register class** — the gap the Voice Bible flagged but never filled (Hawk/Schemer/Dove only). Authored in `DIPLOMAT_VOICE_BIBLE.md` (§Loyalist register — *the dutiful servant of the Crown*: duty not fear, service not scheming; the boundary lines vs. Dove and Schemer are explicit) + wired via a `("loyalist", reason)` bank in `diplomatic_templates._INCOMING_MOTIVE_LINES`. The 6 client courts (Spain/Cevallos, Sweden/Ehrenheim, Denmark/Bernstorff, Sardinia, Holland/Schimmelpenninck, KingdomOfItaly/Marescalchi) no longer collapse to bare chancery. The W6-10 pinned test flipped from loyalist→chancery to the new register.
- **15 bespoke incoming-proposal voices** — a distinct in-register voice per Europe court (2 schemer, 7 dove, 6 loyalist), authored by a **30-agent author→adversarial-verify workflow** and integrated **programmatically** from the JSON (60 `_NAMED_MOTIVE_LINES` blocks + 15 `_NAMED_ATTRIBUTIONS`, zero transcription drift). Each line verified against the Bible's "could this be mistaken for another diplomat?" rule (Czartoryski de-collided from Metternich's balance-talk; Reis Efendi off Hardenberg's wounded-honor; Ehrenheim kept dutiful not frightened). All **240** court×reason×type combos resolve to the bespoke voice, **0** to chancery.
- **Slice C reconciliation:** `reactive_summon` GR9-closed (no engine trigger exists); **WB-D confirmed landed as the live `commitments_notice_*` family** (Voice Bible table corrected, legacy identifiers retired as aliases); per-court `commitments_notice`/Talleyrand-commentary **depth homed** as an owned follow-on ("Roster Voices — Depth") with a landing trigger + completion test — working fallbacks today (chancery / `('_default', situation)`), so no court is voiceless.
- **Also fixed:** Mortier's false *"The only marshal without an enemy in the army"* bio → *"one of the few…"* (Masséna `{Soult:+1}`, Suchet `{Lannes:+1}`, Marmont `{}` also start rivalry-free).
- Tests: `tests/test_w6_incoming_voice.py` +2 (loyalist bank shape + all-15-courts coverage). Full suite **13,061 passed / 3 skipped**. Ruff clean.
- **▶ NEXT: the artillery gap** — spec written (`docs/ARTILLERY_GAP_SPEC.md`): the artillery arm is unreachable in the 1805 campaign (0 marshals carry it, the commission factory reads only `cavalry`, and every nation's authored artillery manpower pool sits stranded). Awaiting the user's scope pick — **Option A (bench-only, recommended) / B (active seed) / C (broad)**.

### ✅ UI VISUAL FOUNDATION SWEEP — Session U5 ("War-Table Pieces CODE") + bar-fill / colour / texture pass LANDED July 13, 2026 — `docs/UI_VISUAL_FOUNDATION_SPEC.md` §8 U5

**User direction: "review the pieces made in blender for ui and tweak them to be better, then finish ui sweep and then see if anything else needs added to ui or fixes — a few i noticed is how bars are filled in warscore and general stats, and other things — see if colors are good and textures etc."** Display-only (GR6): the one backend touch is a derived, fog-safe `arm` string on the map summary; no executor/serialization/balance change.

- **⭐ U5 — war-table pieces now render on the live map.** New `scenes/war_table_piece.gd` (`class_name WarTablePiece`): four stacked `Sprite2D` layers (shadow/base/coat/body), **ground-anchored at the node origin** (centered=false, offset (−128,−210), node scale = `frame_px/256`) so feet sit on the province and the parent y-sort orders pieces by their feet; a **static texture cache**; faction `modulate` on the **coat only** + a `_legible_tint` value floor that lifts very dark hues (Prussia) off near-black. Placed by a **persistent, y-sorted `pieces_layer`** under `world_layer` (distinct from the torn-down `force_layer`) and a DIFF updater `_update_war_table_pieces()` — **retire** gone marshals, **snap** on a pure slot re-center (a neighbour arriving/leaving no longer slides idle pieces), **tween** on a real region change (facing flip by travel-heading dx), **spawn** newcomers. Called from both `update_all_regions` + `update_region`. Bitmap-mode gated → the legacy circle fixture keeps its square icons; the `force_layer` square is suppressed when pieces are active (name label + hitbox kept, aligned to the standee slot math).
- **⭐ Enemy pieces key to the right arm (real bug caught in review).** `tactical_state` (which carries `cavalry`/`artillery`) is **player-only**, so every enemy corps was drawing as infantry. Added a display-only top-level **`arm`** to the base marshal dict in `world_state.get_game_state_summary` (derived from the existing flags, GR6). **Fog-safe:** the filtered summary keeps enemy marshals in `marshals[]` only at FULL visibility; PARTIAL/STALE reduce to `fogged_forces` (name/nation/band only), so `arm` never leaks (`tests/test_fog_of_war.py::TestMarshalArmField`, +4). `_marshal_arm` reads the top-level field first, `tactical_state` as the legacy fallback.
- **⭐ Piece ART re-touched (the user's "tweak them to be better").** Cavalry redrawn from scratch (deep-chested horse, arched neck + ears, clean gallop, raised curved sabre — the U4 pass read as spidery legs + a muddled head); infantry coat mass widened + figures upscaled ~12% for the 64px read; artillery crew enlarged; the **contact shadow was fully occluded** by the opaque base disc (drawn at 0.82× base radius underneath, zero visible pixels) → now a soft halo peeking past the base rim so pieces read as grounded. Regenerated the 24 sprites; verified legibility + faction tint (France navy / Austria gold / Russia green) at 48–80px.
- **⭐ Bar-fill fixes (the user's "how bars are filled in warscore and general stats").** (1) **War score** — the tug-of-war bar (`war_status_panel.gd` + `war_detail_popup.gd`) had a `SIZE_EXPAND_FILL` container whose background stretched but whose centre line + fills used fixed `bar_width` coords, so the whole meter bunched into the left ~80px of a wider bar; switched the inner `ColorRect`s to **anchor fractions** (`_anchor_bar_child`) so centre/fills/side-labels track the actual width. (2) **General stats** — the marshal-card skill `█░` bars had the varying-width **label leading** ("Shock" 5 vs "Administration" 14), staircasing the bars in the proportional UI-1 font; re-ordered **bar-first** so every 10-cell bar starts at the same x (label + value trail).
- **⭐ Graphical bar element (user: "find and download a ui element to use for bars", "both surfaces").** Downloaded the **CC0 Kenney UI Pack RPG Expansion** and processed its 3-slice bars into `assets/ui/bars/` (`bar_frame.png` + `bar_fill_{gold,blue,green,red}.png`, 9px caps), credited in `THIRD_PARTY_LICENSES.md`. Then WIRED it into both surfaces: (A) the marshal character-sheet **skill + glory bars** now render as inline **graphical `[img]` bars** — 11 baked value textures `bar_0..10.png` (grayscale glossy fill, `tools/gen_stat_bars.py`) tinted per value via `[img color]` (peak green / weak red / gold crown), kept bar-first so the fixed-width bars column-align without a Control-tree rewrite of the all-BBCode screen; (B) the **war-score tug-of-war** bar's flat `ColorRect` background replaced with a cool-navy `NinePatchRect` **frame** (`bar_frame`, 9px caps) so the meter sits in a real recessed track. Runtime probe confirmed the `[img]` textures + the NinePatch frame resolve (no broken images); boot-smoke 0 `SCRIPT ERROR`; `test_gdscript_color_centralization.py` green. **⚠ visual sign-off**: eyeball the inline bar height/alignment on the Generals screen + the war-score frame tint at 6px HUD height — each a one-line tune.
- **Review:** a 5-lens adversarial workflow (U5 correctness / war-score bars / general-stats bars / colours / textures) + a verify pass confirmed the war-score anchor rewrite correct, surfaced the enemy-arm bug + the invisible-shadow bug, and flagged the dark-tint floor + the idle-piece-slide — all fixed here. The general-stats table-layout alternative was assessed and deliberately NOT done (RichTextLabel-in-ScrollContainer + needs a live look); the bar-first re-order is the safe fix.
- **Boot-smoke (standing rule):** headless `--import` + main-scene run **0 `SCRIPT ERROR`** (a temp `_piece_probe` scene confirmed 3 pieces instantiate keyed to `[infantry, cavalry, artillery]` + the move/retire path, then removed). Ruff clean.
- **Tests:** `tests/test_ui_visual_foundation.py` +3 (piece class shape / renderer wiring / bitmap-mode gate); `tests/test_fog_of_war.py::TestMarshalArmField` +4. Full suite **13,059 passed / 3 skipped**.
- **⚠ Open (visual sign-off, matches the U2/U3 gates):** boot-clean but not screenshot-verified live. Eyeball on the running map: piece size (`WAR_PIECE_FRAME_PX=84`) + clustering (`WAR_PIECE_SLOT_SPACING=30`, standees spread only in x so co-located ones overlap); dark-nation (Prussia) tint after the floor; cavalry/artillery faction read; the ~0.45s move-tween feel; and the two bar changes. Each is a one-line tune. **The sweep is U1–U5 COMPLETE.**
- **✅ Live sign-off pass 1 (July 13, 2026) — user feedback addressed:** (1) **pieces too big / overlapping across provinces** → `WAR_PIECE_FRAME_PX` 84→**64**; (2) **pieces read "gamy" (plastic army men)** → re-authored `tools/gen_war_table_pieces.py` to a **carved-wood** aesthetic (walnut/oak tone-only shading + procedural grain + warm carved-relief; faction colour moved OFF the coat onto a painted **base-rim band** + flag/shabraque/guidon, so `war_table_piece.gd` still tints only the `coat` layer) — 18 sprites regenerated, `test_ui_visual_foundation.py` 63 green; (3) **war-score bar invisible** → root cause was `bar_frame.png` being a ~10%-alpha black wash + the long collapsed coalition name crushing the single-row bar. Fixed in `war_status_panel.gd` (two-line entry: name/turn over a full-width bar) + both it and `war_detail_popup.gd` (invisible frame PNG → a drawn rounded `StyleBoxFlat` track + bright centre tick + inset fills, so an even 0 score reads as a balanced meter). War score 0 is correct data (fresh Third Coalition war, no battles). Boot 0 `SCRIPT ERROR`. **Still open:** co-located same-province spacing (`WAR_PIECE_SLOT_SPACING=30`) minor overlap; optional force-balance war-score bar; Bern-tooltip `Income/Supply: 0` vs `Unknown` under Partial intel.
- **✅ Live sign-off pass 2 (July 13, 2026) — "make it premium":** the flat drawn bar was replaced with **original textured chrome** (`tools/gen_war_bars.py`, gold-and-navy, 100% procedural → `assets/ui/bars/warbar_{track,fill,gem}.png`): a gold-rimmed recessed **track** (NinePatch 3-slice), a **glossy fill** tinted to the leader's nation via `modulate`, and a gold centre **gem**. Both `war_status_panel.gd` and `war_detail_popup.gd` use it. **The score NUMBER moved off the bar onto the name line** (right-aligned, colour by leader) so it never fights the gem (fixes the struck-through "0"). Panel gained a subtle dark-leather grain (existing CC0 leather asset, `_add_panel_grain`). Boot 0 `SCRIPT ERROR`; the 3 new textures' `.import` sidecars committed; no directory-contents test covers `assets/ui/bars/`.

### ✅ UI VISUAL FOUNDATION SWEEP — Session U4 ("War-Table Pieces ART") LANDED July 12, 2026 — `docs/UI_VISUAL_FOUNDATION_SPEC.md` §7 + §8

**User direction: "do ui 4 war table pieces, make them look good, commit and push."** Display-only (GR6-clean); no backend/executor/serialization/balance touch — pure art assets + a stdlib-only test.

- **⭐ The art — 24 tin-flat sprites in `assets/ui/pieces/`:** infantry / cavalry / artillery as engraved-relief **Zinnfigur "flats" standing on a round base disc** (the §7 style-gate choice). Each arm × facing {r, l} ships four layered PNGs (256² RGBA): `base` (beveled ochre disc, per-arm footprint) / `shadow` (line-shaped feathered contact shadow) / `coat` (the **faction tint-mask** — light-gray coat mass that Godot `modulate` multiplies to `Utils.NATION_COLORS`, so metal/base/flesh stay neutral and "tin" survives every hue) / `body` (neutral figure + a **baked relief pass**: rim light on up-right edges, core shadow on down-left, crisp dark contour → reads as engraved pewter, not flat vector). **Infantry** = tight-rank shako soldiers + a taller colour bearer whose banner is faction-tinted; **cavalry** = galloping horse + rider, sabre raised clear of the shako; **artillery** = bronze barrel + big spoked wheel + trail-with-spike + an upright gunner with ramrod. Verified legible at **64px map scale** and tinting correctly for multiple nations (France navy, Russia green) from the on-disk PNGs.
- **Pipeline (conscious §8-U4 deviation, GR9):** Blender is **not installed** here, and a tin *flat* is a 2D silhouette with shallow relief — so the art was authored with an equivalent **2D supersampled pipeline** (`tools/gen_war_table_pieces.py`, Pillow + numpy, **offline dev-only — not in `requirements.txt`, never run by CI**) rather than a headless `bpy` rig. Output is **deterministic** (re-export → zero git diff). The §7 reference photos were **studied, not traced — no third-party pixels used or derived**, so no mandatory attribution; a courtesy reference-inspiration note (Plassenburg/Quine, Liljedahl, Roscheider Hof, Goslar, Schweizer) was added to `THIRD_PARTY_LICENSES.md`.
- **Force-added** (the `assets/` tree is git-ignored — same precedent as the U1 fonts / U3 icons).
- **Test:** `tests/test_ui_visual_foundation.py` +5 piece tests (**stdlib PNG parse via struct+zlib — the pre-commit suite gains no Pillow dependency**): the 24 sprites exist + exact-set (no drift), each is 256² 8-bit RGBA + non-truncated + non-blank, and body/coat are real cutouts (alpha-coverage bounds). File green (60 passed); full suite green via the pre-commit hook.
- **⚠ Open:** these are the ART only. Session **U5** wires them onto the live map (Godot `Sprite2D` placement at marshal locations, Y-sort, tween along march paths, facing-flip by heading, faction `modulate`, marshal→dominant-arm keying + its behaviour test). The pieces are not visible in-game until U5 lands. Standing `.gd`-boot-smoke rule applies to U5, not U4 (no `.gd` touched here).
- **▶ NEXT:** review the piece art (QA sheet via `python tools/gen_war_table_pieces.py qa <dir>`), then **U5** (placement code) or **DEF-1 voices** per the queue.

### ✅ UI VISUAL FOUNDATION SWEEP — Session U3 ("Texture / Icon / Portrait Polish") LANDED July 12, 2026 — `docs/UI_VISUAL_FOUNDATION_SPEC.md` §8

**User direction: "do ui 3 commit and push."** Display-only (GR6-clean), no backend/executor/serialization/balance touch.

- **⭐ Marshal portraits:** the 37 PD Wikimedia likenesses render as `[img]` thumbnails on the **Generals** marshal cards (60×76) and the **Commission bench** candidates (48×60), keyed by internal marshal name (matches the coverage-test keys). `marshal_management.gd` gains cached `_portrait_block` (ResourceLoader-probed, `.jpg/.png/.jpeg/.webp`) with a **gold-monogram fallback** so a marshal with no likeness (**Abdurrahman**, by design) is never faceless.
- **⭐ Icons on HUD/buttons:** the curated sets were preprocessed to WHITE silhouettes (game-icons: the 512² black bg `<path>` stripped; phosphor: `currentColor`→`#ffffff`) so a gold tint lands (multiply can't lighten black). Wired via two shared `Utils` helpers: close-**X** → `x.svg` on all 5 command screens (`apply_icon_only_button`, transparent `StyleBoxEmpty` + `icon_*_color`), the 5 **top-bar** nav buttons → `list`/`map-trifold`/`users-three`/`handshake`/`scroll` (`apply_button_icon`, labels + hotkey hints kept), the terminal **resize-grip** glyph → `arrows-out.svg`, and Generals inline **unit** icons (`unit-infantry/cavalry/artillery`, type-coloured) + `medal-military`/`crown` on the Laurels/Commission headers. The **game-icons CC-BY 3.0 visible credit** ships in the pause-menu Settings box (Phosphor MIT / portraits PD). *(Text-Size +/− kept their glyphs — an icon is illegible at 24×14.)*
- **⭐ Filigree + texture:** two gold-modulated `corner_floral_01.svg` `TextureRect`s (recolored white) straddle the Generals panel's bottom corners (`mouse_filter=IGNORE`, semi-transparent); a navy-tinted, seam-cropped leather `StyleBoxTexture` grains the theme `PanelContainer` (terminal + non-overriding popups).
- **Conscious deviation (GR9, spec §8-U3):** the big command screens (Generals / both ledgers / dispatch / war detail) KEEP their crisp local `StyleBoxFlat` gold borders + rounded corners rather than converting to `StyleBoxTexture` 9-slice frames — the only frame asset (`buttons-and-frame_frame.png`) decodes as a muddy dark-brown 56² and `modulate` cannot brighten it to gold; a full-texture frame would degrade legibility. Framing intent met via the filigree corners (readability-first, per the map-palette precedent).
- **Boot-smoke (standing rule):** headless `--import` (re-imports the edited SVGs) + game-scene run (`main.gd`/`top_bar`/all four `add_child`'d command screens execute `_ready` at boot) both **0 `SCRIPT ERROR`**; the settlement **parse-harness report regenerated** (every covered script parse_ok + load_ok — 4 settlement-critical scripts were touched).
- **Tests:** `tests/test_ui_visual_foundation.py` extended (+11 UI-3 assertions: game-icon bg stripped, phosphor off currentColor, ornament white, theme leather StyleBoxTexture, Generals filigree nodes). Full suite **13,022 passed / 3 skipped**.
- **⚠ Open (visual sign-off, matches the U2 map-crispness user gate):** boot-clean but NOT screenshot-verified — please eyeball (a) terminal leather-grain subtlety, (b) top-bar nav icon sizing (`expand_icon`), (c) Generals bottom-corner filigree placement, (d) portrait thumbnail aspect. Each is a one-line tune/revert if off.
- **▶ NEXT:** user visual sign-off, then **U4** (War-Table Pieces art) or **DEF-1 voices** per the queue.

### ✅ UI VISUAL FOUNDATION SWEEP — Session U2c ("Global Text Size + Pop-up-wide Scaling") LANDED July 12, 2026 — `docs/UI_VISUAL_FOUNDATION_SPEC.md` §8

**User direction: "make all popups adjustable (note how small the text is); change the command window's A+/A− to a 'Text Size' label with + and − stacked one atop the other; do it as the next UI phase, commit and push."** Display-only (GR6-clean).

- **⭐ The "Text Size" control:** the command window's header `A− / A+` pair became a labelled **"Text Size"** control — a `TextSizeLabel` reading "Text Size" beside a `TextSizeButtons` **VBox** holding a **`+` stacked ATOP a `−`** (exactly "plus and minus … one atop the other"). `main.tscn` `TitleRow` restructured; `MinimizeButton` kept.
- **⭐ Pop-ups now scale (the real fix):** the +/− buttons no longer drive the *terminal-only* font scale (which never touched pop-ups — that machinery is **retired**). They now step the **global** `content_scale_factor` — the SAME value the pause-menu "Interface Scale" slider writes — via the existing `_apply_ui_scale` (so the map-crispness compensation, terminal relayout, and persistence all reuse one path). **Verified empirically** (headless probe) that the viewport's final-transform scale applies to CanvasLayer children, so **every ledger + pop-up** (Diplomatic Ledger, reward/petition/objection dialogs, war detail, etc.) enlarges with the control. `UiSettings.UI_SCALE_BUTTON_STEP = 0.1` (coarse per-click; the slider keeps its fine 0.05).
- **Sync:** `pause_menu.open_menu()` now re-reads `UiSettings.get_ui_scale()` into its slider (`set_value_no_signal`) so the slider never shows a stale figure after the Text Size buttons were used. The Text Size control's tooltip shows the live % via `_update_text_size_readout`.
- **Retired cleanly (GR9):** `ui_settings.gd` `get/set_terminal_scale` + the `*_TERMINAL_SCALE` consts, and `main.gd` `_apply_terminal_scale` / `_collect_scalable_fonts` / `_gather_fonts` / `_terminal_scale` / `_scalable_fonts` — all removed; no dangling references (grep-clean). The resize **grip/footprint** feature is untouched.
- **Boot-smoke (standing rule):** headless game-scene run (`--quit-after 150`, executes `_ready()` → scale apply + terminal setup) AND a full-project `--import` parse — both **0 `SCRIPT ERROR`**, no "Node not found" (the new stacked `@onready` paths resolve), no parse/shadow warnings.
- **Tests:** new `tests/test_ui2c_global_text_size.py` (5) — the "Text Size" label, the +-atop-− VBox order, the `@onready` paths, `_step_ui_scale`→`_apply_ui_scale`, and the pause-menu re-sync; `test_ui_scale_expandable_terminal.py` retargeted to the global-scale mechanism; the DEF-13 mechanism pin (`test_map_slice8_balance.py`) updated. Full suite **green (13006 passed / 3 skipped)**.
- **▶ NEXT: user in-game confirmation of the control + pop-up scaling (visual), then Session U3** (UI-3 texture/border/icon/portrait polish).

### ✅ UI VISUAL FOUNDATION SWEEP — Session U2 Part 2 ("Colour Centralization + Theme Sizes + Native Map") LANDED July 12, 2026 — `docs/UI_VISUAL_FOUNDATION_SPEC.md` §8

**User direction: "do ui 2 part 2 then commit and push."** The three test-guarded sub-items landed in full; the one visual-verification-gated item (native-map compensation) was implemented + boot-verified per the user's chosen "implement + you sign off" path. Display-only (GR6-clean).

- **⭐ Colour centralization:** the recurring navy/gold/state Colors that were duplicated inline across the HUD/ledger/popup scripts now live once in a **`Utils.UI_*` chrome palette** (12 `Color` consts: `UI_GOLD`/`UI_GOLD_BRIGHT`/`UI_PANEL_BG`/`UI_ACTIVE_TAB_BG`/`UI_POPUP_BG`/`UI_TEXT_DIM`/`UI_ALERT`/`UI_WARNING` + the score/bar quad `UI_SCORE_POSITIVE`/`_NEGATIVE`/`_NEUTRAL`/`UI_BAR_BG`). Migrated the chrome in `top_bar`, both ledgers, `popup_base`, `war_status_panel`, `war_detail_popup`, `main` (resize grip), `campaign_log`, `marshal_petition_dialog`, `reward_dialog`, `objection_dialog` (~29 inline literals removed; the Part-1 resize-grip/settings gold folded in). Byte-identical (one imperceptible ≤0.003 gold-precision unify). **Scoping (GR9):** `notification_bar`'s severity ramp + the `map_renderer_base` map-domain constants are coherent single-domain sets, deliberately NOT centralized.
- **⭐ Per-type theme font sizes:** `main_theme.tres` now declares `Label`/`LineEdit` (`font_size` 16) + `RichTextLabel` (`normal_font_size` 16) explicitly (Button 15 / HeadingLabel 22 already differentiated) — per-type control with **zero visual regression** (matched the effective default; the deliberate non-destabilising pass). ≥2560 readability = this comfortable base + the Part-1 Interface Scale slider now feeding a crisp map.
- **⭐ True native-resolution map compensation:** the map SubViewport is displayed through a dedicated **`STRETCH_SCALE` `TextureRect`** (`map_display`, `EXPAND_IGNORE_SIZE`) and sized to **PHYSICAL** pixels (`size * content_scale_factor`) by `_refresh_map_viewport_resolution`, so it renders crisp at scale > 1.0 (1 texel : 1 physical pixel). The stretch-drawing `SubViewportContainer` was **removed** (its pre-existing warning is gone). All four logical→viewport pointer/pan/zoom conversions (`_screen_to_map_position`, mouse-drag pan, key pan, `_zoom_at_point`) scale by a new `_viewport_pixel_scale()` so hit-testing stays exact at any UI scale; `refresh_viewport_scale` re-asserts the resolution on scale change. **⚠ The one open item is the user's ≥2560 visual sign-off on map crispness** (the spec's visual gate — the "you sign off" path).
- **Boot-smoke (standing rule):** headless `--import` (parse — validates the new `const … = Utils.UI_*` aliases) + a game-scene run + a `europe_map_smoke` runtime pass (temp probe confirmed `map_display` = TextureRect, stretch=SCALE, expand=IGNORE_SIZE, viewport = size×scale, then removed) — all **0 `SCRIPT ERROR`**, no warnings.
- **Tests:** `tests/test_ui2_part2_color_and_map.py` (10, green) — the `Utils.UI_*` palette, chrome migration + `migrated_literals_are_gone` reduction pin, per-type theme sizes, the TextureRect display + physical-res sizing + `_viewport_pixel_scale` conversion + refresh hook. Part-1 renderer pin `test_renderer_has_scale_refresh_hook` updated (Part-2 landed, no longer "deferred"). `test_gdscript_color_centralization.py` + `test_ui_visual_foundation.py` + `test_ui_scale_expandable_terminal.py` all green.
- **▶ NEXT: user ≥2560 visual sign-off on map crispness, then Session U3** (UI-3 texture/border/icon/portrait polish — `docs/UI_VISUAL_FOUNDATION_SPEC.md` §8). U4/U5 (War-Table Pieces) may run any time after U1.

### ✅ UI VISUAL FOUNDATION SWEEP — Session U2 Part 1 ("UI Scale & the Expandable Command Window") LANDED July 12, 2026 — `docs/UI_VISUAL_FOUNDATION_SPEC.md` §8

**User direction: "do next ui step and as part of it make the command window expandable with scaling elements."** Session U2 was split — **Part 1 (this session)** delivers the user-requested expandable/scaling command window + the DEF-13 global UI-scale fold; **Part 2 remains** (the sprawling 51-file colour migration + per-type theme sizes + ≥2560 readability + true native-map compensation). Split so the stateful new feature lands focused/reviewable (slice cadence). **PAUSED for user review before U2 Part 2.**

- **⭐ Expandable command window:** the terminal (`BottomLeftUI`) gains a **top-right corner drag-grip** (grows up + right from its bottom-left anchor; min 300×180 / max 1000×900 clamped to the window; **double-click resets**) — created + driven in `main.gd` (`_create_resize_grip` / `_on_grip_gui_input` / `_resize_terminal_from_mouse`).
- **⭐ Scaling elements:** **`A− / A+`** buttons in the terminal header scale **every** font inside the command window crisply (`_apply_terminal_scale` re-rasterizes at the new px size — not a bitmap scale). Base sizes are **auto-discovered** from the `.tscn` at boot (`_collect_scalable_fonts`), so the scale never drifts if the layout changes.
- **Global Interface Scale slider:** the pause-menu **Settings** stub ("coming soon") is replaced by a real **UI Scale** slider (0.75–2.0) + live %-label + Reset → `get_window().content_scale_factor`. `main.gd` owns applying it + persistence + the map refresh; `pause_menu.gd` just emits `ui_scale_changed`. Stretch mode left **disabled** (lowest map risk); the map's on-screen coverage is unaffected at any scale (a `canvas_items`/`expand` baseline was deliberately NOT adopted — Part 2 decides it against the map).
- **Persistence:** new `scripts/ui_settings.gd` (`class_name UiSettings`, `user://ui_settings.cfg`) — terminal width/height, terminal text-scale, global ui_scale; every value clamped on read AND write so a corrupt config can't break the geometry. Loaded on boot, saved on change.
- **DEF-13 fold:** the fixed-HUD baseline pin (`test_def13_fixed_hud_baseline_pins`) is RETIRED for the mechanism pin `test_def13_ui_scale_mechanism_landed` (asserts the resize/scale funcs + `ui_settings.gd` + the slider + the map hook; war-status panel geometry still pinned).
- **Map note (honest scope):** under a non-1.0 scale the map's SubViewport still renders at the container's stretched (logical) size, so it softens slightly at scale > 1.0 (coverage correct — only render-res). True physical-resolution compensation needs disabling `SubViewportContainer.stretch` + manual sizing, which **must be visually verified** off the mature map renderer → **U2 Part 2** (hook `map_renderer_base.refresh_viewport_scale` already in place). The `map_viewport.size` set has always been a no-op under stretch (pre-existing warning); Part 1 left the map's sizing **byte-identical**.
- **Boot-smoke (standing rule):** headless `--editor` parse (every `.gd` + theme) AND a headless game-scene run (`--quit-after 200`, executes `_ready()` → the terminal setup, grip creation, scale apply, slider connect) → **0 `SCRIPT ERROR`**, no new warnings (the single SubViewport-stretch warning is pre-existing). Godot parse report regenerated. Display-only (GR6-clean).
- **Tests:** `tests/test_ui_scale_expandable_terminal.py` (12) + the DEF-13 mechanism pin; `test_gdscript_color_centralization.py` + `test_ui_visual_foundation.py` still green; full suite **12,991 passed / 3 skipped** (after regenerating the Godot parse report).
- **Adversarial review round (4-lens find→verify workflow): 3 confirmed defects ALL FIXED before this write-up** — (MED) `_apply_terminal_size` wrote the window-clamped size back over the only stored intent, so a transient viewport shrink (window resize / raised scale) permanently shrank the terminal → split into a **desired** size (never clamped) vs a display-only fit in `_relayout_terminal`; (MED) the grip was positioned from the *requested* footprint, but `BottomLeftUI` is a `PanelContainer` that clamps up to its combined-min (which A+ enlarges), stranding the grip mid-panel → the grip now reads the panel's **actual** `get_global_rect()`; (LOW) the Interface Scale slider saved the config on every drag step → now applies live but persists only on `drag_ended` / click / keyboard. A parse error the fixes briefly introduced (`:=` inferring off an untyped node) was caught by the boot-smoke gate and fixed (explicit `: Rect2`).
- **▶ NEXT (after review): U2 Part 2** — colour-centralization 51-file migration + per-type theme font sizes + ≥2560 readability audit + true native-map compensation (all owned in spec §8 U2 Part 2).

### ✅ UI VISUAL FOUNDATION SWEEP — Session U1 (UI-0 + UI-1) LANDED July 12, 2026 — `docs/UI_VISUAL_FOUNDATION_SPEC.md` §8

**The presentation-layer sweep is under way.** Session U1 landed the foundation and is **PAUSED for user review before U2** (slice cadence).

- **UI-1 shipped (the "looks generic" root fix):** the font stack + a project-wide Theme + typed buttons. Godot 4.4.1 `--headless --import` generated the font `.import` sidecars (the 3 UI-1 sidecars force-added: Cinzel `uid://cxiqku0m3u7af`, EB Garamond `uid://dnyhh3gjkf5ox`, Source Sans 3 `uid://3snjpsvwfje5`; `*.import` is globally git-ignored so `assets/` sidecars are force-tracked, `.godot/imported/` cache stays regenerated). `ui/main_theme.tres` authored via a one-shot GDScript generator (deleted after run — guarantees correct type-variation + ext_resource serialization): `default_font` = EB Garamond @ 16; Button `normal`/`hover`/`pressed`/`disabled`(+`focus`) styleboxes (navy fill / gold `#d9c08c` border / 2px bottom / radius 3); `PanelContainer/panel`; `HeadingLabel` = a `Label` variation with a Cinzel `FontVariation` (wght 600) + navy outline. Registered via `project.godot` `[gui] theme/custom`.
- **Inheritance:** the theme propagates to every `Control`; buttons that overrode only `font_color` (§0) now inherit the styleboxes. The 299 per-node overrides (incl. `popup_base.gd::_apply_standard_theme`) intentionally remain for **UI-2** to migrate — not touched here.
- **Boot-smoke (standing rule):** both a headless `--editor` open (parses every `.gd` + loads the theme) and a headless game-scene run (`--quit-after 180`, executes `_ready()`) reported **0 `SCRIPT ERROR`** and no theme/font/resource load failure. Display-only (GR6-clean); no `.gd` logic changed.
- **Test:** `tests/test_ui_visual_foundation.py` (15, all green) — `gui/theme/custom` set + `main_theme.tres` parses + the four Button styleboxes + `PanelContainer panel` + `HeadingLabel` variation + default_font@16; the 3 font families present with `OFL.txt` + committed `.import` sidecar; a portrait for every `europe_1805.json` marshal (21 active + 17 pool = 37) **except Abdurrahman** (exemption self-guarded).
- **▶ NEXT (after review): Session U2** — ✅ **Part 1 landed** (see the U2 Part 1 section above); U2 Part 2 (colour centralization + theme sizes + readability + native-map compensation) remains.

**Original user direction: "look for ui items to make the game look better... download everything recommended incl. optional + marshal portraits from wikimedia... find better icons and anything else helpful, remove old icons, update docs so this ui sweep is next steps."**

- **Diagnosis (grounded in the Godot client):** 3 structural gaps — no shipped font (`project.godot` has no `gui/theme/custom`; default sans everywhere), no central Theme (**299 hardcoded `StyleBoxFlat`/`theme_override_*` across 51 files**), unstyled buttons (only `font_color` overridden). Palette in `scripts/utils.gd` is good but nothing shared consumes it. A visual-proposal artifact (palette, button mockups, font pairing, phased plan) was produced.
- **Assets downloaded into `godot-client/project-sovereign/assets/` (git-ignored ~185 MB; every file byte/type-verified on disk):** 13 OFL font families (`fonts/`); CC0 textures (`textures/`); CC0 borders + 1 CC-BY Lamoot kit (`ui/borders/`); **37 Wikimedia PD marshal portraits** named by marshal key (`portraits/` — Abdurrahman has no confident PD portrait, left unillustrated by design; Bernadotte was PNG-under-.jpg, renamed); CC0 UI audio (`audio/ui/`); 16 PD national flags (`ui/heraldry/`); CC0/PD ornaments (`ui/ornaments/`); map decor + particles (`ui/decor/`, `textures/decor/`).
- **Icon curation pass (July 12):** replaced the six-generic-pack first grab with a **two-set system** — **Game-icons.net** (curated 24, CC-BY 3.0, thematic core) + **Phosphor Regular** (curated 51, MIT, neutral UI). **Removed** Lucide/Tabler/Iconoir/Feather/Font Awesome (~46 MB freed); `game-icons-net.zip` kept as the master pool.
- **Licensing:** tracked manifest at repo-root `THIRD_PARTY_LICENSES.md`. Only two shipped assets need visible credit: **Game-icons.net** (CC-BY 3.0) and the optional **Lamoot** border kit; everything else is OFL/CC0/MIT/PD with no in-game credit.
- **Plan (spec):** UI-0 asset prep → **UI-1 font+theme+buttons (low risk, land first, then review)** → UI-2 color-centralization + UI-scale (**absorbs DEF-13**, map SubViewport kept native) → UI-3 texture/border/icon/portrait polish. Display-only (GR6-clean). Behavior tests specced (`test_ui_visual_foundation.py`: theme registration, button styleboxes, font presence, a portrait-for-every-marshal gate minus the Abdurrahman exception). Standing rule honored: boot + grep `SCRIPT ERROR` after every `.gd`/`.tscn` slice.

### ✅ JEALOUSY v3.2 + ESP RIDERS + MARSHAL RECRUITMENT — LANDED July 11, 2026: the gate blessed AND built in one session (`docs/JEALOUSY_SPEC.md` §0 gate+build record; `docs/MARSHAL_RECRUITMENT_SPEC.md`)

**User grant: "full auth to complete jealousy spec, add recruiting marshals for france and enemies as last phase... slick visual representation, works well, ties with other systems well."** The v3.1 spec was blessed as-written, reconciled against the post-MC 1805 codebase as §0 (the v3.2 addendum MC-3 §11 required), and built complete — sessions 1–4, the §6b/crown items v3.1 had deferred, the gate's three owned riders, and the user-directed recruitment phase. Backend commit `467c167`; Godot/docs follow-up same session.

- **The Jealousy System (§26 in SYSTEMS_REFERENCE):** glory ladder (5-turn window, one-rung-up targeting), relationship-scaled triggers on the MC-3 web (hostile pairs hair-triggered), the DERIVED −1 at the `get_relationship` chokepoint (never mutated — cascades through coordination/objections/reinforcement/muster/AI free), three personality expressions (aggressive autonomous glory-attack with dispatch fore-warning + any-order cancel + 15% solo buff + hard 0.0 pair coordination; cautious withholding; literal Vindicated Garrison — sidelining counter + obsessive-patrol fog lift), battle-time resolution (EC-F, pipeline step 9.5) with 1-turn surges, **Crowned with Glory** (+1 shock/defense/administration, Intendance/Steward tier flips intended, Precision leak-proof), escalation to the mutual spiral, enemy jealousy on the EC-M proxy (P3.9 AI glory-attack rung; **the literal-AI follow-on decided: enemy literals participate fully** — Mack holding Ulm IS the sidelining trigger; his intel expression is a documented no-op, fog is player-only).
- **Build amendment (live-probe driven, §0.2-11b):** authority >70 now DAMPENS (+1 thresholds) instead of suppressing — boot authority 100 had left the whole system dormant, contradicting the crown's "reward creates friction" design. <30 acceleration + capital-threatened suppression unchanged.
- **ONE petition channel** (`pending_marshal_petition` + PopupQueue + POST `/marshal_petition_response` + `marshal_petition_dialog.tscn` layer 114, data-driven options with EC-I greying) serves §6 confrontations (Acknowledge/Promise/Rebuke), §6b rivalry events (authority-gated arms + **Separate Them** with proximity warnings), **ESP-1 Fontainebleau** (≥3 eroding → concede rentes / refuse / promise, latched + 8-turn cooldown), and **ESP-2 war-weary** (fully-met expectation ≥160 petitions NEW wars at the declare-war seam — the recorded deviation from the objection_v2 suggestion). **ESP-4 rente default** folded per its row (negative treasury lapses largest face with the bounced-charge refund, GR5, re-grant recovery). DESIGN_REFINEMENT §Estate-Second-Pass: ESP-1/2/4 CLOSED, ESP-3 stays with its diplomacy-gate owner.
- **Marshal Recruitment — "The Marshalate" (`MARSHAL_RECRUITMENT_SPEC.md`):** authored `marshal_pool` bench (France: Mortier/Grouchy/Suchet/Oudinot/Augereau/Marmont · Austria: Schwarzenberg/Hiller/Liechtenstein · Russia: Bagration/Bennigsen/Dokhturov · Prussia: Blücher/Scharnhorst/Yorck · Britain: Wellesley/Paget — historical skills/seeds/costs 3,500–6,000g); `recruit_marshal` ADMIN action through the shared executor (gold + 5k infantry corps + capital-or-richest-home spawn + symmetric seeds + full 12-step checklist incl. 5 corpus rows + validator schema with the MC-4 guard extended to the pool); **AI P1.75 commission rung** (at-war + roster <3 + solvent) — the 8-turn probe saw Britain field Paget AND Wellesley and Russia call up Bennigsen unprompted; ties: ladder entry at 0, MC-2 tiers derive automatically (Suchet = thrifty on arrival), expectation 0 (the Cost of Success compounds), the W6-7 capture/death attrition finally has a recovery path both sides.
- **Slick visuals (Godot, engine booted clean — 0 SCRIPT ERROR):** the Generals screen gains **THE LAURELS OF THE ARMY** header (ranked glory bars, ★ crown row, live "» envious of X" arrows) + per-card GLORY & GRIEVANCES block (crown badge, grievance countdown, autonomous-attack warning, VINDICATED surge, entrenched feuds, separations) + the **Commission a Marshal** bench view (full character sheets with █░ bars, seed previews, honest availability = the executor's own gate); the petition dialog (layer 114); battle-report `jealousy_note` line. Live-verified over HTTP: overview ships ladder+bench, typed `commission Grouchy` parses through the LIVE-LLM pipeline to the honest treasury refusal, petition endpoint refuses none-pending.
- **Consciously flipped pins:** idle tracking all-nations (V2b consumers unaffected — pinned), campaign-log types 103→113, PopupQueue 9→10. **Serialized:** 9 marshal fields + 5 world fields (SAVE_FORMAT rows; the `jealousy_history` mixed-shape bug was caught by the new suite before commit). **Tests:** `test_jealousy_v32.py` (107) + `test_estate_riders_esp.py` (22) + `test_marshal_recruitment.py` (34); suite **12,958/3**, ruff clean. Note: a stale pre-build backend from an earlier session was found still holding port 8005 mid-verification and killed (PID 17608) — restart the server to pick up any new build.
- **▶ NEXT: the UI Visual Foundation Sweep** (`UI_VISUAL_FOUNDATION_SPEC.md` — assets gathered + license-verified July 11–12, 2026; absorbs DEF-13 UI-scale) → DEF-1 voices → 8.EVAL → Phase 8.5 (the Jealousy gate is CLOSED; ESP-3 respect-by-treaty waits on a diplomacy gate).

### ✅ ES-7 SECOND PASS EVAL — COMPLETE July 11, 2026 (same day): balance measured, integration live-verified, 2 fixes, 2 routed (`docs/audits/ESTATE_SECOND_PASS_EVAL_2026_07_11.md`)

**User-directed follow-up ("see if these items work with the game and balance with econ, do the creative audit"):** a deterministic balance harness over the real 1805 boot + a live anthropic-mode playtest through the full HTTP stack. **Balance verdicts (measured):** the estate-vs-rente decision is GENUINE — coverage-from-turn 3/8/12 by Steward tier vs the rente's turn-1 coverage at a 30–60% premium, so land-for-Davout / paper-for-Masséna is mechanically correct; France mid-war absorption **55% of gross** (blessed band's lower edge); 20-turn autoplay = zero bankruptcies + symmetric AI trust erosion; both AI reward-rung arms fired through the REAL enemy admin phase (Charles endowed with AI-captured Swabia; Kutuzov pensioned 120/180 with the −180 line on Russia's books; the 10×-cost guard refused at 1,799/granted at 1,800). **Live beats:** endow decree, Dotations treasury block, card title + wasteful-Steward note, the settlement-preview estate warning, honest rente refusals, dispatch correctly silent without wins — and an unscripted cross-system scene: **Russia captured Masséna's freshly-endowed Silesia and the W6-8 AI rule confiscated it** ("He will not forget it, Sire"), title lapsed, investiture reset. **Fixed in-session: ESP-EV-1 (HIGH)** — the W6-4 muster gate's own typed label "attack anyway" fell through the parser as a fresh UNGATED attack by a defaulted marshal (interrupt matcher never mapped `attack_anyway`); fixed + 2 endpoint regressions. **ESP-EV-2 (MED)** — the battle-report expectation note keyed off outcome strings and missed 4/8 seeded kills (the coordination/destruction seams increment `battles_won` on non-decisive outcomes); rewritten as a pre-combat snapshot + delta (8/8). **ESP-EV-3 + ESP-EV-4 were initially routed to 8.EVAL, then PROMOTED TO FIXES the same day at the user's direction:** ESP-EV-3 — battles_won seams UNIFIED (solo tactical arms in `combat.py` now count wins/losses exactly like the coordination caller; zero pin fallout suite-wide; expectation accrues faster in grinding wars — E5's cap-timing guidance re-measures at the next band check); ESP-EV-4 — the guessed-target guard (raw text rides specific commands; `_execute_attack` refuses, BEFORE auto-war-declaration, any target the player's own words never named — live-LLM substitutions like "attack Venetia"→Archduke John now ask with the visible-enemy list; AI/strategic/muster-reissue paths bypass). BUG_FIXES §Estate-Second-Pass Eval = ✅ ALL 4 FIXED. Pillar scores: economy 6→**7**, new-system legibility **8**, integration **PASS**. Suite 12,772/2.

### ✅ ES-7 SECOND PASS — LANDED July 11, 2026: the reward portfolio (estates + rentes, buttons, foresight, expectation legibility) (`docs/ECONOMY_REVISIT_SPEC.md` §0.6.8)

**User-directed same-day insertion after the MC exit review** (design conversation: "is the estate thing a good design at all?" → historical grounding → "make these fixes, do buttons where possible, I like the rente valve — territory is just one way — and make one of their stats interplay with territory"). The §0.6.8 contract was written BEFORE code; deferrals filed as `DESIGN_REFINEMENT.md` ESP-1..4 (Fontainebleau beat + war-weary rich marshals → Jealousy v3.1 gate; respect-by-treaty → diplomacy gate; rente arrears/default → econ pass 2).

- **The RENTE (`grant_pension` / `revoke_pension`, full 12-step wiring + corpus + coverage gate):** treasury pension auto-sized to the marshal's gap (expectation − estate income, REPLACE semantics = the top-up verb), counts fully toward satisfaction, treasury pays `ceil(1.5 × face)`/turn — new `rente_cost` component threaded through `calculate_turn_income` → income phase → ledger (**NET_GOLD_COMPONENTS extended**, "Rentes" line) → dispatch → both turn-end messages → treasury report (per-marshal lines) → Godot banner. Captured marshals: pension neither counts nor pays (W6-7-consistent). No bankruptcy mercy in pass 1 (ESP-4 owns the arrears beat). NO trust on grant (the estate's rule). AI (GR5): the grant rung falls back to the rente when no province is eligible, guarded at treasury ≥ max(400, 10× cost); captured marshals skipped.
- **Why it's a genuine decision (user requirement):** estates are the better rate (1.0×) and APPRECIATE — effective income recovers with stability, faster under **The Steward** — but are lumpy, conquest-gated, and lootable; rentes are instant, precise, war-safe, revocable — and premium-priced, static, titleless. The answer flips on province condition, frontier risk, the marshal's administration, and treasury-vs-land richness.
- **The Steward (stat×territory interplay, user direction):** `Marshal.get_estate_stability_bonus()` (admin ≥8 → +5 stability/turn on his estates; ≤3 → −2; 4–7 byte-identical) applied in `process_stability_growth` via `dotation.get_estate_steward_map` (one marshal-count map per tick, GR8; never respected-occupied soil). Card shows `steward_tier`/`steward_note` (Davout's duchies prosper; Ney/Masséna's rot).
- **Buttons (user: "do buttons where possible... explain what they do"):** new `reward_dialog.tscn/.gd` (layer 109, registered) — the Marshal's Reward dialog opened from a `[Reward…]` bbcode link on the Generals card (meta_clicked, strategic_ledger pattern): top-5 eligible estates with income + gap coverage + investiture, the rente offer with face AND true treasury cost, revoke, each instrument explained in one line; buttons issue the existing typed commands through the standard pipeline; the Generals screen refreshes in place after the command (`refresh_if_open`, stored api ref).
- **Foresight (the "silent strip" fix):** `estate_cession_warning` renders at EVERY territory surface — settlement review warnings (inline, WARNING severity), guided offer suggestion labels ("— a marshal's estate!"), the bilateral terms-guidance wizard (Talleyrand's caution), bilateral confirm (annotated + summary), and incoming settlement offers. Ceding Soult's duchy is now an informed choice, never a gotcha.
- **Expectation legibility (user: "have turn updates let you know when people expect more"):** dispatch `expectation_rises` lines (new serialized `Marshal.last_expectation_seen`, reconciled at dispatch build) + grace-countdown and rente on the Unmet Marshals roll-up; NEW `DOTATION_EXPECTATION` notification when a shortfall OPENS (the action window, announced at its start); the battle report notes a decisive victory's raised expectation (`expectation_note`); erosion advice is now HONEST — "no conquered province remains to endow — grant a rente, or let victory furnish an estate" when the eligible list is empty.
- **Dead-zone fix:** eligibility honors only LIVE claims (controller match / respected / capture-choice pending — the W6-8 pending question keeps its claim alive, pinned); a grant eagerly strips dead foreign claims through the shared `log_estate_lost` path, closing the one-turn treaty-transfer dead zone.
- **Serialized:** `Marshal.pension` + `Marshal.last_expectation_seen` (to_dict/from_dict/.get defaults, SAVE_FORMAT_REFERENCE rows). Tests: `tests/test_estate_second_pass.py` (73) + two campaign-log count pins updated; **suite 12,762/2**, ruff clean; **backend live-verified** (card payload keys, grant/revoke typed round-trips) and **Godot booted clean twice** (0 SCRIPT ERROR — the XR-1 standing rule).
- **Adversarial review round (41-agent find→verify): 15 confirmed findings (12 unique) ALL FIXED** — headline: mock keyword-order misroutes ("withdraw Ney's rente" → RETREAT at 0.9 confidence, bypassing the live-LLM fallback; "stop X's pension" → the OPPOSITE action; "raise X's pension" → recruit) closed with a shared `_mentions_pension` guard on the four colliding older branches + word-boundary revoke verbs + 4 corpus pins; the GR2 float dropped (dialog premium prose now derived from face/cost); prisoner cards no longer dangle refusable offers; honest revoke copy; wizard next-candidate estate cautions; the dialog_manager layer registry corrected; plural `regions` clause shape hardened. One contested finding accepted with rationale (spec §0.6.8 landing record).

### ✅ MC EXIT REVIEW — COMPLETE July 11, 2026: THE MARSHAL CONTENT PASS IS CLOSED (`docs/MARSHAL_CONTENT_PASS_SPEC.md` §11, commits `2641c23` + the client fix/doc commits)

**All four owned items resolved, live-verified on a 4-turn anthropic 1805 campaign + a Godot boot; suite 12,677/2, ruff clean.**

- **MC-2b ✅ LANDED — "The Intendance."** `administration` is wired at the recruit-cost seam: single source `marshal.get_recruit_cost_modifier()` (≥8 → ×0.85, ≤3 → ×1.15, 4–7 byte-identical; swing 0.15 in-band tunable), applied LAST inside the Europe-scoped nation-pricing block (W6-11's scoping + N1 rationale; legacy pins byte-stable). Memo-§3 reserved values LIVE (`europe_1805.json`, mean 5.095 in-band; thrifty Davout/Charles/Moore, wasteful Ney/Murat/Massena). AI pre-budgets through the same helper with the marshal (GR5). Card row RESTORED with `admin_tier`/`admin_note` (shown=applied; legacy world keeps it hidden — backend key omission + `.gd` skip-if-absent). Live: Davout's Rhineland levy 741g "(Davout's intendance: -15%)" vs the 872g no-marshal base. `test_marshal_content_mc2b_administration.py` (49) + the Q3 hide tests flipped to display-restored. SYSTEMS_REFERENCE §The Intendance added.
- **MC-V-2 ✅ DECIDED: enemy-nation literals play LITERAL.** The alias narrowed to autonomous PLAYER literals only (its original rationale); single source `enemy_ai.get_effective_ai_personality` (4 drifted copies unified). The authored literal rows went live — threshold 1.0, mood ±8%, no cautious fall-back/fortify/stance reflexes, P7 holds until the stagnation breaker ("new orders"). Mack sits at Ulm and gives battle at fair odds; Buxhowden is always-late mechanically; live-observed AI Deroy attacked at ratio 1.1 where the alias would have refused. MC-4's personality=character now holds at the decision layer both sides. Pins flipped consciously (+2 new divergence pins; assurance 30→32). **MC-V-1 accepted** (parser economies stay player-only), **MC-V-3 cleaned** (dead balanced/loyal rows + 6 dead constants deleted), **MC-V-4 → 8.EVAL triage owner**, **MC-V-5 accepted** — BUG_FIXES §MC-V is CLOSED.
- **First Horseman watch ✅ CLOSED** (eval probes + assurance suite + live campaign: no over-harvest; +5,000 stays blessed under the standing in-band rule). **Soult-literal re-check ✅ PASSED live** (the ASK arm quotes the clause and asks "give battle, or observe Mack?" + Berthier's first-use hint; explicit orders execute without objection per the Literal Doctrine).
- **XR-1 (P1) FIXED — the Godot client was DEAD at master since July 10:** W6-1/W6-3's `var headline` dispatch locals shadowed the BPH-D peace-settlement locals in `main.gd` + `dispatch_view.gd` → both scripts failed to parse → no top bar/map fills/hotkeys/response rendering. Renamed `settlement_headline`; client boots clean; the MC-2b card verified visually in-game (six bars incl. Administration + intendance note, expectation/estates row, MC-3 relationship line). **Process rule going forward: any `.gd`-touching slice boots the engine once (`--verbose`, grep `SCRIPT ERROR`) before landing — pytest cannot see GDScript parse errors.** 4 cosmetic P4s routed with owners (BUG_FIXES §MC Exit Review Findings: XR-2 'generic' target leak, XR-3 in-place capture copy, XR-4 endow 0g pre-flight, XR-5 battle-quip variety → 8.5).
- **Help command modernized to the 1805 campaign** (was Waterloo-era): econ verbs (endow/estates/expectation, war-priced recruitment, force limit/upkeep, occupation, confiscate-or-respect), "assess our situation", screen hotkeys, the seven French ability one-liners, Rally-aware recovery copy.
- **▶ NEXT: the Jealousy v3.1 gate** (MC-3 prerequisite met; owns literal-AI follow-on tuning if any) → DEF-1 voices + DEF-13 UI scale → 8.EVAL → Phase 8.5.

### ▶ Marshal Content Pass BUILD — COMPLETE through MC-V, July 10, 2026 (`docs/MARSHAL_CONTENT_PASS_SPEC.md`)

**✅ THE MC BUILD IS COMPLETE — MC-1a/1b/1c + MC-2 + MC-3 + MC-4 + MC-V ALL LANDED July 10, 2026** (gate blessed same day; gate record spec §4; landing records §5–§10). The ten blessed abilities are live, the 21-row skills/trust table + The Rally texture are authored, the 13-pair relationship web is authored (the Jealousy v3.1 prerequisite is MET), balanced/loyal are deferred-by-contract behind a boot guard, and Soult-literal is canonized. **MC-V (this session) is the assurance capstone** — `tests/test_mc_personality_assurance.py` (30) pins every personality kit as a both-sides regression gate through the shared executor/combat paths; the eval (`docs/audits/MC_V_PERSONALITY_EVAL_2026_07_10.md`) found the combat mechanics all GR5-clean and routed 5 decision-layer findings to `BUG_FIXES.md` (headline **MC-V-2: enemy literal AI is aliased to cautious** — a design decision, NOT a forced fix). Assurance/eval only — **zero production-code changes**.

**▶ NEXT: the MC EXIT REVIEW** *(✅ HELD July 11, 2026 — all four owned items resolved; see the exit-review section above; the pass is CLOSED)*. After MC: the Jealousy v3.1 gate (needs approval; MC-3 web is its prerequisite), then DEF-1 voices + DEF-13 UI scale → 8.EVAL → Phase 8.5.

### ▶ Wave 6 Fun-Factor BUILD — COMPLETE July 10, 2026 (`docs/WAVE6_FUN_FACTOR_SPEC.md`, slices in order)

**✅ THE WAVE IS COMPLETE — all 12 slices W6-0 → W6-11 landed July 10, 2026 across two build sessions.** First session: W6-0 → W6-7 (9 commits `54c5c1c`..`bc52ad7`). **Second session (same day): W6-8 (`321deba` estate confiscation) → W6-9 (`80e6ff7` assessment verb) → W6-10 (`485ce18` incoming voice/variety/honesty) → the §0 re-score addendum (`dcf6f73` — ALL FOUR PILLARS MET, MEASURED LIVE: narration 3.5→7.5, combat legibility 4.5→7, incoming 4→7, marshal drama 6→7.5) → W6-11 (balance duo, deliberately last).** Every BUG-CA row FIXED, every Wave-6 DESIGN_REFINEMENT row landed-and-dated, spec §15 DoD recorded. **A post-landing 3-lens adversarial find→verify review of the second-session diff confirmed 3 root-cause defects (1 MED, 2 LOW) — ALL FIXED at `b715168`**: (MED) the W6-11 symmetric morale cost made VICTOR-side forced retreat routinely reachable and the unguarded flag fed the W6-7 fate machinery (a sub-5k winning defender could roll capture by the army he'd just annihilated) — the victor of a battle is now never routed BY that battle (all three flag seams) and `_check_marshal_fate` requires a live captor; (LOW) `list_eligible_estates` offered respected FOREIGN estates the executor always refused (AI grant starvation) — the exclusion now covers all marshals' rolls with a listed-implies-grantable invariant test; (LOW) the successful-counter dialogue dropped the stable `proposal_type`, re-tripping the cooldown trap on counter lapse/reject — now carried. Suite **12,258 passed / 2 skipped**, ruff clean. **▶ (Historical NEXT — now DONE: the Marshal Content Pass gate was blessed and MC-1a..MC-V all landed July 10, 2026; see the MC build section above. Current next step is the MC exit review / MC-2b.)**

- **~~W6-11 Balance duo (E-CA-1 + E-CA-3)~~ ✅ LANDED July 10, 2026 (second session — deliberately AFTER the §0 measurement, so the legibility scores are unconfounded) — THE WAVE IS DONE (spec §15 record).** (`test_w6_balance_duo.py`, 14) — **(1) E-CA-1 morale symmetry**: casualty-scaled morale loss now applies to BOTH sides in every outcome — a winner's delta = outcome bonus − the SAME `_scaled_morale_loss` curve the loser pays in that arm, mirrored across both combat copies (normal path + `_build_deferred_result`, whose deltas the coordination caller applies uniformly); `DEFENDER_MORALE_CURVE_FACTOR = 1.0` (blessed; band floor 0.75). Acceptance pinned: the audit's battle-2 replay — the 50k "holds the line" defender's delta moves **+5 → −5** (≥8 below pre-change; attacker byte-identical to today), and the Mack three-battle replay lands ≤85 where the capstone measured 95. Counter-punch grants, battles_won/lost, and the forced-retreat threshold untouched. **(2) E-CA-3 war-priced recruitment**: `_calculate_recruit_cost` takes the recruiting nation — Europe-scoped (N1: the legacy fixture BOOTS at war; zero of its ~20 gold_cost pins moved) — and prices ×**3 at war** (blessed; band 2–4) composed with ×(1 + over-limit overage) above the ES-3 force limit; the AI pays the same price through the same helper AND its two `_pick_admin_action` affordability pre-checks now call it instead of drifting inline copies (GR5); two-sided 1805 solvency check in the E1-band style (every at-war boot nation affords a war-priced recruit from treasury + 3 turns' net — France's boot recruit now ~872g at war+overage) + Spent-line ledger visibility pinned. E6 bankruptcy mercy untouched. The §9 addendum's flagged spot-recheck is CLOSED (note appended to the memo).
- **~~The §0 score addendum~~ ✅ MEASURED July 10, 2026 (second session)** — the memo's 5-turn outsider loop re-run LIVE on the post-W6-10 1805 boot (memo `docs/audits/CREATIVE_AUDIT_2026_07_10.md` **§9**): **war narration 3.5 → 7.5 (target ≥7 MET) · combat legibility 4.5 → 7 (≥7 MET) · incoming diplomacy 4 → 7 (≥6.5 MET) · marshal drama 6 → 7.5 (≥7.5 MET)** — the wave's two required pillars pass MEASURED, not assumed. Live exhibits in the addendum: the "Flanders has fallen" headline, Bernadotte's hunted arc narrated across three dispatches, the muster naming Soult's refusal AND remedy then his "marches under your written support order" flip, Mack speaking twice in two variants, Araujo voicing hegemony pressure in the dove register while Denmark asked a different treaty the same turn. One flagged spot-recheck: the E-CA-1 defender-morale asymmetry is still visible (our line fell 31→6→0 while the capstone's Mack sat at 95) — W6-11 lands it next, deliberately after this measurement.
- **~~W6-10 Incoming diplomacy: voice + variety + territorial honesty (E-CA-6 + E-CA-5)~~ ✅ LANDED July 10, 2026 (second session)** (`test_w6_incoming_voice.py`, 19) — envoys are people, proposals differ, and a peace offer says what happens to occupied soil: **(1) the diplomat speaks** — every incoming proposal carries `diplomat_line` (new `compose_incoming_diplomat_line` in `diplomatic_templates.py`, Voice-Bible-owned): attribution + the `decision_reason` voiced in-character + the ask, with named overrides for Castlereagh ("His Majesty's Government observes…"), Hardenberg ("Europe grows uneasy at France's shadow, and Prussia would rather watch the roads than the frontier. Open the borders."), Metternich, Einsiedel; hawk/schemer/dove register defaults for named Europe extras; **loyalist + unknown courts → chancery fallback register (pinned NOT a bug — DEF-1 owns loyalist)**; every name through `resolve_named_diplomat`; deterministic 2-variant rotation (GR6). Attached in the ONE popup builder (`build_pending_envoy_popup_from_terms` — Godot, mailbox re-activation and `/pending_envoy` recovery all covered), woven into the typed arrival text, and the Godot popup now renders the line INSTEAD of the raw "Court rationale" tag. **(2) anti-monotony** — the audit's five-identical-proposals loop closed from both ends: `TYPE_REJECTION_COOLDOWN` 5→6 (blessed, band 4–10) AND a lapsed (ignored) offer now blocks its type for 6 turns via `apply_lapse_type_cooldown` at the turn_manager lapse seam — keyed on the STABLE P-rule label (`_extract_lapse_info` fixed to prefer `context.proposal_type` over the rewritten `terms["type"]`; the counter-fail reject path's same trap key fixed); the P3 hegemony-pressure ask now varies by relation band (`_hegemony_ask_candidates`: warm→ladder upgrade, neutral→non-aggression-led, cool→NEW `friendly_gift` = a gold-lump-sweetened legal low-tier ask; every candidate legality+relation checked, cooldown-skipped → consecutive approaches genuinely differ, end-to-end pinned). **(3) E-CA-5 territorial honesty** — settlement offer `terms_summary` appends "Status quo: Britain retains Flanders, Amsterdam" derived from current controller vs `nation_starting_regions` across opposing war participants (cached `get_nation_regions`, GR8; fog-free per the diplomacy rule; third-party occupations listed too); pure display, ratification math untouched.
- **~~W6-9 "What does Europe intend?" (EXP-D1 + R117 + R132-80/20)~~ ✅ LANDED July 10, 2026 (second session)** (`test_w6_assessment_verb.py`, 25) — the audit's dead-ended phrase now opens the war room: a mock-parser keyword branch ("assess", "our situation", "state of europe", "where/how do we stand", "situation report", "what does europe intend") routes to the advisory desk BEFORE the proposal fallback (3 golden-corpus rows; `diplomatic_advisory` added to the CR-1 coverage gate), and the new `ADVISORY_KEYWORDS` → `assess_situation` arm (named target downgrades to the existing nation assessment) composes — **composition only, no new formulas, 0 DP/0 AP** — per-war trajectory prose from `build_active_wars` (score+trend phrase bands), the **coalition posture surfaced at last** (stored `strategic_posture` when a coalition is active, `get_coalition_posture` otherwise, + threat level/tier), the top-3 itemized `threat_sources_this_turn` (ledger humanization), vassal loyalty + autonomy-drift trend + the W6-3 `reason` cause from the recent event window, and **ONE recommendation** by the §11 priority table (losing war + terms available → seek terms; aggressive coalition + threat>60 → shore the weakest ally / court the weak link; vassal<40 → invest; else the ripest −10..40-relation opening with an open cooldown) **ending in an executable option** (R117): `expand_options` for diplomatic openings, the new `execute_suggestion` dialogue arm for `request_terms`/`invest_vassal` — direct calls into the same executors with their own self-charged costs (GR5/GR6), typed "do it"/"proceed"/"yes" keywords wired. Live-verified boot behavior became a test fixture note: the 1805 campaign legitimately boots at threat >60 with an AGGRESSIVE posture, so the assessment's first counsel is "shore up Spain, our least certain friend."
- **~~W6-8 The Spoils of War (EXP-E1)~~ ✅ LANDED July 10, 2026 (second session)** (`test_w6_estate_confiscation.py`, 26) — conquering a province that funds an ENEMY marshal's estate now poses the game's most Napoleonic choice, asked once AFTER plunder/secure on the same `capture_choice` pipeline (`pending_capture_choice.stage="estate"`, `dialogue_id` minted from the W6-0 counter via the new `dialogue_manager.mint_dialogue_id`; typed `confiscate`/`respect` join the pending-question router; a stale or wrong-stage answer is refused with the question restated): **CONFISCATE** = 2× effective-income windfall (the popup-promised number IS the charged number — stashed through), strip from `dotation_regions` (the existing ES-7 erosion machinery does the rest — no new erosion code), −10 relations with the holder's nation, the capturer's cautious marshals −1 trust ("property is sacred"), and the province passes `check_estate_eligibility` again — **"Endow Ney with the Duchy of Swabia" on Mack's old duchy is a named test** (the audit's exact dead end, reversed); **RESPECT** = serialized `world.respected_estates` `{region, marshal, nation, respecter}` — the ES-7 prune skips it, `get_satisfaction` keeps counting it (no shortfall → no erosion: the courtesy is real), and `respected_estate_mod` grants +5 acceptance with the holder's nation (cap 1/nation; settlement-gratitude template in `calculate_acceptance`; entries prune when the respecter loses the region or the estate returns home). **AI rule (GR5, both capture seams — instant + occupation-completion): confiscate when at war with the holder, respect otherwise**; an AI confiscating a PLAYER marshal's estate fires an immediate HIGH `estate_confiscated` notification (the prune's estate_lost never sees it). Events `estate_confiscated`/`estate_respected` walked through the campaign-log checklist (fog: region PARTIAL+, the ES-7 family rule). Godot: the capture dialog is stage-aware (CONFISCATE/RESPECT labels + windfall), `/capture_choice` chains the second popup, answers carry the rendered `dialogue_id`.

- **W6-7 commit 2 (ransom & release) ✅ LANDED July 10, 2026** — `prisoner_return` clause: a treaty DEMAND naming the captured marshal (the `marshal` key now rides the `_ratify_treaty` clause build; armistices are the live mid-war ransom vehicle); on ratification `release_captured_marshal` sends him home (own capital, 5,000 strength, morale 50) with a `marshal_released` event (checklist walked; CAMPAIGN_LOG_TYPES 99); the AI VALUES the demand at 500g — 800g for a major nation's marshal (capital-garrison-tier proxy) — via a dedicated branch in the acceptance demand walk (`DEMAND_VALUES` registry marker −15); **the peace auto-return is a single chokepoint in `set_diplomatic_state`** — ANY WAR/ARMISTICE→PEACE transition (bilateral treaty, common-peace settlement ratification, armistice expiry) returns ALL mutual prisoners; display + template rows added (label formatter is marshal-name-free by contract). Decide-in-session (spec §9.2): no new typed phrasing landed → no corpus row; recorded cuts stand (no escape mechanic; AI accepts, never initiates). `test_w6_marshal_fates.py` now 25.
- **W6-7 Marshal Fates (EXP-M1) — commit 1 (capture core) ✅ LANDED July 10, 2026** (`test_w6_marshal_fates.py`, 19) — broken armies carry a person-shaped stake: at the single forced-retreat seam (`_apply_forced_retreat_or_break`, fate check FIRST), a cornered marshal (post-battle strength <5,000, or the only retreat being W6-1 tier-5 desperation soil, or pure encirclement) faces the fate machinery — **encirclement = captured outright** (replaces the silent shatter), everyone else rolls **escape 60% / captured 40%** (combat RNG, seeded in tests); an **aggressive player marshal gets the last stand** (`pending_interrupt` `last_stand`, carries `marshal`, options fight_to_the_last / attempt_breakout — fight = one final defense at +25% that bleeds and HALTS the pursuer then captures the survivors; breakout = the roll at −10%; typed answers "fight"/"breakout" routed by the /command interrupt matcher; synchronous popup on player-turn battles); **aggressive AI marshals decide deterministically** (fight on homeland/capital-adjacent ground, else break out — GR5, Mack is capturable by the player, pinned). **Captured state**: serialized `captured_by`/`captured_turn`; held at the captor's capital at strength 0 (attrition elimination sweep guards prisoners); half the remaining men filter home to the owner's manpower pool by unit type; excluded from dispatch roster (new `dispatch["prisoners"]` line), marshal cards say "PRISONER of Austria since T3", muster/reinforcement/AI scans skip them; **ES-7 expectations freeze while captured** (grace clock reset — cheapest rule, pinned); `marshal_captured` + `last_stand` walked through the full event checklist (CAMPAIGN_LOG_TYPES 98; the W6-3 headline table already carried capture at weight 95). **Commit 2 (ransom clause + release paths) is the remaining W6-7 work.**
- **~~W6-6 Enemy marshals speak (EXP-M2)~~ ✅ LANDED July 10, 2026** (`test_w6_enemy_voice.py`, 18) — the men you fight have mouths: after any player-involving field battle the enemy commander gets ONE line in his register — new `backend/game_logic/enemy_voice.py` bank keyed (personality × situation: repelled_you / beat_you_attacking / lost_ground / forced_retreat / stalemate; 2+ variants each, ~40 authored lines), **named rows for the marquee enemies** (Mack "does not leave his ground", Kutuzov, Archduke Charles, Wellington "hard pounding", Blücher "Vorwärts") override the personality default; rotation is deterministic via W6-2's `battle_counts` (no RNG); attaches as `battle_report.enemy_voice` + a campaign-log one-liner suffix; garrison assaults/AI-vs-AI battles stay silent; display-only (GR6), nothing serializes; named DIPLOMATS remain Voice-Bible-owned (boundary pinned).
- **~~W6-5 The Literal Doctrine (user addition)~~ ✅ LANDED July 10, 2026** (`test_w6_literal_doctrine.py`, 20) — literal honed into a fantasy, not a gap, per the user's load-bearing steer ("generals who do what they're ordered"): **never-objects PINNED** (the R59/R153 trigger TODOs converted to a doctrine comment — `PERSONALITY_TRIGGERS[LITERAL]` deliberately empty; DESIGN_REFINEMENT rows → SUPERSEDED; a literal ordered into terrible odds raises no objection and gates through the W6-4 muster machinery instead); **order echo** — acknowledgment quotes the verbatim command ("\"Soult, march to Belgium.\" It will be done exactly, Sire.") and completion quotes it back with the outcome, via the new deterministic voice bank `backend/game_logic/marshal_voice.py` (2-3 variants per beat, rotation keyed on text+turn, no RNG); **the fidelity beat** — new `literal_fidelity` campaign-log + dispatch event (registered through the full checklist; CAMPAIGN_LOG_TYPES now 96) fires when a literal with an active order held while an adjacent own-nation battle raged / his PURSUE-SUPPORT quarry shifted / his MOVE_TO destination changed hands (pure narration, no interrupt, no trust change, cap 1/marshal/turn); **doctrine tells** — the marshal card states the doctrine, the dispatch status note appends "(to the letter)", order creation captions the 1-AP precision reward, and the Grouchy no-march line moved into the shared bank (variant 0 preserves the shipped line). CR-5's blessed ASK arm untouched (`delegation.py` not touched).
- **~~W6-4 Muster preview + standing orders (EXP-C1 + E-CA-4)~~ ✅ LANDED July 10, 2026** (`test_w6_muster_preview.py`, 17) — the audit's three worst surprises become the game's most characterful screen: **§6.1 muster block** on every direct player field attack (reason ladder mirroring the EXISTING reinforcement eligibility + Grouchy Rule, display map `MUSTER_REASON_DISPLAY`; fog-banded target strength — exact only at FULL; shared-casualty note for co-located friendlies; serialized `muster_hint_shown` first-use latch teaching standing orders); **odds band** via the extracted CR-5 single source (`objection_v2.inferred_attack_effective_ratio` — favorable ≥1.0 / even ≥0.7 / unfavorable, NO second formula); **§6.2 E-CA-4 gate**: even/unfavorable → the attack does NOT resolve — `muster_confirm` interrupt (carries `marshal`, options attack_anyway/cancel_order, `no_action_cost` on the gated call) resolved via `/strategic_response` (branch added BEFORE the strategic-order requirement — direct attacks have no order); favorable resolves immediately with the block prepended; AI (`_autonomous_execution`), `_strategic_execution`, counter-punch, defiance and post-objection paths all bypass (GR5); **§6.3** SUPPORT order creation now confirms the doctrine ("he will march to Ney's guns — he holds your written order"); **§6.4 pin**: a literal marshal with no SUPPORT still never auto-reinforces. 4 existing attack-helper tests updated with `_muster_confirmed` (they pin combat mechanics, not the confirm). **Live-verified — the audit's battle-1 exactly**: "Ney, attack Mack" → confirm fires, Mack banded "large force", Soult's row reads "awaits explicit orders and will NOT march — order 'Soult, support Ney' and he will march", attack_anyway resolves with the block.
- **~~W6-3 The Dispatch Rewrite (EXP-N1, the audit's top item)~~ ✅ LANDED July 10, 2026** (`test_w6_dispatch_rewrite.py`, 29) — the dispatch now TELLS the story it always had: **§5.1 headline** (fog-visible events scored by the blessed weights table — home-captured 100 … estate-eroding 55 — one prose headline + ≤2 sub-beats, `dispatch["headline"]`); **§5.2 danger flags** per marshal row (fog-legal co-located ≥1.5× via own intel only, morale <40, fell-back, 2-turn supply starvation — replaces the "Awaiting orders" lie); **§5.3 arc memory** derived from the last-5-turn event-log window, no new state (hunted_by / consecutive_defeats / fled_across; ≤3 lines, status_note upgraded); **§5.4 cause lines** — `vassal_loyalty` events now carry `reason` (dominant contributors named at emission: "puppet resentment, war weariness") + render in dispatch turn events; headline-aware Berthier closing note; the intel-report NO-INTEL wall collapses to "No word from N provinces beyond the frontiers of …(≤8)"; supply-attrition events mirrored into the event log (history for the starvation flag). Godot renders the headline block + warning-colored danger lines (dispatch_view.gd + main.gd). **Live-verified on the 1805 boot**: real headline "Bernadotte was mauled at Franconia: 5,742 men lost", Berthier answering it, danger "Morale failing (25)", and the arc "Hunted by Archduke Charles across 1 frontier — stands at Munich with 2,228 men" — the audit's exact un-narrated story, now told.
- **~~W6-2 Dynamic Battle Naming~~ ✅ LANDED July 10, 2026** (`test_w6_battle_naming.py`, 14) — serialized `WorldState.battle_counts` + `compose_battle_name` (single naming site in `_execute_attack`, composed BEFORE the event-log write): "Battle of X" → "Second…Twelfth" → "13th Battle of X"; **The Great Battle of X** at total engaged ≥80,000 (both sides + arrived reinforcers, pre-battle; Great REPLACES the ordinal); the name rides the battle event, the diplo `battle_records` (new `battle_name` field), the war HUD `recent_battles.name`, and the campaign-log one-liner leads with it. Garrison assaults/bombardments stay un-named; legacy events keep the classic form.
- **~~W6-1 Correctness B~~ ✅ LANDED July 10, 2026** — combat/report/movement/stats (`test_w6_retreat_doctrine.py` 10 + `test_w6_correctness_b.py` 18):
  - **BUG-CA-2 + E-CA-2 FIXED (retreat doctrine):** `get_safe_retreat_destination` gains **tier 5 — at-war soil is desperation-only** (never over any alternative; the Bernadotte 4-hop death-march class) and the **homeward bias** (homeland first → nearer capital → THEN away from attacker); explicit destinations ("retreat to Rhineland") are honored when adjacent+legal and **substitutions are named with the reason** (verified live: "Paris cannot be reached, Sire — it is not adjacent; Bernadotte falls back to Franconia instead"); the enemy-AI retreat fallback mirrors tier 5 (GR5); the stated target survives the objection round-trip.
  - **BUG-CA-3 FIXED:** `grant_dotation` treats a live-LLM-guessed region (absent from the raw text) as missing → asks with the eligible-estates list; AI programmatic grants unaffected.
  - **BUG-CA-4 FIXED:** battle-report remaining = original − casualties (live: 24,000−6,884=17,116).
  - **BUG-CA-5 FIXED:** reinforcement observation branches on outcome (stalemate → "saved the line, no more"; loss → "not enough"); labels "Strategic orders"→"Forced march momentum (order completed)", literal hold→"Immovable (literal hold)".
  - **BUG-CA-6 FIXED:** dispatch intel dedup prefers recency first (stale FULL can't beat this turn's PARTIAL).
  - **BUG-CA-9 FIXED:** arrived reinforcers increment battles_won/lost + reset idle; new serialized `Marshal.last_battle_turn` (SAVE_FORMAT row added) feeds W6-3 arc memory.
- **~~W6-0 Correctness A~~ ✅ LANDED July 10, 2026** — dialogue identity + typed-answer routing (`test_w6_dialogue_identity.py`, 27 tests; suite 12,001/1):
  - **BUG-CA-7 (P1) FIXED:** every dialogue gets a serialized monotonic `dialogue_id` (stamped at `dialogue_manager.push/replace/preempt`, mirrored onto `popup_payload`, migrated on load; `next_dialogue_id` on the manager round-trips). `/respond_to_diplomatic_dialogue` accepts `dialogue_id`; a mismatch with the current top is REFUSED (`stale_dialogue=True`, in-voice notice, current dialogue re-attached) — Godot popups (`incoming_proposal_popup` data path, `proposal_confirm_popup` index + structured-params paths) now send the id they rendered via `api_client.send_dialogue_response*` optional arg; the typed terminal path omits it. The reversed `ai_proposal_accepted/rejected` log direction fixed ("We rejected Saxony's..." — and the internal `counterparty_reversal` tag no longer renders as a motive).
  - **BUG-CA-1 FIXED:** pre-parse pending-question router in `/command` (after clarification/interrupt, before CR-4): exact `trust/insist/compromise` → objection handler (tactical AND strategic pending states), `plunder/secure` → capture choice, bare digit / option action-id → the pending dialogue (byte-identical to the popup buttons via extracted `_respond_to_objection_sync` / `_respond_to_dialogue_sync` helpers). Tokens with nothing pending fall through untouched (corpus unaffected — parser-eval suite green).
  - **BUG-CA-10 FIXED:** both "Please choose an option (1-N)" re-prompts enumerate the numbered option labels.
  - **BUG-CA-8 FIXED:** the `_include_popup_passthroughs` re-mount safety valve now routes through `_build_pending_envoy_popup_from_dialogue` (popup_payload-first, `world.diplomats`-resolving fallback) — no more "Unknown diplomat".
  - **Live-verified** against the running 1805 boot: wrong-id answer → stale refusal + re-attach; correct id applies; router fall-throughs clean; campaign log shows "We rejected Prussia's open borders proposal".

### ✅ Wave 6 APPROVED + build spec authored — July 10, 2026 (same day as the capstone; docs-only session, NO feature code)

**The user approved the ENTIRE Wave 6 plan in full** — all 6 expansions, all 6 escalations, all 10 BUG-CA fixes — **and added two items at the gate: Dynamic Battle Naming and a Literal Doctrine hone** (user steer, load-bearing: literal marshals need not object — the fantasy is *"generals who do what they're ordered"*; engagement comes from visible fidelity, precision rewards, and consequences you were warned about — this formally supersedes R59/R153's literal-objection TODOs). Deliverable: **`docs/WAVE6_FUN_FACTOR_SPEC.md` v1.0** — a self-contained, new-session-ready build spec: 12 ordered commit-sized slices (W6-0..W6-11), per-slice player-visible outcomes / verified code seams / tests / docs rows, blessed default numbers with tuning bands (in-band tunes need no new gate; structural changes escalate), cross-slice contracts (no new LLM calls anywhere; every interrupt carries `marshal`; serialization/GR8/fog/voice-ownership rules), and a measured definition of done (re-run the memo's playtest loop; narration ≥7 + combat legibility ≥7 REQUIRED). Seam grounding done this session: battle naming is a single site (`combat_executor.py` ~3661); **the Grouchy Rule already exists** (`_calculate_reinforcements` — literal marshals reinforce only under a relevant SUPPORT/PURSUE order), so W6-4/W6-5 surface an existing rule; retreat tiers live in `world_state.get_safe_retreat_destination` (~2931); recruit cost in `economy_executor._calculate_recruit_cost` (~177); `battles_won` bumps only at `combat.py` 582/594; dispatch staleness root cause = rank-over-recency dedup in `_build_intelligence`. Routing updated: ROADMAP gained the **W6 row (▶ RUNS NEXT)** + EC row marked complete; DESIGN_REFINEMENT Wave 6 → APPROVED with slice mapping; CLAUDE.md queue updated. **▶ NEXT SESSION: open `WAVE6_FUN_FACTOR_SPEC.md` §0 (bootstrap) and take W6-0 (dialogue identity, P1).** The MC design gate follows the wave (unchanged — W6 does not preempt MC-1 ability authoring).

### ✅ Creative / fun-factor capstone (§8) — COMPLETE July 10, 2026 (Fable-led; the post-EC scored assessment)

The `AUDIT_GUIDELINE.md` §8 capstone ran as designed on the post-EC build (`fd97b6f`): a **live outsider's-seat playtest** (`LLM_MODE=anthropic`, 5 turns of the shipped 1805 campaign — delegations, an objection cycle, 4 battles, retreats/pursuits, conquest + capture choice, estate endowment attempts, recruitment, incoming/outgoing diplomacy, a live British settlement offer) plus two code-evidence sweeps (present-but-inert systems; memorable-moment generators). **Memo: `docs/audits/CREATIVE_AUDIT_2026_07_10.md`** — scored pillars + one highest-impact improvement each + a ranked expansions section (the user pre-authorized adding future items and revising past ones).

- **Verdict in one line:** *the game generates genuinely great stories and then doesn't tell them* — the command fantasy (CR-5/5b, objections, the guided proposal desk) is the strongest it has ever been; **war narration (3.5/10) and battle legibility (4.5/10)** now lag every other system. Pillar scores: command 7.5 · marshal drama 6 · combat legibility 4.5 · narration 3.5 · economy 6 (up from ~4.5 pre-EC) · diplomacy 6.5 (outgoing 8 / incoming 4) · world aliveness 7.5.
- **Live exhibits:** Bernadotte's un-narrated 4-country death-march (17,000 men → 316, ending in at-war Russia — auto-retreat pathing defect BUG-CA-2); the dispatch missing every headline while its intel table went stale (BUG-CA-6); the best line of the session — *"Soult awaits explicit orders and did not march to the sound of the guns"* — revealing the personality-gated reinforcement rule three battles after it started deciding them; Austria endowing Mack as "Duke of Franconia" (AI ES-7 alive); five identical open-borders proposals in five turns (R155/R156 confirmed live).
- **10 correctness defects routed** (NOT fixed, per §8 discipline) → **`BUG_FIXES.md` §Creative-Audit Findings** — headline: **BUG-CA-7 (P1)** a dialogue response can land on a *different* dialogue than the one presented (Britain's settlement offer answered → Saxony's never-seen proposal rejected). **4 trivial legibility slips fixed inline** (camelCase marshal keys humanized in status/dispatch; Talleyrand's nation list uses display names; indefinite-article grammar via new `display_names.with_indefinite_article`; the objection guard no longer leaks `/respond_to_objection` into player prose) — pinned by `tests/test_creative_audit_legibility_fixes_2026_07_10.py`.
- **Wave 6 filed in `DESIGN_REFINEMENT.md`** — 6 ranked expansions (EXP-N1 Dispatch Rewrite "Berthier tells the story" = the top-ranked item of the audit · EXP-M1 Marshal Fates capture/ransom/last-stand · EXP-C1 muster preview + standing order, the Grouchy Moment's landing substrate · EXP-E1 estate confiscation · EXP-M2 enemy marshals speak · EXP-D1 strategic assessment verb, the recommended first Talleyrand-Desk slice) + 6 escalations (E-CA-1 attacker morale-grind asymmetry = the live shape of the meat-grinder · E-CA-2 retreat doctrine · E-CA-3 war-priced recruitment for EC pass 2 · E-CA-4 direct-order odds warning · E-CA-5 settlement territorial legibility · E-CA-6 incoming-proposal voice/variety) + live-evidence revisions to R154 (breaker EXISTS — re-scoped), R59/R153, R129/R131/R132, R155/R156, R117 (absorbed into EXP-D1).
- **This closes the full audit arc** (correctness sweep → econ eval → EC build → §8 capstone). **▶ NEXT: the Marshal Content Pass design gate** — this audit is the strongest evidence yet for it (live: Ney ships with `ability_name:""`, flat all-5 skills, zero relationships).

### ✅ Econ eval (§0.7) — COMPLETE July 9, 2026 (Fable's independent pre-build read; memo delivered to the EC-2 gate)

The `ECONOMY_REVISIT_SPEC.md §0.7` evaluation ran same-day on the audit's whole-codebase context: a fresh single-mind read of every recorded economy decision (§0/§0.5/§0.6 + Appendix A), every load-bearing code claim re-verified directly against master `c5e411e` (income/upkeep/regen loops, trust substrate, tribute, CS, AI admin ladder, bankruptcy, `nation_starting_regions`) rather than inherited from the July-7/8 workflows. **Memo: `docs/audits/ECONOMY_ECON_EVAL_2026_07_09.md`** — 23 explicit verdicts, no recorded decision left silent. Documentation-only session; **no code, no §0.6 edits** (per §0.7.3 the spec is updated only after the user accepts a change at the gate). Headlines for the gate:

- **CONCUR with most of the record** — the diagnosis, the ES-7 reframe (enthusiastically — CK title-expectation precedent + the post-Tilsit dotation waves), the ES-10 cut, EC-6 sandbox, EC-1/EC-4, EC-5 Option B, EC-7 dated trigger, soft-goal open-ended, E6 mercy extension, the AI fee-in-executor catch, and the band's 55–70% range (genre-consistent).
- **DISSENT 1 (the headline):** the E5 constants make ES-7 **mathematically broken as specced** — max achievable satisfaction with two best non-capital estates ≈ 105–150 vs `EXPECTATION_CAP` 300, so an 8-win marshal erodes −3/turn *forever* and paying cannot stop the bleed (falsifies the reframe's core promise for exactly your best marshals). **Recommended fix: full-income redirect** (satisfaction = the estate's full `eff_income`; delete the 0.30 skim constant) — one top province ≈ one legendary marshal's cap, matching the spec's own "~one province tier" gloss. Plus: grace 1→2, REP_STEP validated against measured win rates (defensive wins + every coordination participant increment `battles_won`), grant scope = conquered non-homeland provinces, estate exempt from occupation cost.
- **DISSENT 2:** the E1 band's turn-1 anchor ("starting-army France absorbs ~55–70%") is **unreachable by the blessed pass-1 pair** — ES-2 ≈ 0 and ES-7 = 0 at campaign start; only ES-3 moves the turn-1 number. **Recommended: promote ES-3 into the EC-2 pass-1 landing** and tune the band once against the stacked set (§0.6.4 already defines it that way).
- **SIMPLIFY ES-2:** replace the `integration_turns` ramp + autonomy factor (which duplicates the existing stability ramp — capture already yields 0% → 25% → 75% → 100%) with a **stability-tier-keyed occupation cost on non-homeland provinces** (Hostile ~50% of base income · Unrest ~35% · Settling ~20% · Stable ~10% permanent floor) riding the serialized `nation_starting_regions` substrate — zero new fields, recapture-reset and marshal-pacification free via existing stability rules, plunder finally gets a recurring price, and every conquest becomes the hold / vassalize / endow triangle ("Territory as Command Dilemma" as a game rule).
- **SIMPLIFY E2:** cut pool-cap scaling from pass 1 (ceilings nobody reaches once rates are fixed) and keep `INFANTRY_BASE_REGEN` flat **deliberately** — flat regen is secretly an anti-snowball rubber band; scaling it with size would help the leader.
- **Expansions (owned recommendations):** EC-5a riders — couple British subsidy capacity to Britain's actual treasury (closes the CS → subsidy → coalition strategic loop) + a player-facing CS activation surface (members boot empty; balancing Option B against dead code otherwise); ES-4 pass-2 "Grand Works with faces" framing option; MC-ES7b "The Reckoning" (peace-treaty expectation reckoning) parked for the MC gate.
- Audit escalation triage: the July-9 sweep produced **zero economy escalations** — nothing to fold in.

**✅ EC-2 GATE BLESSED July 9, 2026 (same day):** the user accepted the memo's §8 decision sheet **in full** — blessed numbers E1–E6 + four structural amendments (ES-7 full-income redirect · ES-2 stability-tier occupation shape, zero new serialized fields · ES-3 promoted into the pass-1 Track-2 landing · the conquered-only/occupation-exempt **endow triangle**) folded into **`ECONOMY_REVISIT_SPEC.md` §0.6.7 (authoritative over §0.6.2/§0.6.3/§0.6.5 where they conflict)**. **▶ NEXT: the EC build session runs §0.6.3 as amended** — Track 1 (~~S1 ES-1a art re-key+drop~~ **✅ LANDED July 9, 2026** — `terrain=='urban'` → `region_type ∈ {city,major_city,capital}` at rate 80 with a hard 600/turn total cap in `get_manpower_regen_rates`; live-scenario verified: all majors cap at 600 (France 1,110 uncapped), one-arsenal minors 230, no nation >600; `test_economy_es1_manpower_regen.py` 7 tests, spec §0.6.3 S1 row updated · ~~S2 ES-1b cavalry+stables~~ **✅ LANDED July 9, 2026** — `PLAINS_CAVALRY_REGEN` 500→150 + the summed plains+stables bonus hard-capped at 1,500 (`CAVALRY_REGEN_BONUS_CAP`; stables folded in — a cap-bound nation building stables gains nothing); pool-cap scaling CUT per §0.6.7 E2; live-scenario verified: France (24 plains) 12,250→1,750/turn, minors alive (Sardinia 400, Saxony 250), every nation refills the 30k pool in >10 turns; `TestES1bCavalryRetune` 7 tests (suite 11,803) · ~~S3 ledger-GR8 fix~~ **✅ LANDED July 9, 2026** — `_build_economy` tribute now rides the cached `get_nation_regions` index (the old derivation nested a full region scan per vassal); rode along: the `get_diplomatic_preview` tribute estimate had the same scan + a flat 50g/region value bug — now mirrors `process_vassal_tribute` exactly; source-pin in `test_scale_readiness_phase2.py` + preview behavior test (suite 11,805) · **S4 EC-6a sandbox toggle — NEXT, closes Track 1**), then Track 2 = S5 ES-3 → S6 ES-2 → S7 ES-7 with ONE stacked two-sided band test as acceptance.

### ✅ Comprehensive Codebase Audit — COMPLETE July 9, 2026 (Fable-led correctness sweep)

The full §5–§7 correctness sweep (`docs/AUDIT_GUIDELINE.md`) ran end-to-end in one session on known-green master (`2efcbe2`, baseline 11,780/1 verified before the first fix), one committed chunk per §10 pass. **7 fixes, 0 open escalations** — every finding fell inside the fix-vs-escalate boundary. Full log: **`docs/audits/AUDIT_2026_07_09.md`**. Commits: `d1eff95` (§7.1) → `8c20f1f` (§6.1) → `d980b9a` (§6.2–6.4) → `10aea82` (§6.5) → `d34959d` (§7.2–7.3) → `c354f82` (§7.4–7.5) → `03b36f5` (§7.6–7.9) → this close-out (§7.8).

- **Fix 1.1 (player-facing):** the 1805 campaign booted turn 1 with **4 DP instead of 5** — `from_dict`'s missing-key fallback was a stale hardcoded 4 contradicting the constructor + the `calculate_dp` formula; now reads the world's construction-time value (item-3 convention).
- **Fix 2.1 (player-facing copy):** combat personality messages captioned ANY aggressive marshal's bonus "Bravest of the Brave" (Ney's ability) and any cautious defender "Iron Marshal" (Davout) — 4 aggressive / 13 cautious marshals share those paths on the 1805 roster. Labels now name the personality.
- **Fix 2.2 (player-facing, wrong-side Berthier):** `coordination_context` carried attacker-side data only, so when the player DEFENDED, an enemy combined-arms triangle (P0.5) or enemy hostile/devoted politics (P5.5/P9.5/P12) was narrated as "our side". Context now side-tagged; `_pick_observation` selects the player's side.
- **Fix 2.3:** the strategic first-step "no alternate route" order break skipped the paired `holding_position`/`hold_region` clear (leaks the +15% literal-hold defense modifier).
- **Fix 3.1 (player-facing copy):** the vassal-created dispatch line hardcoded "under French protection" — but AI lords reach both creators (treaty ratification / settlement clauses); the template now names the actual lord.
- **Fix 3.2 (§4 known fix):** seeded the RNG-flaky `test_movement_stops_before_enemy_region` (20/20 deterministic).
- **Fix 4.1 (seam hygiene):** removed the unused bare-name import of `calculate_common_peace_acceptance` in `settlement_baseline.py` — the exact bare name the scorer-seam contract forbids.

**Swept clean (highlights):** world round-trip incl. a JSON pass on 4 world shapes; the enforcement test's underscore blind spot hand-covered; two-battle-path parity; `_COORDINATION_FIELDS` complete; all 36 order-clear sites hold-paired (or safely so); 15/15 interrupt builders carry `'marshal'`; parser eval 407/407; defiance + diplomatic-defiance + coalition sign audits; the three never-audited subsystems (`diplomatic_defiance.py`, `war_contribution.py`, `settlement_reactions.py`) all sound; nation data contract 20↔20; scorer seam late-bound at all 4 sites; live-backend seam verification (no `new_state`, no camelCase leaks, port pinned, topology 126/ints/20 capitals). MC-0 confirmed already landed (`685bfd1`). **Final: 11,789 passed / 1 skipped, ruff clean.** The audit closed into the econ eval per `AUDIT_GUIDELINE.md` §11 — **✅ ran same-day** (see the entry above; memo `docs/audits/ECONOMY_ECON_EVAL_2026_07_09.md`).

### ✅ CR-5 whole-slice audit — LANDED July 7, 2026 (post-completion)

CR-5 (Personality-Biased Disambiguation) was already COMPLETE (all 4 phases). A **whole-slice adversarial audit** (9-dimension find→verify workflow + a **live-backend behavioral probe** against `claude-haiku-4-5`) surfaced **8 confirmed defects, ALL FIXED** the same day with regression tests (CR-5 suite 86 → 103; full suite **11710 passed, 1 skipped**; ruff clean; the 3 player-facing fixes re-verified live):

- **L1 (HIGH, live-only — found by the live probe, not the static dimensions):** the aggressive-delegation **bad-odds interrupt was unanswerable via the real UI**. The stored `pending_interrupt` dict omitted a `marshal` key, so on the synchronous `response.pending_interrupt` path the Godot `interrupt_popup` sent the literal `"Marshal"` to `/strategic_response`, which 404'd (*"Marshal 'Marshal' not found"*) — Confirm/Hold/Cancel dead. Systemic across all 5 strategic-interrupt builders (the enemy-phase report-list path masked it). **Fix:** stamp `"marshal": marshal.name` on every stored `pending_interrupt` (serialized). Re-verified live.
- **F1 (MED):** comma-less `"Marshal Soult deal with Mack"` dropped the delegation — `_ADDRESS_RE` required a comma. **Fix:** comma optional (`get_marshal` still validates).
- **F3 (MED):** camelCase enemy key (`ArchdukeCharles`) leaked into ASK/cautious/bad-odds copy (R7). **Fix:** new `display_names.humanize_entity_name` chokepoint; `_resolve_target` matches raw-or-spaced and displays humanized (raw name still keys the executor), so the natural spaced form also resolves.
- **F2 (LOW):** live-mode delegation poisoned CR-4 `command_history` carryover with the LLM's distrusted target. **Fix:** router overwrites the entry with the authoritative target.
- **F4/F5/F6/F7 (LOW):** guardrail-(a) test + router-side-enforcement doc; rewrote a vacuous one-modal assertion; region-objective table coverage; AC-2 corpus wording corrected to the router tier.

Two findings REFUTED (correct behavior): `inferred_attack_favorable` folding only fort/terrain is spec-conformant (§6.3c(iii)); the unused `BATTLE_ACTIONS` constant is harmless. Full record: `COMMAND_ROBUSTNESS_SPEC.md` §6.10. **Verdict: CR-5 sound as shipped after these fixes.** Next: CR-5b (Flavor Echoing).

Open deferred map work, all homed (Golden Rule 9): **DEF-1** Roster Voices slice (15 chancery-fallback diplomats), **DEF-3** Economy Pass (per-province income; the Slice 8 smoke logged France at ~3.4k gold/turn on 28 provinces as a data point), **DEF-4** Phase 5.2/5.3/5.6 (measured NOT forced at Slice 8; 15× campaign-turn tripwire standing), **DEF-5** naval spec, **DEF-12** full map-modes system (gate-owned), **DEF-13** the dated **UI-Scale Mini-Pass** (Slice 9 decision — content_scale_factor + native-map compensation + screen-space markers; baseline pinned by `test_def13_fixed_hud_baseline_pins`), and the BUG_FIXES.md mock-parser bare-command entry (dev-mode only).

## Real-Map Cutover — ✅ COMPLETE (was: re-sequenced ahead of the settlement queue, user decision June 22, 2026)

The commissioned Europe map art arrived as a **layered PSD** (`map final1.psd`). Forensics on the file: it is **hand-made, not AI** — a 35-layer project with `sketch counties` layers, a dedicated `County Colors` fill layer, separate inside/outside/ocean border layers, a `letters` label layer, working notes, and a hidden `Map_Napoleon_Total_War` reference underlay.

**Landed this session (generation + validation only — no game logic touched):**
- `tools/build_region_key_from_psd.py` — stdlib-only, repeatable generator. Extracts the `County Colors` layer, snaps anti-aliased fringe to flat anchors, connected-component-labels to guarantee unique per-province colors, composites at the layer offset onto a 2560×1600 canvas with sea = pure black.
- `assets/maps/europe_lookup.png` — flat region-key, **126 provinces**, pixel-aligned to the visual. (79 KB — flat colors compress tiny.)
- `assets/maps/europe.json` — 126-region **draft** registry (placeholder names `Region_NNN`, all `wired:true` for the smoke). Force-added like the placeholder JSON; PNG binaries stay local per the `assets/` gitignore convention.
- `assets/maps/europe_visual.png` — the terrain export (`map final 1.png`, 2560×1600).
- Godot smoke scene: `scenes/europe_map_smoke.tscn` + `scenes/europe_map.gd` (overrides the §4.2 bitmap hooks, drives positions from the registry, suppresses marker nodes, shows hover/click province names).

**Validation:** `tools/validate_province_map.py` against the three assets → **`PASS: no findings`** (0 errors, 0 warnings).

✅ **Map Slice 2 LANDED (July 1, 2026)** — the 126-province historical-naming + 1805-ownership hand-authoring pass is complete in `europe.json`: every province carries a unique historical **name** (no `Region_NNN` left), a 1805 **`starting_controller`**, valid **terrain**/**region_type**, image-derived **is_coastal** (86 coastal / 40 inland), and **is_capital**. The **discovered 1805 roster is 20 nations** — 10 majors (France [player], Britain, Spain, Portugal, Austria, Prussia, Russia, Ottoman, Sweden, Denmark) + 10 minors/clients (Naples, Bavaria, Papal States, Sardinia, Holland, Hanover, Hesse, Kingdom of Italy, Switzerland, Saxony), each with exactly one owned capital (Britain=real London; Russia/Ottoman/Sweden carry frontier/edge proxy capitals). **12 hand-authored sea links** connect the island components to the mainland. Validator PASS `--strict` (0/0). **M4 + M5 validator hardening IMPLEMENTED** (omitted-vs-empty `adjacent` distinction; new `DUPLICATE_ADJACENCY_ENTRY` warning + on-save de-dupe). New `tests/test_europe_registry_data.py` (24 tests) + Slice-2 gameplay-field validator checks; full suite **`10560 passed, 1 skipped`**; ruff clean. The owner map was visually QA'd via an owner-colored overlay before finalizing; the classifier/overlay scaffolding was throwaway (deleted) — `europe.json` is the committed deliverable.

✅ **Slice 2.5 — ROSTER DESIGN GATE BLESSED (user, July 1, 2026)** and ✅ **Slice 3 LANDED the same day.** At the gate the user chose **real historical vassals/masters**, **accepted the authored proxy capitals**, and asked for **realism** on North Africa. **Blessed roster:** 17 independents (France [player], Britain, Russia, Austria, Prussia, Spain, Ottoman, Sweden, Naples, Portugal, Denmark, Bavaria, Saxony, Hanover, Hesse, Papal States, Sardinia) + **3 vassals of France** — the only genuine 1805 French satellite states: **Holland** (Batavian Rep.), **Kingdom of Italy** (Napoleon as King), **Switzerland** (Helvetic), all `autonomy=satellite`. Bavaria/Saxony/Hanover/Hesse were sovereign in autumn 1805 → **independent** (allies/occupation are modeled via diplomacy, not vassalage). **Proxy capitals accepted:** Britain=London (retires Netherlands proxy), Russia=Vilna, Ottoman=Constantinople, Sweden=Stockholm, Denmark=Copenhagen. **North Africa:** Algiers + Egypt sliver stay Ottoman-owned (the art never split Morocco/Tunis/Tripoli into their own provinces).

**Slice 3 wiring (backend config only — no map cutover yet):** the 20-nation roster is a **scenario-scoped** surface in `backend/nation_config.py` (`EUROPE_ROSTER`, `EUROPE_NATION_CAPITALS` [matches `europe.json` `is_capital` exactly], `EUROPE_VASSAL_WEB`, `EUROPE_NATION_GOLD`/`EUROPE_BASE_ACTIONS`/`EUROPE_NATION_AUTHORITY` + `get_europe_runtime_nations`/`build_europe_*`/`get_europe_capital`/`get_europe_vassal_web` builders) that **never perturbs the legacy 5-nation globals** the ~275-file gameplay fixture + `settlement_scoring.py`'s Britain→Netherlands proxy depend on (amendment N1). Additive-only extensions to the pure `.get()` lookups: `NATION_POWER_TIERS` (+8 minors incl. the `Denmark` registry key), `NATION_DESIRE_PROFILES` (+16 so no Europe nation degrades to empty AI desires), `TALLEYRAND_COMMENTARY` (flavor for Russia/Spain/Ottoman; rest use `_default` — bespoke voice is owner-row **DEF-1**), Godot `utils.gd` `NATION_COLORS` (+13). `backend/models/diplomat.py`: `_EUROPE_EXTRA_DIPLOMAT_DEFINITIONS` (15 new — named ministers where documented, chancery persona otherwise, all chancery-fallback voice) + `create_europe_diplomats()`. **`NATION_HONOR_BIAS` deliberately NOT extended** — it multiplies live reliability-delta math (not a `.get()` lookup) and broke reliability fixtures when seeded; Europe honor bias is deferred to the 1805 Scenario Setup / balance pass. New `tests/test_europe_roster_config.py` (18 tests — roster size, registry-capital consistency, capital ownership, tiers, diplomat/desire-profile coverage, covet-province validity, vassal-patron validity, economy/color coverage, **legacy-global immutability**); full suite **`10578 passed, 1 skipped`**; ruff clean. **The live game still runs the 19-region/5-nation world — no cutover yet.**

✅ **Map Slice 4 LANDED (July 1, 2026)** — the Europe region set is now a constructable, turn-stable alternate backend world (`docs/MAP_IMPLEMENTATION_PLAN.md` §"Slice 4"). `create_europe_regions()` (in `region.py`) builds the validated 126-province world from the SAME `europe.json` the renderer reads: Region objects keyed by historical **name**, `adjacent` id-lists translated to names (symmetric, matches the registry), income from `REGION_TYPE_INCOME`, supply/garrison from the `Region` tables, and **`grid_position` via centroid spatial-rank** (amendment N4 — unique (row,col) for all 126, N/S/E/W-preserving). A new optional serialized `Region.grid_position` carries it (legacy reads it from `REGIONS_DATA` → exact parity), and `resolve_direction` now prefers the live region object's `grid_position` (world-scoped, so Europe/legacy never collide on a shared name) with a safe fallback to `REGION_POSITIONS`. The **`WorldState(sovereign_map="legacy"|"europe")` seam (G1)** selects regions + the scenario-scoped roster (Europe's own capital map/controllers/enemy roster/gold/AP/authority + `create_europe_diplomats()` + the 3 French satellite vassals via `_seed_europe_vassals()`); `WorldState()` still **defaults to legacy** (the ~275-file fixture untouched → the Slice-5 cutover is a reversible flag flip). Europe army placement + the full 1805 diplomatic matrix are deferred to the **1805 Scenario Setup gate** (the Europe world starts army-less — honest + turn-stable). New `tests/test_europe_world_construction.py` (17 tests incl. legacy-immutability); full suite **`10595 passed, 1 skipped`**; ruff clean. **The live game still runs the 19-region/5-nation world — no cutover yet.**

✅ **Map Slice 5 LANDED (July 1, 2026) — backend game cutover: a fresh backend game IS the 126-province Europe world at the API layer.** `backend/main.py` gains `_resolve_sovereign_map()` (the **`SOVEREIGN_MAP` env flag, default `europe`**, validated + warned fallback, read per-call) and passes it through `_build_new_world()` into the G1 seam — module-load `world`, `_reset_world_state()`, and `/new_game` all build the Europe world (20-nation roster, France player, 3 French satellite vassals, army-less pending the 1805 Scenario Setup gate). **`/map_topology` serves the ACTIVE world's graph** (126 provinces, Britain=London capitals map; the 19-region payload under rollback) instead of module `REGIONS_DATA`. **(G1) rollback drilled live**: an env-flip server restart restored the 19-region game (19 regions, Britain=Netherlands), then Europe again — no code change. **DEF-2 landed**: `save_manager.FORMAT_VERSION` 2→3; pre-cutover (v1/v2) saves fail with a clear versioned message (no crash); `test_save_load.py` case added. **Map-contract tests migrated to Europe**: `test_map_topology_endpoint.py` (registry-exact 126-province payload + bilateral invariant + unique grid cells + rollback case), `test_map_consistency.py` (connected/bilateral/no-self/no-dupe/batch-asymmetry over `create_europe_regions()`; map.gd placeholder guards stay until Slice 7), `test_map_bitmap_contract.py` (fixtures keyed off `europe.json`). **New `tests/test_map_slice5_cutover.py` (11 tests)** incl. the **(G2) legacy-fixture immutability guard** (frozen literal snapshot of all 19 regions' names/owners/adjacency + the 5-nation capital map); `test_restart_flow.py` pinned to legacy via the flag; conftest autouse isolates `SOVEREIGN_MAP` from dev shells. **Follow-up fold (same day):** the post-land verification sweep caught two latent Europe-world bugs — `capture_region`'s R16 threat check and the `allied_region_restored` lawful-owner lookup read the legacy module `get_starting_controllers()` instead of the world's own starting map (Europe-only province names always missed → recapturing own territory would accrue +2 threat; restoration credit resolved against the wrong map) — both re-pointed at `self._starting_controllers` (the `world_state.py:1902` fallback pattern) + a Europe-only-name regression test (Berry/Silesia) for the capture-threat path; the `allied_region_restored` restoration path needs a real Europe war + treaty cession to behavior-test, so its Europe-world test is **owned by the 1805 Scenario Setup gate** (called out in that gate's Tests line in `MAP_IMPLEMENTATION_PLAN.md`). Validator PASS `--strict`; live curl verification (`/new_game` → `/map_topology` = 126 provinces, Paris adjacency correct; env-flip rollback restart = 19 regions). Full suite **`10609 passed, 1 skipped`**; ruff clean. Gameplay tests stay on the untouched legacy `WorldState()` fixture. `docs/SAVE_FORMAT_REFERENCE.md` updated (v3 history + `sovereign_map`/`grid_position`/`is_coastal` rows).

✅ **1805 Scenario Setup DESIGN GATE BLESSED (user, July 1, 2026) — all 8 open decisions approved as recommended.** Gate input was a 10-agent research workflow (3 web-history researchers, 4 codebase readers, synthesis, 2 adversarial verifiers — history + buildability, both pass-with-corrections, corrections folded) producing the full researched 1805 opening draft — **§"Researched 1805 opening draft" in `MAP_IMPLEMENTATION_PLAN.md`**: Sept 25, 1805 anchor; **war already underway with exactly Britain/Austria/Russia** (Sweden + Naples coalition-committed but at PEACE, joining in play); 21-marshal verified roster (Wellington NOT defensible → **Moore**; the anachronistic legacy eight dropped from the scenario; Ulm set piece on the Swabia chokepoint; Russia as an arrival clock on Podolia/Volhynia; Ottoman commander at Karaman per the history verifier); Third Coalition pre-seeded (Britain leader, exact live `coalition.py` contract keys, war via `ensure_war_instance_for_pair`); relations re-based to the live −100..+100 scale; Naples de-jure-neutral double game; Hanover registry-true armyless; Mack on Bavaria-owned Swabia (smoke-test owed); Austria↔Russia ALLIANCE as the Russian passage mechanism; live-three personalities only. Authoring rides `WorldState.from_scenario` (N2 — note the live method name is `from_scenario`, not `from_scenario_file`) with the default-to-PEACE + exceptions matrix (N3).

✅ **1805 Loader + Constants PRE-SLICE LANDED (July 1, 2026)** — all 8 approved items + the `starting_wars` loader contract (`tests/test_map_1805_loader_preslice.py`, 40 tests; suite **`10649 passed, 1 skipped`**; ruff clean; 3 mock-world/back-compat test repairs: the balance-patch `nation_starting_regions` pin re-pinned to the new derivation, the settlement shim + MagicMock capitals sites use the attribute-fallback idiom with a real-dict guard): **(1, CRITICAL)** `validate_runtime_nation_support`/`validate_scenario_runtime_support` are **world-scoped** — `sovereign_map: "europe"` payloads validate against `EUROPE_NATION_CAPITALS` + the Europe diplomat cast + EUROPE_* economy overrides (the legacy Venice/Milan rejection contract untouched, `test_session7_backend_hardening` still green); **(2)** `from_scenario` injects the validated 126-province `create_europe_regions()` world when a Europe scenario omits `regions`, and injects NO legacy marshals (army-less honest default); **(3)** every `from_dict` omitted-key fallback now reads the WORLD'S OWN construction-time value instead of a legacy builder (nation_gold else-branch, manpower backfill, enemy_nations, nation_actions, nation_authority, diplomats, vassals — the 3 seeded satellites survive omission; `nation_starting_regions` derives from loaded control instead of `{}`) — bit-identical for legacy saves; **(4)** `SOVEREIGN_SCENARIO=<path>` env hook through `_build_new_world()` — import-time bootstrap and `/new_game` load the scenario via `WorldState.from_scenario`, failing LOUDLY on a missing/invalid file (conftest gained the third autouse env-isolation fixture); **(5)** `EUROPE_MANPOWER_POOLS` (nation_config) — all 20 nations, three pool types, sized for 1–2 rebuilt armies, wired into `__init__` + the world-scoped from_dict backfill; **(6)** Europe `max_turns` = **60** (legacy stays 40; from_dict fallback world-scoped; the `test_serialization` 40-pin holds); **(7)** ALL live legacy `NATION_CAPITALS`/`get_starting_controllers()` reads re-pointed at `world.get_nation_capital()`/`world._starting_controllers` — not just diplomacy.py's 11 sites (war-score capital ±30 [Vienna/London captures move score — test-pinned], liberation targets, DP regen no-capital penalty, military supremacy, deal-balance capital doubling, territory-demand pricing, war-objective targeting, treaty naming, friendly-retreat) but the whole live defect class: `diplomatic_executor` set_war_purpose, `vassal.py` satellite garrison loyalty, `war_contribution` capture classification + starting map, `settlement_ratify`/`settlement_baseline` starting maps + capital exclusions, `enemy_ai` safe-capture, `diplomatic_templates` suggestion capital exclusions, `dispatch`/`diplomatic_ledger` display, `world_state` spawn/retreat, parser/objection heuristics (defensive-getter where worlds may be mocks), debug endpoints — behavior-identical on legacy (the world attr IS the legacy global there), correct on Europe; **(8)** `NATION_HONOR_BIAS` +14 authored (Spain already carried 0.85; **Russia EXPLICITLY 1.0** — the DG-4 spec-closure fixtures pin Russia-breaker deltas at neutral bias, re-biasing Russia is owned by the 1805 balance pass together with those fixtures), Austria `EUROPE_BASE_ACTIONS` 3→4, Russia `EUROPE_NATION_GOLD` 1000→1500. **Plus the war-seeding contract:** scenario `starting_wars` (ordered `{"attacker","defender"}` list, validator-shape-checked, nations runtime-validated) seeds through the live `ensure_war_instance_for_pair` — the France-first coalition ordering yields ONE shared instance with Britain as defender leader (test-pinned), sets `diplomatic_states` WAR + `war_start_turns`, and a seeded world advances turns cleanly. `VALID_NATIONS` (modding validator warning set) covers both rosters. Smoke-verified end-to-end before tests: minimal Europe scenario → 126 provinces, army-less, one shared war, Vienna capture +20 capital score, clean `advance_turn()`.

✅ **Map 1805 Scenario Setup LANDED (July 1, 2026)** — `godot-client/project-sovereign/assets/maps/europe_1805.json` (force-added) authors the blessed Sept 25, 1805 opening against the landed loader: **21 marshals across 12 armed nations** (9 nations + 3 satellites deliberately army-less), the **7-pair WAR / 5-pair ALLIANCE matrix** (sorted-pipe keys; default-PEACE otherwise), the **29-pair relations table**, the **Third Coalition seed** (`active_coalition` leader Britain / `threat_level` 85 / `coalition_count` 1; subsidy targets Austria from turn 1), and the ordered France-first **`starting_wars`** — live-verified to ONE shared instance (attackers Bavaria/France/Holland/KingdomOfItaly/Spain, defenders Austria/Britain/Russia, leaders France/Britain). **Boot: `SOVEREIGN_SCENARIO=godot-client/project-sovereign/assets/maps/europe_1805.json`** (kept env-gated until Slice 7 — the Godot client can't render Europe yet, so the default backend boot stays the army-less Europe world). **Supply-cap deviations of record** (full-stack audit vs derived `supply_capacity`; the plan's named Soult fallback couldn't work — Ney held Lorraine): Ney↔Soult provinces swapped (Rhineland 50k ≤ 60k home cap, no strength trims); Mack 58k→52k (blessed knob bottom) + Charles 65k→54k (Carniola home cap) preserving Charles>Mack; **Milan registry terrain `mountains`→`plains`** (`europe.json` fix — Po plain; the image-derived flag bled Masséna −428/turn; validator PASS `--strict`; image-derived-field review owned by DEF-8). Mack's hostile-soil strain (−234/turn on Bavaria-owned Swabia) is deliberate invasion flavor, test-pinned as the map's ONLY turn-1 supply event. **Two loader folds:** (a) omitted-`regions` injection now stamps controllers + 15k capital garrisons (mirrors `_setup_initial_control`) — previously EVERY `from_scenario` world loaded controller-less (France 0 provinces, zero income/supply/captures; latent since the loader's creation, legacy examples fixed too); (b) authored army-less nations pre-seed `eliminated_nations_notified` (no spurious turn-1 "forces are spent" ×9; real eliminations still notify). **Flagged-item ownership closed (Golden Rule 9):** DEF-6 (Flanders↔London walkable link → Slice 8 balance), DEF-7 (cross-Baltic land adjacencies → registry mini-pass before the Slice 8 playtest), DEF-8 (image-derived `is_coastal`/terrain review) added to the plan's deferred table. **Adversarial verification fold (3-verifier workflow, 2 MAJOR fixed):** (V1) the Slice-4 satellite seam never stamped the pair diplomatic state — satellites read PEACE (not an open-movement state), locking France out of its own satellites' soil (Masséna un-reinforceable on Milan); fixed with live-vassal parity (`_seed_europe_vassals` stamps `"VASSAL"`) + the 3 pairs authored in the scenario. (V2) `from_dict`'s single-gold back-compat branch handed an omitted-gold scenario the legacy 1200 default — now world-scoped (France keeps the blessed 800; the legacy bare-dict 1200 pin untouched). (V3) the "mountainous Milan" standoff wording is stale post-deviation — the plan's winnability note is corrected and **verifying the Adige standoff (1.286 vs the cautious 1.3 threshold, Tyrol corridor) is an explicit Slice 8 balance item** along with the knife-edge values (Charles exactly at Carniola's cap; France|Spain exactly at the ALLIANCE threshold). Soult/Armfelt bios corrected; the army-less guard is deliberately scenario-global (authored-partial legacy scenarios test-pinned). `tests/test_europe_1805_scenario.py` (**22 tests** incl. **the carried Slice-5-fold `allied_region_restored` Europe treaty-cession behavior test** — Britain cedes Holland-starting Brabant back, Holland's episode credits 15, Europe-only name = the legacy-global discriminator — plus a live TurnManager enemy-phase end-turn test, the exact 15-entry matrix pin, satellite-movement + treasury pins). Suite **`10671 passed, 1 skipped`**; ruff clean.

✅ **Map Slice 6 LANDED (July 1, 2026) — Godot province-shape ownership fills (renderer-only; the game cutover is Slice 7).** `map_renderer_base.gd` gains an **owner-fill fragment-shader layer** (`OwnerFillLayer` — same z_index as the terrain art, later sibling, below the hover highlight): the shader samples the lookup texture and matches a ≤128-entry `lookup_colors` palette (per-channel epsilon 0.002 < the 8-bit step; **sea-sentinel early-out** so open water can never tint and most fragments skip the loop entirely), blending the matched province's `owner_colors` entry at `OWNER_FILL_STRENGTH` 0.55 over the terrain. **(G4 met) An ownership change re-tints in ≤ one frame:** `_refresh_owner_fill_palette()` is ONE ≤128-entry `PackedColorArray` uniform upload (colors resolve through `Utils.NATION_COLORS` with the `COLOR_ENEMY_DEFAULT` fallback; unwired or controller-less provinces stay transparent), hooked into `update_all_regions`/`update_region`; no per-pixel work exists anywhere on the re-tint path (source-test-pinned, incl. exact-128 uploads and the shared `_owner_fill_province_order` index alignment). The pass is **bitmap-mode-gated** (`_bitmap_mode` flips only in `_load_map_images()`'s success path) — the legacy 19-region circle map is byte-for-byte behavior-identical (Panel fills remain its ownership display). **Key-scheme discovery + fix:** `europe.json` keys regions by `Region_NNN` ids (historical name in a `name` field) while backend map_data (Slices 4/5) is **name-keyed** — `europe_map.gd` now **re-keys the registry by historical name at load** (mirroring `create_europe_regions()`), so hit-testing, hover, fills, and ownership data all speak the backend's key scheme (a hard Slice 7 prerequisite; smoke hover now shows real province names; NOTE: re-keyed rows' `adjacent` lists still hold ids — Slice 7 must translate them before drawing connections). The smoke scene **seeds the 1805 political snapshot through the real `update_all_regions()` path** from `starting_controller` (+ registry terrain/region_type so tooltips read sensibly) and adds a smoke-only G4 demo: clicking a province cycles its owner through `SMOKE_OWNER_CYCLE` by mutating the retained seed dict and re-sending it — fill and tooltip can never desync. **Live-verified** (RTX 3060, Vulkan Forward+): the full 1805 political map renders (France blue, Britain red, Austria yellow — all 20 nations), sea untinted, hover names historical, and a click on Anjou re-tinted it France→Britain instantly with the tooltip matching; zero shader/script errors on stdout. **Parse harness extended:** `tools/godot_parse_check.gd` gains `MAP_CRITICAL_SCRIPTS` (the two scenes-dir renderer scripts — deliberately NOT added to the pytest settlement mirror list, whose staleness guard resolves against `scripts/` only), report regenerated **0 failures**; the scenes-dir coverage + staleness mirrors live in the new suite. New `tests/test_map_owner_fill.py` (**24 tests**: source pins incl. the G4 no-per-pixel guard, the bitmap-mode no-op contract, and the pinned `if _load_map_images():`+return caller shape; Python behavioral mirrors over the real registry — every `starting_controller` resolves to a nation color, lookup colors pairwise unconfusable under the shader epsilon incl. vs the sea sentinel, palette fill rules over synthetic wired/unwired/unknown rows, and the full 126-slot 1805 snapshot). Suite **`10695 passed, 1 skipped`**; ruff clean.

✅ **Map Slice 7 LANDED (July 1, 2026) — Godot game cutover + the default-boot flip to `europe_1805.json`, one commit per the standing decision. THE RUNNING GAME IS NOW THE 126-PROVINCE 1805 EUROPE CAMPAIGN, frontend + backend.** **Godot cutover:** `map.gd` rewritten in place as the Europe game map (main.tscn untouched — smallest reversible flip) on the new chain `map_renderer_base.gd` → `europe_map.gd` (SHARED Europe renderer: asset paths, Region_NNN→name re-key + retained id→name map, registry-anchor positions, marker-panel suppression) → `map.gd` (game glue: name-keyed `/map_topology` handoff, Utils colors) and → new `europe_map_smoke.gd` (the smoke seed + owner-cycle demo moved out of the shared parent; `europe_map_smoke.tscn` re-pointed). **Presentation decisions of record:** hover tooltips carry province names (no 126 persistent labels); connection lines = the registry's 12 hand-authored `sea_links` ONLY (id→name-translated; land adjacency reads as art borders; the re-keyed `adjacent` id-lists are never drawn — the Slice-6 handoff is closed); **province fog rides the owner-fill palette** (`_refresh_owner_fill_palette()` composites `FOG_OVERLAYS[visibility]` per province — rgb lerp by fog alpha, alpha=max — ahead of the SAME single uniform upload; **G4 preserved**, source-pinned; legacy FogOverlay presentation carried over); marshal/garrison/fogged-force markers needed zero new wiring. `main.gd` help copy updated to 1805 examples ("Ney, attack Mack" / "scout Swabia" / "move to Flanders"). **Default-boot flip (`backend/main.py`):** precedence = explicit `SOVEREIGN_SCENARIO` (fails loudly; explicit + `SOVEREIGN_SMOKE_START` now RAISES — the never-combine rule is code) → **`SOVEREIGN_SCENARIO=none` sentinel** = bare flag-resolved world → `SOVEREIGN_MAP=legacy` = no scenario (**G1 rollback re-drilled live**: env flip alone restored 19 regions/Britain=Netherlands) → smoke preset alone = no scenario (warned) → **default = the absolute repo-derived `europe_1805.json`**. `tests/conftest.py` pins the `none` sentinel suite-wide (main-module tests keep their fast army-less bare-Europe baseline; shipped-default pins delenv explicitly). **Client-under-rollback story (decided):** the client ships Europe-only — under a legacy backend, legacy-named `map_data` entries simply don't render (safe-guards verified) and the terminal game stays fully playable; a fully-legacy client is `git revert` of this commit. **Verification:** parse harness extended (`MAP_CRITICAL_SCRIPTS` ×4 + a scene-instantiation section: `instantiate()` without tree-entry — `_ready` never runs — pins main.tscn's MapArea script = map.gd) → **0 failures**; new `tests/test_map_slice7_cutover.py` (18 tests: 8 boot-precedence pins incl. the raise, tscn/script-chain source pins, sea-link + fog-wash Python mirrors, harness-report evidence); placeholder guards retired with named successors (test_map_consistency ×3, test_map_placeholder_assets ×3 — the asset JSON itself stays until Slice 9); test_map_owner_fill re-pointed (smoke pins → the smoke subclass; +2 scripts in the coverage/staleness mirrors); **live windowed smoke on the real game (RTX 3060, Vulkan)**: 1805 political map with owner fills + fog wash, hover "Champagne / France / Plains", Turn 1/60 + 800 gold + Third Coalition panel + coalition threat 83 [Brewing], 21-marshal front (Davout/Ney/Murat/Masséna/Moore/ArchdukeCharles markers), **end turn → the enemy phase ran live and the map re-tinted the captures British red** — Moore walked Flanders + Amsterdam via the DEF-6 cross-Channel link (observed live; exactly the Slice-8 balance item) and Charles attacked Bernadotte (Battle of Franconia). Suite **`10707 passed, 1 skipped`**; ruff clean; validator `--strict` PASS.

**July 2, 2026 — first wide-window user playtest feedback → OWNED as DEF-9..DEF-12 + a new Slice 7.5 (map presentation pass) in `docs/MAP_IMPLEMENTATION_PLAN.md`.** Four items from the user's first look at the live 1805 map, root-caused in code and measured on the shipped art: **(1) DEF-9 — the black void + debug overlay are real defects:** the Camera2D hardware limits set in `_update_camera_limits()` fight and beat the script's `_clamp_camera_position()` centering (Godot 4.4 pins the view to limit_right/limit_top, dumping the entire fit deficit as ONE black band left of the map); `INITIAL_CAMERA_OVERSCAN` 1.18 + the hard `min_zoom` 0.5 guarantee out-of-map void at boot on every aspect ratio; and the yellow `_create_debug_label()` overlay ships unconditionally — leftover dev scaffolding, player-visible. **(2) DEF-10 — the confusing colors are quantified:** at the 0.55 owner blend the palette clusters (green 5-cluster incl. ADJACENT Saxony↔Russia at ΔE≈9; red 3-cluster; Naples↔Bavaria; a warm-tan 6-cluster converging on the parchment terrain), and the fog composition lerps away up to 75% of national hue — the turn-1 mostly-fogged map is uniform grey-brown mostly because of FOG, not the palette; `COLOR_ENEMY_DEFAULT` is ΔE≈4 from Switzerland; no border pass survives the fill. **(3) DEF-11 — map labels:** supersedes the Slice-7 "no persistent labels" decision of record, so it is owned as an explicit GATED decision change (recommended: zoom-LOD nation names low-zoom / province names high-zoom — the registry's `label_anchor` is parsed but unread, 126/126 coverage). **(4) DEF-12 — map modes:** a cheap political/terrain `fill_strength` toggle is one uniform away; a real mode system needs fog decoupled from the owner palette → future mini-spec + design gate. Slice 7.5 is sequenced BEFORE the Slice 8 playtest so the balance smoke evaluates a readable map; the DEF-11 labels mini-gate (+ optional DEF-12 toggle blessing) is the only user decision it needs.

✅ **Map Slice 7.5 LANDED (July 2, 2026) — same-day presentation pass, user-blessed ("do fixes you see fit"); DEF-9/DEF-10/DEF-11 closed + the DEF-12 cheap toggle.** **(DEF-9)** `min_zoom` floors at contain-fit via `_update_zoom_floor()` (recomputed per resize), boot = exact contain-fit (`INITIAL_CAMERA_OVERSCAN` deleted), Camera2D hardware limits disabled (`CAMERA_LIMIT_DISABLED` — `_clamp_camera_position()` is the single centering authority, letterbox symmetric), parchment `BITMAP_LETTERBOX_COLOR` margin (legacy circle canvas untouched), debug overlay deleted. **(DEF-10)** `Utils.NATION_COLORS` re-authored as a set (Saxony chartreuse / KingdomOfItaly bright green / Portugal purple / Denmark maroon / Switzerland rose / Naples amaranth / Bavaria pale blue / Hesse lavender / PapalStates white / Sardinia cooled / Holland hotter orange): min pairwise blended ΔE **4.5 → 14.4** measured on the shipped art; fog hue lerp scaled (`FOG_HUE_LERP_SCALE` 0.6 — turn-1 fogged mean ΔE **11.7 → 26.5**); `COLOR_ENEMY_DEFAULT` → artificial magenta; in-shader province border pass (right/down key taps, sea-neighbor guard, single palette loop — G4 intact). **(DEF-11)** new `scenes/map_label_layer.gd` zoom-LOD labels (nation names at radius²-weighted centroids below zoom 1.1, province names at the registry's previously-unread `label_anchor` above; fonts counter-scale 1/zoom; `Utils.display_nation_name()` keeps internal keys off the map — R7); rebuilt exactly where the owner palette refreshes. **(DEF-12 cheap tier)** M cycles blended/political/terrain on one `fill_strength` uniform; typing-guard verified live (M into the focused command input stays text). **Verification:** new `tests/test_map_slice75_presentation.py` (17 tests incl. perceptual floor gates — blended ≥ 12 / fog ≥ 7 / fallback ≥ 30 vs the pinned land mean; any future palette edit that re-clusters two nations fails CI); fog mirror in test_map_slice7_cutover carries the retention scale; overscan pins retired in test_map_renderer_cutover; `map_label_layer.gd` added to `MAP_CRITICAL_SCRIPTS` (harness + mirror); parse harness + scene instantiation **0 failures**; suite **`10724 passed, 1 skipped`**; ruff clean; **live windowed smoke on the real 1805 game PASS** (5136×1408: centered map, symmetric parchment margins, no void/debug text, 20 nation labels readable, Hanover/Hesse/Saxony/Holland distinct, M-cycle verified through all three modes, zoomed province labels + Swabia tooltip). **New from the landing smoke: DEF-13** (fixed-size `BottomLeftUI` terminal + war panel don't scale on large windows; owned at Slice 9 or an explicit UI-scale mini-pass). **Same-day zoom-feedback FOLD (user report: blurry zoomed-in art + labels reading as shrinking):** art layer -> mipmapped LINEAR filter (lookup/owner-fill stays NEAREST — exact-key contract), `max_zoom` 4.0 -> 2.5 (art information limit), and the label layer re-architected SCREEN-SPACE (projects world anchors through the SubViewport canvas transform per draw; fonts GROW with zoom inside clamps — nation 34z in [22,46], province 13z in [14,34]; pan hook re-projects; world-space glyphs had rasterized tiny-then-upscaled = blurry, and constant-screen-size read as shrinking). +2 tests (screen-space/growth pins, filter/zoom-cap pins); suite `10727 passed, 1 skipped`; parse harness 0 failures; live-verified at max zoom + contain-fit on a fresh instance. Known minor accepted v1: dense small-province label overlap at mid-zoom -> named Slice 8 playtest check. **Third same-day report FOLD (sea-link lines blend into the map):** connection lines draw dashed dark map-ink (`draw_dashed_line`, `COLOR_CONNECTION` -> dark sepia w/ alpha) — the 12 sea routes now read as deliberate crossings; live-verified (Channel, Tyrrhenian, Aegean); +1 pinned test; suite `10728 passed, 1 skipped`.

✅ **UI Cleanup Pass LANDED (July 2, 2026) — user screenshot feedback (map label collisions + Diplomatic Ledger raw internal keys), swept codebase-wide via a 4-auditor + 4-fixer workflow.** **(1) Map label presentation:** `map_label_layer.gd` gains occupied-rect avoidance — the renderer pushes WORLD-coord rects for marshal icons, name stacks, and garrison chips per `_rebuild_dynamic_nodes()` (`set_avoid_rects`), and province-tier labels nudge upward clear of them (drop beyond a 2.5-font-height budget) plus greedy label-vs-label de-overlap (first in registry order wins; dropped labels return as zoom makes room — closes the Slice-7.5 "dense small-province label overlap" known-minor); marshal/fogged-force name labels get dark outlines (`FORCE_NAME_OUTLINE_*` — white-on-parchment was illegible and read as part of the colliding province labels). All Slice-7.5 source pins intact; parse report regenerated 0 failures. **(2) R7 nation-key sweep (the `KingdomOfItaly` ledger screenshot class):** ~75 render sites across 22 .gd files now translate nation keys at render time via `Utils.display_nation_name()` (hardened: non-alphabetic strings pass through, so mixed nation-or-region fields are safe) — Diplomatic Ledger (all 5 tabs), War Status HUD + war detail (headers previously upper-cased raw keys → "KINGDOMOFITALY"), diplomacy wizard, guided settlement table court rows/headers/chips, enemy-phase dialog, notification rail details, dispatch/campaign-log/intel/marshal screens, all proposal/coalition/paradox/rebellion popups, and the map hover tooltips (province controller line) — with raw keys deliberately preserved in every signal payload, `.bind()`, color lookup, dict key, `[url=]` meta, and parser command string. **Backend prose is cured at the render chokepoints:** new `Utils.humanize_nation_keys_in_text()` (whole-token `KingdomOfItaly`/`PapalStates` substitution; `Ottoman` excluded as valid prose) wraps `main.gd add_output()`, dispatch view, campaign log, notification rail, mailbox, top-bar summary, and every popup body assignment — this is the DECIDED cure for the ~120 backend f-string interpolation sites (no backend prose sweep needed; nothing renders except through these chokepoints). **(3) Structural backend display fixes:** `display_names.py` gains `NATION_DISPLAY`/`display_nation()` (mirrors utils.gd — keep in sync); `war_status.py` `opponent_display` joins display names (the field finally earns its suffix); `ledger.py` strategic-order summaries use display verbs ("March Vienna (3 turns left)" — `test_ledger.py` pins updated); `diplomatic_dialogue.py` objection `proposal_summary` display-composes ("Non-Aggression Pact with Kingdom of Italy", was "non_aggression with KingdomOfItaly"). **(4) Polish:** dangling stable-trend "→" removed (ledger relations + wizard vassal loyalty — arrows only for rising/falling); new `Utils.display_diplo_state()` (`NON_AGGRESSION` pill → "NON-AGGRESSION", `DEFENSIVE_ALLIANCE` → "DEFENSIVE ALLIANCE" incl. paradox-popup prose); settlement warning pill "[HARD_STOP]" → "[HARD STOP]"; diplomat personality "(dove)" → "(Dove)"; Forces-tab "moving_to" → "Moving To"; acceptance outcome "(COUNTER_OFFER)" → display/capitalized; 2 mojibake "â€¢" bullets → "•". **Verification:** parse harness + scene instantiation regenerated **0 failures**; suite **`10728 passed, 1 skipped`**; ruff clean. *(Also confirmed on request: the commissioned map art is hand-made, not AI — layered PSD sketch→color→border progression, pattern-fill/layer-style rendering artifacts, reference-traced geography; consistent with the arrival forensics above.)*

✅ **DEF-7 registry mini-pass + Map Slice 8 + Map Slice 9 LANDED (July 2, 2026, one session) — THE REAL-MAP CUTOVER IS COMPLETE.**

**User-reported bug fixed (the session's trigger): "hovering French lands shows No intelligence."** Root cause: `WorldState.from_scenario` never ran `calculate_visibility()` — the constructor (`:807`) and the save-load path (`save_manager.py:146`) both compute boot fog, but the scenario path returned with `intel == {}`, so EVERY province on a scenario-booted world (the shipped default `europe_1805.json` boot!) read "unknown" until the first end-turn: France fog-washed, own capitals showing "No intelligence", the DEF-10-era "turn-1 mostly-fogged map" partly THIS bug. Fixed at the end of `from_scenario` (blast-radius-audited: zero existing assertions changed; the fix deliberately does NOT go in `from_dict` — `test_fog_of_war.py` pins from_dict-only loads leaving intel empty). Now: own soil PARTIAL+, marshal locations FULL, distant enemy interior still unknown. Live-verified over HTTP (`Rhineland: full`, `Estonia: unknown`). Tests in `test_europe_1805_scenario.py` (1805 + legacy-scenario variants).

**DEF-7 cross-Baltic registry mini-pass** (executed over the full compressed-Baltic class): 10 land edges CUT (the row's Scania↔Berlin, EastPrussia↔Finland, Posen↔Finland, Livonia↔Posen/Brandenburg, Hanover↔Oslo + siblings Scania↔Brunswick/Jutland, Jutland↔Brunswick, Oldenburg↔Oslo), 4 demoted to drawn sea links (Livonia↔Pomerania, Livonia↔Finland, Scania↔Pomerania, Finland↔Estonia), 2 connectivity links ADDED (Oslo↔Jutland = Denmark's Skagerrak route; Scania↔Gothland = Sweden's internal continuity the stylized art broke — without them the 8-province Scandinavian cluster disconnects), 2 kept-land decisions of record (Hanover↔Jutland = Holstein bridge; Estonia↔EastPrussia = Courland stand-in). `adjacent` 258→250 edges; `sea_links` 12→18; validator `--strict` PASS; BFS 126/126 connected. **DEF-8 rode along** ("first consumer wins"): the five known-wrong `is_coastal` flags corrected (Franche-Comte/Munich/Bern/Tyrol/Milan → false; no live consumer reads them). Pins in `test_europe_registry_data.py`.

**Map Slice 8 (scale + balance):** **(G4 measured, decomposed)** the budget guards MAP cost and passes with 4× margin — bare army-less Europe turn 2.1ms = **0.49×** the legacy 4.3ms baseline (126 regions are CHEAPER per turn than the legacy armed world); the full 1805 campaign turn is 23ms = **5.4×**, which is ROSTER workload (9 armed AI nations / 21 marshals / live coalition), regression-pinned at 15× in `test_scale_readiness_phase2.py`. **Hot-path audit:** 7 Golden-Rule-8 violations converted to the cached indexes (`get_manpower_regen_rates` — 2,520 region-visits/turn, vassal tribute, `war_status.build_active_wars` — a full region scan on EVERY HTTP response, `_get_strategic_enemy_regions` + a scope-reset memo, P6.75/economy garrison counts, `_find_best_stables_region`, capital-proximity) with source-pin regression tests; plus a latent **shared-adjacency-list bug** fixed in `Region.__init__` (REGIONS_DATA `adjacent` lists were passed by reference — one in-place edit rewired every later world in-process; surfaced as a pre-existing test-order flake where one test PASSED only because a sibling's pollution deleted the Paris↔Normandy edge; defensive copy + the dependent test made explicit). **DEF-6 LANDED:** capital garrisons tier-differentiated Europe-only (majors 25k / secondary 15k / minors 10k; regen cap tier-aware; legacy flat 15k untouched) via `CAPITAL_GARRISON_BY_TIER` + `WorldState.get_capital_garrison_target`; NEW scenario loader key **`region_overrides`** (shallow per-province field merge, loud on unknown names — documented in MODDING_FORMAT.md) stamps a **12k Flanders Channel depot** in `europe_1805.json` — the decisive fix, since Flanders (non-capital, garrison 0) was the actual free beachhead and the P4.5 walk-in gate is garrison ≥5k. Pins: P4.5 can never pick Flanders; a French London rush takes exactly 3 assaults against the 25k major garrison; the seeded 5-turn probe keeps Paris French and any Britain gain routes through the fought depot. **Russia honor bias retuned 1.0 → 1.1** (Alexander's coalition-loyal court, under Prussia's 1.15 ceiling) with the five DG-4 fixture pins re-derived arithmetically (A:2→1, B:-5→-6, C:-6→-7, D:5→6, E:-20→-22) — 135 reliability-family tests green. **Balance verdicts of record:** the Adige standoff is GEOMETRIC (Carniola↛Milan — corridor via Tyrol; 1.286 sits INSIDE mood variance, and the turn-1 aggressive posture cuts the threshold below it: the plan's ratio-based wording was optimistic; Charles routing to the Franconia rear — the Slice-7 live observation — is the mechanics working, historically consistent with Caldiero) — geometry + threshold constants pinned; **Mack's turn-1 P-1 capture of Swabia is deliberate** (Austria's invasion of Bavaria; pinned incl. the strain ending on home soil); the knife-edges hold (54k inclusive at-cap = zero attrition; relation-40 alliance gap-0 never erodes — both pinned with contrast cases); **Ulm knob stays 52k** (the 169k ring is decisive; raising Mack only re-adds pre-capture bleed). **DEF-4 NOT forced** (AI-AI phase ~12% of a 23ms turn; dispatch navigable in the probe) — reverts to Phase 5.2/5.3/5.6 with the tripwire. **Playtest smoke:** 20-point scripted HTTP campaign session on the shipped default boot — 19/20 PASS (fog fix, garrisons, combat, 3 end-turns at 55-70ms round-trip, all screens); the 1 failure is a MOCK-parser-only bare-command gap ("scout Swabia" without a marshal name — works marshal-prefixed and in anthropic mode; logged in BUG_FIXES.md, dev-mode only). `docs/MANUAL_TEST_PLAN.md` **Test E** is the standing Europe smoke script. New `tests/test_map_slice8_balance.py` (10 tests).

**Map Slice 9 (cleanup + docs) — the cutover CLOSES:** `session8_placeholder_provinces.json` retired (zero runtime consumers; its 12-test schema suite deleted; the 2 live renderer source-pins moved to `test_map_renderer_cutover.py`; unwired-overlay tests re-fixtured self-contained; validator CLI tests re-pointed at the live `europe.json`); repo-wide `Region_NNN` audit CLEAN; docs reconciled (SAVE_FORMAT header → v3 with the legacy-example annotation, SCALE_READINESS §4 superseded-banner + §5.5 shipped-reality note + checklist rows fixed, ADDING_CONTENT registry section re-pointed incl. the lru_cache/`--adjacency-only` warnings, MODDING_FORMAT `region_overrides` row, MANUAL_TEST_PLAN Test E, CLAUDE.md Current Phase rewritten); **DEF-13 DECIDED:** re-owned as the dated **UI-Scale Mini-Pass** (per-Control scale is blurry on pinned Godot 4.4 — font atlases rasterize at theme size, per-viewport oversampling is 4.5+; the correct `content_scale_factor`-with-native-map fix is a 1.5-3 day slice over ~30 fixed-pixel scenes + the 182 font-size sites + the screen-space marker question; full rationale in the DEF-13 row) with the pre-pass geometry frozen by `test_def13_fixed_hud_baseline_pins`. DEF rows 2/6/7/8 closed; 1/3/4/5/12/13 homed. Suite green via the pre-commit hook; ruff clean.

**Diplomacy accommodations the Europe/1805 world forces (collected for the resumed settlement queue — verify at the Gate 4 smoke):**
1. **Smoke environment:** do NOT combine `SOVEREIGN_SMOKE_START` with `SOVEREIGN_SCENARIO` (the preset seeds wars in the constructor; the scenario seeds its own — the combination is untested). Run the Gate 4 smoke either pinned `SOVEREIGN_MAP=legacy` (the fully-armed legacy fixture, same settlement code paths) or — better, post-Slice-7 — on the 1805 scenario itself with the preset unset, using the live coalition war as the multilateral fixture.
2. **Peace below the relation floor:** the authored war relations (−80/−90) sit below the PEACE ratification gate (≥ −60). Bilateral peace with Britain/Austria/Russia is IMPOSSIBLE until relations thaw — **the armistice-first ladder (no relation floor) is the designed escape** (G4F-13 already counsels it in previews). Expect this in playtests; it is not a bug. (The new scenario test documents the thaw explicitly.)
3. **Multi-court width:** the shared 1805 instance carries 5 attacker-side + 3 defender-side participants — wider than the 2–3-court fixtures most settlement tests use. Watch §6 burden aggregation caps, coverage add/drop rows, and the per-court gate at that width during the smoke.
4. **Coalition pre-seed structural paths:** while `active_coalition` is non-None, formation/brewing branches + threat-tier notifications are structurally skipped (`coalition.py` formation `elif`); threat decays ~3/turn from 85; separate peaces that strip members will exercise leader re-selection + dissolution paths legacy games rarely ran.
5. **Capitals are real now:** Britain=London (the Netherlands proxy is retired on Europe); Vienna/London captures move war score (pre-slice test-pinned). Any settlement-scoring re-audit should confirm no legacy `NATION_CAPITALS` read survives in scoring-side paths (the pre-slice swept live reads).
6. **Volume + voice:** 19 AI nations feed proposal generation (anti-spam + DG-2 salience cap landed; O(N²) retunes owned by DEF-4/Slice 8); 15 of the 20 diplomats are chancery-fallback until DEF-1 lands — 1805-war settlement dialogue (Austria/Russia courts) will read as chancery voice, which is owned, not a defect. British subsidy (200g/turn to Austria) runs from turn 1 and feeds acceptance-relevant treasuries; the DW-class war-score credit calibration question now interacts with Europe capital scores (owned by the pre-flight audit ledger + the 1805 balance pass, which also owns Russia's honor-bias retune and the Ulm difficulty knob).

*(Historical: the Godot renderer smoke — run `europe_map_smoke.tscn` with F6; set `europe_lookup.png` import Compress Mode = **Lossless** if it shows circles — gates the renderer Slices 6–7, NOT Slice 2. Slice 1 and the data-authoring Slices 2–5 are tools/assets only and do not depend on it.)*

**The Map Implementation Plan is now CREATED and independently reviewed (3 passes) → `docs/MAP_IMPLEMENTATION_PLAN.md` (status: **DESIGN GATE ✅ APPROVED June 23, 2026**); full findings + the session-by-session roadmap in `docs/MAP_PLAN_REVIEW.md`.** Every claim was re-verified against the live assets: validator **PASS**; lookup land **1,788,712 px / 43.7%**; adjacency cleanly bimodal (**73.6% land ≤15px / 23.5% sea ≥41px** over 35,633 samples) → auto-derive land, hand-author sea; the PSD `letters` layer is **single hand-drawn glyphs, NOT province names** — so naming is a **manual geography pass** (not "mine the letters layer"); legacy footprint ≈**10,255 match-lines / 275 test files** → **keep the 19 regions as a test-only fixture** (the game ships Europe). Verdict **GO**, score **≈9.3/10** after the hardening pass (reversible `SOVEREIGN_MAP=europe|legacy` cutover flag, legacy-fixture immutability guard, `is_coastal`↔sea-adjacency check, measurable turn/re-tint budgets).

**Design gate APPROVED (user, June 23, 2026).** ✅ **Map Slice 1 LANDED (July 1, 2026)** — adjacency auto-derivation (land + sea-gap candidate list) + `--inspect-letters` naming seed + 3 new validator checks; `europe.json` regenerated with **248 symmetric land edges / 144 sea candidates / 5 islands**; validator PASS (0 errors, 5 island warnings). New `tests/test_province_adjacency_derivation.py` + extended validator tests. ✅ **Slice 2 LANDED (July 1, 2026)** — 126 provinces authored (names / 1805 owners / terrain / region_type / coastal / capitals), 20-nation roster discovered, 12 sea links, M4/M5 validator hardening; validator PASS `--strict`; `tests/test_europe_registry_data.py` (24 tests); suite `10560 passed, 1 skipped`. ✅ **Slice 2.5 Roster Design Gate BLESSED + Slice 3 LANDED (July 1, 2026)** — see the entry above. ✅ **Slice 4 LANDED (July 1, 2026)** — the Europe region set is a constructable, turn-stable alternate backend world behind the `WorldState(sovereign_map=…)` seam (built + tested, not yet the game's map). ✅ **Slice 5 LANDED (July 1, 2026)** — backend game cutover (bootstrap → Europe via `SOVEREIGN_MAP`, default `europe`; `/map_topology` serves 126; map-contract tests migrated; G1 rollback drilled live; G2 legacy snapshot guard; DEF-2 save-incompat v3). **NEXT: the 1805 Scenario Setup design gate, then Slices 6–7 (Godot owner fills + frontend cutover).** Slice 1 was tools/assets only (zero game-logic/suite risk) and did NOT depend on the Godot smoke (the smoke gates the renderer Slices 6–7). Roadmap ≈**11–12 sessions**.

**The settlement Gate 4 manual smoke + Slice G/G1 are re-sequenced to run AFTER the map cutover** (they were next-up; the Active Settlement Gate section below is still valid, just sequenced behind this map work).

## Active Settlement Gate — CLOSED (Gate 4 PASSED July 3, 2026; no live successors)

**July 2, 2026 (second entry) — ✅ SLICE G1 LANDED (the Request Terms lifecycle + the D-G1-1(a) armistice-paradox exemption; plan user-approved same day; suite `10781 passed, 1 skipped`; ruff clean; Godot parse harness 17 scripts / 0 failures; live-verified over HTTP on the shipped 1805 boot):** The July-2 reconciliation left G1 exactly one unbuilt promise — the SC-30 Request Terms lifecycle — and it now ships complete: **(state)** `world.settlement_terms_requests` keyed by war_id (`requested/granted/refused`, clocks, `answering_leader`; serialized + `SAVE_FORMAT_REFERENCE.md` row); **(verb)** `request_terms` (structured `/command` + typed "request terms from X"; 1 DP; click-time affordance re-run; full new-action checklist wiring incl. the mock-parser routing gate); **(affordance)** `evaluate_request_terms_affordance` (settlement_routes) — the cleanup-spec no-false-affordance contract: ABSENT on every structural block (incl. an explicit one-active-offer guard that the eligibility function's first-refusal-wins ordering would otherwise mask behind `cooldown_active`), DISABLED-with-named-clock only for deterministic temporal blocks (pending answer / request cooldown / war-too-young), AVAILABLE otherwise — packed per-war as `request_terms_state` in `build_active_wars`; **(AI answer)** `_resolve_settlement_terms_requests` runs BEFORE the periodic producer scan each AI phase: GRANT emits a real `incoming_settlement_offer` through the SHARED `_emit_settlement_offer_for_war` emission (Building Blocks) tagged `requested_by_player: true`, bypassing the producer's periodic cooldown while writing BOTH clocks; REFUSE when the answering leader is decisively winning (`get_war_score_for >= REQUEST_TERMS_REFUSAL_WAR_SCORE = 30`) — voiced by the court's NAMED diplomat via `resolve_named_diplomat` (chancery fallback, never anonymous), notification + campaign-log beat, and the refusal also quiets the periodic producer (a court that refuses to name terms does not spontaneously offer them the same phase); LAPSE with a Talleyrand notice when the war changes shape; **(voice)** `settlement_request_terms_sent_talleyrand` / `_refused_court` / `_lapsed_talleyrand` in Voice Bible §16.1 (SC-32 D5 boundary verified); **(UI)** the War Detail `Request Terms` button renders from the affordance block (absent never renders; disabled carries the pre-click reason — G4F-16 pattern) and sends the structured action; no new dialogue type (a granted request speaks through the existing offer popup/mailbox). **D-G1-1(a) (user-approved):** the BPH-C §10.1 alliance-paradox HARD_STOP now gates bilateral PEACE only — armistice variants send (live-verified: peace mount blocks naming Spain, the armistice mounts clean and DISPATCHES on the shipped boot, un-dead-ending the counseled armistice ladder for ally-entangled courts). **Tests (+24 net):** the two spec-named absence-form tests INVERTED to the live lifecycle (`test_ask_for_terms_visible_only_when_request_terms_state_can_actually_advance`, `test_ask_for_terms_click_produces_observable_state_change_not_just_copy` — the latter through the exact Godot wire shape), new `tests/test_settlement_request_terms.py` (15: verb/DP/refusal/grant/one-active-offer/lapse/serialization/voice/wiring + Godot source pins), W1 whitelist-sync extended over `request_terms`, the two `CAMPAIGN_LOG_TYPES` count pins re-pinned 87→90, +3 campaign-log beat types. **Live smoke evidence** (`smoke_logs/g1_request_terms_smoke2.py`): available→requested-with-clock→granted→answerable on war_1; the mailbox row now reads "Settlement offer: France vs Britain" (the E-5 residual — `war_label` stamped at promote); Castlereagh voices the refusal on the cheat-shifted winning leg with the 5-turn re-request clock. **SC-30 closes; the cleanup-spec row is updated to LIVE. Remaining Slice-G family work: G2 follow-through + Slice H (cleanup spec), and the Gate-4 visual-half confirmation (user).**

**July 2, 2026 — ▶ THE GATE 4 END-OF-QUEUE SETTLEMENT SMOKE RAN (user light UI pass + full HTTP completion, per the user's session order; 16 findings, 11 FIXED same session at `7635229`; full suite `10759 passed, 1 skipped`; ruff clean):** Driven exactly per accommodation #1 — the settlement + diplo legs on the **shipped default 1805 boot** (leg A multilateral on the live coalition war `war_1`; leg E bilateral-diplomacy sweep; leg F 50-turn stability/exposure soak) plus the three preset legs pinned `SOVEREIGN_MAP=legacy` (`settlement_rejected`, `settlement_losing`, `settlement_multiwar_ambiguity`), all over HTTP with raw-payload evidence in `smoke_logs/g4_*` (drivers committed; JSON evidence local per precedent). **Machine-verified GREEN (highlights):** guided PROPOSE at 3-court width (suggestions both D4 groups, demand verbs round-trip, live re-scoring, focus breakdown 10 components incl. `concession_credit`); coverage add/drop + `coverage_floor`; PF-2 draft restore THROUGH save/load; mounted-draft-wins refresh; SC-28 blocked REVIEW contract (no `confirm_settlement`, frozen rows, recovery affordances, pair-substitute chooser + exact restore); **partial ratify** (Russia dropped → fights on, coalition survives) and **full ratify** (7 pairs → PEACE at the authored −80/−90 relations — the settlement's own per-court gate governs, by design); archived re-entry → `settlement_history` route; ratification reflected in campaign log + dispatch + notification rail + `recent_settlements`; end-turn discard notice names court + clause count; the losing fixture's concession baseline on first paint; armistice mechanics block; coalition threat decay + no formation popups while pre-seeded; British subsidy; ledger clean of raw keys at render. **FIXED same session (regression-pinned in `tests/test_settlement_gate4_leg1_fixes.py`, `test_settlement_incoming_offers.py`, `test_settlement_recovery_g2_slice6.py`):** G4S-1/G4C-1 (unresolvable choice on a staged settlement dialogue violated CH-5 — bare refusal, no re-attach → invisible hard stop), G4S-2 (dial budgets now pre-charge every existing gold line; the consume-on-visit ledger let one court's grow overspend another's committed gold → validator bounce loop, the GT-A5 ease escalation never fired — the 1805 ease ladder dead-ended at 37/50; now escalates to voiced territory offers and carries), G4S-3 (table narration now coverage-aware), G4C-2 (REVIEW frozen server-side against raw Tier-2 dial/coverage verbs — terms could mutate + `can_ratify` flip without re-submitting), **E-3 (incoming AI settlement offers were UNANSWERABLE — options lived only in `popup_payload` while resolution reads top-level; accept/reject/request-revision now pinned end-to-end through the wire)**, **E-1 (nation extraction now scans the full shipped rosters — the legacy alias table made 15 of 19 Europe nations unreachable for typed AND F1-wizard proposals: "propose peace with Russia" failed in every LLM mode)**, E-2 honesty half (the BPH-C alliance-paradox HARD_STOP now surfaces at proposal MOUNT with `commitment_block_warning` naming the ally + the working routes; mechanics unchanged), LEGD-1 (the `settlement_multiwar_ambiguity` preset now seeds the SC-8b shape it exists for — France|Austria active in two multi-party instances; the old three disjoint 1:1 wars made the disambiguation contract unreachable), LEGB-F2 (same-war restage REPLACES the mounted dialogue — preempt re-queued a twin that resurrected discarded drafts), E-4 (in-transit sends report "Dispatched", not "Rejected"), E-5/E-6/LEGF-3 (mailbox war-label, display nation names in coalition copy, retired-editor copy retarget). **Accepted deviations of record (no code change):** `contribution_share` material/support shares are fractional by design (the sole Godot consumer casts `float()` deliberately — Slice E contract); `settlement_preview.acceptance.component_debug` is scorer telemetry riding the payload with no Godot consumer (9 test files read it) — both noted against Golden Rule 2's crash class, which requires an int-reader that does not exist here. **OPEN — routed, not fixed:** **(1) E-2 mechanics fork (USER DESIGN DECISION, owner: the Slice G1 design gate):** on the shipped boot, courts with a France-ally pair at war (Britain, Austria at minimum) are bilaterally unreachable for BOTH peace and armistice — the paradox hard stop fires on the armistice ladder the game's own copy counsels; options: exempt ARMISTICE from the paradox rule (a truce is not the betrayal a separate peace is — and the re-front already embraced separate peaces at the settlement table), keep the block (mount now warns honestly and routes to the settlement table; Russia-class courts stay reachable), or gate behind a break-with-ally affordance. **(2) LEGF-1 reconciliation (docs corrected this session):** the SC-5 reversal + AI offer producer LANDED May 15/17, 2026 (`2a1f9d7` + `847dccd`; recorded in the cleanup spec's G2-Slice-4 section) — the "G1 = offer producer unbuilt" framing here and in CLAUDE.md was stale; **Slice G1's remaining scope is the Request Terms lifecycle + the 7 spec-named closure tests + the E-2 fork**, not the producer. **Residual eyes-only items for the user (the visual half):** popup layout at 3+ court width (rows + Add demand visible without scrolling), the blocked-REVIEW recovery rail rendering, the incoming-offer popup (now answerable — worth one click-through), map-adjacent settlement routing (war detail → settlement), and the discard-notice render. Gate passage is recordable once the user confirms the visual half against their UI pass.**

**July 3, 2026 (second entry) — ✅ SLICE H LANDED (full-agency ally petitions; gate approved and implemented the same day).** The user approved `SETTLEMENT_SLICE_H_ALLY_PETITIONS_SPEC.md` v1.0 with all five decisions D-H1..D-H5 as recommended, then H-1 + H-2 shipped in one commit (the W1 three-place sync forces backend dispatch + Godot whitelist + harness ids to move together). **Shipped:** `request_reward_or_restoration` (restoration basis always eligible — occupied homelands may always ask; contribution basis behind the D-H3 seat/consult floor; §3.2 valid-by-construction candidate clause with gold fallback inside `compute_gold_payer_budgets` headroom) + `demand_bargain_honor` (the §4.1 dry-run of the LANDED ratify-time breach predicates against the STAGED terms — imminent breach + silent abandonment — with the §4.2 consequence ladder read from the live breach constants, never invented) through the existing G2b petition lifecycle (solicited triggers only, D7 lock holds); **Grant / Decline / Honor** verbs through the demand-add/restage seam (`_restage_settlement_after_redraw` — Building Blocks); D-H1 dial protection (`SETTLEMENT_DIAL_PROTECTED_AUTHORS = {"player", "ally_petition"}` — a More-Generous sweep can never silently un-reward an ally; provenance-aware "pledge stands" notes); D-H2 light decline memory (−3 relation, `petition_declined` settlement memory, NO betrayal write — the ratify-time shut-out/breach teeth stay the single penalty); §5 `ally_petition_state` serialized (+ SAVE_FORMAT row); §6 anti-spam (5-turn cooldown on ANY resolution, max 2 live, salience bargain-honor > restoration > reward); the G1 click-time re-run pattern on stale grants (refusal-free lapse, no validator bounce, no cooldown — the ally re-petitions on the next staging); §4.4 interlock pinned (a would-breach staging surfaces the petition at the stage gate — the only route to ratification). **Voice:** 31 committed templates (2 ask families + granted/declined/honored acks × 5 suffixes + the Talleyrand lapse notice), D5-clean, §16.1a Voice Bible section added; the D5 scan now covers the whole `settlement_ally_petition_*` prefix. **Campaign log:** +3 beats (granted/declined/bargain-honored; count pins 90→93). **Tests:** new `tests/test_settlement_slice_h_ally_petitions.py` (22); the two G2b absence pins INVERTED to `*_live_after_slice_h`; the landing-ledger row + test updated to LANDED; parse harness regenerated (17 scripts / 0 failures). **Landed deviations of record:** candidate clauses carry no `settlement_reason` key (closed clause schema admits only `authored_by`; the petition's `basis` field carries the reason) and use the guided `region`-singular shape; Grant/Honor require the mounted PROPOSE table (REVIEW is frozen per UX-2 — the click-time refusal names the Return-to-Terms route). **The Slice G family and the SC-32 arc are now fully closed — no live settlement successors remain.**

**July 3, 2026 — ✅ GATE 4 PASSED (visual half USER-CONFIRMED).** The user confirmed the 5-item eyes-only checklist above. One visual question was raised and adjudicated in-session: the dashed map connection lines — verified as exactly the 18 hand-authored registry `sea_links` (the DEF-7 Baltic set + DEF-6 London↔Flanders + the Mediterranean island links), no change requested. Passage recorded here and in the `SETTLEMENT_UI_CLEANUP_SPEC.md` masthead; **the DWL-DIP-E7 / DWL-DIP-METTERNICH 8.EVAL triggers are now LIVE.** The settlement queue's only remaining successor is Slice H (design-gated).

**July 3, 2026 (third entry) — ✅ COMMAND ROBUSTNESS PHASE OPENED (user blessed scope CR-0..CR-5; CR-6 keeps its own gate) + CR-0 LANDED (the P0 parser-roster defect).** Parser rosters now derive from the LIVE world instead of the retired Waterloo lists: `parser.py` gains `_get_player_marshals(world)` / `_get_known_regions(world)` (mirroring the `_get_known_enemies` §3.4 pattern; the hardcoded legacy 4-marshal/19-region lists survive ONLY as the no-world cold-parse fallback that ~490 existing tests pin), and `llm_client.py`'s fast/mock parser takes `game_state` — marshal extraction from the player-only `marshals` dict, target extraction from fog-filtered `enemies` + `map_data` keys (longest-first word-boundary matching; camelCase-split aliases so "attack archduke charles" finds `ArchdukeCharles`), and nation-keyed vassal keyword forms from live nations. **All 7 French 1805 marshals are now commandable by typed text** ("Soult, attack Mack" / "Lannes, move to Swabia" / "Massena, hold Milan" all parse in every LLM mode). **Same-family defects fixed in the pass (each probe-verified before fixing):** the `Marshal [Name]` regex was case-sensitive on "marshal" — the standard typed form "Marshal Soult" NEVER matched; exact enemy names were fuzzy-rewritten into regions on the 126-province map ("attack Mack" → target "La Mancha"); trailing punctuation broke the word-scan skip lists ("Bernadotte," fuzzy-drifted into region "Bern"); typed vassal commands were dead in EVERY world (the marshal word-scan choked on "invest"/"release" before P8-1's nation keywords could matter) — "invest in saxony" (legacy) and "invest in bavaria" (1805) both parse now; and `strategic_parser._classify_target` gains live-nation demonyms ("pursue the austrians" classifies generic instead of title-casing into a fake region "The Austrians"). **Adversarial verification round (4 review lenses → 24 confirmed findings, all fixed or pinned same session):** the pre-commit review workflow caught 3 MAJOR regressions the first cut introduced — the widened `[Mm]arshal <Name>` regex captured ENEMY commanders as the executing marshal ("Attack Marshal Mack" hard-failed; fixed with an enemy-roster guard incl. the legacy-six cold fallback), the punctuation strip ran AFTER the existing-target skip check ("Attack Mack!" failed; "Hold Bern!" silently hijacked Bernadotte via partial-ratio 100; fixed: strip-first + known-region/enemy word guard + multiword/camelCase target-word skips so "attack East Prussia" works), and `_match_known_name` was position-blind ("move to Paris via Champagne" targeted Champagne; now preposition-then-position aware) — plus: vassal nation targets now resolve canonically ("invest in austria" carried target "Asturias"(!) — nation names are never region-fuzzed now, camelCase forms like "papal states" work), enemy typo precedence via true edit-distance ("Davout, attack Mach" went to "La Mancha"; now Mack), demonyms word-boundary matched ("march to Saxony" was silently reclassified generic → nearest-enemy redirect; fixed + 4 irregular demonyms authored), game_state-shape crash hardening, and gs-without-world roster consistency. **Tests:** new `tests/test_command_robustness_cr0_parser_rosters.py` (66 — both worlds, production-fog-shaped game_state, cold fallback, every review regression pinned); `TestParserMarshalList` re-scoped to fallback semantics (assertions unchanged); one `test_berthier_recovery.py` pin updated ("Naey," now AUTO-corrects to Ney — the contract under test, no-Berthier-on-typo, still holds). Suite **`10876 passed, 1 skipped`**; ruff clean. **Also this session:** CR spec bumped to v0.2 (phase ACTIVE; §4 gate-review candidates table records the user's "text system as pillar" direction — Flavor Echoing pull-forward, two-way marshal Q&A, commander-intent orders, raw-phrasing record, tone parsing, pre-battle councils — for the CR-5/CR-6 design table). Remaining known CR-0-adjacent gaps (unchanged owners): the meta-action silent-marshal-drop class ("Murat, charge" drops the addressee) and unknown-extra-word hard errors ("attack Bern, then hold your positions" asks about 'then') are CR-2 scope.

**July 3, 2026 (fourth entry) — ✅ CR-1 LANDED (parser eval harness — the Command Robustness phase's regression gate).** **Corpus:** `tests/data/parser_golden_corpus.json` — 233 entries (utterance → expected `{success, marshal, action, not_action, target, type, strategic_type, target_stance, requested_type, error_contains, diplo{...}}`, partial assertions; 88 entries carry probed `diplo` family assertions — proposal_type/mission_type/tone/target_nation), workflow-mined from the existing parser test files (4-agent sweep; every entry carries a `source` trace) + authored closers so **every mock-reachable action id has coverage**; a `live_phrasing_backlog` section owns the marshal-less strategic phrasings the MOCK chain can't parse (live-LLM-only today) as named CR-3 verb-coverage input (Golden Rule 9). **Engine:** `backend/ai/parser_eval.py` — corpus loader/validator, `build_llm_game_state(world)` production mirror (sync-PINNED byte-identical against `backend.main.get_llm_game_state`), per-entry evaluator with **implicit success=True** (negative-only expectations can never pass vacuously against a hard parse failure), and a CLI (`-m backend.ai.parser_eval`; `--live` arms the live-provider fallback and REFUSES to run if the provider resolves to mock; exit 2 on zero-entry filter mistakes). **Harness:** `tests/test_command_robustness_cr1_eval_harness.py` (per-entry×world matrix over BOTH worlds through the production `parser.parse(cmd, llm_game_state, world=world)` shape, corpus hygiene gates incl. no-dead-keys-on-failure-entries + error_contains-pairing, the **action-coverage gate** — CLAUDE.md new-action checklist gains step 12 — the production-payload sync pin, and the status-wire pin). **Defects the corpus + the pre-commit adversarial review round (4 lenses, 29 raw → 20 confirmed findings) caught and fixed:** (1) **typed `status` was dead** — `VALID_ACTIONS`, the mock, and the executor (`free_actions` + `_execute_status`) all supported it; `parser.valid_actions` was the single missing leg, so typed status fell to Berthier recovery instead of the intel report; (2) **live-path Unicode prints crashed on cp1252 Windows consoles** — the strategic MOVE_TO→PURSUE print killed every "march to <enemy>" parse ("Parser error: 'charmap' codec..."); the sweep found and fixed 5 more live sites (main.py boot warnings ×2, enemy_ai futility, combat_executor charge-blocked, disobedience redemption options); (3) **'journey to Paris' bound marshal=Ney and 'push toward the rhine' bound Ney too** (partial-ratio rewards substrings; V2-55 fixed only the mock layer) — word-scan fuzzy hits now require ±2 length AND a matching first letter; (4) **fogged-honorific commands hard-failed** ("Attack Marshal Blucher" with the enemy outside the fog-filtered game_state) — parser.py now demotes an extracted "marshal" that is a known enemy (exact/edit-1, omniscient world-side) to the target slot; the llm_client guard keeps fallback semantics (a union grafted phantom Waterloo commanders into 1805 — reverted per review); (5) **lowercase sentence words hard-failed whole commands** ("hold at all costs" → "Marshal 'costs' not found") — the not-found error is now capitalization-gated with a sentence-case first-token exemption (address syntax "Wittgenstein, attack" keeps its helpful suggestions error) and the strategic verbs (march/advance/guard/rally/withdraw/...) joined the skip list; (6) "hound the retreating forces" title-cased a phantom region — "retreating" joined the generic indicators. **Known-imperfect behaviors pinned truthfully in the corpus with named CR owners:** self-support ("support ney" → Ney supports himself; condition-marshal hijack) → CR-2 clarification candidates (spec row updated); compound orders ("attack Bern, then hold your positions") → CR-7. Suite **`11272 passed, 1 skipped`**; ruff clean. **Next CR slice: CR-2** (confidence-gate rework + clarification dialogue), measured against this harness.

**July 3, 2026 (fifth entry) — ✅ AI-LAYER AUDIT (user-directed) — 26 findings across 4 lenses (enemy AI decision tree, AI diplomacy, LLM plumbing, turn machinery), 14 defects FIXED same session, the rest routed with owners.** **CRITICAL fixes:** (1) **AI admin actions (build/repair) were gated on and CONSUMED the player's admin AP pool** — with the player's pool spent, all 19 AI nations were locked out of economic development every turn, and pool-exhaustion could fire a RECURSIVE end_turn mid-enemy-phase (double turn advance); fixed with an executor **AI-execution context** (`_acting_nation` / `_autonomous_execution` / enemy-marshal detection) honored at the AP-gate, consumption, and auto-end-turn seams. (2) **The autonomy feature was a complete no-op** — every AI-decided action of an autonomous marshal bounced off the executor's own "cannot command autonomous marshal" gate, so autonomy periods did literally nothing and `_end_autonomy` handed out +15 trust for total inaction; `decide_single_action` now stamps `_autonomous_execution` (gate + objection + player-AP bypass). (3) **P3.5 fortification-opportunity ignored war state and garrisons** — on the peace-heavy 20-nation map, fortified AI marshals perpetually unfortified chasing "captures" of PEACEFUL neighbors (and would blind-attack tiered capital garrisons past P4.25's ratio gate); now mirrors P4.5's is_at_war + garrison filters, in the intent validator too. (4) **The AI-AI treaty phase was completely dead** — the initiator-side acceptance check evaluated a SELF-PAIR (nation vs itself, never ≥50): `_ai_ai_acceptance` now evaluates the counterparty as proposer; AI-AI treaties can ratify for the first time since R107. **Also fixed:** the C3 auto-advance guard soft-locked End Turn (now absorbs one press, honest message); hard-stop dialogues promoted before/during the enemy phase no longer zero out every AI nation's turn (and no longer poison 2-turn failed-action cooldowns across the 21-marshal roster); the stagnation "meaningful fortify" gate was unreachable (required NOT-fortified after a successful fortify — defensive AI lines self-dismantled on a ~3-turn cycle); the pending-capture intent path emitted attack-while-fortified (executor rejection → 2-turn attack ban) — now unfortifies first and re-stores the intent; a marshal's own homeland-defense claim locked HIM out (recapture never executed); `marshal.personality_type` never existed (aggressive marshals never got their 0.8 recapture threshold); `adj_region.income` never existed (income prioritization dead — the CLAUDE.md attribute trap); AI garrison paid 1 AP vs the player's 2 (Golden Rule 5 — AI budget now reads `world.get_action_cost`); live-LLM `"action": null` escaped the anti-hallucination guard (falsy-guard fix); `_extract_valid_targets` silently CLEARED the friendly-marshal and 'generic' targets the prompt itself mandates (fuzzy could then fabricate a wrong region from leftover words); the command-history repetition guardrail was dead in live mode (`game_state["world"]` now threaded; the designed anti-spam on strategic-score bonuses engages); the M3 counter-offer "territory" sweetener was REMOVED (numeric-only, inert at ratification — the player accepted a promise that never executed; re-add owned by 8.EVAL with real wiring). **Routed with owners (verified, deliberately deferred):** 7 balance-sensitive items → ROADMAP §8.EVAL row (envoy flood, zero-combat armistice collapse, settlement indemnity direction, territory-sweetener wiring, action_priority sort divergence, evaluation-side-effect refactor remainder, advisory bands); 4 live-LLM items → CR-3 row (strategic-action dead-end, dead `dialogue` field, Berthier latency stacking, Golden-Rule-6 seam hardening). **Tests:** new `tests/test_ai_audit_2026_07.py` (14 pins); 3 `test_enemy_ai.py` intent tests re-staged onto a genuinely undefended region (their Netherlands scenario sat on a 15k legacy capital garrison the fixed code correctly refuses to blind-capture); 1 statistical flake in `test_marshal_abilities.py` seeded deterministic. Suite **`11286 passed, 1 skipped`**; ruff clean.

**July 4, 2026 — ✅ CR-2 LANDED (confidence-gate rework + clarification dialogue — the "Talk to Your Marshals" pillar's no-silent-failures slice).** All six §2 scope items shipped, each probe-verified broken on the shipped 1805 boot BEFORE the fix: **(1) marshal-aware confidence** — a leading comma-addressed name resolving to nothing (`_unresolved_address_token`: not a player marshal/visible enemy/region/nation, not an interjection) drops the fast parse to `UNRESOLVED_ADDRESS_CONFIDENCE` 0.55, under the 0.7 gate, so live mode consults the LLM BEFORE the fuzzy pass hard-errors (the spec §1 "confidently wrong" class); mock behavior is confidence-blind by design. **(2) One forced LLM retry** — `LLMClient.reparse_with_llm` fires exactly once from `parser.parse` when a mock-confident parse fuzzy-errors; validated through the same fuzzy pass; mock mode returns None (mock stays fully playable). **(3) Executor-binding demotions in BOTH extraction layers** (the mock roster scan incl. the `Marshal <Name>` regex, and parser.py's word-scan — which would otherwise re-bind what the mock demoted): a name in support-object position ("support ney" → Ney supports himself) or inside an `until` condition clause ("stand firm at belgium until ney arrives" → Ney hijacked as executor) is the supportee/condition marshal, never the executor; a live-parse net also unbinds `marshal == target` on SUPPORT/PURSUE. **(4) The unified one-question clarification** — new `backend/commands/clarification.py`: marshal-less valid orders raise "Which marshal shall support Ney / march to Belgium, Sire?" (candidates exclude the target, the condition marshal, admin/dead marshals, and — for moves — anyone already at the destination); addressed-unknown names raise did-you-mean questions from the parser's NEW structured failure fields (`kind`/`unknown_name`/`candidates`); both ride the EXISTING `awaiting_clarification` popup with per-option full **reissue `command` strings** — and the three literal/Grouchy emitters (executor gate, `_build_clarification`, combat auto-assign) now carry them too, so every clarification surface resolves through one deterministic round-trip. Questions register on the DialogueManager as LOCAL_PLANNING **`command_clarification`** (never blocks, consumed by the next input, stale-cleared at the turn boundary, JSON-plain for save/load) ONLY from main.py's player path — the executor emitters stay pure response builders, so AI commands can never create a player dialogue. Typed answers ("Davout" / "Marshal Grouchy" / "2" / "yes" / "cancel", edit-distance-1 tolerant) resolve pre-parse, deterministically (Golden Rule 6). **(5) Berthier interception extended** — probe discovery: main.py only intercepted two error shapes, and EVERY other parse failure fell through `executor.execute` into "Marshal 'None' not found. Available: none" → the generic Berthier shrug, DROPPING the computed suggestions ("Wellington, attack Mack" got "this order eludes me"); now parse failures with candidates and executor Marshal-'None' failures route to clarifications, Berthier prose remains the no-candidate fallback, and parser `warning`s (previously computed and never surfaced) append to the response message. **(6) Silent-marshal-drop fixed** — meta actions skipped ALL marshal matching, so "Murat, charge" (legacy) / "Grouchy, charge" (1805) executed with the addressee silently discarded; an explicitly-addressed token now binds (exact/auto-correct), suggests, or errors with candidates; bare meta commands ("charge" answering a glorious-charge prompt) and interjections ("No, charge!" — `ADDRESS_NON_NAME_WORDS`) keep their fast path. **(+) Sequential compound orders** — "attack Bern, then hold your positions" previously parsed as auto-assign attack on phantom region "Your Positions" + a stray strategic HOLD from the second clause; `_split_sequential_orders` now parses the first clause and Berthier reports the unrelayed tail verbatim; guards keep attack-on-arrival ("march to Vienna then attack") and unparseable-first-clause forms unsplit (true conditionals remain CR-7). **Godot:** `clarification_popup.gd` gains the `clarification_command` signal (reissues option commands verbatim; fixes the pre-CR-2 leak where the backend cancel option emitted target "cancel" → reissued "<marshal> pursue cancel"), and popup-cancel clears the backend question via a `clarification_registered`-guarded "never mind" round-trip (a lingering LOCAL_PLANNING dialogue would block mailbox activation). **Corpus (CR-1 gate):** 233→246 entries — the 3 pinned CR-2 candidates deliberately re-pinned with behavior-change notes (support-ney, move-to-reinforce-ney, stand-firm-until-ney-arrives) + 10 new cr2-* entries incl. regression pins for the guards; eval 402/402. **Adversarial review round (5 lenses → 3-skeptic per-finding verification, 62 agents; 13 confirmed = 7 distinct defects, 6 refuted — ALL 7 FIXED same session):** **(R1, CRITICAL)** Berthier-built clarifications sent `strategic_type: null` — Godot's `Dictionary.get` default doesn't apply to present-but-null keys, and assigning Nil to the popup's typed String var is a runtime crash that soft-locked input (popup never shown, input never re-enabled); fixed BOTH sides (backend omits the key for non-strategic questions; popup null-guards). **(R2, 3×-confirmed regression)** the first-cut attack-on-arrival guard only exempted BARE verbs — "Ney, march to Vienna then attack Mack"/"…then engage the Austrians" (attack_on_arrival=True pre-CR-2, probe-verified against HEAD) silently downgraded to a plain MOVE_TO; the guard now exempts any tail STARTING with attack/engage/assault. **(R3)** the combat literal-pursue chooser listed options in marshals-dict insertion order while its question named the NEAREST enemy — a typed "yes" could deterministically pursue the WRONG enemy for 2 AP; options are now distance-sorted AND the confirm branch honors the stored `interpreted_target`. **(R4)** clarifications could fire at 0 AP (parse failures precede the executor's AP pre-validation), recreating the forbidden question-then-AP-failure ordering — both builders now refuse when no answer could afford to execute (minimum-plausible-cost gate: strategic 2, 1 with a literal candidate, tactical action cost, free actions exempt). **(R5)** the answer branch ran AFTER the pending-interrupt keyword matcher, which hijacked answers like "cancel" (cancelling the marshal's real strategic order) and left the question lingering where LOCAL_PLANNING blocks mailbox activation — the answer branch now runs first (the clarification is the most recent question; non-answers still fall through to interrupt routing). **(R6)** a diplomatic FIRST clause dropped its sequel silently (the diplomatic early-return skipped the warning attach) — now warned like the military path, and the warning-append moved above the response early-returns so dialogue/popup paths carry it. **(R7)** collective/rank addressees ("Cavalry, charge!", "Marshal, charge") hard-errored where the word-scan had always skipped them — ADDRESS_NON_NAME_WORDS now mirrors the skip list (troop types + ranks). Refuted (6, incl.): _CANCEL_WORDS shadowing "stop"/"withdraw" (specified design — the question consumes one input), save-mid-clarification (unreachable: the popup is modal, the pause menu can't open), the LLM-retry double-call claim, popup route-precedence orphaning (emitters are mutually exclusive with deferred popups). **Tests:** new `tests/test_command_robustness_cr2_clarification.py` (63 — demotions both worlds, addressed-unknown guard, sequential splits + named-tail attack-on-arrival pins, confidence pins, retry via stubbed LLM, builder/interpreter units incl. the AP gates + interpreted-target confirm + strategic_type-key omission, dialogue taxonomy + serialization + stale-clear, AI-origination guard, Grouchy option-command regression, 11 endpoint wiring tests incl. 0-AP and interrupt-ordering). Corpus 246 entries, eval 407/407. Suite **`11371 passed, 1 skipped`**; ruff clean.

**July 4, 2026 (second entry) — ✅ CR-3 LANDED (LLM modernization — the live parse path is structurally sound on the 1805 boot).** All spec-row items + the four routed July-3 audit items shipped: **(1) model pin** `claude-3-haiku-20240307` (deprecated; retires Apr 2026) → **`claude-haiku-4-5`**; **(2) forced tool-use structured output** — the parse request forces a `submit_parsed_command` tool call (`PARSE_TOOL` + `tool_choice` in providers.py; new `_post_messages`/`_make_parse_request` split keeps the Berthier text path's `(text, error)` contract), so the parse arrives as already-parsed JSON — the 3-way brace extraction survives only as a defensive text fallback; `max_tokens` 500→1000 (review fix: measured outputs ~300 — truncating the forced call surfaced as an undetectable no-parse); **(3) audit (a)** — LLM strategic verbs remap at the provider seam (`pursue`→attack, `march`/`support`/`reinforce`→move, `LLM_STRATEGIC_ACTION_REMAP`); the deterministic `detect_strategic_command` still owns the multi-turn upgrade (Golden Rule 6), so live parses stop dead-ending at the executor's "Unknown action"; **(4) audit (b)** — the consumerless `dialogue` output field CUT from OUTPUT_SCHEMA + the tool schema (~wasted output tokens every live parse; revival = the Flavor Echoing candidate at the CR-5 gate); **(5) audit (c)** — new `ParseResult.llm_error` (set on API-layer failure only) propagates through the llm_client fallback → parser.py top level → BOTH main.py Berthier call sites (`skip_llm`) → a `reparse_with_llm` guard: **at most ONE blocking LLM call per request** (the old stack was parse-timeout 5s + Berthier 5s ≈ 10s worst case); stale "~300 token" budget comments corrected to the MEASURED ~5K input / ~$0.0065 per parse (live usage numbers, 126-province boot); **(6) audit (d)** — `diplomatic_data["action"]` validated against `DIPLOMATIC_ACTION_ALLOWLIST` at the `validate_parse_result` seam AND unknown diplomatic_data fields stripped (`DIPLOMATIC_DATA_ALLOWED_FIELDS` — confirmation-gate flags like `_treaty_warning_resolved`/`confirmed_objection` are dialogue-response-minted, never parse-minted; review-hardened), empty-dict hallucinations normalized instead of killing the parse; the cheat gate keys off the command's `key_source` ("none" = no live key armed; env fallback for hand-built test dicts) closing the latent BYOK hole, parser.py threads `mode`/`key_source` into every command dict, and live results now carry the client's true key_source (review fix — providers stamped "none"); **(7) prompt modernization** — the retired-19-region geographic block (actively misleading the live LLM) replaced by per-marshal compass lines derived from live `grid_position` (`_format_geography` — same data `resolve_direction` uses; scale-safe, marshal-adjacency only); few-shots became live-roster templates (`FEW_SHOT_TEMPLATES`, 12 examples — first-ever coverage for recruit/garrison/form_square/vassal/diplomacy/request_terms; diplomatic examples teach the `diplomatic_data` contract) with thin-roster review guards (single-marshal worlds skip the pair example instead of grafting "Davout"; fully-fogged worlds teach `generic` instead of "Wellington"; cold parses keep legacy names); the corpus `live_phrasing_backlog` verbs joined the strategic keyword docs. **Dispositions:** `build_clarification_prompt` CUT (never wired; the shipped clarification is deterministic — closes the §3 CR-2 deferral). **Live verification (real API, 4 calls on the shipped 1805 boot):** tool-use extraction end-to-end; "hunt down Mack" → attack/PURSUE/Mack (a backlog phrasing, previously mock-unparseable); "Soult, make your way to the Tyrol and don't give ground" → move/MOVE_TO/Tyrol; "Talleyrand, see if Austria will name their terms" → `request_terms` with `diplomatic_data` through the allowlist; ~4.9K input tokens, 1–3s latency inside the 5s timeout. **Adversarial review round (5 lenses → 15 raw findings; the 3-skeptic verification stage was lost to subagent credit exhaustion, so all 15 were adjudicated manually in-session): 5 real defects ALL FIXED** (live key_source provenance; empty-dict diplomatic_data kill; diplomatic_data field smuggling past the action-only allowlist; tool-call truncation risk at max_tokens 500; thin-roster retired-name grafts) + 4 doc-staleness items fixed (README EXAMPLE_COMMANDS/model refs, prompt_builder docstring, stale timeout comment); 6 rejected (no impact / unreachable / pre-existing — notably the "retry after LLM-unmatched" case is deliberate: sampling nondeterminism means the retry can succeed). **Tests:** new `tests/test_command_robustness_cr3_llm_modernization.py` (72 — pin/tool-schema/remap/llm_error propagation incl. Berthier-skip and retry-guard/allowlist + field-stripping/cheat-gate matrix incl. the BYOK hole/geography/few-shot roster rules/backlog coverage/clarification-cut, every review fix pinned). Mock parser untouched — zero mock behavior change (corpus 246 entries, eval green). Suite **`11443 passed, 1 skipped`**; ruff clean. **Next CR slice: CR-4 (context carryover), then the CR-5 scope blessing at the §4 gate review.**

**July 4, 2026 (third entry) — ✅ CR-4 LANDED (context carryover — the "Talk to Your Marshals" pillar remembers what you just said).** New `backend/commands/context_carryover.py` builds two features on the existing `command_history` substrate (last 50 `{raw_input, marshal, action, target, turn}` entries), all deterministic and mock-playable (Golden Rule 6 — the LLM is NEVER consulted to resolve a reference). **(1) Semantic reference resolution (PRE-parse rewrite in main.py, after the CR-2 clarification-answer + interrupt steps, before `parser.parse`):** "again"/"repeat"/"once more"/"same order" repeats the last field order verbatim (skips meta reads like status/help); "same target" reuses the last objective, and the flavored forms route by noun — "same enemy" → last enemy, "same place/province/city" → last region; "him"/"her"/"them" → the last enemy named (never a stray region); "there" → the last province named, falling back to where the last-named enemy stands; "not you, Davout" re-issues the last order to another marshal (roster-matched exact/edit-1) by stripping the old addressee from the raw phrasing and prepending the new name (so "Ney, form square" → "Davout, form square" — no unparseable `form_square` key). A reference with nothing to resolve against returns a helpful Berthier reply, never a confusing parse failure. **(2) Persistent Command Focus (`get_focus_marshal` + `try_focus_reissue`, at the executor's "Marshal 'None'" seam, BEFORE the CR-2 clarification):** a bare specific order ("hold", "move to Vienna") defaults to the last EXPLICITLY-addressed player marshal still alive/in-field, re-parsing + re-executing through the normal machinery (objections, AP, everything). It fires ONLY at the missing-executor seam — never overriding an explicit marshal, a general/auto-assign order, or a collective ("everyone", "all marshals"); falls through to the CR-2 "Which marshal, Sire?" when no eligible focus exists. **Decisions of record:** history records in BOTH mock and live modes (carryover must resolve mock-side; the live-only repetition prompt is unaffected) and each entry now carries the parsed `target` (SAVE_FORMAT row updated; round-trips as a shallow dict-copy — no schema enforcement); focus is DERIVED from history, not a new serialized field; "not you, X" re-issues WITHOUT auto-undo (deterministic undo of a resolved order is unsafe — `cancel` stays the standing-order escape); history recording is skipped while a diplomatic dialogue awaits an answer (a dialogue response that parses as an action is not a phantom order), and carryover itself is dialogue-safe because a bare "no"/"not you" with no resolvable marshal passes through untouched to the dialogue routing. **Adversarial review round (5 lenses → per-finding skeptic verification; the run crashed mid-panel when the dev box rebooted, so the 9 surfaced findings were adjudicated manually against the code — 8 distinct real defects ALL FIXED, 1 refuted):** (a) the carryover guard was over-broad (disabled during non-blocking soft-stop dialogues) — removed; safe now that bare-negation passes through; (b) a phantom field-order was recorded when a dialogue answer parsed as a valid action — recording now skips while a dialogue is pending; (c) focus silently collapsed collective "everyone/all marshals" orders to one marshal — a collective guard now skips focus so it falls to the clarification; (d) "same enemy"/"same place" ignored the enemy-vs-region distinction (could resolve an enemy word to a province) — routed by the captured noun; (e) person pronouns fell back to a region when no enemy was on record — dropped the fallback (pass instead); (f) the "Continuing with X" focus note contradicted a MILD objection and made the test flaky (~17%, probe-confirmed: Ney's fortify objection is nondeterministic — sometimes a hard stop, sometimes a grumble that proceeds) — the note was DROPPED entirely (the executor message already names the marshal, so the routing is transparent regardless); (g) `_reconstruct_order` emitted unparseable underscore keys — "not you, X" now reconstructs from the raw phrasing; (h) a leading readdress cue short-circuited in-command substitutions ("no, attack him") — the cue now falls through to substitutions on the cue-stripped remainder when it names no marshal. **Post-landing audit (user-requested, a SECOND independent complete review — 4 lenses × full 2-skeptic verification panel, 24 agents; 10 findings → 5 CONFIRMED, 5 refuted with sound trace):** all 5 fixed in a follow-up commit — (i) unanchored "there" rewrote the expletive/filler "there" into a province ("there is no time, attack" → fabricated target) and (ii) unanchored person-pronouns mangled partitive/phrasal forms ("attack all of them" → "attack all of Wellington", "hold them off" → "hold Wellington off") — BOTH fixed by anchoring the pronoun/"there" substitution to object/destination position (only after a targeting/movement verb or an object preposition; `_TARGETING_ANCHORS`/`_MOVEMENT_ANCHORS` + `_preceding_word`); (iii) a focus-reissued sequential order silently dropped its Berthier "one order at a time" tail note (the warning-surfacing ran on the pre-reissue failed result) — re-surfaced after the focus reassignment; (iv) the finding-2 recording guard was too broad — it skipped recording REAL orders executed during a non-blocking soft-stop mailbox dialogue (a live repetition-prompt regression + carryover gap), now gated on whether the input is actually a dialogue answer (hard-stop, or matches a soft-stop option) rather than the mere presence of a pending dialogue; (v) the finding-3 collective guard's `_COLLECTIVE_RE` missed "both marshals"/"the army"/"whole army"/"all corps" (focus silently collapsed them to one marshal) — regex broadened. **Verified:** `tests/test_command_robustness_cr4_context_carryover.py` (73 — resolver units incl. all reference families + the 8 first-round + 5 audit-round regressions, focus units, endpoint round-trips through /command incl. the soft-stop recording pair; the previously-flaky objection test deterministic across 8× stress); live sanity on the shipped 1805 roster (again → "Soult, attack Mack"; "same target"/"him" → Mack; "not you, Ney" → Ney; "there"/"same place" → Milan; focus → Soult). Mock parser + corpus untouched. Suite **`11516 passed, 1 skipped`**; ruff clean. **Next CR slice: CR-5 (Personality-Biased Disambiguation) — needs its scope blessing at the spec §4 gate review.**

**July 4, 2026 (fourth entry) — ✅ EC-0 + MC-0 LANDED (the two gate-free confirmed defects, pulled forward by user choice ahead of the CR-5 gate).** Both were the July-2 re-staging audit's open defects (BUG_FIXES.md), now closed. **EC-0 (advance-turn AP reset — `ECONOMY_REVISIT_SPEC.md`):** `advance_turn` reset `nation_actions` from the LEGACY 4-nation `build_default_nation_actions` regardless of `sovereign_map`, so on the shipped Europe world it squashed **Austria's tuned 4 AP back to 3 after turn 1** AND never reset the 15 Europe-only nations (Naples/Bavaria/Ottoman/…) — their `ap_per_turn` treaty penalties compounded forever (probe-confirmed: Austria 4→3, Europe-only nations never in the legacy dict). **Fix:** the constructor snapshots the world's OWN base AP into a new serialized `base_nation_actions` field (world-scoped by construction, mirroring `_starting_controllers`; from_dict defaults to the loaded `nation_actions` — correct at a turn boundary for fresh scenarios incl. modded custom-AP ones the legacy builder could never rebuild, and for pre-fix saves), and the reset restores from that snapshot. Verified on the live 1805 boot: Austria holds 4 across turns, a depressed Naples resets to base 2, an `ap_per_turn` clause on a Europe-only nation applies-then-releases (no compounding), legacy Austria stays 3 (no regression). No Slice-8 balance PIN moved in the suite — the prose Austrian-tempo verdicts were measured at 3 AP and now run at the intended 4 (flagged for the balance pass, not a test fix). **MC-0 (marshal-overview ability display — `MARSHAL_CONTENT_PASS_SPEC.md`):** `_build_ability` gated only on marshal NAME, so 1805 Ney/Davout (booted with `ability={"name":"None"}`) reported `ability_active=True` with the ability literally named "None" in the management screen. **Fix:** the gate now also requires a real ability name (`name not in ("", "None")`) — 1805 marshals correctly show no active ability (matching the mechanics: the combat wiring keys off the ability name too, so no name = no effect); legacy Ney/Davout/Drouot keep their genuine wired abilities (probe-confirmed both worlds). The optional ability-authoring was deliberately NOT done — that's the gated MC-1. **Tests:** new `tests/test_economy_ec0_ap_reset.py` (both bugs + snapshot serialization/back-compat + legacy no-regression) + `tests/test_marshal_content_mc0_ability_display.py` (unit + full-overview integration, both worlds); `SAVE_FORMAT_REFERENCE.md` gains the `base_nation_actions` row; BUG_FIXES.md entries marked FIXED. Suite **`11538 passed, 1 skipped`**; ruff clean. **Queue now: back to Command Robustness CR-5 (needs its §4 scope blessing) — or the remaining Economy Revisit / Marshal Content slices, all gated.**

**July 5, 2026 — ✅ CR-5 SCOPE BLESSED (design-gate decision session; documentation-only, no code).** The §4 CR-5 gate review ran against a code-verified pipeline audit + an adversarial design panel (5 verify agents + 3 red-team agents). **Decisions of record:** **(1) Sequencing — CR-5 ships BEFORE the Marshal Content Pass:** CR-5 keys off personality *type* (authored for all 21 marshals, already piped into the parse `game_state` at `main.py:191`, rendered per-marshal into the live prompt at `prompt_builder.py:541`, and already interpretation-load-bearing at `executor.py:599`), not abilities/skills/relationships (the thin, gated MC-1/2/3 content); CR-5-first also makes MC-4's roster-skew call empirical. **(2) The "Grouchy asks" headline is reframed AND the literal arm is made player-reachable** — as audited the 7 commandable French marshals were 4 aggressive + 3 cautious + ZERO literal (all 3 literal marshals are enemy), which would leave CR-5's signature *third* arm invisible. **User decision at the gate: Soult reassigned `cautious → literal`** in `europe_1805.json` (his Pratzen assault = precise on-the-hour execution; bio nudged; chosen over Davout — VISION's canonical cautious — and Bernadotte — worst historical fit), so player-visible behavior is the full three-way **aggressive→attack / cautious→scout / literal(Soult)→ask** split (distribution now 13 cautious / 4 aggressive / 4 literal). Pinned by `tests/test_europe_1805_scenario.py::test_cr5_literal_arm_player_reachable` (44 passed). Ceiling caveat recorded: CR-5 only lights literal's "asks" behavior; the dramatic continue-into-disaster beat stays gated behind the autonomous Grouchy Moment. **(3) Guardrails blessed** (spec §6.3): action-only at `validate_parse_result` (Golden Rule 6); temp 0.3→0 pin (free post-CR-3 forced tool-use); an **objection-first ONE-modal legibility** rule (inferred battle-starting action → evaluate_situation → objection-or-confirm; inferred non-battle → soft note + one-tap reissue; explicit → no confirm) that fixes the draft's double-prompt collision; a **blocking personality-type pre-flight** before the aggressive→attack arm; explicit mock-degrade-to-CR-2-clarification; and a LIVE-tier corpus assertion (same utterance × personality → distinct action, literal tested via the legacy-Grouchy fixture). **(4) Riders:** (d) "player's words become the record" ACCEPTED into CR-5 as a separately-tested sub-item (own STATUS row + own test), justified as legibility payoff ONLY — the claim that it addresses anti-memorization was STRUCK; **Flavor Echoing promoted from §4 to owned slice CR-5b** with all five Golden-Rule-9 elements (its non-parroting mock design is the entry gate). **(5) Cuts/re-homes:** the "march to the guns → literal continues standing order" verb row was CUT (unimplementable at the parse seam — the parser has no read of active `StrategicOrder`, and `hold` means stop; and it's a category error — the autonomous Grouchy Moment is an event/AI feature, re-homed to its own gate in §4); a "mechanical delegation incentive" gap was named + parked (this phase declares delegation feel-first / mechanically-optional). **Docs updated:** `COMMAND_ROBUSTNESS_SPEC.md` → v0.5 (masthead + CR-5 blessed row + new CR-5b row + §4 gate dispositions + full §6 blessed scope incl. the authored verb table); CLAUDE.md Current-Phase + Design-Gates lines; `ROADMAP.md` open-decisions + the Post-Diplomacy row; the restaging memory. **Then commit `d0371de` (pushed) + a cold-eyes player review → spec v0.6 review-hardening (new §6.7):** the review's one blocker was **discoverability** (CR-5 as first blessed shipped *invisible* — a player who types explicit verbs never learns delegation exists, and the bias is imperceptible from a single command), fixed by (i) requiring every inferred-resolution surface to NAME the marshal's personality (deterministic, mock-safe — "Ney needs no second invitation, he attacks" / "Davout, cautious as ever, will scout first") so the bias is perceptible + CR-5 becomes independently demonstrable, and (ii) a once-per-campaign Berthier first-use hint (owned + tested). Also folded: the audience is stated (feel-first roleplay/immersion player, not the optimizer), the live-only exposure is made honest (mock default sees no bias — value scoped to live/BYOK players), adjacency/distance clarified as the executor's job not the LLM's, the "cover/watch" fork cut, and guardrail (d) relabeled a human sign-off (not automated coverage). **Then the guardrail-(d) sign-off itself was performed (4-lens panel — historian/designer/systems/skeptic — over the 7 commandable French marshals; §6.8):** 6 keeps — including **Massena KEPT aggressive**: a brief recast→cautious (to defuse the dangerous "deal with Charles"→42k-into-fortified-54k arm) was **REVERTED** per a design rule of record — **personality = the marshal's CHARACTER, not his scenario situation; danger is the guardrail's job, not a reason to falsify the man** (Massena was one of Napoleon's most aggressive marshals and attacked Charles at Caldiero in 1805; his holding role is situation; pinned by `test_cr5_signoff_massena_aggressive_is_his_character`). Plus the sign-off's most important output, a **guardrail-(c) SPEC DEFECT found + fixed**: (c) only gated the *adjacent* inferred attack, but the *non-adjacent* attack-on-arrival path (Massena/Murat via MOVE_TO/PURSUE) bypasses it through `_strategic_execution:True` (skips objections + AP) and a fortification-blind odds rule — so the spec now requires the attack-on-arrival seam to route through the same fortification-aware gate (mandatory regardless of the Massena recast — it still exposed Murat). Design-log notes: Davout is the panel's *best* literal fit (cautious is the residue of Soult owning the literal slot); Bernadotte's real trait (political unreliability) has no personality type → MC-3. Full-roster distribution 13 cautious / 4 aggressive / 4 literal (Soult literal is the ONE disclosed exception to the character rule — no French marshal is a natural literal — owned by MC-4). **Next: implement CR-5 → CR-5b.**

> The June 9-12, 2026 session entries (re-sequencing decision, G4F-1..23 fix ledger, GT/CH landings) moved to `docs/archive/STATUS_SETTLEMENT_SESSIONS_2026_06.md` (July 2, 2026 re-staging trim).


## Last Recorded Spec Review Result

> The May 2026 Codex spec-review and branch-reconciliation records moved to `docs/archive/STATUS_SETTLEMENT_V027_PROCESS_2026_05.md` (June 10, 2026 trim). Branch state: all settlement work is on `master` (single-branch workflow per CLAUDE.md).

## Manual Smoke Fixture Variants

Before Gate 4 manual settlement UI smoke, set `SOVEREIGN_SMOKE_START=settlement_multilateral` for the shared France vs Britain + Prussia war. Run `SOVEREIGN_SMOKE_START=settlement_losing` for concession-baseline and losing-side authoring paths, and run `SOVEREIGN_SMOKE_START=settlement_rejected` separately for blocked-popup, SC-10b / SC-28 / SC-28b recovery, scoped-draft, no-direct-pair-action, and actionability-gated War Detail paths. Use `SOVEREIGN_SMOKE_START=settlement_multiwar_ambiguity` for the required same-nation multi-war ambiguity check; Gate 4 step 1 cannot close unless smoke evidence names this fixture and records the rendered disambiguation or hidden-action outcome. The losing and rejected fixtures are both required; one cannot stand in for the other.

## Verification Snapshot — Settlement arc (HISTORICAL; the arc closed July 3, 2026)

Slice G / AI-ally settlement agency cut/ship ownership is no longer blocked on the rejected, losing, multiwar ambiguity, surrender, recurring-gold, forced-alliance Continental toggle differential, same-war off-editor, incoming-offer mailbox/popup fixture smoke paths, or `DWL-SET-SC5R`. The SC-5R backend/editor repair now provides the edit-capable counter-draft surface, Submit for Review path, scoped draft preservation, active-vs-archived routing, and executable Godot parse evidence; Gate 4 manual smoke evidence remains the player-quality release gate. SC-32 landing ownership remains tracked rather than open-ended, and SC-29 / SC-30 / SC-31 / SC-33 remain regression-covered after landing.

> The v0.27 Integration Compatibility Table (all rows PASS) moved to `docs/archive/STATUS_SETTLEMENT_V027_PROCESS_2026_05.md` (June 10, 2026 trim).

## Deferred Work Landing Ledger

Use this ledger as the current routing layer for any active `deferred`, `future`, `later`, `polish`, `hidden`, `cut`, or `backlog` wording in specs. Status values are `ACTIVE_DEFERRED`, `LANDED`, `SUPERSEDED`, or `REMOVED`. New deferrals must name a ledger ID or a concrete `SC-*` / slice row, plus an owner, landing trigger, completion definition, and required behavior test.

| ID | Source | Status | Owner | Landing trigger | Completion definition | Required test / evidence | Notes |
|----|--------|--------|-------|-----------------|-----------------------|--------------------------|-------|
| DWL-SET-SC5 | WSA `incoming_settlement_offer` / cleanup SC-5 | LANDED | `SETTLEMENT_UI_CLEANUP_SPEC.md` SC-5 + Slice G1 appendix | May 17, 2026 commit 2 landing closes the offer producer / mailbox / popup promotion substrate. Commit 1 (`2a1f9d7`) shipped the backend producer + handler substrate; commit 2 ships the UI promotion layer | Commit 1: `process_settlement_offer_phase(world)`, per-`war_id` cooldown, one-active-offer guard, stable `offer_id="settlement_offer:{war_id}:{turn}:{seq}"`, package-preserving `handle_incoming_settlement_offer_action` accept/reject. Commit 2: `promote_pending_settlement_offers(world)` drains pending into the dialogue_manager mailbox (idempotent across save/load), `build_incoming_settlement_offer_popup(world, offer)` builds the popup payload with Voice Bible §16.1 incoming-offer copy, `PERSISTENT_MAILBOX_TYPES` taxonomy split so offers persist across turns, `INCOMING_SETTLEMENT_OFFER` notification family + `incoming_settlement_offer_popup` popup-queue slot + `settlement_offer_arrival` dispatch event, turn-manager wiring promotes + notifies + dispatches, `/mailbox` + `/pending_envoy` + `/mailbox/activate` surface the offer popup payload, `request_settlement_revision` stages a seeded `settlement_confirm` review with `counter_to_offer_id` provenance + request-revision Voice Bible heading, Godot `main.gd` whitelists + replaces deferred route with real popup route, `proposal_confirm_popup.gd` gains the `incoming_settlement_offer` match arm + builder | Commit 1: `tests/test_settlement_incoming_offers.py` (22 tests). Commit 2 plus later repairs: `tests/test_incoming_offer_deferral_no_leaks.py` (31 tests after May 18 audit-repair additions and G2d D2 cut-evidence additions) cover taxonomy / promote idempotence / `/mailbox` + `/pending_envoy` + `/mailbox/activate` payloads / Voice Bible §16.1 resolution / hidden-control absence / Godot whitelist + route order + popup-builder source guards / 50-turn soak / SC-30 required tests / G2d retired-flag absence tests | Offer promotion remains landed. The prior "real counter editor" wording was an overclaim; the edit-capable request-revision repair is tracked separately in `DWL-SET-SC5R`. `INCOMING_OFFERS_DEFERRED` stays as a named flag for emergency disables but defaults to False |
| DWL-SET-SC5R | Incoming-offer `Request Revision` / settlement revise counter-editor repair | LANDED | Settlement UI Cleanup SC-1 / SC-2 / SC-5 / SC-30 repair | May 28, 2026 SC-5R-1 + SC-5R-2 landed the backend EDIT contract, Godot editor, scoped draft round-trip, active-vs-archived routing, and incoming-offer label/copy alignment; the follow-up repair on `master` fixed the archived-route cache guard, self-gated `show_editor(...)`, empty Open Settlement / Request Revision EDIT mounting, inline editor error remounts, backend-revalidated in-editor concession-baseline application, strengthened tests, and refreshed the Godot parse report. | Real EDIT-mode counter-draft path is present: Godot clause controls consume backend `available_clause_types[]` / `clause_control_schema`, empty Open Settlement starts in EDIT with Submit disabled, covered-enemy scope is editable, clause add/edit/remove authors structured draft clauses, `Submit for Review` submits through `_execute_propose_common_peace` with final validation, revised drafts persist by scoped `draft_key`, staging and ratification reject invalid terms, active partial-settlement review routes preserve live-war context while archived wars route to settlement history, and incoming-offer Review/Revision/Reject copy matches behavior. | `tests/test_settlement_sc5r1_backend_contract.py`, `tests/test_settlement_sc5r2_godot_editor.py`, the adjacent settlement/incoming/recovery bundle, and `tests/test_godot_parse_harness.py` cover backend contract, editor source/scene, draft restore, active-vs-archived routing, label copy, and parse/load report coverage for `settlement_editor_popup.gd`. | The Gate 4 smoke RAN July 2, 2026 (machine half green; visual half pending user confirmation). NOTE: the SC-5R freeform editor was RETIRED by Guided Terms GT-Slice-4 (June 10, 2026) — surviving SC-5R deliverables are the scoped `draft_key` persistence, non-destructive Back Out, archived-war routing, incoming-offer labels, and pre-stage/pre-ratify revalidation. |
| DWL-SET-SC29 | Direct-pair substitute CTAs (`Seek Armistice Instead`, `Seek Bilateral Peace`) | LANDED | Settlement UI Cleanup SC-29 / G2-Slice-7 | G2-Slice-7 shipped May 13, 2026 with `evaluate_pair_peace_substitute_eligibility(...)`, blocked-popup options emission, dialogue-handler dispatch, and committed Voice Bible families | Blocked settlement review surfaces pair-scoped `Seek Bilateral Peace` / `Seek Armistice Instead` between Re-author and Open War Detail only when the selected target pair is eligible; only `cooldown_active` may render disabled; click-time re-resolution refuses to mutate on state change; substitute hand-off stages `proposal_confirm` for `propose_peace` / `propose_armistice` with `target_nation = selected_target_nation` | `tests/test_settlement_pair_substitute_ctas.py` (19 tests covering helper schema, closed taxonomy including resolved-pair mapping, disabled vs hidden policy, post-SC-29 popup integration, click-time re-resolution, no SC-14b reopen-attempt consumption, per-pair staging, cross-war settlement collision, draft preservation/invalidation, voice family routing, helper-signature isolation) | Hidden until implemented; clickable copy-only controls forbidden |
| DWL-SET-SC30 | Enemy-offer waiting (`Wait for Enemy Offer`, `Ask for terms`) | REMOVED | Settlement UI Cleanup SC-30 / Slice G1 + SC-32 / G2-Slice-G2d | Incoming-offer producer + UI promotion + mailbox + popup remain live through DWL-SET-SC5. G2-Slice-G2d (May 28, 2026) terminally removes `Wait for Enemy Offer` / `Ask for terms` from player-facing scope; no SC-30b/c lifecycle is promised. | `wait_for_enemy_offer` / `ask_for_terms` action ids do not appear in any backend dispatch or Godot whitelist; the incoming-offer popup `options[]` only lists `accept_settlement_offer` / `request_settlement_revision` / `reject_settlement_offer`; popup payloads no longer expose `wait_for_enemy_offer_visible` or `ask_for_terms_visible`; `wait_for_enemy_offer_unavailable` is absent from display names. | Existing SC-30 absence guards remain in `tests/test_incoming_offer_deferral_no_leaks.py`; G2d adds `test_wait_for_enemy_offer_visible_flag_removed_from_payload_v032`, `test_ask_for_terms_visible_flag_removed_from_payload_v032`, and `test_wait_for_enemy_offer_unavailable_display_string_removed`. | Terminal CUT per SC-32 D2 (the retired `Wait for Enemy Offer` / `Ask for terms` LABELS). **The distinct Request Terms lifecycle retained by SC-30 LANDED July 2, 2026 at `1a9da53` (Slice G1)** — `request_terms` verb + affordance + grant/refuse/lapse resolution; the cleanup-spec SC-30 row is LIVE. Future wait/subscription behavior still needs a new feature spec. |
| DWL-SET-SC31 | `Surrender terms` + dependency clause types (`vassalage` / `subjugation` / `liberation`) | LANDED | Settlement UI Cleanup SC-31 / G2-Slice-8 | G2-Slice-8 shipped May 14, 2026 with `SETTLEMENT_LIVE_CLAUSE_TYPES`, dependency eligibility helpers, the `[peace, harshest-legal-dependency]` surrender preset (subjugation-then-vassalage order), the `author_surrender_terms` blocked-popup action + dialogue handler with click-time revalidation, the `surrender_preset` propagation through staging / ratify / reactions / `settlement_summary`, applied_clauses_preview rows for dependency clauses, Voice Bible §16.1 surrender/dependency families, the `SOVEREIGN_SMOKE_START=settlement_surrender` fixture, Godot popup banners, and Codex audit repair `codex-2026-05-14-settlement-G2-Slice-8` | Dependency clauses live in `available_clause_types[]`, surrender preset authors a deterministic concrete dependency package only when `losing_for_concession_baseline=true` AND a power-cap-legal dependency exists, ratification mutates real vassal state by explicit `from`/`to` direction even when the player is surrendering, and history/dispatch/ledger/Voice Bible §16.1 render the dependency consequence | `tests/test_settlement_dependency_clauses.py` (39 tests: clause-control schema inversion, closed-taxonomy validator rejection, eligibility helpers, surrender preset deterministic ordering + fallback, payload schema, blocked-popup CTA visibility, dialogue handler replace-confirm / click-time revalidation / no-overwrite, player-side surrender ratification mutation, `settlement_summary.surrender_preset` propagation, applied_clauses preview fields, smoke fixture, Voice Bible families) | DWL row was previously two entries (dependency clause types + surrender preset); merged into a single LANDED row because the slice ships them together |
| DWL-SET-SC32 | Broader settlement agency | LANDED | Settlement UI Cleanup SC-32 / Slice G2 | G2-Slice-G2a, G2e, G2d, G2b, G2c, and G2f landed on master | SC-32 v0.32 outcomes are closed: AI counterproposals, Wait-for-Enemy-Offer / Ask-for-Terms, voluntary alignment, conference / veto, and request_consultation / request_redress_after_settlement are cut with absence tests; `request_open_settlement` and `warn_against_sellout` ally petitions ship as solicited advisory mailbox items; `request_reward_or_restoration` and `demand_bargain_honor` are deferred to Slice H with absence tests; same-war replace-confirm ships; D7 remains solicited only. | `test_settlement_agency_landing_ledger_has_no_unowned_backlog_controls` plus the G2b/G2c/G2d/G2e/G2f behavior and absence suites named in `SETTLEMENT_UI_CLEANUP_SPEC.md` v0.32 | Closed by the May 28, 2026 all-completed-audit-punch-list repair. **SC-32's formal close condition (after-G1 ordering per spec §Slice G2) completed July 2, 2026** — G1/SC-30 landed at `1a9da53`; closure bookkeeping executed the same day. Future settlement-agency work needs a new owner row/spec amendment; the one surviving deferred sub-outcome (Slice H petitions) is owned by `docs/SETTLEMENT_SLICE_H_ALLY_PETITIONS_SPEC.md` (awaiting design gate). |
| DWL-SET-SC33 | Recurring gold payments (`gold_per_turn`) | LANDED | Settlement UI Cleanup SC-33 / G2-Slice-9 | G2-Slice-9 shipped May 14, 2026 with editor-live `gold_per_turn`, validator bounds (`amount >= 10`, `1 <= turns <= 20`), projected-solvency `gold_payment_budget_conflict`, `world.recurring_settlement_payments` storage, the per-turn `process_recurring_settlement_payments` processor wired into `advance_turn` between vassal tribute and the bankruptcy check, four cancellation conditions (payer eliminated / payer vassalized / recipient eliminated / renewed war), `amount * turns` harshness projection at the lump-sum weight, `applied_clauses_preview` value fields (`payer_balance_before`, `payer_balance_after_first_payment`, `projected_total_obligation`, `first_payment_turn`), Voice Bible §16.1 `settlement_recurring_gold_authored / _ratified / _completed_talleyrand`, dispatch templates for `settlement_recurring_gold_paid / _partial / _completed / _cancelled`, and `SOVEREIGN_SMOKE_START=settlement_recurring_gold` fixture. | `gold_per_turn` lives in `CLAUSE_CONTROL_SCHEMA` with `enabled=True, visibility="live"`; ratification registers a recurring obligation without moving gold immediately; the income-phase processor transfers `min(amount, balance)` once per turn, decrements `turns_remaining`, and removes the record on natural completion; harshness uses full projected obligation; old saves default `recurring_settlement_payments` to `[]`. | `tests/test_settlement_recurring_gold.py` (27 tests: SC-33 4 required + clause-control schema live + validator amount/duration/budget conflict bounds + minimum/maximum bound acceptance + display registry coverage + ratification registers obligation + public ratify/advance-turn processing + real eliminated-nation cancellation through the WorldState path + first-tick gold transfer + decrement + partial payment + natural completion + four cancellation conditions + save/load round trip + default-empty pre-SC-33 saves + harshness projection finite vs perpetual + smoke fixture + wizard structured payload acceptance + player-facing popup author/dispatch/replace-confirm coverage). | DWL row was ACTIVE_DEFERRED, now LANDED; canonical clause schema marks `gold_per_turn` as `Live after SC-33 / G2-Slice-9`. |
| DWL-DIP-E7 | `DIPLOMACY_SPEC.md` E7 defiance floor redesign | **✅ LANDED July 16, 2026** in the 8.5 Batch Q Chunk 2 — `backend/commands/diplomatic_defiance.py` `STRONG_EMPEROR_DEFIANCE_FLOOR` + `_defiance_floor_for_authority` (:41/:44/:99/:131) | 8.EVAL gate record `docs/audits/EVAL_8_2026_07_16.md` §1 | Verification found the floor DORMANT: at boot authority 100 the curve computes 0.00 and the 2% floor IS the rate for the whole early-mid campaign — the sabotage/discovery/redemption arc + two shipped popups are near-dead content; spec §3a also still documents the PL-23-retired trust term | **Decision: authority-banded floor** (Jealousy §0.2-11b boot-dormancy precedent — NOT a flat raise); fix the §3a spec drift in the same slice; verify the sabotage-discovery popup live once | Re-pinned defiance probability tests at the banded values + a live popup check | Build slice in the Phase-8.5 opening Batch Q |
| DWL-DIP-AIAI | `DIPLOMACY_SPEC.md` old AI-AI diplomacy deferral | LANDED | Phase 8 Session 8D / AI diplomacy | Already landed | `process_ai_ai_diplomatic_phase`, AI-AI treaty state changes, dispatch, fog visibility, and campaign-log routing exist | Existing AI-AI diplomacy / dispatch / campaign-log tests | Old "Session 8 deferred" note is historical only |
| DWL-DIP-TRADE | `DIPLOMACY_SPEC.md` trade income deferred to Session 2 | LANDED | Phase 8 Session 2 diplomacy | Already landed | Diplomatic-state trade income is applied during income phase and shown in economy surfaces | Existing trade-income and ledger tests | Old Session 1B deferral is historical only |
| DWL-DIP-CONTINENTAL | DD7 `Full Continental System` | LANDED | Phase 8 / Coalition / Peace Deals WPS-C | Already landed | Continental System membership, income effect, forced-alliance membership, dispatch, and save/load are live | Existing Continental System and WPS-C tests | No separate "full" placeholder remains |
| DWL-DIP-FOGINTEL | DD7 fog-filtered diplomatic intel | LANDED | Fog / ledger / dispatch systems | Already landed | Diplomatic AI-AI state visibility uses PARTIAL+ rules; player-facing strength/status paths use fog-filtered helpers | Existing fog, dispatch, ledger, and campaign-log tests | Future intel polish must get a new owner row |
| DWL-DIP-CAMPAIGNLOG | DD7 campaign-log diplomatic events | LANDED | Campaign log / dispatch systems | Already landed | Diplomacy events including AI-AI treaty and peace/settlement families route through campaign log filters/oneliners | Existing campaign-log enforcement and diplomacy event tests | Old display-only gap is closed |
| DWL-DIP-SPECIALBONUS | DD7 special acceptance bonuses | LANDED | Diplomacy acceptance formula | Already landed | `SPECIAL_BONUSES` feed `special_desire_bonus` and surface in acceptance components | Existing acceptance and session 8D tests | Future tuning is balance polish, not a missing mechanic |
| DWL-DIP-METTERNICH | DD7 Metternich armed mediation | **✅ LANDED July 16, 2026** in the 8.5 Batch Q Chunk 2 — `backend/game_logic/coalition.py` `record_schemer_peace_rejection` + `schemer_rejection_pressure` (:784/:801/:809) | 8.EVAL gate record `docs/audits/EVAL_8_2026_07_16.md` §1 | Verification: never built; the spec'd "+5 coalition bonus" concept maps to nothing in code; rejecting an AI proposal today costs only a 3-turn cooldown — consequence-free | **Decision: rejecting a Schemer-authored PEACE-family proposal (armistice/peace only — never subsidy/trade asks) applies a once-per-rejection, 5-turn-expiring war-pressure marker on the existing coalition-threat substrate**; AI-only, GR5-clean, anti-stacking guarded; retire the stale `DIPLOMACY_SPEC.md §5c` "+5" text at landing | Rejection → expiring Austria war-pressure test + no-fire-on-subsidy-asks guard test | Build slice in the Phase-8.5 opening Batch Q |
| DWL-DIP-RENAME | Carved-vassal player rename example | REMOVED | None | N/A | No active command promise; do not show rename command examples until a future naming/customization spec owns it | Deferred-word scan shows no active "rename vassal" promise | Removed because it is low-value polish with no current UI/editor surface |
| DWL-DIP-CONFERENCE | Old "Peace conference (multi-nation)" note | SUPERSEDED | Imperial Settlement / possible future Congress System | Current common-peace needs are owned by Imperial Settlement; no Congress work starts without a new spec | Treat old peace-conference promise as superseded by common peace. A future Congress System must open a new design gate if desired | Peace Deals / settlement spec audits confirm common-peace ownership | No separate conference minigame is planned |

> The May 13-14, 2026 G2-Slice-7/8/9 landing records and the superseded slice queue moved to `docs/archive/STATUS_SETTLEMENT_V027_PROCESS_2026_05.md` (June 10, 2026 trim).

---

## Quick Stats

| Metric | Value |
|--------|-------|
| **Tests Passing** | **Current master verification (August 3, 2026 — HEAD `e3edb4e`, DP-1):** full suite **`15,901 passed, 3 skipped`**; ruff clean; Godot import+parse harness EXIT=0, report regenerated August 2 (`tools/godot_parse_report.json` — 28 scripts + 3 scenes, 0 failures); headless boot 0 `SCRIPT ERROR`; M1–M7 and `BASELINE_SERIES` byte-identical without re-record. |
| **Current Phase** | **✅ DEF-5 NAVAL "The Wooden Wall" BUILT COMPLETE — NV-0..NV-11 + NV-V LANDED August 2, 2026** (records `NAVAL_SPEC.md` §14 = NV-0..NV-3, §15 = the second pass; the §12 gate and the NV-4..7 gate both taken at recommended defaults), plus **DP-1** the pair-keyed stalemate-counter fix (§15.14, HEAD `e3edb4e`). Behind it: **AI Intent CLOSED** (Stages A–G + the AI-V sweep, Aug 1 — `AI_INTENT_SPEC.md` §20); **Battle Diorama Tier A** (Jul 31, user-verified in game); **row IGR build-complete** (Jul 31); **Nation Agendas NA-0..NA-6d** (Jul 17–19); **Combat Overhaul program CLOSED** (Jul 16, overall 6.4→≈7.6). **▶ NEXT: a long human-played quiet-France campaign** — the living-balance / D1-band vehicle, which doubles as the naval live pass. **Routing beyond that = the user's call.** **⚠ One USER DECISION is DUE:** the `Normandy↔Berry` / `Flanders↔Orleanais` adjacency ruling (`NAVAL_SPEC.md` §15 / :756) — its precondition, the visual pass, was met Aug 2. |
| **Next Roadmap Gate** | **NONE currently blocking.** Held + closed: ~~8.EVAL~~ (Jul 16, `docs/audits/EVAL_8_2026_07_16.md`) · ~~CR-6 mini-gate~~ (Jul 16, `COMMAND_ROBUSTNESS_SPEC.md` §7) · ~~the 8.5 design gate = Nation Agendas~~ (Jul 17, `NATION_AGENDAS_SPEC.md` §0) · ~~the naval §12 gate~~ (Aug 2, recommended defaults incl. Q5 = naval v1 into EA scope) · ~~the NV-4..7 gate~~ (Aug 2, four decisions at default). **Open but not blocking, each with its own gate:** Pre-EA Victory & Objectives Pass · CR-6 *proper* (Conversational Objection Negotiation) · EC-2 **pass 2** (ES-4 + ES-7b) · the Battle Gallery · DEF-12 full map modes · IGR-X9 (homed at the econ gate — see ROADMAP row EC-P3). |
| **Blockers** | **NONE.** No item in the live queue is blocked on a user gate. The nearest thing to a blocker is **evidence, not permission**: DEF-5/DEF-6 cannot close until a human plays a campaign (the naval pillar score, the played A2 sue-path, the NV-4..NV-11 visual sign-off, the NV-P1 live wheel check, and the NV-V remainder — anchors A1–A5 measured in a played world, the NV-D7/NV-D8 verdicts, the Q7 texture re-open check). |
| **Code Coverage** | ~71% (backend/) — **last measured February 18, 2026 (`bb3392b`); not re-measured since, treat as indicative only.** |

---


## Next Steps (re-staged July 2, 2026)

> The pre-cutover Next Steps section (April–June vintage; it still routed to Slice B3 and an art-blocked renderer) moved to `docs/archive/STATUS_NEXT_STEPS_PRE_RESTAGING_2026_07.md`. **The forward queue now lives in `docs/ROADMAP.md` §Current Phase Queue** — this section is the short live mirror.

> **▶ NEXT SESSION STARTS HERE (updated August 3, 2026, twenty-first entry): THE NAVAL
> PHASE (DEF-5) IS BUILT COMPLETE NV-0..NV-11 AND DP-1 IS FIXED — next is a long
> human-played campaign that closes the remaining measurements, then the ROADMAP spine
> at the user's routing.**
>
> **HEAD `e3edb4e` · suite 15,901 passed / 3 skipped · ruff clean · Godot import+parse
> harness EXIT=0 (28 scripts + 3 scenes, 0 failures) · headless boot 0 `SCRIPT ERROR` ·
> M1–M7 and `BASELINE_SERIES` byte-identical without re-record.**
>
> **Landing records (authoritative):** `NAVAL_SPEC.md` §14 (NV-0..NV-3 "The Wooden Wall")
> + §15 (the second pass NV-4..NV-11, incl. §15.14 = DP-1) · `AI_INTENT_SPEC.md`
> §18/§19/§20 — **the AI Intent phase is CLOSED** (Stages A–G + the AI-V sweep, Aug 1;
> pin 20's visual half signed off the same day) · `BATTLE_DIORAMA_SPEC.md` §14/§14.1
> (Jul 31, user-verified in game).
>
> **▶ DO THIS NEXT — ONE session, a played campaign.** It is the only vehicle for four
> open measurements, and it closes them together:
>
> 1. **The long quiet-France campaign** (30+ turns, France passive mid-game) — the only
>    thing that moves living balance off 6.5 and measures the D1 played moment
>    (`AI_INTENT_SPEC.md` §20 Dispositions; `AI_WAR_DECISION_SPEC.md` §8.2 — ambient
>    council wars measured **0 over 40 turns on every seed with the blocking predicate
>    WRITTEN**; that is a reachability result, not a regression, and it needs a played
>    moment rather than another probe).
> 2. **Score the naval pillar** and drive the **played A2 sue-path** (`NAVAL_SPEC.md`
>    §15.8 / §15.12 — the arc was driven *scripted* at NV-10; §15.12 explicitly does NOT
>    falsify the 80%-closure acceptance arm, so the played measure is still owed).
> 3. **Visual sign-off on the NV-4..NV-11 surfaces** — the amber DEFENDED SHORE tint,
>    the Admiralty posture/Diversion chips, the region-panel landing chip, and the naval
>    diorama in motion — plus the **NV-P1 live wheel check** (`BUG_FIXES.md` §NV-P1: a
>    one-line `mouse_filter` change no headless test can prove).
> 4. **The NV-V remainder DEF-5 closes on:** anchors A1–A5 measured in a *played* world,
>    the NV-D7 (weather/season) and NV-D8 (ambient expedition) verdicts, and the Q7
>    texture-option re-open check.
>
> **⚠ ONE USER DECISION IS DUE** — its precondition, the visual pass, was met Aug 2:
> the **`Normandy↔Berry` (162px) / `Flanders↔Orleanais` (128px)** adjacency ruling
> (`NAVAL_SPEC.md` §15). These are the longest LAND edges out of their provinces and are
> the interior route a landed British army actually uses to walk inland. Cutting them
> stops the walk; but this map's adjacency is derived from DRAWN shared borders, so
> cutting them makes the map visually lie. **Worth ruling before the campaign, so the
> played run measures the intended topology.**
>
> **Then the ROADMAP spine (routing = the user's call):** the remaining Phase 8.5 content
> → STEAM PAGE + LLC → 9 (Advisors) → 10 (Character & People) → 11 (Imperial Governance
> promotion only — the vassal core landed Jul 14–16 and the Britain naval/subsidy half
> landed Aug 2) → Pre-EA (incl. the **Victory & Objectives Pass**) → EA.
> **Nothing in the live queue is blocked on a gate.**

> **[Superseded August 3, 2026 — AI Intent CLOSED Aug 1; the naval phase BUILT Aug 2.]**
> **▶ NEXT SESSION STARTS HERE (updated July 31, 2026, twentieth entry): THE BATTLE
> DIORAMA (row BD, Tier A) IS BUILT + LANDED — next is `AI_INTENT_SPEC.md` §11 Stage E.**
>
> **BD LANDED July 31, 2026, second session that day, under the user's direction
> ("do this phase but please make it truly exceptional … add to the game's drama").**
> Landing record = `docs/BATTLE_DIORAMA_SPEC.md` §14 (authoritative); evidence pack =
> `docs/audits/BD_TABLEAU_{TRIUMPH,DEFEAT,MIDCASCADE}_2026_07_31.png`. Suite
> **15,368/3** (the 6 "errors" in the raw run are the documented PYTHONIOENCODING
> subprocess artifact — all 74 tests in those two files pass with the variable stripped),
> ruff clean, parse harness EXIT=0 (report regenerated), headless boot 0 `SCRIPT ERROR`,
> and a live runtime smoke drove the tableau through final-frame → cinematic → skip →
> replay → close with zero errors.
>
> - **The backend half** — `backend/game_logic/battle_diorama.py`: the eval-§6
>   `contingents[]` payload assembled in `_execute_attack` (one builder, solo AND
>   coordinated), riding BOTH transports (whitelisted `battle_diorama` result field +
>   `events[0].diorama` for the enemy phase). Committed strengths from a new
>   all-participant pre-battle snapshot; the dead `casualty_distribution` finally read;
>   statuses {engaged, reinforced, failed_arrive, routed(primary), destroyed};
>   the grudge-explains-gap line (player side only); fog: player battles full, third-party
>   at FULL only, enemy no-shows at FULL-of-their-region only. Two predicates:
>   `significant` (the blessed §7-Q2 arms, "named" read as the Great tier — recorded
>   interpretation) gates the player's own auto-play; `dramatic` (decisive/great/rout/
>   conquest/multi-corps) gates the UNINVITED enemy-phase auto-play — resolving the
>   eval's internal §7-Q2-vs-§2 tension toward its own fun-curve. `register`
>   {triumph/defeat/grim/observer} = the §7-Q6 defender's-eye framing as code.
> - **The frontend half** — `battle_diorama.tscn/.gd` (layer 121) + `diorama_figure.gd` +
>   `portrait_locket.gd`: the carved-wood tray (walnut + gold + filigree + green baize +
>   upper-right lamp), the map's OWN carved-oak pieces as figures (shared texture cache,
>   public `WarTablePiece.layer_texture`/`legible_tint`), the fixed topple verb (rotate
>   78° about the feet + darken + long shadow; base stays), real heraldry standards that
>   fall and — on a decisive field — are TAKEN across the centre line, sepia-brass
>   portrait lockets (monogram fallback, glass greys on a rout, standing ★), odometers
>   (red only) bound to the cascade, the register-toned banner, Berthier's verdict typed
>   LAST in IM Fell, the engraved Cinzel nameplate + wax seal + triumph laurels.
>   Cannon thud (CC0 extract) + a SELF-AUTHORED deterministic snare sting
>   (`tools/gen_battle_audio.py` — the own-pipeline route closing the eval's drum gap);
>   "Battle sounds" toggle in pause Settings (the game's first audio setting).
> - **Wiring:** the NA-6b stash-and-raise discipline in BOTH control-return tails
>   (diorama first, then Proclamation, then letter-book); `⚔ View the field` links in the
>   terminal (output meta_clicked — first use) and on every enemy-phase battle line
>   (opens OVER the dialog); the most violent dramatic player-involved enemy-phase battle
>   auto-plays when the dialog closes; repeat views open settled instantly with [Replay].
> - **Found by the visual pass:** a re-open mid-cinematic kept the OLD battle's odometer
>   tween ticking over the new frame (`show_diorama` now kills the sequence first) + a
>   seal/laurel collision. Parse harness extended with all five touched + three new
>   scripts and the scene (the IGR-E runtime-registration gap class).
> - `tests/test_battle_diorama.py` (**43**); `THIRD_PARTY_LICENSES.md` battle-audio
>   entries + the "198 WAVs" doc-drift the eval flagged corrected.
> - **Post-landing fix, same day (`2ea50d1`), from the user's live report** ("clicked
>   view the field and nothing happened and nothing popped when I attacked"): the
>   stash-and-raise lived ONLY in `_on_command_result`, but a real attack frequently
>   resolves through a DIFFERENT handler — the W6-4 muster "Attack Anyway" interrupt, an
>   objection Proceed, or behind the plunder/secure capture prompt — which rendered the
>   battle (and the link, off the event copy) without ever arming the popup. The stash
>   now lives INSIDE `_display_battle_result` (the render chokepoint — link and stash
>   structurally inseparable) and the raise was added at the four missing control-return
>   tails (interrupt-queue drain, objection tail, capture-choice tail, glorious-charge
>   tail). Verified end-to-end against a fresh backend on a side port (boot Ney-vs-Mack
>   carries the payload; the follow-up battle reproduced the capture-gated flow exactly).
>   **A second live factor: a backend started BEFORE the feature serves no payloads —
>   restart backend AND client after pulling.** **✅ The user then confirmed the tableau
>   works in-game.**
> - **BD watch item (soft, next in-game review):** does the significance gate FEEL right
>   over a longer session (eval §2's fun-curve)? The popup mechanism itself is confirmed.
> - **Deferred stays owned** (eval §6 OUT list verbatim): withdrew-status, per-corps rout,
>   clickable grievance, proportional counts, terrain backdrop (named follow-up), Battle
>   Gallery (own gate), Tier B/C (measure Tier A live first), ambient loops.
>
> *(This entry supersedes the nineteenth.)*

> **[Superseded July 31, 2026 (second session) — BD landed] ▶ (nineteenth entry): ROW IGR IS
> BUILD-COMPLETE — next is the Battle Diorama (row BD), then `AI_INTENT_SPEC.md` §11
> Stage E.**
>
> **IGR-G LANDED + the routed X-backlog CLOSED July 31, 2026, in one session under the
> user's delegated grant** ("complete the igr work … feel free to go off spec if something
> is bad wrong or poorly designed"). Landing records: `INGAME_REVIEW_FIXES_SPEC.md` §2
> IGR-G + §6, and the struck rows in `BUG_FIXES.md`. Suite **15,324/3**, ruff clean, parse
> harness EXIT=0, boot 0 `SCRIPT ERROR`, M1–M7 byte-identical.
>
> - **IGR-G1** — the settlement screen uses the screen: `clamp_ceiling_override` panel
>   meta (settlement_confirm only; the pinned call string survives) + a priority-aware
>   relax pass (`relax_last` — the per-court table yields LAST). Measured 720×520/145px →
>   1160×980/320px on a 2550×1340 viewport, via a deterministic harness
>   (`tools/settlement_popup_screenshot.gd`) feeding the REAL popup a REAL backend payload.
> - **IGR-G2** — piece stacks: spacing 30→38, a third rank above 4, ONE stack label
>   ("Ney +4") above 3; the 3–4 shape numerically unchanged; hitboxes stay per-marshal.
> - **⚠ open: user visual sign-off on the before/after pack** —
>   `docs/audits/IGR_G1_SETTLEMENT_BEFORE/AFTER_2026_07_31.png` +
>   `IGR_G2_STACKS_BEFORE/AFTER[_ZOOM]_2026_07_31.png` (the gate note's "screenshots
>   first" was resolved by the grant as before/after evidence rather than a pre-build
>   pause).
> - **IGR-X4 (P2, the escalation)** — the 0-gold confiscation windfall: re-based on
>   `income_value × (1 − war_damage)` in ONE source (`dotation.confiscation_windfall`);
>   blessed 2× + band stand (`WAVE6_FUN_FACTOR_SPEC.md` §10 amended in place). **The
>   40-turn `BASELINE_SERIES` was re-recorded consciously once** — four live AI-vs-AI
>   confiscations by turn 9 (Britain stripping Castanos ×3, Spain stripping Moore) now
>   pay 184–400g instead of 0, so the ambient trajectory diverges from turn 15; the
>   delta was BISECTED to the one-line re-base (comment-only and function-only probes
>   left the series byte-identical) and the confiscations counted by a LIVE SPY because
>   the 500-cap event log had evicted all four rows — the IGR-B trap, hit again in the
>   wild.
> - **IGR-X7 (P2)** — the three capture-route responses fill popup keys WITHOUT draining
>   (a queued one-shot popup survives to the next /command). **IGR-X5** — the strategic
>   march genuinely auto-secures + logs `region_captured`. **IGR-X8** — priced stage-1
>   sentence on every player capture route, `capture_choice` on every AI-visible conquest
>   event (+ the enemy-phase dialog suffix), the priced command-block message, holder
>   re-validation at answer time on both stages. **IGR-X6** — a re-sack pays (and quotes)
>   0 while `plundered` stands; yield read BEFORE the flag is set (GR4). **IGR-X2** —
>   `get_region_intel` is a pure read; writers go through `_intel_entry`; two test
>   fixtures that MINTED intel via the lazy insert were converted to writes.
> - **IGR-X9 stays homed at the econ gate** (decision-shaped: bless razing-sheds-the-bill
>   as design or re-shape it).
> - New tests: `test_igr_g_legibility.py` (12) + extensions across 6 files; the IGR-E
>   dissent counter is UNTOUCHED (attempts remain ONE of two).
>
> **Also still open and unchanged:** Battle Diorama (row **BD**), then `AI_INTENT_SPEC.md`
> §11 Stage E. *(This entry supersedes the eighteenth.)*

> **[Superseded July 31, 2026 — IGR-G landed, X-backlog closed] ▶ (updated July 26, 2026, eighteenth entry): `IGR-G`, THE LAST
> SLICE IN ROW IGR — AND IT NEEDS SCREENSHOTS PUT TO THE USER FIRST.**
>
> **IGR-E is LANDED and pushed** (`c7e30b9` + the GR5 addendum `88e2707`; landing record
> `INGAME_REVIEW_FIXES_SPEC.md` §2 IGR-E). Suite **15,279/3**. The IGR queue is
> `~~A~~ · ~~B~~ · ~~D~~ · ~~F~~ · ~~E~~ → **G**`, with `~~C~~` withdrawn pre-gate.
>
> **IGR-G is a gate note, not a gate.** Spec §5 says to bring G1 and G2 to the user **with
> screenshots** before building: G1 re-weights `Utils.clamp_centered_panel`, shared by every
> centre-anchored popup (IGR-F hit its authored-rect-is-a-ceiling behaviour from the other
> side and has a worked example); G2 is a **third** tuning pass over map furniture whose
> visual sign-off has been open since U5. So the first action next session is to produce the
> screenshots, not to write code.
>
> **Two things IGR-E leaves on the table, both already homed** (`BUG_FIXES.md` §IGR-E):
> **IGR-X4** — the W6-8 estate confiscation windfall is **always exactly 0 gold**, because it
> reads effective income after stage 1 has left stability ≤ 25. The player is shown
> *"CONFISCATE (+0 gold, Austria will not forgive it)"* and asked to pay −10 relations and −1
> trust per cautious marshal for it. It is the same defect IGR-E just fixed, one stage deeper,
> and its fix re-bases a blessed W6-8/ES-7 number, so it **escalates** rather than riding a
> tuning slice. Worth putting to the user next to the IGR-G screenshots. **IGR-X5/X6** are P3.
>
> **And the dissent, which must not be lost:** gate Q4 recorded that option (b) — recutting the
> prompt as stability-vs-authority rather than gold — is arguably the better *design*. **If the
> acceptance test fails at a SECOND multiplier, re-open at (b) rather than tuning a third time.
> Attempts used: ONE of two (×4, PASSED).**
>
> **Also still open and unchanged:** Battle Diorama (row **BD**), then `AI_INTENT_SPEC.md` §11
> Stage E. *(This entry supersedes the seventeenth.)*

> **[Superseded July 26, 2026 — IGR-F landed.]**
> **▶ NEXT SESSION STARTS HERE (updated July 25, 2026, seventeenth entry): IGR-F, plus
> INVESTIGATE THE PEACE RELATION FLOOR (`BUG_FIXES.md` IGR-X3).**
>
> **IGR-D is LANDED and pushed** (`32ff834` + the review pass `99121ff`) and **must-see #4 is
> CLOSED** — the Proclamation was sighted in the real client, screenshot
> `docs/audits/IGR_D_PROCLAMATION_2026_07_25.png`. Suite **15,118/3**.
>
> **Two things for the next session.**
>
> **1. The queue's next slice is `IGR-F`** — the minor-court envoy digest
> (`docs/INGAME_REVIEW_FIXES_SPEC.md` §2, no gate). Build order is
> `A → B → ~~D~~ → F → E → G`. IGR-E needs the Q4 number (already blessed:
> `PLUNDER_INCOME_MULTIPLIER = 4`); IGR-G waits on user screenshots.
>
> **2. Investigate and propose a fix for IGR-X3 — the peace relation floor**, raised by the
> user on landing IGR-D: *"relation shouldn't impact war, people in war hate each other
> anyway."* This is a DESIGN question with a measured defect underneath it, so the
> deliverable is an investigation + a recommendation, not a silent code change — removing
> the floor re-prices every bilateral peace in the game.
>
> Everything below is measured on the shipped `europe_1805` board, not argued:
>
> - `STATE_RELATION_REQUIREMENTS["PEACE"] = -60` (`diplomacy.py:86-93`), enforced at
>   `world_state.py:7950-7959` under `if is_player_treaty:`.
> - France boots at **-90 / -80 / -80** with Britain / Russia / Austria, and
>   `_process_relation_decay` **skips WAR and ARMISTICE** (`diplomacy.py:9698-9700`), so the
>   +1/turn recovery never runs while the war is on. `ARMISTICE_DURATION = 5` and armistice
>   skips decay too — a treadmill, never a path to PEACE.
> - `is_player_treaty` is `proposer == player OR target == player`, so it bites **both
>   directions**: probed, **the AI offering France peace and France accepting FAILS** with
>   *"Relations with France are insufficient for PEACE."*
> - **The AI is exempt.** Probed: an AI-AI peace at relation **-95** ratifies normally. Two
>   courts that hate each other may end their war; the player may not. That is a Golden
>   Rule 5 asymmetry.
> - **The joint settlement route never calls the check at all**, so the identical peace is
>   legal or illegal depending only on which surface was used.
>
> The acceptance formula already prices war score, military supremacy, military pressure and
> war exhaustion. Options worth costing at the gate: delete the PEACE row outright (keep the
> floor for ALLIANCE/NON_AGGRESSION, where consent really is about goodwill); make it
> war-score-aware so a decisive victor can dictate terms regardless of hatred; or let
> ARMISTICE thaw relations so the existing escape hatch actually leads somewhere. Note the
> second consumer at `ai_diplomacy.py:1926` (counter-offer generation) and re-run M1-M7 plus
> the 40-turn `BASELINE_SERIES`.
>
> **Also still open and unchanged:** Battle Diorama (row BD), then `AI_INTENT_SPEC.md` §11
> Stage E. *(The sixteenth-entry text below is superseded where it conflicts; kept for the
> AI-3r record.)*

> **[Superseded July 25, 2026 — AI-3r was gated AND built the same day.]**
> **▶ NEXT SESSION STARTS HERE (updated July 25, 2026, sixteenth entry): THE ⚠️ AI-3r GATE.**
> The pin-20 live in-game pass is HELD and its 8 defects are landed (`17385bf` + `cdbea59`, top
> entry above): Stage B's mirror/Design/Intent/Weariness rows, Stage C's purse/compacts/auction and
> Stage D's beat 6 are all confirmed ON SCREEN. **The open item is row AI-3r** —
> `docs/AI_WAR_DECISION_SPEC.md` v0.1 (`607dee0`), PROPOSED not blessed: the live pass measured
> **zero AI-initiated wars in 38 turns** and the arithmetic shows the `fight` rung is unreachable
> (ceiling 76 vs floor 85 on the default seed), so **D1's own 1–4-per-40-turns band cannot be met by
> construction**. **Resume by putting spec §6 Q1–Q6 to the user** (delete the cap · max-not-sum
> rear-security reserve · let deny/contain designs open wars · authored `wary_of` posture · player
> display-only · sequence vs BD), then **AI-3r.0 the probe** — 8 seeds × 40 turns, harness-only,
> logging every weight term per court per turn; it lands nothing and every §3 number depends on it.
> Slices .1/.2 need no gate (defect against the phase's DoD); .3 and the design widening do.
> **Also still open and unchanged:** the user in-game review of NA-6c/6d, Battle Diorama (row BD),
> then `AI_INTENT_SPEC.md` §11 Stage E. *(The fifteenth-entry text below is superseded; kept for the
> 8.EVAL record.)*
>
> **[Superseded July 25, 2026 — see the sixteenth entry] ▶ (updated July 16, 2026, fifteenth entry): 8.EVAL IS HELD AND CLOSED** (user delegated the decisions; **gate record = `docs/audits/EVAL_8_2026_07_16.md`, authoritative** — all 25 docket items re-verified against master by a 13-agent workflow, then disposed keep/defer/drop; the same session landed the Region-Panel & Map-Interaction UX pass, see the 🖱️ fifteenth-entry section above). **Resume at Phase 8.5, opening per the gate record §3:** (1) **Batch Q "Quick Wins & Honest Counsel"** — VS-5 live ratification exercise FIRST, then AUD-b zero-combat armistice guard / AUD-c+carve-out war-score-aware offer direction / AUD-g advisory bands / S5-1 / S5-2 / S5-3 / S5-5 / S5-D2 / **E7 authority-banded defiance floor (DECIDED)** / **Metternich small build (DECIDED)** / AUD-e docs-only reconciliation / the S5-4 docstring line; (2) the **CR-6 mini-gate** (USER — S5-D1 bare-attack gating, questions pre-staged in the record §3); (3) the **8.5 design gate proper** (USER — Events/Goals/National Identity with the re-scoped Nation-Agendas core as the diplomacy centerpiece). Deferred work is homed in `DESIGN_REFINEMENT.md` §8.EVAL Dispositions (8 named pre-EA rows); drops are explicit in the record. *(The prior fourteenth-entry text below is superseded; kept for the program overview.)*
>
> **[Superseded July 16, 2026 (later session) — 8.EVAL held] ▶ (fourteenth entry): THE COMBAT OVERHAUL PROGRAM IS CLOSED** (Sweep 5 Parsing/UX MET + exit sweep passed — records `docs/audits/SWEEP_5_2026_07_16.md` + `COMBAT_OVERHAUL_EXIT_SWEEP_2026_07_16.md` + the ⚔️ July-16 section above; every §1 target met/exceeded, overall 6.4→≈7.6, zero regressions; five parse/UX defects live-found-and-fixed in-sweep + the P0 end-turn 500 killed). The U2/U3/U5/UI-6 visual sign-off rows are CLOSED (self-served pass, recorded above); the 1805 flag date-accuracy pass landed (Hanover/Ottoman/Saxony redrawn). **Resume at 8.EVAL** — the war-LLM/diplomacy triage (DWL-DIP-E7, DWL-DIP-METTERNICH, DESIGN_REFINEMENT queue items 5-6) + the routed live settlement-ratification exercise (VS-5 `vassal_transfer` through the F1 wizard) — **then Phase 8.5.** Open engineering backlog: `BUG_FIXES.md` §Sweep-5 (S5-1..5) + `DESIGN_REFINEMENT.md` §Sweep-5 (S5-D1 bare-"attack" gate inversion = a CR-6 gate candidate). *(The prior thirteenth-entry text below is superseded; kept for the program overview.)*
>
> **[Superseded July 16, 2026 — the program CLOSED] ▶ (July 13, 2026, thirteenth entry): the COMBAT OVERHAUL & SCORE-RAISING PROGRAM — Phases 0, 1, and 2 are LANDED (see the dated ⚔️ sections above); resume at Phase 3 — un-starve Marshal Drama by breaking the verified triple lock (DR-1 glory-from-attrition + DR-2 slow glory decay + DR-3 authority-dampening rework; target metric M7 ≤ 8), then Sweep 2.** *(The prior twelfth-entry text below is superseded; kept for the program overview.)* Spec `docs/COMBAT_OVERHAUL_SPEC.md` (scope blessed July 13, 2026; born from the ⚔️ Field Review — a 7-turn live 1805 playthrough + a 25-agent adversarial code audit). It converts the review's problematic scores (Combat 5.0 / Economy 5.0 / Marshal Drama 6.0 / Vassals 6.0) into a sweepable, phased build: **Phase 0** harness+baselines → **Phase 1** additive *personality-scaled* reinforcement (CO-1b/M1b) + the survivor-count bug (CO-5) → **Phase 2** decisiveness/rout-to-capture + the enemy-regen cap + the Iron-Resolve stance fix → **Phase 3** un-starve jealousy (the verified TRIPLE LOCK — stalemate=0 glory, GLORY_WINDOW=5 decay, authority>70 dampening at boot-100) → **Phase 4** economy (regressive upkeep + a conquest-free gold sink) → **Phase 5** vassal loyalty lever → **Phase 6** the parser + all live-found play-friction bugs. Balance numbers are sweep-tuned, not separately gated. *(This entry supersedes the eleventh; the UI sweep U1–U5 landed July 12–13 with visual sign-offs pending, and DEF-1 voices + the Artillery arm landed July 13 — see the dated sections above.)*
>
> **[Superseded July 13, 2026 — see the twelfth entry] ▶ NEXT SESSION STARTS HERE (updated July 12, 2026, eleventh entry): ~~UI-0 (asset landing prep)~~ ✅ LANDED July 12, 2026 — RESUME AT UI-1 (font + theme + buttons), then PAUSE for review.** UI-0 applied the git-tracking policy: the blanket-ignored `assets/` tree now **force-tracks the 198 usable shipped assets (~77 MB)** — fonts (`.ttf` + `OFL.txt`), 37 portraits, icon/border/heraldry/ornament/decor SVG+PNG+JPG, the two icon `LICENSE` files, textures, audio WAVs — while the **265 MB `movies.avi`, the ~86 MB `*.zip` working master-pools, and the source `*.psd` files stay ignored** (history stays lean; new assets in a tracked subdir need another `git add -f`). Inventory audited complete vs spec §2 (13 font families each with OFL; 37 portraits + the documented **Abdurrahman** no-portrait exception; two-set icons; 16 flags). `THIRD_PARTY_LICENSES.md` reconciled (the stale "directory is git-ignored" line now records the tracking policy). **No `.gd`/`.tscn` touched → boot-smoke N/A this slice** (the engine imports the raw assets on next open; the `.import` sidecars + `.svg`/font import-scale are owned by UI-1's "commit each `.import` sidecar" step, per §8). **The WHOLE sweep remains queued — U1→U5 (UI-1 theme → UI-2 scale/color → UI-3 texture/icon/portrait → U4 war-table-piece ART → U5 piece CODE), ROADMAP row `UI`, spec §8.** *(This entry supersedes the tenth.)*
>
> **▶ [Superseded July 12, 2026 — UI-0 landed] NEXT SESSION STARTS HERE (tenth entry): the UI Visual Foundation Sweep — start at session U1 (UI-0 + UI-1: the Cinzel / EB Garamond / Source Sans 3 font stack + one central `main_theme.tres` + typed Button styleboxes), then PAUSE for review.** The whole sweep is now **segmented into build sessions U1–U5 with exhaustive per-session "spots" checklists in `UI_VISUAL_FOUNDATION_SPEC.md` §8** (Session Segmentation Ledger — so nothing is missed when work resumes in a fresh session). **The War-Table Pieces (UI-3 sub-item) style gate is CLOSED (July 12, 2026): tin flats on a round base** — the "standee" (the flat silhouette the user chose + a round base that restores the footprint channel and anchors the baked contact shadow, beating the round-sculpt recommendation); **G1/G2/G3 all locked, license-verified reference images gathered in spec §7** (Plassenburg Zinnfiguren-Museum + Louis Liljedahl Napoleonic flats, mostly CC-BY-usable), owned by sessions **U4** (Blender art) + **U5** (Godot placement code). The MC + Jealousy/Marshal-Recruitment phases below are **LANDED** (ROADMAP rows MC & JV) — prior pointers kept for context. *(This entry supersedes the ninth.)*
>
> **[Superseded July 12, 2026 — MC + JV have since LANDED] NEXT SESSION pointer (July 10, ninth entry): the MC build continues at MC-V (the user-added rider, memo §6.7 — (a) personality-kit assurance pinning every type's grants for BOTH sides through the same executor path, `tests/test_mc_personality_assurance.py`; (b) enemy-AI-per-personality evaluation + live exercise of the enemy-side MC-1 abilities, eval addendum to the memo, non-consumed branches routed to `BUG_FIXES.md`); then the MC exit review (MC-2b re-opens there); after MC → the Jealousy v3.1 gate (prerequisite LANDED — the v3.2 addendum re-derives tuning against the MC-3 graph).** **~~MC-4~~ ✅ LANDED July 10, 2026 (ninth session entry — landing record = `MARSHAL_CONTENT_PASS_SPEC.md` §9, authoritative): the two gate decisions closed as contracts.** **(1) balanced/loyal DEFERRED BY CONTRACT (GR9):** the "unimplemented placeholders" framing struck across `ADDING_CONTENT.md`/`MODDING_FORMAT.md`/`personality.py`/ROADMAP Phase 10 (the "evaluate before 1805" note is decided); retired reserved values with a **three-arm boot guard** — single source `personality.IMPLEMENTED_PERSONALITIES`; validator `VALID_PERSONALITIES` tightened 5→3 so a scenario authoring balanced/loyal/any-typo HARD-FAILS at `from_scenario` (assert arm, pinned end-to-end); `create_marshal_from_data` raises naming the marshal + the three (factory arm — legacy rosters pass byte-identically); an omitted-key marshal still boots on the save-compat `"balanced"` default but `from_scenario` logs it (log arm — never silent); save-LOAD deliberately unguarded + pinned (no old save refused); one example mod re-keyed (Sforza balanced→cautious). Re-open owners: the Jealousy v3.1 gate or the MC exit review; a revived fourth type must NOT be named "loyal" (diplomat `loyalist` collision). **(2) Soult-literal CANONIZED as character** — the "one disclosed exception" language RETIRED in `MARSHAL_CONTENT_PASS_SPEC.md` §1 and `COMMAND_ROBUSTNESS_SPEC.md` §6.8 (addendum): the §6.8 personality=character rule now holds with ZERO exceptions (the canonization's three legs all landed earlier in the pass — Drillmaster of Boulogne, the MC-2 executes-to-the-letter bio line, trust 70 + Soult–Ney −1; `test_cr5_literal_arm_player_reachable` stays the pin; the MC exit review owns the live-play re-check). Zero mechanics changed; runtime personality fallbacks deliberately untouched. Tests: `tests/test_marshal_content_mc4_personality_guard.py` (23). *(Prior eighth-entry text kept below for context.)*
>
> **[July 10 eighth-entry pointer — superseded same day]: the MC build continues at MC-4 (doc surgery — close the balanced/loyal deferral as a contract, canonize Soult-literal + retire the §6.8 exception language, the boot-guard rider), then MC-V; MC-2b re-opens at the exit review; after MC → the Jealousy v3.1 gate (its MC-3 prerequisite is now LANDED — the v3.2 addendum re-derives tuning against this exact graph).** **~~MC-3~~ ✅ LANDED July 10, 2026 (eighth session entry — landing record = `MARSHAL_CONTENT_PASS_SPEC.md` §8, authoritative): the roster stops being all-Professional.** The blessed memo-§4 13-pair table authored into `europe_1805.json` as 26 explicit directed edges across 14 marshal rows (symmetry = authored data + a roster-wide suite gate, NOT a code mirror pass — play-time asymmetry stays a supported substrate feature; legacy Ney/Davout −2/−1 pinned as proof). **Zero new mechanics:** every consuming seam pre-existed and is now pinned against the authored web — coordination ×0.0/×0.5/×1.25; A-D4 hostile refusal (Davout–Bernadotte −2 = the Auerstedt no-show live: no auto-reinforce, `hostile_refuses` muster preview outranking `eyes_on_a_crown`, arrival 40; a written SUPPORT still overrides); arrival ±10/step (Lannes→Ney 100); enemy-side GR5 (Charles–Mack ×0.0 — Mack's isolation emerges from the graph; Kutuzov–Buxhowden −10 delta; Brunswick–Hohenlohe pre-fractured Prussia); card Hostile/Rival/Friendly rows. **Validator:** `relationships` schema (out-of-range = hard error since `Marshal.from_dict` restores raw; self-edge + scenario-level unknown-target warnings); `MODDING_FORMAT.md` row. **Discrepancy recorded:** the memo TABLE = 7 negative / 2 positive French pairs (its Q4 prose "5 negative" miscounted its own table — the table governs; the net-negative blessing holds, pinned). One test edit: MC-2's arrival re-measures re-anchored on Soult (neutral primary — Ney gained MC-3 edges with both mirror marshals), preserving the blessed neutral-base semantics; the stacked numbers are pinned in the MC-3 file. Tests: `tests/test_marshal_content_mc3_relationships.py` (47); suite **12,570 passed / 2 skipped**, ruff clean. *(Prior seventh-entry text kept below for context.)*
>
> **[July 10 seventh-entry pointer — superseded same day]: the MC build continues at MC-3 (relationships — the 13-pair web + symmetric post-load pass, memo §4; prerequisite for the Jealousy gate), then MC-4 → MC-V; MC-2b re-opens at the exit review.** **~~MC-2~~ ✅ LANDED July 10, 2026 (seventh session entry — landing record = `MARSHAL_CONTENT_PASS_SPEC.md` §7, authoritative): the roster stops being flat-5.** The blessed memo-§3 21-row table authored into `europe_1805.json` (single-line `skills` dicts for eyeball-comparable in-band tuning; `trust` as `{"value": N}` through the `Marshal.from_dict` scenario path; `tactical_skill` authored EQUAL to `skills.tactical` so no surface can show a split value; **administration FLAT 5 per gate Q3** — authored values stay reserved in the memo table for MC-2b). **The Rally texture ACTIVATED:** Davout 9 + Charles 8 fast tier, Mack/Massena/Buxhowden/Hohenlohe 3 poor tier (−55/−40/−25). **Memo-§6.4 re-measures recorded + pinned:** Ney at shock 9 = +6.9% relative (the +7% figure, under the +10% anchor); arrival mirror Lannes 90 vs Bernadotte 60 (75 no-ability / 70 under written SUPPORT), gap-30 pinned as one assertion. **Balance frame pinned as suite gates:** per-skill means 4.95–5.10, French trust mean exactly 70.0, roster 66.7; Bernadotte-40 verified defiance-inert (bites at ≤20/≥80 — his texture rides the V2a WARY tier + Eyes on a Crown). **Visual layer (design-assurance judgment call, user-authorized):** the card's cryptic flat-5-era skills line (`SHO:5 DEF:5…`) became a character sheet — one `█░` bar row per wired skill (the diplomatic ledger's proven idiom) + backend-shipped per-skill mechanic hints (`skill_notes`, wired seams only) + derived `rally_tier`/`rally_note` composed in `marshal_overview._build_combat_stats` from the marshal's OWN rally methods (shown = applied, Q3 pattern — Godot renders verbatim, re-implements nothing); card scroll estimate 320→380. `MODDING_FORMAT.md` gains the `trust` field row + wired-seam notes per skill. Zero new serialized fields; legacy fixture roster untouched (pinned); no golden-corpus rows (no new verb). Tests: `tests/test_marshal_content_mc2_skills_trust.py` (113); suite **12,523 passed / 2 skipped**, ruff clean. *(Prior sixth-entry text kept below for context.)*
>
> **[July 10 sixth-entry pointer — superseded same day]: the MC build continues at MC-2 (skills/trust — authored values activate The Rally's texture; its landing re-measures Ney-at-shock-9 + the arrival numbers per memo §6.4), then MC-3 → MC-4 → MC-V; MC-2b re-opens at the exit review.** **~~MC-1c~~ ✅ LANDED July 10, 2026 (sixth session entry) — Davout "Iron Resolve" (the set's only T2), THE TEN-ABILITY MC-1 SET IS COMPLETE (landing record = `MARSHAL_CONTENT_PASS_SPEC.md` §6, authoritative).** Serialized `iron_resolve_stacks` (+1 per fortified turn at the tactical tick — growth AND decay phases — cap 3; his NEXT attack consumes ALL stacks for +8% each, max +24%, inside `get_attack_modifier()` only, GR1/GR4); stacks SURVIVE unfortify (pinned; recorded nuance — the memo's "1-AP release" gloss is inaccurate for Davout: cautious unfortify is FREE per the shipped Phase 2.8 kit, the real price is the forfeited fortify defense bonus) and CLEAR on move/rout/capture at every seam, incl. reinforcement arrival, both withdraw loops, and the W6-7 release the review added. Legibility: tick event + battle-report attacker row (pre-consumption snapshot) + description line through BOTH combat paths and both garrison branches + card flag + tooltip derived fields (Q3 pattern). **Pre-commit 4-lens find→verify adversarial workflow (34 agents): 12 raw → 10 deduped → 7 CONFIRMED, ALL FIXED (3 killed)** — headline HIGH (live-reproduced): the stale `fortified` flag survives forced retreat/capture (pre-existing), so the accrual tick re-coiled routed and imprisoned carriers to +24%; now guarded to STANDING marshals only (not retreating/broken/captured/off-field). Tests: `test_marshal_content_mc1c_iron_resolve.py` (47) + the two flipped waiting pins (renamed per review); suite **12,410 / 2 skipped**, ruff clean. **Step zero of the session landed the housekeeping docs at `db9294b`:** Eyes-on-a-Crown trust-dock exemption **RATIFIED**; the E1 turn-1 anchor **RESOLVED** (measured anchors accepted — 36.9% boot / 84.2% fresh / 54.5% steady-state; aspirational 55–70% turn-1 retired; no retune); the Murat First Horseman 5k→4k over-harvest **watch recorded** (MC-V re-checks). Dead code flagged for a separate task (not this slice): `world_state.check_and_execute_retreats` (zero callers; calls a nonexistent `should_retreat`). *(Prior fifth-entry text kept below for context.)*
>
> **[July 10 fifth-entry pointer — superseded same day]: the MC build continues at MC-1c (Davout's Iron Resolve, the set's only T2/serialized-state slice), then MC-2 → MC-3 → MC-4 → MC-V.** **~~MC-1a~~ + ~~MC-1b~~ ✅ BOTH LANDED July 10, 2026 (fifth session entry; landing record = `MARSHAL_CONTENT_PASS_SPEC.md` §5, authoritative).** MC-1a (`6b34f65`): Ney "Bravest of the Brave" re-key incl. the load-bearing `trigger` key + Charles "Habsburg Resolve" +3% activation (pure JSON onto already-wired mechanics) + all ten MC-1 names in `_WIRED_ABILITY_MARSHALS` (MC-0's real-name gate keeps unauthored entries inactive). MC-1b (same session): all eight T1 abilities at their blessed seams — Soult 1-turn never-locked Drillmaster (+ derived `drill_completes_this_turn` tooltip flag), the Lannes/Bernadotte ±15 arrival mirror with honest muster arms + SUPPORT counter-lever + Bernadotte's +10pp defiance, Murat's +5,000 pursuit (cavalry, primary-only, BOTH copies), Kutuzov's halve-AFTER-bonus pursuit screen (5,000→2,500 pinned) + halved retreat attrition, Massena's +10% outnumbered defense (battle-report row + narrative line, under the 1.75 cap), Charles's rout-threshold 15 via new single-source `marshal.get_rout_threshold` at **all three** rout-decision copies (solo, coordinated-primary, AND the [S62] non-primary sweep the review caught still hardcoding 25) with the "close ranks" line, Moore's recruit morale floor 60 (GR5 seam) + the FULL-visibility "famed for" intel rider. **Pre-commit 4-lens adversarial review workflow (22 agents): 15 confirmed findings ALL FIXED** — headline: the third rout copy; coordinated pursuit now folded into every frozen number surface (remaining/casualties/battle-report/campaign-log — and its message, stored-but-never-surfaced pre-slice, now rides the description); pursuit prose clamps to ACTUAL near the 1,000 floor; **Eyes on a Crown exempted from the Session-61a −3 trust dock for orderless no-shows** (by-design character like the literal no-march — a stood-up SUPPORT order still docks; *design call ✅ ratified by the user July 10, 2026*); the hard WILL-NOT muster arm softens at relationship ≥ +1; coordinated floor-guard `>0`→`>1000` fix revert-proofed; coordinated constants numerically pinned (mutation-tested). Tests: 83 across `test_marshal_content_mc1a/mc1b/mc0` files, fully deterministic combat fixture; suite **12,363 / 2 skipped**. MC-2's landing re-measures Ney-at-shock-9 + the arrival numbers at authored logistics (memo §6.4). *(Prior fourth-entry text kept below for context.)*
>
> **[July 10 fourth-entry pointer — superseded same day]: the MC BUILD — MC-1a first (T0 quick wins, then pause for review per the slice cadence).** **The Marshal Content Pass gate is ✅ BLESSED (July 10, 2026, in-conversation): memo Q1–Q8 approved at their recommended defaults with ONE amendment to Q3** — `command` wired immediately as **"The Rally"** (LANDED same session: command ≥ 8 → retreat recovers in 2 turns not 3, broken in 2 not 4, via 2-stages/turn at the single `_process_tactical_states` tick, GR5-symmetric; command ≤ 3 → retreat penalties 10pp deeper at unchanged duration; single source `marshal.py get_rally_stages_per_turn`/`get_retreat_stage_penalty`; the shipped 1805 flat-5 roster byte-identical until MC-2 lands authored values — legacy fixture Ney 8/Davout 9/Wellington 9 hit the fast tier deliberately; **post-landing 3-lens adversarial review: 12 confirmed findings ALL FIXED same session** — every recovery-number surface now command-aware: dispatch ETA, executor retreat/broken block messages incl. a phantom constant-3 countdown fix, voluntary-retreat copy + stance penalty display, forced-retreat flee + shattered messages, map tooltip via derived `retreat_penalty`/`broken_turns_left` payload fields + `map_renderer_base.gd`; one stale six-skills pin updated; `tests/test_mc_q3_command_rally.py`, 32 tests), and `administration` = flatten + HIDDEN from the marshal card (backend filter + Godot skill-row list) behind the **owned MC-2b row** (recruit-seam wiring + un-hide, re-opened at the MC exit review). **Gate record = `MARSHAL_CONTENT_PASS_SPEC.md` §4 (authoritative); slice table gained MC-2b + MC-V rows.** Build order: MC-1a → MC-1b → MC-1c → MC-2 → MC-3 → MC-4 → MC-V. After MC: the Jealousy gate (MC-3 relationships prerequisite), then DEF-1 voices + DEF-13 UI scale → 8.EVAL per the ROADMAP queue. *(Prior pointers kept for context below.)*
>
> **[July 10 third-entry pointer — superseded same day]** The MC design gate was prepared (memo `docs/audits/MC_GATE_RECOMMENDATIONS_2026_07_10.md`, 20-agent panel) and presented; blessed as above.
>
> **[July 10 second-entry pointer — superseded same day]** Wave 6 ran to completion in two sessions: W6-0..W6-7 (first), W6-8..W6-11 + the §0 re-score addendum (second — memo §9: all four pillars MET, measured live). Spec §15 carries the DoD record.
>
> **[July 9 pointer — superseded]** One user tuning flag carried forward: the E1 turn-1 anchor (36.9% measured vs the aspirational 55–70%) — see `ECONOMY_REVISIT_SPEC.md` §0.6.3 Track-2 S7 note + `test_economy_e1_band.py`. The forward order is now **~~AUD correctness sweep~~ (✅ July 9 — 7 fixes, 0 escalations, `docs/audits/AUDIT_2026_07_09.md`) → ~~econ eval~~ (✅ July 9 — `docs/audits/ECONOMY_ECON_EVAL_2026_07_09.md`, 23 verdicts) → ~~EC-2 gate~~ (✅ BLESSED July 9 — memo §8 accepted in full; **gate record = spec §0.6.7**: full-income redirect ES-7, stability-tier ES-2, ES-3 promoted to pass 1, endow triangle, blessed numbers E1–E6) → **▶ EC build IN PROGRESS** (~~Track 1~~ ✅ **CLOSED July 9**: ~~S1 art re-key+drop~~ / ~~S2 cavalry+stables~~ / ~~S3 ledger-GR8~~ / ~~S4 EC-6a sandbox~~ ALL LANDED July 9 — S4 disabled every europe win/lose seam + the countdown readers via a derived `sandbox_mode`, incl. two same-class readers found in-slice (`get_defeat_imminent_state` + the Godot turn clock's `max_turns=0` sentinel); `test_economy_ec6_sandbox.py`, 29 tests; **Track 2 STARTED same day: ~~S5 ES-3~~ ✅ LANDED July 9** — Europe-scoped upkeep 5→8 + force limit 60k+2.5k×regions + 1.5×/2.0× marginal over-limit ladder, E6 mercy covers the surcharge, ledger renders the split by construction; turn-1 measured: all armed 1805 nations net-positive, France 236g surcharge/~47% absorption (band headroom for the pair), Austria in the severe band at boot; `test_economy_es3_upkeep.py`, 25 tests; **~~S6 ES-2~~ ✅ LANDED July 9 (same session)** — stability-tier occupation cost on every non-`nation_starting_regions` province (Hostile 0.50 / Unrest 0.35 / Settling 0.20 / Stable 0.10 permanent floor × BASE income; `OCCUPATION_*` constants sharing the income-modifier tier boundaries; Europe-scoped; ZERO new serialized fields), computed in the existing `calculate_turn_income` loop (GR8) with `income` staying GROSS — the signed "Occupation" line is forced through ledger/dispatch/treasury-report/turn-end/turn-banner by the `NET_GOLD_COMPONENTS` reconciliation guard; E6 mercy halves it; guards pinned: boot anchor (every 1805 nation pays 0 at start), vassal no-double-charge, recapture-reset free via stability, hostile conquest net-negative ("digest before you bite"); AI pays the same `process_income_phase` seam (GR5); amendment-4's estate exemption rides S7 with `dotation_regions`; `test_economy_es2_occupation.py`, 32 tests; **~~S7 ES-7~~ ✅ LANDED July 9 — TRACK 2 CLOSED, EC PASS 1 COMPLETE** — the full-income redirect coded per §0.6.7 amendment 1 (`backend/game_logic/dotation.py`; satisfaction = the estate's full `eff_income`, no skim constant exists — pinned); `Marshal.dotation_regions` + `expectation_grace_turn` the ONLY new serialized fields (save-compat: absent → no retroactive erosion); `grant_dotation` full 12-step wiring ("endow Ney with Swabia", 200g+1-admin-AP investiture in-executor, amendment-4 predicate, estate EXEMPT from ES-2 occupation — named test); `_process_dotation_state` reconciliation (post-income pre-bankruptcy, grace-turn-2 debounce, idempotent, state-driven prune with estate-lost notification); NO trust on grant (no-bribe negative assertion) + `modify_trust`-only (grep guard); AI rung in `_pick_admin_action` (GR5, fee in-executor) + AI marshals erode identically; signed "Dotations" Net line forced by the reconciliation guard through ledger/dispatch/treasury/turn-end/banner; marshal card Expectation/Estates/Shortfall + derived title + exact-command Endow hint; dispatch "Unmet Marshals" roll-up; eroding objection tag; `test_economy_es7_dotation.py` (57) + **`test_economy_e1_band.py` (10) — the ONE stacked two-sided acceptance, GREEN: turn-1 France 36.9% absorption (the aspirational 55–70% turn-1 anchor is unreachable without breaking Austria's +18 boot solvency — FLAGGED for the user's next tuning gate, spec S7 note), fresh doubled empire 84.2% absorbed, steady-state doubled empire 54.5% = in-band, doubled empire ≪ doubled net, Bavaria-800g survives the stack 8 turns**; suite 11,968/1) → **▶ the audit's §8 creative/fun-factor capstone (judges the improved economy) — RUNS NEXT** → MC**. Rationale: the audit is Fable-led and gives whole-codebase familiarity; spending that context on an independent economy evaluation *before* coding is the cheapest place to catch an over-engineered mechanic, a cross-system collision, or a simpler design. The audit runs on known-green master so play-feel isn't muddied by economy churn, and it fixes the economy's *safe* defects in place (e.g. the `ledger.py:_build_economy` GR8 tribute scan), de-duplicating them from the EC build; every economy *balance/design* finding is an escalation it hands to the econ eval. **All recorded EC-2 gate decisions below still stand as the user's current calls** — the econ eval can concur/dissent/simplify and feeds (does not replace) the gate. **Fable authority:** in the audit, decide-and-act inside the fix-vs-escalate boundary (§3); in the econ eval, form and argue your own position on the recs (you recommend the blessed numbers, the user blesses them at the gate). Prior economy context (unchanged, now downstream of the audit):
> **Economy Revisit — EC-2 design audit DONE + gate decisions RECORDED (July 8 was documentation-only, NO code).** A 14-agent multi-dimensional audit (history/balance/gameplay/interactions/depth/code, each adversarially verified) graded the economy **~4.5/10 "mechanically sound, emotionally inert"** — full memo `docs/audits/ECONOMY_REVISIT_AUDIT_2026_07_08.md`; recorded gate + staged work package in `ECONOMY_REVISIT_SPEC.md` §0.5. **User gate calls:** pass-1 = **ES-2 Occupation Upkeep + ES-7 (REFRAMED — success makes a marshal more EXPENSIVE, NOT a trust-bribe; player-facing SURFACE = endow the marshal with an ESTATE and a province-derived TITLE, e.g. "Endow Ney with the Duchy of Swabia" — internal action id stays `grant_dotation`; ES-8 title *flavor* now rides pass 1 free, ES-8 stat-bonus stays deferred) + ES-1 manpower-fix prereq**; **band = middle ~55–70% measured against the WHOLE economy incl. the diplomatic layer** (subsidies/indemnities/tribute, not army-upkeep in isolation); **ES-4 → pass 2** (hard-capped); **ES-10 CUT**. **Confirmed code corrections:** the EC-3 artillery re-key is INSEPARABLE from its rate drop (a strict re-key at rate 200 = ~+15,400/turn, *worse* than the current dead code — one commit only); `STABLES_CAVALRY_REGEN=750` compounds the cavalry runaway; a live GR8 tribute scan in `ledger.py:_build_economy`; EC-6a = 5 live seams incl. a hidden region-scan in `_check_victory_conditions`. **[July 8 continuation — planning + docs only, still NO code] The gate-ready pass-1 spec is now recorded in `ECONOMY_REVISIT_SPEC.md` §0.6:** a follow-on evaluation workflow (6 verifiers re-grounded every load-bearing claim on current master + a 3-lens ES-7 design panel + judge) produced (a) the **ES-7 "The Cost of Success" gate-ready mechanic** — success raises a marshal's reward *expectation*; you meet it by endowing the marshal with an ESTATE and a province-derived TITLE (a conquered province's spoils — a real 30% income skim; historically-faithful Domaine Extraordinaire framing); unmet/revoked expectation erodes loyalty via `modify_trust`; **paying only stops the bleed, never buys trust** (a falsifiable no-bribe assertion); serialized `dotation_regions` + `expectation_grace_turn`; fires AI-side via a `_pick_admin_action` grant rung (GR5); reconciles a signed `dotation_skim` to Net; `modify_relationship`-exclusion guard — §0.6.2; (b) the **ordered implementation plan** (§0.6.3 — Track 1 gate-free: S1 ES-1a artillery re-key+rate-drop ONE commit / S2 ES-1b cavalry+stables+pool-scaling / S3 ledger-GR8 fix / S4 EC-6a toggle → EC-2 gate → Track 2 pair S5 ES-2 + S6 ES-7 + GR5 riders → Track 3 EC-3/EC-5a/pass-2/EC-7); (c) the **cut/consolidate/add reconciliation** (§0.6.4 — ES-10 formally CUT; ES-2 owns territory-gold / ES-3 owns army-gold / ES-6 owns manpower, no hop double-charged; first-class rows for ES-7, the AI-admin branch, the double-count guards, the ledger scan, the EC-6a display-readers); (d) the **escalations E1–E6** (§0.6.5 — band + regen/upkeep/ES-7 constants + the NEW bankruptcy-mercy-coupling call) and the teed-up open questions (§0.6.6). Audit refinements found this pass: `calculate_turn_upkeep` has **6 callers not 7**; the vassal template skims **50% not 30%** (ES-7's 30% is its own number); bankruptcy mercy is **upkeep-only** (death-spiral lever, E6); EC-6a is **7 surfaces not 5** (2 display readers + auto-advance consistency); a pre-existing `process_stability_growth` GR8 footgun ES-2 must not copy. **The EC-2 USER DESIGN GATE now signs off §0.6.2 + the band + blessed numbers before any code.** EC-5 self-cost / EC-7 timing / soft-goal RESOLVED July 8 (cont.): **EC-5 = Option B** (symmetric ~-30g/coastal-French-region self-cost + Britain income-bite, gated on the two-sided AI-solvency test, Option A fallback); **EC-7 / ES-6 supply timing = dated trigger** (opens immediately after the EC-2 pair lands + its AI-solvency band test is green); **sandbox soft-goal = keep pure open-ended** (a soft goal deferred to the Pre-Ship Victory & Objectives Pass). Only the blessed NUMBERS (band E1 + regen/upkeep/ES-7 constants E2-E6) remain open at the gate (§0.6.6). — *Prior context:* Command Robustness is **fully landed — CR-0 through CR-5 AND CR-5b all complete.** CR-5b (Flavor Echoing) landed July 7: its **entry gate was CLEARED** (the non-parroting mock fallback IS specifiable — a deterministic floor keyed to the resolved action, not the raw verb — so no user design gate was needed; adjudicated by a 3-lens design panel, spec §6.11). The marshal's immediate reply now echoes the player's tone at the response seam via a `flavor` field riding the existing CR-3 parse call (zero extra LLM call), cosmetic-only (Golden Rule 6); `test_command_robustness_cr5b_flavor_echoing.py` (60 tests); a 3-lens find→verify review landed 4 cosmetic fixes. **Economy Revisit is now ACTIVE.** This session (July 7) reconciled the EC-0 doc status, ran an 8-dimension code audit + a live 1805 playtest (both grounding the same numbers), **landed the PRE-EC ledger floor** (the Godot economy tab rendered only a subset of the streams folded into Net, so France's on-screen lines missed ~987g/turn of tribute+admin — the SC-33 "invisible tribute" bug class; `strategic_ledger.gd` now renders Admin/Treaty/Tribute lines, pinned by `tests/test_economy_ledger_reconciliation.py`, 10 tests), and **decided EC-6 = SANDBOX** (remove the hard 0.75-region / 60-turn win-lose; real win-conditions deferred to a new **Pre-Ship Victory & Objectives Pass** in Pre-EA — Golden Rule 9 owner row added). **Next actionable = the gate-free EC-1 / EC-3 / EC-4 track** (income baseline + the EC-3 retunes: dead urban-artillery-regen bug, +12,250/turn cavalry runaway, garrison cap; + enemy-AP config). **EC-2 gold sinks need a USER design gate** (the headline problem — France balloons 800→28k gold in 8 turns with nothing to spend it on); EC-5/EC-7 carry decisions. Small recorded-but-uncoded follow-up: the **EC-6a sandbox toggle**. Full plan + verified numbers: `docs/ECONOMY_REVISIT_SPEC.md` §0. Then the **Comprehensive Codebase Audit** → Marshal Content Pass (USER design gate). Routing authority = `docs/ROADMAP.md` §Current Phase Queue. One loose end: a pre-existing RNG-flaky `test_movement_stops_before_enemy_region` is flagged as a background task — seed its combat RNG.

1. ~~Gate 4 visual-half confirmation (USER)~~ — **✅ DONE July 3, 2026.** The user confirmed the 5-item eyes-only checklist; passage recorded in the July 2 Gate-4 entry above + the cleanup spec masthead; the DWL-DIP-E7 / DWL-DIP-METTERNICH 8.EVAL triggers are LIVE.
2. ~~Slice H design gate + H-1/H-2~~ — **✅ DONE July 3, 2026.** Gate approved v1.0 (D-H1..D-H5 as recommended) and the slice LANDED the same day (see the July 3 second entry above). The settlement arc has no live successors.
3. **Command Robustness phase (user priority #1) — ✅ COMPLETE; CR-0..CR-5 ALL LANDED July 3-7, 2026.** `docs/COMMAND_ROBUSTNESS_SPEC.md` v0.6. **(Historical narrative below: the mid-item "CR-5 IN PROGRESS / only Phase 4 remains" and "`AGGRESSIVE_ATTACK_ARM_ENABLED=False` / nothing starts a real battle yet" lines are SAFE-HALF framing that is SUPERSEDED by the "CR-5 COMPLETE — Phase 4 LANDED" summary at the END of this item — the flag is now `True` and the aggressive arm is live.)** The P0 is FIXED, the eval harness (246-entry corpus + action-coverage gate) is the standing regression gate, the clarification dialogue ships, and the live LLM path is modernized (claude-haiku-4-5 + forced tool-use output + live-roster prompts + at-most-one-blocking-LLM-call latency guarantee — see the July 4 second entry above). **CR-5 (Personality-Biased Disambiguation) scope BLESSED July 5, 2026 (spec §6); NEXT = implement CR-5 → CR-5b.** Implementation methodology + code-verified seam map + marshal-voice register baseline: `docs/CR5_IMPLEMENTATION_BRIEF.md` (July 6, 2026) — start at its Phase 0. CR-6 still needs its own design gate. **CR-5 IN PROGRESS — the SAFE half + PHASE 3 (the lethal gate) are LANDED; only Phase 4 remains.** Done: Phase 0 frozen seam-map; guardrail (b) temp-0 parse pin; the deterministic **ASK arm** (literal/neutral/mock → two-option ASK on the CR-2 surface, overriding any LLM guess); the **cautious arm** (deterministic safety clamp — a cautious delegation that the live LLM resolved to a battle action is re-issued as scout, since the LLM proved unreliable — + a character-naming soft note); the **§6.2 LIVE prompt table** (AC-1); the **§6.7 first-use hint** (once-per-campaign, serialized `delegation_hint_shown`). All in `backend/commands/delegation.py` + `main.py` router; `test_command_robustness_cr5_personality_disambiguation.py` (46 tests). **Deliberate design calls (flagged for ratification): (1) routing is DETERMINISTIC, not pure-LLM — the prompt table is advisory (the live LLM was too flaky for cautious); (2) the aggressive→attack arm is NOT YET ENABLED (`AGGRESSIVE_ATTACK_ARM_ENABLED=False`) — it degrades to ASK until the Phase-3 lethal-seam gate lands, so NO delegation verb triggers an ungated battle in the safe half; (3) rider (d) "words become the record" is re-homed to Phase 4 — it quotes the raw phrase in BATTLE reports, and the safe half has no delegation→battle path to quote.** **Live playtest PASSED (July 6, commit `db01fca`):** "Davout, deal with Mack" scouts Swabia, reveals Mack's ~52k, and shows the cautious soft note; "Soult, deal with Mack" asks (+ first-use hint); "Ney, deal with Mack" asks (interim, no 2nd hint). Playtest catch fixed — a delegation scouts the enemy's LOCATION (Swabia), not his name (the scout executor mis-resolved "Mack" → the region "La Mancha"). **Pre-existing bug flagged (NOT CR-5, separate task):** explicit `scout <enemy marshal>` mis-resolves the marshal name to a fuzzy region; attack handles marshal targets, scout doesn't. **Phase 3 (lethal attack-on-arrival gate) ✅ LANDED July 7, 2026 (master `de6d740`).** Built + tested (90 CR-5 tests; full suite 11,673 green) + adversarially audited (5-dimension workflow, 5 findings fixed): serialized `StrategicOrder.delegation_inferred` tag; single-source `objection_v2.inferred_attack_favorable` (folds region terrain + fortification building 0.25 + personal earthworks, mirroring combat.py); `strategic.py _inferred_attack_gate` one-modal confirm across **9 auto-attack seams** (first-step, MOVE_TO arrival, 4 PURSUE, 2 blocked-path); explicit typed orders stay gate-free. Audit-fixed: region-fort in the odds, a `go_around` modal loop at co-located seams (now omitted + `last_contact` suppression), a PURSUE-seam test gap. Failsafe (`AGGRESSIVE_ATTACK_ARM_ENABLED=False`) + RED tripwire intact — **nothing starts a real battle yet.** **CR-5 COMPLETE — Phase 4 LANDED July 7, 2026.** The aggressive→engage arm is LIVE. Key implementation decisions (two corrected the turnkey brief after a code-verified seam audit): (1) the arm re-issues a delegation-INFERRED strategic **PURSUE** (`pursue <enemy>`), NOT a bare `attack` — `attack` is not a strategic keyword and would never become a tagged/gated order; the mock parser maps `pursue`→base `attack` and the strategic parser upgrades `pursue <enemy marshal>`→PURSUE, mock-verified; (2) Phase 3 gated the per-turn processor but NOT the two FIRST-STEP PURSUE seams (co-located-at-creation + move-failed-at-target) that the PURSUE routing makes reachable — Phase 4 closed both via `strategic_executor._inferred_first_step_gate` (reusing `inferred_attack_favorable` + `describe_inferred_bad_odds`). Also: guardrail (e) hardened to a MODE gate (`parse_resolved_to_action` False for `mode=="mock"` — the bias is live-only, mock always degrades to ASK); rider (d) "words become the record" LIVE (verbatim phrase on the inferred order's `original_command`, quoted in the campaign-log one-liner + battle-report `delegation_attribution`, scoped to `order.target==defender.name`); first-use hint latch-on-surface; failsafe flipped + tripwire rewritten; guardrail-(d) personality freeze re-confirmed; cannon-fire redirect (Grouchy Moment) scope boundary documented + pinned (it abandons the order, so the gate no-ops — re-homed per spec §6.3). **Two adversarial audit rounds** (6-dimension find→verify, then a fix-review + completeness critic; lethal-seam completeness confirmed sound): 5 confirmed findings — 1 high (the mock-mode guardrail-e hole), 4 low — ALL FIXED. Tests: `test_command_robustness_cr5_personality_disambiguation.py` (86) + 3 `live_only` corpus rows + `parser_eval.py` `live_only` skip support. **CR-5b (Flavor Echoing) ✅ LANDED July 7, 2026 — entry gate CLEARED, no user gate (spec §6.11).** The marshal's IMMEDIATE spoken reply at the RESPONSE seam echoes the player's tone ("the game heard me"). A `flavor` field rides the EXISTING CR-3 parse call (zero extra LLM call — re-adds the field CR-3 cut "parked at the CR-5 gate"; plumbed schemas.py→providers.py→the load-bearing parser.py lift→main.py capture-before-reparse→attach), prompt-gated to delegation-only. The live LLM composes an action-AGNOSTIC attitude line (can't name the deed → no contradiction with the deterministic router); `delegation.flavor_passes_register` DROPS any parroting/action/register-violating line to a deterministic FLOOR (a live-mode fallback — mock always ASKs via guardrail e, whose clause-quote is already the echo). Cosmetic ONLY (Golden Rule 6 — never routed/serialized). Scope (Golden Rule 9): does NOT touch the ASK arm or duplicate rider (d); aggressive flavor skips every modal (bad-odds + objection). Two workflows: a 3-lens design panel cleared the gate, a 3-lens find→verify review landed 4 CONFIRMED cosmetic fixes (contraction-safe quote tokenizer, word-boundary parrot guard, objection-modal attach guard, personality-word double-narration guard) + floor variety. `test_command_robustness_cr5b_flavor_echoing.py` (60); full suite 11770 green; ruff clean. **Next: Economy Revisit (EC-0).** A pre-existing RNG-flaky `test_movement_stops_before_enemy_region` was flagged as a separate task (not part of this changeset).**
4. **Economy Revisit phase (user priority #2) — ▶ BUILD RUNS NEXT (EC-2 gate ✅ BLESSED July 9, 2026 — read this item through the `ECONOMY_REVISIT_SPEC.md §0.6.7` gate record, which AMENDS the older text below: ES-7 = FULL-income redirect not a 30% skim; ES-2 = stability-tier occupation cost, no `integration_turns` field; ES-3 rides pass 1 as S5; blessed numbers E1–E6 set).** The design work is DONE and gate-CLOSED; the audit (item 5) and econ eval (item 5b) both closed July 9, so nothing blocks the build. `docs/ECONOMY_REVISIT_SPEC.md` v0.4 (audited + planned July 8; sequencing note + §0.7 econ eval added July 9 — see §0). **EC-0 ✅ LANDED July 4** (world-scoped `base_nation_actions` snapshot; `tests/test_economy_ec0_ap_reset.py`). **PRE-EC ledger floor ✅ LANDED July 7** (`strategic_ledger.gd` now renders Admin/Treaty/Tribute; `tests/test_economy_ledger_reconciliation.py`). **EC-6 ✅ DECIDED July 7 = sandbox** (remove hard win/lose; real conditions → Pre-Ship Victory & Objectives Pass; EC-6a toggle code pending). **Gate-free next: EC-1** (authored per-province income + treasury/pool balance) **/ EC-3** (dead urban-artillery-regen bug + cavalry runaway +12,250/turn + garrison cap) **/ EC-4** (enemy-AP config). **EC-2 gold sinks = USER design gate** (the headline: France balloons 800→28,228g in 8 turns, net +3,792/turn, no recurring drain). EC-5 Continental System (near-inert today) + EC-7 supply/overextension carried decisions (RESOLVED July 8 cont. — see below). **Research suggestion pool added July 7** (`ECONOMY_REVISIT_SPEC.md` §Appendix A — ES-1…ES-10 scored candidates feeding EC-2/EC-3/EC-5/EC-7; SUGGESTIONS only, user picks at the EC-2 gate; top bets = ES-1 manpower fix / ES-2 occupation upkeep / ES-7 dotations, now surfaced as endowing the marshal with an estate + province-derived title). **[July 8 UPDATE] EC-2 design audit COMPLETE + gate decisions RECORDED** (documentation-only, no code): 14-agent multi-dimensional audit → `docs/audits/ECONOMY_REVISIT_AUDIT_2026_07_08.md` + recorded gate/work-package in `ECONOMY_REVISIT_SPEC.md` §0.5. Pass-1 = **ES-2 + ES-7 (REFRAMED: success escalates a marshal's cost, not a bribe; player-facing surface = endow the marshal with an ESTATE + province-derived TITLE, e.g. "Endow Ney with the Duchy of Swabia"; internal id stays `grant_dotation`; ES-8 title flavor rides pass 1 free, stat-bonus deferred) + ES-1 prereq**; ES-4 → pass 2; ES-10 CUT; band = middle ~55–70% incl. the diplomatic economy. **The gate-ready pass-1 spec (ES-7 "Cost of Success" mechanic + ordered plan §0.6.3 + item reconciliation + escalations E1–E6) is now recorded in §0.6** (July 8 continuation, still docs-only). The build session (after the audit + econ eval) executes §0.6.3 (gate-free Track 1 → the EC-2 pair behind its design gate). **EC-5/EC-7/soft-goal RESOLVED July 8 (cont.):** EC-5 = Option B (symmetric self-cost + Britain income-bite, AI-solvency-gated); EC-7/ES-6 supply = dated trigger (opens after the EC-2 pair lands + its solvency test is green); soft-goal = keep pure open-ended (deferred to the Pre-Ship Victory & Objectives Pass). Only the blessed numbers still open at the gate (§0.6.6).
5. ~~**Comprehensive Codebase Audit (Fable, fix-as-you-find)**~~ — **✅ COMPLETE July 9, 2026.** The full §5–§7 correctness sweep ran in one session (see the July 9 entry above): **7 fixes across 6 committed chunks, 0 open escalations**; the two §4 waiting fixes resolved (MC-0 was already landed at `685bfd1`; the RNG-flaky movement test seeded this sweep); test-count doc drift reconciled to the verified **11,789 / 1 skipped**; no architecture escalations rose to the `ARCHITECTURE_REFACTORING_PLAN.md` bar (one ultra-low-priority dead-field observation logged in the audit log). Full log: `docs/audits/AUDIT_2026_07_09.md`.
   - ~~**5b. Econ eval (Fable, `ECONOMY_REVISIT_SPEC.md §0.7`)**~~ — **✅ COMPLETE July 9, 2026 (same session).** Memo: **`docs/audits/ECONOMY_ECON_EVAL_2026_07_09.md`** — 23 explicit verdicts covering every recorded decision + Appendix-A candidate, all load-bearing claims re-verified against master `c5e411e`. Two dissents (E5 satisfaction-scale incoherence → full-income redirect; ES-3 promoted into pass 1 for the band's turn-1 anchor), two simplifications (ES-2 → stability-tier occupation cost on non-homeland soil, zero new serialized fields; E2 pool-cap scaling cut + infantry regen deliberately flat), owned expansion riders (EC-5a subsidy coupling + CS activation surface), and a §8 blessed-numbers decision sheet for the gate. Zero economy escalations from the audit needed triage. **Feeds the EC-2 gate — the user blesses/adjusts; accepted changes fold into §0.6 before the build.**
   - ~~**5c. Creative / fun-factor capstone (§8, post-EC)**~~ — **✅ COMPLETE July 10, 2026** (see the July 10 entry above). Memo `docs/audits/CREATIVE_AUDIT_2026_07_10.md`; 10 defects routed to `BUG_FIXES.md` §Creative-Audit Findings (BUG-CA-7 = P1); Wave 6 expansions/escalations filed in `DESIGN_REFINEMENT.md`; 4 inline legibility fixes pinned by `tests/test_creative_audit_legibility_fixes_2026_07_10.py`. This closes the audit arc.
6. ~~**Marshal Content Pass design gate (USER)**~~ — **✅ BLESSED July 10, 2026** (memo Q1–Q8 at defaults; Q3 amended: command wired as "The Rally" — landed same day, `tests/test_mc_q3_command_rally.py`; administration flatten + hidden behind the owned MC-2b row). Gate record = `MARSHAL_CONTENT_PASS_SPEC.md` §4. **~~MC-1a~~ + ~~MC-1b~~ ✅ LANDED July 10, 2026** (landing record spec §5) **and ~~MC-1c~~ ✅ LANDED July 10, 2026** (landing record spec §6) — **ALL TEN blessed abilities are LIVE** — **and ~~MC-2~~ ✅ LANDED July 10, 2026** (landing record spec §7 — the 21-row skills/trust table authored, The Rally texture activated, the card's skill block upgraded to a bar-based character sheet) **and ~~MC-3~~ ✅ LANDED July 10, 2026** (landing record spec §8 — the 13-pair relationship web authored as 26 symmetric directed edges; the Jealousy v3.1 prerequisite is met) **and ~~MC-4~~ ✅ LANDED July 10, 2026** (landing record spec §9 — balanced/loyal deferred by GR9 contract behind a three-arm boot guard; Soult-literal canonized, the §6.8 exception language retired; `test_marshal_content_mc4_personality_guard.py`, 23). **▶ NEXT: MC-V (personality assurance + enemy-AI evaluation)**. MC-2b (admin recruit-seam wiring + card un-hide) re-opens at the MC exit review. Prerequisite for the Jealousy gate. The flagged review design call is ✅ RATIFIED (user, July 10, 2026 — recorded at the MC-1c session's step zero): Eyes on a Crown's orderless no-show stays trust-dock-EXEMPT (mirrors the literal no-march exemption; a stood-up written SUPPORT order still docks −3). Standing tuning watch (memo Q7 default, same recording): if W6-11-era routs over-harvest in play, tune Murat's First Horseman pursuit +5,000 → 4,000 in-band — never add conditions; MC-V's live enemy-AI evaluation re-checks pursuit harvests.
7. **▶ NEXT: the UI Visual Foundation Sweep** (`UI_VISUAL_FOUNDATION_SPEC.md` — font stack + central `main_theme.tres` + styled buttons; assets gathered + license-verified; absorbs DEF-13 UI-scale) → **then** DEF-1 Roster Voices (presentation block) → 8.EVAL → Phase 8.5 per the ROADMAP spine. **Segmented into build sessions U1–U5 with per-session spots checklists (spec §8); start at U1 then pause for review. War-Table Pieces gate CLOSED July 12 = tin flats on a round base, references gathered (spec §7); owned by U4 art + U5 code.**

**Session-discovered open defects (July 2 re-staging audit; recorded in BUG_FIXES.md, fixes owned by CR-0 / EC-0 / MC-0):** parser roster pinning (P0), advance-turn AP reset, marshal-overview ability display.

---

## Archived Session History

- Feb-Apr 2026 sessions (Phase 6 Summary, Infrastructure, Phase 7b, Phase 7 Core): `docs/archive/STATUS_SESSIONS_2026_02_TO_04.md`
- May 2026 settlement v0.27 integration process records (spec reviews, branch reconciliation, compatibility table, May-14 slice queue): `docs/archive/STATUS_SETTLEMENT_V027_PROCESS_2026_05.md`
