# Bug Fixes

> Broken-now implementation document.
> Treat the current findings as frozen truth until the open items below are fixed.
>
> Last Updated: July 17, 2026 (**EC-W Review Findings section added** — 2 routed OPEN
> rows from the Econ War-Coupling pre-push find→verify review; the review's other 7
> confirmed findings were FIXED in-session before the commit, memo
> `docs/audits/ECON_WAR_COUPLING_RESEARCH_2026_07_17.md` §6.)
>
> Last Updated: July 16, 2026 (**Sweep-5 Findings section added** — the P0 end-turn 500
> FIXED in-session; 5 routed OPEN rows from the Combat Overhaul Sweep-5 12-component
> review, memo `docs/audits/SWEEP_5_2026_07_16.md`.)
>
> Last Updated: July 14, 2026 (**Vassal Playtest Findings — F1/F1c/F3/F6/F8b/C1/C2/F5/F7/F4 ALL FIXED** this session from a live europe_1805 playtest + 14-agent adversarial verification; memo `docs/audits/VASSAL_PLAYTEST_2026_07_14.md`, tests `tests/test_playtest_fixes_2026_07_14.py`. Prior: July 12, 2026 (**Playtest Sweep PS-1..PS-9 — 3 user-reported issues + same-family sweep + the generosity-inversion fix (PS-9: "More generous" lowered a hawk's acceptance); ALL FIXED + verified, suite 12,964/3, Godot parse-clean**). Prior: July 11, 2026 (**Estate-Second-Pass Eval Findings section added** — ESP-EV-1 muster typed-answer misroute + ESP-EV-2 expectation-note under-fire FIXED in-session; ESP-EV-3 battles_won seam inconsistency + ESP-EV-4 attack-region silent redirect ROUTED to 8.EVAL. Prior: **MC-V Enemy-AI Personality Findings section added** — 5 ROUTED items from the Marshal Content Pass MC-V assurance/eval slice, headline MC-V-2 = enemy literal AI aliased to cautious, a design decision owned by the MC exit review / Jealousy gate; none is a forced fix. Prior: the **Creative-Audit Findings section** — 10 correctness defects (ALL FIXED across Wave 6 W6-0/W6-1). Earlier state: CR-0 parser roster pinning + **EC-0 advance-turn AP reset** + **MC-0 marshal-overview ability display** all FIXED. Historical context: the April 12, 2026 renderer notes below predate the July 2, 2026 real-map cutover — the running game is the 126-province 1805 campaign; Session-8 renderer work is COMPLETE.)

---

## EC-W Review Findings — July 17, 2026 (2 routed OPEN)

> From the Econ War-Coupling pre-push find→verify review (memo
> `docs/audits/ECON_WAR_COUPLING_RESEARCH_2026_07_17.md` §6 holds the full
> disposition — findings #1/#2/#3/#4/#6/#9/#10h were FIXED or recorded-with-pins
> in-session; these two carry real design work and are routed with owners).

| ID | Pri | Finding | Fix design | Owner / landing |
|----|-----|---------|-----------|-----------------|
| EWC-F1 | P2 | **A winning-arm settlement offer can stage un-ratifiable:** the AI's purse-priced indemnity (it pays the player) is scored as accepting-side HARSHNESS at ratification (saturating −45 at ≥1,875g), so a marginal court can refuse the AI's own offer after the player accepts — a dead-end click. Pre-existing at the old 2,000 cap; EC-W4's bigger amounts hit it more often. Mitigant: the PROPOSE surface lets the player edit the amount down. | Pre-score the offer package at emission and step the indemnity down until the payer court carries it (`_emit_settlement_offer_for_war` seam); add a winning-direction ratifiability test | Next diplomacy/settlement batch |
| EWC-F2 | P3 | **Rente face can size against disruption-zeroed estate income:** `grant_pension` auto-sizes face = expectation − estate income; a one-turn hostile presence on the estate at grant time (EC-W1) locks an oversized pension, double-counting after liberation. AI auto-grant rungs can trigger it. Pre-existing for captured estates; EC-W1 makes it transient-triggerable. | `ignore_disruption` flag on `get_estate_income` for FACE COMPUTATION only (satisfaction display keeps the disruption rule) | Next econ tuning gate (with EWC-D1) |

---

## Sweep-5 Findings — July 16, 2026 (P0 FIXED; 5 routed OPEN)

> From the Combat Overhaul **Sweep 5** (Parsing/UX) 12-component adversarial review over
> fresh live evidence — memo `docs/audits/SWEEP_5_2026_07_16.md`, live captures
> `docs/audits/SWEEP_5_LIVE_EVIDENCE_2026_07_16.md`. All rows CONFIRMED by an
> adversarial verify pass and verified **pre-existing** (none is a Sweep-5 regression).
> The five Sweep-5 parse/UX defects found the same day were fixed in-session and are NOT
> listed here (see the memo's Half-A section).
>
> **Dispositions set at 8.EVAL July 16, 2026 (`docs/audits/EVAL_8_2026_07_16.md` §1):
> S5-1 / S5-2 / S5-3 / S5-5 → KEEP, land in the Phase-8.5 opening Batch Q ·
> S5-4 → DEFER to the Pre-EA Dialogue Robustness row (`DESIGN_REFINEMENT.md`
> §8.EVAL Dispositions); its one-line docstring refresh rides Batch Q. Re-verify
> note for the builder: S5-5's copy half is INVERTED on master — the message
> already prints the capped count; the real defect is the fixed-corps note at
> `economy_executor.py:415-417` printing post-cap NEW_TROOPS as the corps size.**
>
> **✅ BATCH Q CHUNK 1 LANDED July 16, 2026 — S5-1 / S5-2 / S5-3 / S5-5 FIXED,
> plus the S5-4 docstring refresh (the overflow-to-mailbox fix stays deferred).
> `tests/test_batch_q_fixes.py`. Also in the same chunk: AUD-g band realignment,
> AUD-e doc reconciliation. Remaining Batch Q (next chunk): the VS-5 live
> ratification exercise, AUD-b armistice guard, AUD-c war-score-aware offers,
> and the E7 / Metternich small builds.**

| ID | Pri | Kind | Issue | Root cause | Fix / landing |
|----|-----|------|-------|-----------|---------------|
| S5-P0 | **P0** | crash/fog | **FIXED July 16, 2026 (same session).** End turn with a capture choice raised during strategic processing → naked HTTP 500 AFTER the turn advanced (whole end-turn report lost); the raw pass-through also leaked unfogged enemy actions | `_build_result_response` forwarded `enemy_phase` RAW — per-action `new_state` WorldStates carry tuple-keyed caches that crash `jsonable_encoder` outside the endpoint try/except | Route `enemy_phase` through `_build_visible_enemy_phase` (strip + fog-filter) in `_build_result_response`; poison reproduced then killed; exit-run re-drive: 6 end turns with pending captures, zero 500s. `tests/test_sweep5_end_turn_500.py` (4) |
| S5-1 | P1 | AI waste | Moore's square↔fortify self-cancelling loop burns whole enemy nation-turns (live ×2: abandoned accrued +12% fortify for +7% square, then re-fortified) | P2.5 lacks a `fortified` guard (contra `TACTICAL_TRIANGLE_SPEC.md:239-240`); P3 guards `fortified` but not `square_formation`; `_auto_break_square` skips `ai_square_cooldown` | Suppress P3 fortify while `square_formation`, or set `ai_square_cooldown` on the implicit break (`tactical_executor.py:456`). Behavior test: an AI defender holds ONE stance across 3 turns |
| S5-2 | P1 | R7 leak | Raw camelCase marshal keys in player copy, 5+ live occurrences ("ArchdukeCharles must be dealt with first", pursue/engagement copy) | `combat_executor.py:3154-3159`, `strategic_executor.py:393`, `movement_executor.py:229` bypass `display_names.humanize_entity_name`; the Godot substitution map covers only two nation keys | Route the three seams through `humanize_entity_name`; grep-sweep test for camelCase in executor message templates |
| S5-3 | P2 | stale UI | `DOTATION_EXPECTATION` rail notice created once at shortfall-open with static grace copy — live it said "80g/turn … patience holds 2 turns" while the SAME response's dispatch said "160g/turn … loyalty is fraying" | notice never dismissed/re-added on expectation change or erosion start | Dismiss-by-type + re-add on change (the PF-5 details-filter pattern); live grace countdown |
| S5-4 | P2 | dialogue edge | `DialogueManager.preempt` at QUEUE_CAP silently drops the displaced soft-stop; docstring still says hard-stop-only | preempt appends to a capped queue without overflow handling | Overflow to the mailbox instead of dropping; refresh the contract docstring |
| S5-5 | P2 | gate bypass | PF-7 lows: bombard-no-guns rejection is bypassable via the post-objection route; corps-size copy prints the uncapped count under the field-levy cap | post-objection path re-executes without the guard; copy uses requested not capped size | Close the post-objection route (re-run the guard); print the capped size |

---

## Vassal Playtest Findings — July 14, 2026 (ALL FIXED)

> From a live europe_1805 playtest (anthropic mode) of the VASSAL improvements (VS-1 recovery hint + VS-R authority↔loyalty coupling) plus recent slices (Combat Overhaul, Economy, MC pass), followed by a 14-agent adversarial code-verification. Memo: `docs/audits/VASSAL_PLAYTEST_2026_07_14.md`. Tests: `tests/test_playtest_fixes_2026_07_14.py` (19) + 2 updated pins. Verified live where reproducible; suite green. **What worked (no fix needed):** VS-R crux (authority stays healthy 60-65 while derived grip spirals to ~20 as Paris falls), lever blunting (invest +10→+4 with message), spiral recovery-hint firing, EC-U1 fielded-strength upkeep + Grande Armée surcharge, GR5 enemy AI, W6 narration headlines, MC-2/2b/3 texture.

| ID | Pri | Kind | Issue | Root cause | Fix |
|----|-----|------|-------|-----------|-----|
| F1 | P2 | copy/mechanic | VS-R **spiral** recovery hint recommended "grant autonomy" (a lever VS-R blunts ×0.40) + "pay a large subsidy" (**no such action** — vassal verbs are invest/change_autonomy/make/release) | `vassal.py` recovery_hint hard-coded copy naming blunted + nonexistent levers | Single-source grip-aware `recovery_hint_for_grip(grip)`; spiral copy names only unblunted arrests (win a decisive battle → restores grip; or release). Healthy copy = invest / grant autonomy |
| F1c | P2 | dead lever | Healthy hint + Talleyrand advisory recommended "garrison their capital" — never fires in production | `region.garrison_troops` is **never assigned** (Region has garrison_strength); gate `controller==lord` is false for a self-owning satellite → term always 0 | Dropped "garrison" from all hint copy. Formula block + its tests KEPT (unwired-but-intended); wire-or-remove → DESIGN_REFINEMENT |
| F3 | P2 | correctness | Danger/threat readings counted co-located **allies/vassals/neutrals** as an "enemy force" → false "IN PERIL"; a Bavarian ally (Deroy) at Munich lit the alarm | `dispatch._derive_danger` + 2 sibling helpers filtered only `==player_nation`, never `is_at_war` | New `_intel_marshal_is_enemy` (is_at_war) guards all 3 threat sites; the truthful sightings list (site 4) intentionally still shows allies |
| F6 | P2 | cmd-robustness | Typed autonomy changes dead-ended ("Specify autonomy level") — the exact verb VS-1's hint teaches; also killed the F1 wizard buttons | Executor read `raw_input`/`original_command` (never set); parser sets `raw_command`. Mock required contiguous "change autonomy" | Executor reads `raw_command` + more/grant/loosen/less/reduce directions; mock matches "autonomy" or make/set/turn + a level word |
| F8b | P2 | correctness | A blocked vassal rebellion **orphaned** the vassal: removed from `world.vassals` but left `France\|vassal = VASSAL` (unattackable, never loyalty-processed) while still holding all its territory | `del world.vassals` ran, then the `ok=False` war-alloc branch `continue`d without clearing the VASSAL relation (side-conflict: a co-belligerent satellite) | `ok=False` → **graceful independence**: set the pair to PEACE (sidesteps the war-instance conflict entirely). Emits `vassal_rebellion_independent` |
| C1 | P2 | copy | Talleyrand's `<35` advisory hard-coded the healthy levers (incl. dead garrison) — contradicted the grip-aware event line in the **same** dispatch | advisory copy not grip-aware | Grip-aware via the single-source `recovery_hint_for_grip` |
| C2 | P3 | legibility | Autonomy-up blunt printed a bare "+4" with no cause (unlike invest) | missing blunt note | Appends " - the Emperor's faltering grip blunts the gesture" when gain < 10 |
| F5 | P3 | R7 leak | Berthier recovery prompt fed the LLM raw action ids (`sorted(VALID_ACTIONS)`) → it echoed "Invest_vassal" to the player | prompt injected raw ids verbatim | Map through `action_display_name`; drop meta/debug verbs |
| F7 | P3 | QA tooling | `/debug/vassal_loyalty` showed 4 of ~7 terms (dropped lord's-battles + VS-R grip) → never summed to the real delta | debug endpoint re-derived a partial modifier set | Added `lord_battle_modifier` + `imperial_grip_drift` + `imperial_grip`; garrison term retained (mirrors pipeline) |
| F4 | P3 | cmd-robustness | A messy MOVE target leaked raw: "No path from Milan to **On Archduke John At Tyrol**" | MOVE_TO used the raw target string as the pathfinding dest | `_resolve_region_from_phrase` (region substring → marshal location) + a clean-fail message; never leaks the raw phrase |

**Not fixed as bugs (routed to DESIGN_REFINEMENT):** F2 (muster "odds favorable" is a strength-balance heuristic that omits the baseline defender edge/stance/dice — reworded to "the balance of force looks …"; the deeper fold of the defender baseline into the ratio is a design call), C3 (defensive reinforcers valued by offensive potential — verify-intent-first), C4 (grip recomputed per enemy in the courting loop — perf nit), and the garrison-lever wire-or-remove decision (F1c).

---

## UI-2d — Modal Viewport-Safety at High Scale (OPEN, owned; filed July 12, 2026 from the UI-2c review)

> Filed by the UI-2c ("Global Text Size") adversarial review (a 7-agent find→verify workflow). This is a **pre-existing** robustness gap (the U2 Part 1 pause-menu Interface Scale slider already reached `content_scale_factor` 2.0), surfaced now because UI-2c added a prominent always-visible Text Size control that makes the high end of that range trivially reachable. NOT introduced by UI-2c; deliberately NOT bundled into it (the fix is a multi-scene layout rework needing visual sign-off — slice cadence). Recorded here per GR9 so it is not a silent deferral.

| ID | Pri | Kind | Issue | Root cause | Landing / fix |
|----|-----|------|-------|-----------|---------------|
| UI-2d-1 | P2 | UX/soft-lock | At `content_scale_factor` near 2.0 on a **short viewport** (logical height < the modal's height — e.g. a maximized ≤768px-tall laptop, or a small windowed instance), the fixed-size centered **decision modals** that intentionally have no ESC/background dismissal — `reward_dialog` (680×520; its `option_count==0` branch where Cancel is the SOLE control is the worst case), `incoming_proposal_popup` (680×440), `marshal_petition_dialog` (680×480), `interrupt_popup` — overflow the shrunk logical viewport and push their only exit control off-screen → an uncloseable modal (force-quit). Recoverable overlays (the 3 ledgers, 800–840×600–620) merely clip (they have ESC + background-click). | Stretch mode disabled ⇒ logical viewport = window ÷ `content_scale_factor`; these panels are center-anchored with FIXED offsets and do not reflow; the flagged decision modals wire neither `_input`/ESC nor `BackgroundOverlay.gui_input`. NOT affected: the user's ≥2560 display (logical 720 at 2.0 still fits a 520-tall modal). | **Owner: a focused "UI-2d" slice** (after UI-3, or sooner if the user hits it). **DoD:** the 4 flagged decision modals + 3 ledgers stay fully on-screen and their exit controls reachable at `content_scale_factor` = MAX (2.0) down to a 1280×720 logical viewport. **Preferred fix:** convert each fixed 680×520-style center-offset PanelContainer to a **viewport-anchored panel with margins + a max size, body wrapped in the existing ScrollContainer**, so it shrinks to fit at high scale. **Belt-and-suspenders (optional):** a keyboard scale reset (e.g. `Ctrl+0`) handled in `main.gd`'s root `_input` *before* modal blocking, giving a stuck player a guaranteed way out. **Test:** a new `tests/test_ui2d_modal_viewport_safety.py` asserting each flagged scene uses a viewport-relative root (no fixed center-offset ≥ a screen budget) and wraps its body in a ScrollContainer; plus the boot-smoke. **Do NOT** fix by lowering `MAX_UI_SCALE` or clamping the effective scale to the window — that would cap the user's own core request (big text in a small window). |

---

## Playtest Sweep — July 12, 2026 (3 reported + same-family sweep)

User reported: (1) "Ney attack doesn't work / attack doesn't work", (2) "can't do diplo with other nations unless at war", (3) "where are the buttons for rewarding duchies / giving generals more money per turn" — plus "look for similar issues, do a sweep." A 31-agent adversarial workflow root-caused all three + swept the same families. ALL landed this session; suite 12,963/3, ruff clean, 5 edited `.gd` files pass `--check-only`.

| ID | Pri | Kind | Issue | Root cause | Fix |
|----|-----|------|-------|-----------|-----|
| PS-1 | P1 | HARD | Bare `Ney, attack` / `attack the nearest enemy` refused ("names no foe our maps know") | ESP-EV-4 guessed-target guard (`combat_executor.py`) fired on DELEGATED/auto-resolved targets, not only on live-LLM substitution | Skip guard when target auto-resolved from empty order; skip when raw words are only generic; word-overlap grounding for partial names ("John"→"Archduke John"). "attack Venetia" still refused. `test_estate_second_pass.py` +5 |
| PS-2 | P2 | UX | Neutral-nation diplomacy undiscoverable at peace | Prominent clickable-nation panel is war-only; only entry is the tiny Diplomacy button + F1 | DiplomacyButton salience up (font 14, "⚖ Diplomacy", wider tooltip); Commands help now names Diplomacy (all nations) + Generals(G); stale "June 1815" welcome → "September 1805" |
| PS-3 | P1 | UX | Reward portfolio (duchies + rentes) invisible at boot | `[Reward…]` triple-gated on unmet expectation, which is 0 until a marshal wins battles; system reactive by design (ES-7) | Reactive KEPT (user steer). Card now always shows a dim explainer (`is_dotation_world` flag); shortfall-open notification points to G/[Reward…]; help copy made accurate |
| PS-4 | P2 | HARD | Answering the muster popup drops the plunder/secure capture choice + battle report, then blocks next command | `/strategic_response` used a simple-fields copy; client `_on_interrupt_response` never routed follow-on popups | `/strategic_response` → `_build_result_response`; client routes response through `_route_response_ui` + renders battle via `_display_result` |
| PS-5 | P3 | HARD | War-purpose picker always selects the FIRST objective | Every objective button shared action `select_war_objective`; client first-matched → index 1 | Bind objective buttons to 1-based index; main.gd sends pure-integer action directly (backend already resolves `options[choice-1]`) |
| PS-6 | P3 | HARD | War-weary "we march" petition drops the follow-on declare-war dialogue | `/marshal_petition_response` hand-forwarded only battle_report+marshal_petition | `_build_result_response` forwards the whole result |
| PS-7 | P3 | UX | Last-stand enemy-phase decision never pops (blind-type); silently discarded on other-marshal address | Enemy-phase interrupts deferred; router cleared it on other-marshal address | CRITICAL notification on last-stand; router no longer clears `last_stand`/`muster_confirm` on other-marshal address |
| PS-8 | P3 | polish | Missing button labels; muster reads as a wall; Commission link vanishes on roster wipe; dead bilateral-peace expand-link | — | `attack_anyway`/`fight_to_the_last`/`attempt_breakout` labels; muster message → "Commit the Attack"; Commission link survives roster wipe when a bench exists; bilateral-peace row → plain text |
| PS-9 | P2 | HARD | "More generous" LOWERED / "Harsher" RAISED a proposal's acceptance for hawk/schemer targets (dials inverted; "More generous" button's promise broken) | `calculate_acceptance` (diplomacy.py): a trivial gold demand flipped `is_harsh` (PL-12-C threshold −3), and for a hawk (`harsh_mod +5 > peace_mod −5`) the +10 personality swing overwhelmed the demand's −5 cost. Harsher NAP vs Prussia went 23 → 28 | Clamp the harsh-personality application to `min(peace_mod, harsh_mod)` — harshness may only COST via personality, never CREDIT. Keeps the dove penalty (`min(+10,−10)=−10`), removes the hawk/schemer inversion (`min(−5,+5)=−5`). Now monotonic: harsher 23→18, generous 23→24. `test_bugfix_session11.py` +1 |

**Cleanup done this round:** move-substitution NOTE (movement_executor.py — mirrors the retreat W6-1 pattern; NOTE not refuse since a move is reversible; fires only on a real substitution, silent on exact/echoed destinations); `coalition_declaration_popup` scene deleted (verified no test/runtime reference). **NOT deleted:** `proposal_result_popup` — the sweep mislabeled it an orphan, but `test_session8c_popups_notifications` reads its `.gd` for the "Court rationale:" contract and many paths set `world.proposal_result_popup`; RESTORED. **Refuted by the sweep:** sticky-interrupt keyword hijack (popup is modal, blocks input) and the war-purpose-on-attack wall (France boots AT WAR with Austria/Britain/Russia).

---

## How To Use This Doc

- This is the implementation source of truth for the current open PL items.
- Follow the session order below unless a direct dependency note inside an item says otherwise.
- Inspect only the exact implicated code surfaces and same-family helper paths for the active item.
- Use `docs/GPT_AUDIT_PLAN_RESULTS.md` for routing, collapse rules, and phase sequencing only.
- Use `docs/DESIGN_REFINEMENT.md` for post-fix spec routing. The old "design refinement stays blocked" rule below is historical now that Sessions 1-7 are complete.
- Update `docs/STATUS.md` whenever the open count, duplicate status, or active session changes.

---

## Scope Guard

- No new audit pass during this fix phase.
- No re-scoring, re-prioritizing, or widening of the problem space.
- No new PL items unless a direct code contradiction forces one.
- Approved exception: the shipped Session 2 mailbox lifetime model is reopened inside the owning `PL-27` / `PL-34` family because it now conflicts with the desired diplomacy-gating behavior. Use `docs/DIPLOMATIC_OFFER_LIFETIME_SPEC.md` as the source of truth for that follow-up.
- Same-family sibling failures on the same code path are absorbed into the owning PL item and called out explicitly below.
- Historical note: during the active bug phase, `docs/DESIGN_REFINEMENT.md` stayed blocked. That gate is now cleared because Sessions 1-7 are complete. Do not reopen bug sessions to do design work; use `docs/STATUS.md` + `docs/DESIGN_REFINEMENT.md` for the post-fix spec queue instead.

---

## Active Summary

| Session | Priority | ID | Status | Summary | Routing Note |
|---------|----------|----|--------|---------|--------------|
| 1 | P1 | PL-30 | **FIXED** | Godot null-instance crash on diplomacy button after a masked proposal result | Fixed Apr 10, 2026 |
| 1 | P1 | PL-31 | **FIXED** | Capital-loss instant defeat still live, with a false-negative regression test | Fixed Apr 10, 2026. Unblocks PL-28 |
| 2 | P2 | PL-27 | **FIXED** | Diplomacy interrupt contract: hard-stop/soft-stop taxonomy enforced, envoy recovery surface, typed responses | Fixed Apr 10, 2026 |
| 2 | P2 | PL-34 | **FIXED** | Queued proposals: arrival/expiry/overflow now logged in campaign log | Fixed Apr 10, 2026 |
| 2 | P2 | PL-33 | **CLOSED** (duplicate) | `status` works with soft-stop dialogue — verified as PL-27 duplicate | Closed Apr 10, 2026 |
| 2f | P2 | PL-27/34 | **COMPLETE** | Session 2 follow-up: mailbox inbox panel, `diplomatic_queue` eliminated, badge formula consolidated | Implemented Apr 11, 2026 |
| 2r | P2 | PL-27/34 | **COMPLETE** | Offer lifetime refactor: current-turn lapse, `Not Now`, envoy rename, client-side end-turn gate | Implemented Apr 11, 2026 |
| 2u | UX pass | Informational UI | **COMPLETE** | Notice rail, informational popup downgrade, direct Envoys recovery buttons, mailbox readability pass, adjacent HUD/log polish | Implemented Apr 11, 2026 |
| 3 | P2 | PL-32 | **FIXED** | Raw diplomacy labels can leak into popups because display ownership is split | Fixed Apr 12, 2026 |
| 4 | P2 | PL-28 | **FIXED** | No defeat-imminent warning before game over | Fixed Apr 12, 2026 |
| 4 | P2 | PL-26 | **FIXED** | Combat feels hopeless because the obvious opener teaches the wrong lesson | Fixed Apr 12, 2026 |
| 5 | P3 | PL-29 | **FIXED** | No new-game / restart endpoint | Fixed Apr 12, 2026 |

**Current routed next step:** the **Creative-Audit Findings** below are the open defect queue (July 10, 2026). BUG-CA-7 (dialogue-stack misroute) is the priority item. Overall routing lives in `docs/ROADMAP.md` §Current Phase Queue.

---

## Creative-Audit Findings (July 10, 2026) — OPEN

> Routed from `docs/audits/CREATIVE_AUDIT_2026_07_10.md` (the §8 fun-factor capstone). All were **confirmed live** on the shipped 1805 campaign (turns 1–5, LLM_MODE=anthropic). Per §8 discipline they were routed, not fixed (only trivial legibility slips were fixed inline — commit-tracked, tests in `tests/test_creative_audit_legibility_fixes_2026_07_10.py`). Owning component = `AUDIT_GUIDELINE.md` section.

| ID | Pri | Owning component | Finding (evidence in the memo) |
|----|-----|------------------|--------------------------------|
| BUG-CA-7 | **P1** | §7.4 / R12 dialogue manager | **FIXED July 10, 2026 (W6-0).** Every dialogue now carries a serialized monotonic `dialogue_id` (stamped in `dialogue_manager.push/replace/preempt`, mirrored onto `popup_payload`); Godot popups answer with the id they rendered and `/respond_to_diplomatic_dialogue` refuses a mismatched id (`stale_dialogue=True`, current dialogue re-attached). The reversed "Saxony rejected our..." log line direction also fixed (+ the internal `counterparty_reversal` tag no longer renders). Tests: `test_w6_dialogue_identity.py`. |
| BUG-CA-2 | P2 | §6.5 movement (`movement_executor`) | **FIXED July 10, 2026 (W6-1, incl. the E-CA-2 doctrine).** `get_safe_retreat_destination` gained tier 5 (at-war soil = desperation-only) + the homeward bias (homeland first, then nearer the capital, THEN away from the attacker); a stated destination is honored when adjacent+legal and the substitution is NAMED with its reason ("Paris cannot be reached, Sire — it is not adjacent; Bernadotte falls back to Franconia instead" — verified live); enemy-AI fallback mirrors tier 5 (GR5). Tests: `test_w6_retreat_doctrine.py`. |
| BUG-CA-1 | P2 | §6.3/§6.4 parsing + objection | **FIXED July 10, 2026 (W6-0).** Pre-parse pending-question router in `main.py:/command` (after clarification/interrupt steps, before CR-4/parse): exact tokens `trust/insist/compromise` route to the objection handler while an objection is pending; `plunder/secure` to the capture choice; a bare digit or option action-id to the pending dialogue. Tokens with nothing pending fall through untouched (corpus unaffected). Tests: `test_w6_dialogue_identity.py::TestPendingQuestionRouter`. |
| BUG-CA-6 | P2 | §7.7 read-models (`dispatch.py`) | **FIXED July 10, 2026 (W6-1).** `_build_intelligence`'s sighting dedup now prefers `last_updated_turn` recency FIRST (visibility rank breaks same-turn ties) — a stale FULL snapshot can no longer beat this turn's PARTIAL truth. Test: `test_w6_correctness_b.py::TestDispatchIntelFreshness`. |
| BUG-CA-4 | P2 | §6.1 combat (`battle_report.py`) | **FIXED July 10, 2026 (W6-1).** `generate_battle_report` derives remaining = original − casualties (clamped ≥0) for both sides instead of echoing the stale passthrough. Verified live (24,000 − 6,884 = 17,116). Test: `test_w6_correctness_b.py::TestBattleReportRemaining`. |
| BUG-CA-5 | P3 | §6.1 combat (`battle_report.py`) | **FIXED July 10, 2026 (W6-1).** Reinforcement-arrival observation branches on outcome (stalemate → "saved the line, no more"; loss → "it was not enough"; victory keeps the triumphant bank); labels renamed: "Strategic orders" → **"Forced march momentum (order completed)"**, literal hold → **"Immovable (literal hold)"** (labels only, GR1 math untouched). Tests: `test_w6_correctness_b.py::TestObservationTruthfulness/TestModifierLabels`. |
| BUG-CA-3 | P3 | §6.5/§6.3 (`economy_executor` + parser) | **FIXED July 10, 2026 (W6-1).** `_execute_grant_dotation` receives the raw command text; a target region the player never named (raw or humanized form) is treated as MISSING → asks "Which province, Sire?" with the eligible-estates list, mutating nothing. AI programmatic grants (no raw text) unaffected (GR5). Test: `test_w6_correctness_b.py::TestEndowmentAsksNeverDefaults`. |
| BUG-CA-8 | P3 | §7.6 wiring (proposal re-mount) | **FIXED July 10, 2026 (W6-0).** The `_include_popup_passthroughs` safety valve now routes through `_build_pending_envoy_popup_from_dialogue` (the same recovery builder the mailbox activation uses — prefers the dialogue's rich `popup_payload`, falls back to the `world.diplomats`-resolving envoy builder) instead of the inline impoverished rebuild. Test: `test_w6_dialogue_identity.py::TestRemountDiplomatFidelity`. |
| BUG-CA-9 | P3 | §6.1/§7.7 (stat trackers) | **FIXED July 10, 2026 (W6-1).** Every ARRIVED reinforcement participant now increments `battles_won/lost` with its side (stalemates count for no one — mirroring the primary pair) and resets `idle_turns`; new serialized `Marshal.last_battle_turn` records the turn anyone fought (feeds W6-3 arc memory; ES-7 expectation now grows for reinforcing marshals as the blessed model assumed). Test: `test_w6_correctness_b.py::TestParticipationCounts`. |
| BUG-CA-10 | P3 | §7.4 dialogue prompts | **FIXED July 10, 2026 (W6-0).** Both "Please choose an option (1-N), Sire." re-prompts in `diplomatic_executor` now append the numbered option labels. Test: `test_w6_dialogue_identity.py::TestOptionEnumeration`. |

**Next bug-owned implementation slice:** none - current bug-fix queue closed.

---

## MC-V Enemy-AI Personality Findings (July 10, 2026) — ✅ ALL DISPOSED at the MC exit review (July 11, 2026)

> Routed from the Marshal Content Pass slice **MC-V**; **every row received its disposition at the MC exit review** (record: `docs/MARSHAL_CONTENT_PASS_SPEC.md` §11, commit `2641c23`). Full eval: `docs/audits/MC_V_PERSONALITY_EVAL_2026_07_10.md`.

| ID | Pri | Disposition (July 11, 2026) |
|----|-----|------------------------------|
| MC-V-2 | P3 (design) | ✅ **DECIDED + IMPLEMENTED — enemy-nation literals play LITERAL.** The alias narrowed to the player's own autonomous literals (single source `enemy_ai.get_effective_ai_personality`; the four drifted copies route through it). The authored literal rows went live: threshold 1.0 / mood ±8% / no cautious fall-back/fortify/stance reflexes / P7 holds until the stagnation breaker. Pins flipped consciously in `test_mc_personality_assurance.py` (+2 new divergence pins) and `test_literal_personality.py`. Live-observed: AI Deroy gave battle at ratio 1.1 where the alias would have refused; Mack held Ulm and counter-attacked at fair odds, in character. |
| MC-V-1 | P4 | ✅ **ACCEPTED.** Precision Execution / ambiguity buff / 1-AP discount are command-parser economies — rewards for how the PLAYER phrases orders; the AI has no parser, and its literal expression is the MC-V-2 decision profile. The player-only pins stand as the contract. |
| MC-V-3 | P4 | ✅ **CLEANED.** Dead `balanced`/`loyal` rows deleted from the 4 AI dicts (`.get()` defaults = the MC-4 save-compat floor); the 6 zero-reader trust-bonus constants removed from `personality_modifiers.py`. The `literal` rows are no longer dead (MC-V-2) and stay. |
| MC-V-4 | P4 | ✅ **ACCEPTED as evaluated** — cautious plays its label at field-odds level. Force-husbanding is a net-new AI-depth candidate: **owner = the 8.EVAL triage list** (keep/defer/drop there; do not build ad hoc). |
| MC-V-5 | P4 | ✅ **ACCEPTED by design** — recruitment/economy is a nation-level action, not marshal character. (Note: MC-2b now makes the CHOSEN marshal's administration price the levy, which is the character-relevant slice of this space.) |

**Next bug-owned implementation slice (MC-V findings):** none — section CLOSED.

---

## Estate-Second-Pass Eval Findings (July 11, 2026) — ✅ ALL 4 FIXED

> Source: `docs/audits/ESTATE_SECOND_PASS_EVAL_2026_07_11.md` (balance harness + live 1805 playtest of the §0.6.8 reward portfolio). ESP-EV-1/2 were fixed in the eval session; ESP-EV-3/4 were initially ROUTED to 8.EVAL, then **promoted to fixes the same day at the user's direction** ("fix the not-fixed ones as well").

- **ESP-EV-1 ✅ FIXED (was HIGH) — muster typed answer misroute.** The W6-4 muster gate offers `attack_anyway`, but the main.py interrupt matcher only mapped attack-words to a choice literally named `attack` — typing the popup's own label ("attack anyway") fell through to the parser as a FRESH ungated attack by a defaulted marshal (live: Masséna charged Archduke John into mountains while Soult's muster question stood). Fixed in the matcher (+ "commit"/"proceed" keywords); 2 endpoint-tier regressions in `test_w6_muster_preview.py`.
- **ESP-EV-2 ✅ FIXED (was MED) — battle-report expectation note under-fired.** The §0.6.8 item-4c note keyed off outcome strings, but `battles_won` increments differ by path (solo decisive-only; coordination counts tactical wins; the destruction sweep kills after tactical outcomes) — 4/8 seeds missed. Rewritten as a pre-combat `battles_won` snapshot + delta read (8/8 fire; capped marshals stay silent); pins in `test_estate_second_pass.py`.
- **ESP-EV-3 ✅ FIXED (July 11, 2026, user-directed promotion from ROUTED) — battles_won seams UNIFIED: tactical victories count everywhere.** The solo path (`combat.py` tactical arms) now increments `battles_won`/`battles_lost` exactly like the coordination caller always has (`combat_executor.py:3629` atk_won/def_won include tactical outcomes) — a marshal's record, and his ES-7 reward expectation, no longer depend on whether allies happened to march. Stalemate and mutual-destruction bookkeeping unchanged (already symmetric). This also mends the eval's on-ramp finding: tactical wins against dug-in defenders (the Mack grind) now feed the Cost-of-Success. Note for tuning: expectation accrues faster now — `REP_STEP`/`EXPECTATION_CAP` stay in-band tunable if active marshals cap too early (E5's "caps ~turn 15–20" guidance should be re-measured at the next band check). The "Brutal stalemate vs casualty ratio" sub-claim dissolved on inspection: the classifier reads side-total casualties while the one-liner shows the primary pair — coherent, a display nuance only. Pins: `test_estate_second_pass.py::TestUnifiedWinSemantics` (seed-scanned, both tactical arms + stalemate).
- **ESP-EV-4 ✅ FIXED (July 11, 2026, user-directed promotion from ROUTED) — the guessed-target guard on the attack path.** Root cause was the live-LLM substitution class (BUG-CA-3's family), not fuzzy matching: the mock parser correctly refuses "Venetia"; the anthropic tier substituted a real enemy for the unknown name and the executor faithfully attacked it. Fix: `execute` stashes the raw text on specific command dicts; `_execute_attack` refuses — BEFORE auto-war-declaration — when the raw text names neither the parsed target nor anything the resolution produced (enemy name/location/nation, resolved region; raw or humanized): *"Your order names no foe or province our maps know, Sire — {marshal} will not charge at a guess"* + the fog-legal visible-enemy list. AI, strategic execution, and muster re-issues carry no raw text and bypass the guard. Pins: `test_estate_second_pass.py::TestGuessedTargetGuard` (4: refusal, location-grounded pass, nation-grounded pass, no-raw bypass).

---

## MC Exit Review Findings (July 11, 2026)

> Found during the exit review's live playtest + UI assurance (4-turn anthropic campaign + Godot boot). The P1 was fixed in-session; the P4 polish rows are routed with owners.

| ID | Pri | Status | Finding |
|----|-----|--------|---------|
| XR-1 | **P1** | ✅ **FIXED in-session** (`main.gd`, `dispatch_view.gd`) | **The Godot client was DEAD at master since July 10:** W6-1/W6-3 added a `var headline` dispatch local to the same functions that already declared one in the BPH-D peace-settlements loop — GDScript forbids the shadow, both scripts failed to parse, and the frontend lost its orchestrator (no top bar, no map fills, no hotkeys, no response rendering; only the bare terminal strip survived). Loop locals renamed `settlement_headline`; client boots with zero script errors, full UI verified in-game. **Process lesson (STATUS.md): any `.gd`-touching slice must boot the engine once (`--verbose`, grep `SCRIPT ERROR`) before landing — the pytest suite cannot see GDScript parse errors.** |
| XR-2 | P4 | routed → CR backlog (owner: the standing parser-eval harness; add a corpus row when touched) | A bare verb-phrase reply to the CR-5 literal ASK ("give battle") typed into the terminal parses as a fresh command and can surface a raw `'generic'` placeholder ("Region 'generic' not found") — the live LLM hallucinates a target for target-less verb phrases. The designed answer path (popup option reissue) is unaffected. Guard: drop non-region placeholder targets (`generic`, `unknown`) to a clarification instead of a region lookup. |
| XR-3 | P4 | routed → capture-pipeline polish (owner: `capture_executor` cosmetic sweep, next capture-touching slice) | Capturing the region a marshal already stands in prints "Ney marches from Swabia into Swabia unopposed! (175 lost to march)" — an in-place capture should neither narrate a march nor charge march attrition. |
| XR-4 | P4 | routed → `dotation.py` copy polish (owner: next ES-7-touching slice; candidate for the Jealousy-gate session) | Endowing a war-torn province is legal and the result copy is honest ("revenues (0g/turn)... the endowment falls short"), but nothing warns pre-commit that the estate currently yields 0g, and the message does not say revenues recover as stability does. Add one pre-flight line to the endow confirm + a recovery clause to the result. |
| XR-5 | P4 | routed → Phase 8.5 Marshal Voice (owns battle-quip variety) | Mack's post-battle quip pool is 2 lines; across the 7-battle Ulm grind "The position was sound. It is always sound." repeated verbatim 3×. Delicious once, mechanical by the third — 8.5's marshal-voice tiers should give recurring-battle quips a cooldown/variety bank like W6-10 gave diplomats. |

**Current Session 7 progress:** COMPLETE. Shared nation config now drives world bootstrap/save migration/non-France restart flows, diplomacy and advisory surfaces no longer stamp France into runtime state, enemy AI contact scans now route through cached fog-aware helpers, and scenario validation rejects unsupported nation rosters before `from_scenario()` load.

**Current Session 8 progress:** Cutover slices 1-3 COMPLETE. The renderer now has shared scene-node layers, a placeholder province-definition asset, visible background map/province highlight layers, a hidden color-map lookup path for the current 19-region shell, and a viewport-local `Camera2D` cutover with world-bound clamping while keeping the existing `update_all_regions(map_data)` contract stable. Remaining work is commissioned art-backed layers and final Godot runtime smoke validation.

**Session 6 audit prompt:** `docs/SESSION6_COMMAND_LAYERING_AUDIT_PROMPT.md`.

**Duplicate handling rule:** PL-33 stays listed until the post-PL-27 verification pass is complete. If `status` works with no pending dialogue and with soft-stop diplomacy pending, close PL-33 as a duplicate of PL-27 instead of shipping separate code for it.

---

## Same-Family Decisions

- `PL-30` absorbs both diplomacy-wizard crash paths: Step 1 nation rendering and Step 2 preview rendering. Both failures come from the same masked-result plus coarse `dialogue_pending` contract and the same null-prone `add_output()` recovery path.
- `PL-27` absorbs the nearby same-family command-guard failures on `status`, `help`, `economy`, `treasury`, and `finances`, plus the active-envoy count mismatch, envoy-button recovery failure, and remaining popup handlers that still synthesize parser commands. `PL-33` remains only as a duplicate-candidate verification gate.
- Session 2 follow-up does not create a new PL item. It finishes the player-facing mailbox UX and folds in the same-family regressions found after Session 2 completion: browsable mailbox/inbox flow for 2+ pending items, defer/reopen UX, soft-stop reply routing drift, `/pending_envoy` payload shape drift, badge vs recovery mismatch when queued work exists behind a hard-stop, and the boundary between mailbox-worthy diplomacy and noisy top-bar notifications.
- `PL-34` is the queue/expiry branch of `PL-27`. Do not build a separate UX track for it.
- The approved current-turn offer lifetime refactor also stays inside the owning `PL-27` / `PL-34` family. It supersedes the shipped cross-turn mailbox lifetime behavior without creating a new PL id.
- `PL-32` absorbs all duplicate proposal/clause display maps and raw-token fallback leaks on the active diplomacy popup paths.
- `PL-29` absorbs backend `/new_game`, pause-menu wiring, frontend local-state reset, and autosave semantics as one restart contract.

---

## Architecture Blocker Decision

- Sessions 6-8 do not move earlier as full sessions.
- Only the bug-owned slices needed to close the active PL items ship earlier:
  - Session 2: backend soft-stop taxonomy, authoritative active-plus-queued count contract, typed responses for affected popups
  - Session 2 follow-up: Godot mailbox inbox browsing, defer/reopen UX completion, and PL-27 same-family hardening found after the fix landed
  - Session 2 current-turn offer refactor: replace cross-turn mailbox persistence with same-turn reopen plus turn-end lapse while preserving non-diplomatic soft-stop behavior
  - Session 3: backend-owned display formatting for active diplomacy popups
- Renderer replacement remains in Session 8. `/command` unification follow-up and Session 7 scale-sensitive backend hardening are complete.

---

## Session Order

### Session 1 - Stability And Defeat Truth

**Items:** `PL-30`, `PL-31`

**Goal:** remove the crash and align defeat-state truth across code, tests, and docs.

**Exit criteria**

- Opening Diplomacy after a masked proposal result no longer crashes Godot.
- Capital capture no longer contradicts the intended rule or its regression coverage.
- `docs/STATUS.md` no longer implies the capital-loss issue is already fixed.

### Session 2 - Diplomacy Interrupt Contract

**Items:** `PL-27`, `PL-34`, `PL-33` duplicate check

**Goal:** enforce the hard-stop vs soft-stop split, provide a real recovery surface for soft-stop diplomacy, and stop silent expiry/drop behavior.

**Exit criteria**

- Soft-stop diplomacy no longer blocks ordinary commands.
- Active plus queued diplomatic work is visible and reopenable.
- Expiry and overflow no longer resolve unseen proposals silently.
- `status` is verified after the guard split and either closes as a duplicate or remains as a true separate bug.

### Session 2 Follow-Up - Mailbox UX Completion, Inbox Browsing, And Contract Hardening — COMPLETE

**Items:** follow-up slice under `PL-27` / `PL-34` only. No new PL id.

**Status: COMPLETE** (April 11, 2026). `diplomatic_queue` eliminated. Mailbox panel built in Godot. `GET /mailbox` + `POST /mailbox/activate` endpoints. Badge formula uses `dialogue_manager.get_mailbox_count()`. 37 new tests, 8189 total passing.

**Historical note (April 11, 2026):** The cross-turn mailbox lifetime behavior shipped here is no longer the forward target. Keep this section as shipped-history only. The approved next-step behavior is documented in `docs/DIPLOMATIC_OFFER_LIFETIME_SPEC.md`.

**Goal:** finish the player-facing mailbox UX so soft-stop diplomacy is actually deferrable and browsable in Godot, and harden the Session 2 transport contract where the audit found live regressions.

**Why this is a separate follow-up**

- Session 2 fixed the backend taxonomy and recovery surface, but Godot still treats incoming proposals as a modal dead-end.
- The shipped mailbox button/hitbox fix made a single pending item reliable, but `Mailbox (N)` is still opaque when `N > 1`; the player cannot inspect or choose among multiple pending diplomatic items.
- This follow-up stays inside the owning `PL-27` family. It does not reopen `PL-33` or create a new tracked PL item.
- `PL-32` should not start until the active proposal contract and recovery payload are stable again.

**Next implementation item**

- Build a formal browsable mailbox/inbox panel behind the mailbox button.
- Do this before `PL-32`, before any broad notification redesign, and before any more popup display cleanup.
- Treat the current mailbox button as an interim reliability fix, not the finished UX.

**Exact scope**

- Keep the existing local `Later` / `Ask Later` path in `godot-client/project-sovereign/scripts/incoming_proposal_popup.gd`.
- Add a mailbox panel/list in Godot instead of treating the mailbox button as "reopen one arbitrary pending item."
- Add a backend mailbox-list contract that returns the active soft-stop item plus queued soft-stop diplomacy in one ordered list.
- Add stable mailbox item identity (`mailbox_id`) for every pending diplomacy item that can appear in the mailbox.
- Add a backend activation contract so selecting a queued mailbox item makes it the active soft-stop item before the popup opens.
- Keep the pending dialogue alive when the player defers locally; the inbox is the mechanism for browsing, not implicit destruction or parser workarounds.
- Harden `backend/main.py` soft-stop reply routing so valid delayed replies still work through `/command`, including numeric choices and the common `accept` / `counter` / `reject` path.
- Fix `/pending_envoy` payload construction so it matches the `incoming_proposal_popup.gd` contract exactly instead of rebuilding a parallel shape.
- Eliminate `world.diplomatic_queue` — consolidate into `dialogue_manager` as the single pending-diplomacy queue.
- Fix badge formula to use `dialogue_manager.get_mailbox_count()` exclusively, eliminating the dual-source mismatch.
- Do not widen this slice into a general notification redesign. Record the clutter policy boundary, but keep the implementation focused on diplomacy inbox behavior.

**Mailbox behavior spec**

- **Dual-queue elimination (APPROVED):** The codebase has two separate pending-diplomacy queues. `world.diplomatic_queue` (world_state.py:443) holds raw AI proposals waiting for delivery — max 3, 3-turn expiry, drained by `_dequeue_best()` during end_turn. `dialogue_manager._queue` (dialogue_manager.py:75) holds delivered dialogues that couldn't become active — max 20, auto-promoted on pop. The current badge formula (main.py:170-172) counts `len(diplomatic_queue) + (1 if dm.is_soft_stop() else 0)` which counts undelivered proposals and ignores `dialogue_manager._queue`. `DialogueManager.get_soft_stop_count()` is broader than the mailbox because it includes hybrid soft-stops; the mailbox needs its own count contract. `diplomatic_queue` existed to throttle delivery to one-per-turn and defer acceptance-score calculation. Both purposes are obsolete: the mailbox IS the multi-proposal UI, and `POST /mailbox/activate` can recalculate acceptance scores at display time. **Eliminate `diplomatic_queue` entirely.** Deliver all AI proposals through `deliver_ai_proposal()` → `dialogue_manager.push()` at generation time. Remove the one-per-turn throttle in `turn_manager._process_ai_diplomatic_phase()`. Remove `_enqueue_proposal()`, `_dequeue_best()`, `_expire_queue()`, `try_deliver_queued_proposal()`, and the `diplomatic_queue` field from WorldState (including `to_dict`/`from_dict`). Migrate the PL-34 overflow/expiry ownership into `DialogueManager` itself — queue cap, any retained expiry sweep, and recorded outcomes must all come from the surviving queue, not from legacy raw-proposal helpers. Update all badge count formulas in main.py to use `dialogue_manager.get_mailbox_count()` exclusively (fix the 4 occurrences at lines ~170, ~498, ~858, ~1946). Remove `getattr(world, 'diplomatic_queue', [])` references in `main.py`, `diplomatic_ledger.py`, `meta_executor.py`.
- Mailbox badge count continues to mean: active soft-stop diplomacy item plus queued soft-stop diplomacy items. **Single source of truth: `dialogue_manager.get_mailbox_count()`** — counts `SOFT_STOP_MAILBOX_TYPES` in active slot + all items in `dialogue_manager._queue`. Exclude hybrid soft-stops from the count (see below).
- Clicking the mailbox with count `0` must produce a deterministic empty state, not a no-op.
- Clicking the mailbox with count `1+` opens a mailbox panel/list, not a proposal popup directly.
- True hard-stop modals still block mailbox interaction. Visible hybrid/local-planning popups that are not mailbox items also block mailbox open/activate; the inbox must not steal focus from them. The count may remain visible while blocked.
- The mailbox panel shows one row per pending diplomacy item with, at minimum:
  - `ACTIVE` vs `WAITING` state
  - source nation / actor
  - item type (`incoming_proposal`, `counter_offer`, `counter_offer_response`, `conflict_alert`)
  - arrival turn
  - short summary line suitable for list display
- **Hybrid soft-stop exclusion:** `sabotage_confrontation` and `vassal_rebellion_imminent` are counted by `is_soft_stop()` / `get_soft_stop_count()` but are NOT diplomacy proposals and must NOT appear in the mailbox panel or badge count. **Exclude hybrids from the count.** Add `get_mailbox_count()` to `DialogueManager` that counts `SOFT_STOP_MAILBOX_TYPES` only (not `HYBRID_SOFT_STOP_TYPES`). Use this for badge and `GET /mailbox`. Hybrids keep their own popup flows unchanged.
- **`conflict_alert` dispatch:** `conflict_alert` items currently route to `proposal_confirm_popup`, not `incoming_proposal_popup`. The mailbox panel must dispatch to the correct popup type based on `dialogue_type`. Add a type→popup mapping instead of assuming all items use `incoming_proposal_popup`.
- Ordering rule:
  - active soft-stop item first
  - then queued items by backend urgency/priority ascending
  - then FIFO within equal priority
  - preserve stable order across reopen, save/load, and non-diplomatic commands
- **Ordering metadata ownership:** When raw proposals become dialogues, copy the AI proposal urgency onto the dialogue (`mailbox_priority` or equivalent) and preserve a stable arrival sequence (`mailbox_id` seq or explicit `mailbox_order`) for FIFO ties. Do not rely on incidental list append order after save/load or activation swaps. Same-nation dedup must scan the active slot plus `dialogue_manager._queue`, not the removed `diplomatic_queue`.
- **Ordering consumer rule:** `mailbox_priority` / `mailbox_order` are the authoritative sort keys for both `GET /mailbox` and `DialogueManager._promote()` on `SOFT_STOP_MAILBOX_TYPES`. Keep `DIALOGUE_PRIORITY` only as fallback for non-mailbox types, and keep its mailbox-type fallback values aligned with the implementation order below (`counter_offer: 3`, `counter_offer_response: 3`, `conflict_alert: 4`).
- Selecting the active row simply reopens the current popup.
- Selecting a queued row must activate that item server-side before opening its popup. The previously active soft-stop item returns to the queue without data loss.
  - **Activation guard:** Only swap when the active slot is empty or already holds a `SOFT_STOP_MAILBOX` item. If the active slot holds a `HARD_STOP`, `HYBRID_SOFT_STOP`, or `LOCAL_PLANNING` type, both mailbox open and `POST /mailbox/activate` must return a blocked message instead of burying the active non-mailbox flow.
  - **Cache invalidation:** `world.incoming_proposal_popup` (main.py:1898-1904) caches the popup payload set at delivery time. `POST /mailbox/activate` must overwrite this cache with the newly activated item's data, or the recovery path (`/pending_envoy`, response polling) will show data for the wrong proposal. The same rule applies when an active item mutates in place (for example incoming proposal → `counter_offer`): rebuild the cached popup payload from the new terms, do not only flip flags such as `is_counter_offer`.
  - **Re-queued item lifetime:** When the previously active item is re-queued, preserve its original `turn_created`. Do not refresh the timestamp — this keeps `clear_stale` consistent and prevents indefinite keep-alive via repeated activation cycling.
- **Active popup-cache ownership:** `world.incoming_proposal_popup` is active-item-only state. Queued mailbox arrivals must NOT overwrite it just because a new item was pushed behind another current dialogue. Either store a popup-safe payload on each mailbox dialogue or guarantee `GET /mailbox` / `POST /mailbox/activate` / load-time recovery can rebuild it from dialogue context through one shared helper (including `counter_offer_response` created during `advance_turn`). On load or legacy `diplomatic_queue` migration, rebuild/validate the global cache from the active mailbox item only; ignore stale serialized popup data that points at a different mailbox item.
- **Mailbox identity continuity:** `mailbox_id`, `mailbox_order`, `mailbox_priority`, and the original arrival turn belong to the mailbox item, not to one specific dialogue type string. Preserve that metadata when the active item is enriched or replaced in place (for example `incoming_proposal` → `counter_offer` in `diplomatic_executor.py`) so the inbox row, dismissal state, and stale-selection handling still refer to the same pending item instead of a phantom "new" one.
- **Stale selection handling:** If a `mailbox_id` disappears between `GET /mailbox` and `POST /mailbox/activate` (expired, answered elsewhere, dropped on load cleanup), return a clean stale/not-found response with refreshed counts and leave the current active item untouched.
- `Ask Later` remains local and non-destructive:
  - close popup
  - re-enable normal input
  - keep the selected item pending
  - do not auto-consume or auto-reply
  - **Mailbox lifetime rule:** Do not inherit generic `clear_stale()` timeout behavior for mailbox items. Mailbox-eligible diplomacy is player-deferred, non-blocking inbox content and must not silently disappear on turn N+3. In this follow-up, remove generic mailbox expiry entirely. If any mailbox item ever gets an expiry later, it must be explicit on that item (`expires_on_turn` or equivalent), surfaced in the inbox UI, and covered by outcome logging/tests.
- The inbox panel, not repeated mailbox-button clicking, is the browsing mechanism for `Mailbox (2+)`.
- Accept / Counter / Reject always apply to the currently active item only. The activation step makes that deterministic.

**Recommended backend contract**

- Keep `/pending_envoy` for the simple "reopen current active item" path and backward compatibility, but make it active-item-only once the inbox exists. It must not silently choose a queued item. If there is no active mailbox item (queued-only state, or a hard-stop/hybrid/local-planning item is active with diplomacy queued behind it), return `has_pending = false` with an accurate `pending_envoy_count`; `GET /mailbox` is the authoritative browse surface for queued items.
- **Queued-only steady state:** After `diplomatic_queue` elimination, a mailbox-only queue with no active mailbox item should exist only when a non-mailbox current dialogue is in front, or during legacy-save migration before the first promotion pass. If the active slot is empty and only mailbox items remain, auto-promote the next mailbox item immediately instead of inventing a second long-lived steady state.
- Add `GET /mailbox` returning ordered mailbox-list summaries.
- Add `POST /mailbox/activate` with `mailbox_id`, returning the popup-safe payload for the now-active item.
- Add `mailbox_id` at proposal creation time and preserve it through:
  - `dialogue_manager.push()` (the sole queue after `diplomatic_queue` elimination)
  - delivery to active soft-stop
  - in-place enrichment / replacement of the active mailbox item (for example `incoming_proposal` → `counter_offer`)
  - re-queue of a previously active item
  - `counter_offer_response` items created during advance_turn (world_state.py:4488)
  - save/load serialization
- **`mailbox_id` generation:** Use `f"mb-{turn}-{seq}"` where `seq` is a per-turn monotonic counter on WorldState (e.g., `_next_mailbox_seq`). Serialize the counter. Avoids UUID dependency and stays deterministic for save/load. Reset per-turn is safe because `turn` prefix guarantees uniqueness.
- **Legacy-load metadata backfill:** On load, assign `mailbox_id` / `mailbox_order` / `mailbox_priority` to any restored mailbox dialogue that lacks them, including (a) current or queued `dialogue_manager` entries from pre-mailbox saves and (b) old `diplomatic_queue` items migrated during backward compat. After restoration/backfill, advance `_next_mailbox_seq` past every mailbox item already present for the current turn before generating new IDs, or a same-turn post-load arrival can collide with a restored item.
- Prefer preserving the original arrival metadata when an item is activated from queue; opening an old message should not make it look newly arrived.
- **Add `counter_offer` and `counter_offer_response` to `DIALOGUE_PRIORITY`** (dialogue_manager.py:66-71) as mailbox-type fallback values only. Currently these default to 99, causing incoming proposals (priority 3) to always sort before counter-offers whenever mailbox metadata is missing. Keep the fallback aligned with the ordering rule above: `counter_offer: 3`, `counter_offer_response: 3`, `conflict_alert: 4`.

**Recommended frontend contract**

- Mailbox button opens a lightweight inbox panel anchored to the existing top bar, not a full-screen modal.
- The panel should be non-destructive and easy to close; clicking outside or pressing the mailbox button again can dismiss it.
- Selecting a row triggers `activate -> popup open`.
- The panel should refresh after:
  - local defer
  - response submission
  - queue change from `/command` or `end turn`
  - save/load
- **End-turn rule:** Active mailbox soft-stops do NOT block `end turn` after this follow-up; only true hard-stop dialogues do. `end turn` should close the inbox panel first, then refresh mailbox state from the backend after turn advancement.
- **End-turn while panel open:** Close the inbox panel before submitting `end turn`. `advance_turn` can deliver new proposals, expire queue items, and clear stale dialogues — the panel would become stale. Simplest: close panel on any `/command` submission, reopen from fresh `GET /mailbox` after.
- If count drops to `0` while the panel is open, show an explicit empty state and close cleanly on next dismiss.
- **Replace `_dismissed_proposal_nation`** (main.gd:97): The current single-string tracker only suppresses one nation at a time. With the mailbox panel, either (a) disable auto-show entirely when the panel exists (preferred — the panel IS the browse mechanism), or (b) replace with a Set of dismissed `mailbox_id`s cleared on panel open.

- **Notification clear contract:** Once mailbox-eligible `DIPLOMATIC_PROPOSAL` notifications are suppressed/dismissed, the response/HUD path must explicitly clear the icon strip when none remain. Do not rely on omission of the `notifications` key to clear stale mailbox-related icons.

**Non-goals / adjacent note**

- Do not turn the mailbox into a generic notification center in this slice.
- Record the policy boundary for later HUD cleanup:
  - mailbox is for pending diplomatic decisions
  - mailbox-eligible diplomacy should not also create separate persistent `DIPLOMATIC_PROPOSAL` icon-strip entries once the inbox exists; use the mailbox badge plus campaign log/dispatch, and only a transient terminal/toast surface if an immediate arrival ping is still desired
  - persistent top-bar notifications should be reserved for action-required / strategically urgent items
  - routine combat/readiness notices such as `counterpunch ready` should be demoted later to event log, terminal feed, or transient toast instead of living indefinitely in the top-bar icon strip

**Exit criteria**

- The player can click `Later` on an incoming proposal and keep issuing commands immediately.
- Clicking the mailbox badge with multiple pending items opens a browsable inbox instead of one arbitrary proposal popup.
- The player can inspect and choose a specific pending diplomacy item when `Mailbox (2+)` is present.
- Clicking a queued mailbox row opens that chosen item, not whichever proposal happens to be active already.
- Delayed replies still work via typed popup buttons and through `/command` for `1/2/3`, `accept`, `counter`, and `reject`.
- `/pending_envoy` returns popup-safe data in the same display shape expected by `incoming_proposal_popup.gd` when an active reopenable mailbox item exists.
- Badge count and recovery behavior stay in sync for:
  - active soft-stop only
  - queued proposal only
  - active soft-stop plus queued proposals
  - five pending proposals in stable order
  - hard-stop active with queued proposals behind it
- No pending diplomacy item is lost, silently reordered, or spuriously consumed when the player browses the inbox.

**Regression test matrix**

- Extend Godot-facing popup tests for local defer behavior and re-enable-input flow.
- Add mailbox-list endpoint tests for:
  - active soft-stop only
  - queued-only (only when a non-mailbox current dialogue is in front, or during legacy-load migration before promotion)
  - active plus queue ordering
  - five pending items with stable order
  - hard-stop active with queued proposals still counted but not active
- Add activation tests proving a selected queued item becomes active and the previous active item is safely re-queued.
- Add endpoint tests for `/pending_envoy` covering:
  - active soft-stop returns reopenable popup payload
  - queued-only-behind-blocker (or pre-promotion legacy-load state) returns `has_pending = false` but keeps accurate `pending_envoy_count`
  - hard-stop-plus-queue returns no active popup payload and keeps accurate `pending_envoy_count`
- Add command-path tests proving soft-stop delayed replies still route for numeric and keyword inputs.
- Add save/load tests proving `mailbox_id` and queue order survive round-trip serialization.
- Add mailbox identity continuity tests proving:
  - `incoming_proposal` → `counter_offer` replacement keeps the same `mailbox_id` / `mailbox_order`
  - inbox refresh after a counter-offer still points at the same mailbox row instead of a duplicate/new item
- Add popup-cache ownership tests proving:
  - queued mailbox arrival does NOT overwrite the currently active item's popup payload
  - legacy-load / `diplomatic_queue` migration rebuilds the active popup cache from the promoted mailbox item, not stale serialized `incoming_proposal_popup`
  - `counter_offer_response` mailbox reopen/activation uses the same popup-safe builder as other mailbox items
- Add end-turn guard tests proving mailbox soft-stops do not block `end turn`, while true hard-stops still do.
- Add mailbox lifetime tests after `diplomatic_queue` removal:
  - deferred mailbox items are not force-cleared by generic `clear_stale()` timeout
  - active and queued mailbox items follow the same no-silent-expiry rule
  - if explicit per-item expiry is introduced later, it must be visible in inbox data and outcome logging
- Add hybrid soft-stop edge case tests:
  - hybrid active + diplomacy queued: badge count correct, mailbox shows only diplomacy
  - hybrid active does NOT appear in `GET /mailbox` response
  - hybrid active blocks mailbox open/activate instead of being swapped behind the inbox
- Add queue elimination migration tests:
  - all AI proposals reach `dialogue_manager._queue` after `diplomatic_queue` removal
  - badge count uses `get_mailbox_count()` exclusively (NOT `get_soft_stop_count()`)
  - PL-34 overflow logging fires from `DialogueManager`, not old `_enqueue_proposal` / `_expire_queue`
  - same-source dedup still works when the active item and queued item both live in `dialogue_manager`
  - `GET /mailbox` ordering and `DialogueManager._promote()` ordering both follow `mailbox_priority` + `mailbox_order`
  - no code calls `get_soft_stop_count()` for badge/UI purposes after `get_mailbox_count()` is added
  - `from_dict` backward compat: saved `diplomatic_queue` items are delivered into `dialogue_manager` on load, deduped by source+turn
  - legacy `dialogue_manager` mailbox items missing `mailbox_id` / `mailbox_order` are backfilled on load
  - `_next_mailbox_seq` is advanced past restored current-turn mailbox IDs before any new proposal is generated post-load
- Add `clear_stale` mailbox exemption tests:
  - `clear_stale()` skips `SOFT_STOP_MAILBOX_TYPES` in active slot regardless of `blocking` field value
  - mailbox item with `blocking=True` survives indefinitely (not force-cleared after `BLOCKING_TIMEOUT_TURNS`)
  - non-mailbox blocking dialogues still obey the existing safety valve timeout
- Add activation guard tests:
  - swap blocked when active slot holds `HARD_STOP`, `HYBRID_SOFT_STOP`, or `LOCAL_PLANNING`
  - `incoming_proposal_popup` cache updated on successful swap
  - `counter_offer` transition rebuilds cached popup clauses instead of only mutating `is_counter_offer`
  - re-queued item preserves original `turn_created`
  - stale `mailbox_id` activation fails cleanly without disturbing the current active item
- Add `counter_offer` priority ordering tests:
  - `counter_offer` vs `incoming_proposal` queue ordering after priority fix
- Add numeric-reply routing tests for soft-stop mailbox items:
  - "1" typed while soft-stop active matches first option
  - "2" typed while soft-stop active matches second option
  - numeric reply when no soft-stop active does NOT misroute
- Add dismiss-then-reopen tests for counter_offer_response:
  - "Dismiss" action on counter_offer_response keeps item pending
  - dismissed counter_offer_response reopenable from mailbox inbox
- Add dedup-after-elimination tests:
  - `_has_pending_proposal_from()` scans `dialogue_manager._queue` and active slot, not `diplomatic_queue`
  - same-nation proposal blocked when another from that nation is active or queued in dialogue_manager
- Add mailbox-vs-notification tests proving mailbox-eligible arrivals do not also leave behind duplicate persistent `DIPLOMATIC_PROPOSAL` icon-strip entries, and that the icon strip clears once no mailbox-related notifications remain.
- Re-run the existing Session 2 guard/count/history suite after the mailbox follow-up lands.

**Implementation trap warnings (sixth audit pass)**

These are concrete code paths that previous spec text covers implicitly but does not name. Missing any one will cause a runtime or logic bug:

- **`_has_pending_proposal_from()` (ai_diplomacy.py:277-301):** Scans `_get_queue(world)` for same-source dedup. After `diplomatic_queue` elimination, redirect this scan to `dialogue_manager._queue` (and active slot). Without this, duplicate proposals from the same nation will pile up.
- **`try_deliver_queued_proposal` import in turn_manager.py:302-303, call at 322-324:** Must be removed alongside the ai_diplomacy.py function body, or `ImportError` at runtime.
- **Inline `diplomatic_queue` expiry in world_state.py:4098-4101:** `self.diplomatic_queue = [q for q in self.diplomatic_queue if ...]` is a second expiry path outside `ai_diplomacy._expire_queue()`. Remove this block during step 0.
- **`meta_executor.py:2014-2016` debug cheat fallback:** Creates `world.diplomatic_queue` on demand and appends proposals directly. Redirect to `dialogue_manager.push()` with mailbox metadata.
- **`diplomatic_ledger.py:623`:** `len(getattr(world, 'diplomatic_queue', []))` — replace with `dialogue_manager.get_mailbox_count()` or equivalent pending-proposal query.
- **`diplomatic_executor.py:3217` `replace()` call (incoming_proposal → counter_offer):** Must copy `mailbox_id` / `mailbox_order` / `mailbox_priority` from the current dialogue onto the replacement dict. This is the only mailbox→mailbox `replace()` mutation; other `replace()` calls are local-planning flows that don't carry mailbox metadata.
- **`counter_offer_response` at world_state.py:4488-4514 sets `blocking: True`:** This type is in `SOFT_STOP_MAILBOX_TYPES`, so the step 4 `clear_stale` exemption must cover it specifically — without the exemption, the 2-turn safety valve force-clears it.
- **`_build_pending_envoy_popup_from_queue()` (main.py:1918-1929):** After queue elimination this helper has no callers. Remove it, and update the `elif result["pending_envoy_count"] > 0` branch at main.py:1964-1971 which uses it.
- **`is_soft_stop()` usage in badge formulas (main.py:172, 499, 859, 1947):** `is_soft_stop()` includes hybrids. All four sites must switch to the new `get_mailbox_count()`.

**Implementation order inside Session 2 follow-up**

0. **Eliminate `diplomatic_queue`:** Remove field from WorldState, remove `_enqueue_proposal`/`_dequeue_best`/`_expire_queue`/`try_deliver_queued_proposal` from ai_diplomacy.py, deliver all AI proposals via `deliver_ai_proposal()` → `dialogue_manager.push()` at generation time, and carry forward mailbox ordering/dedup metadata on the dialogue objects themselves. Remove one-per-turn throttle in `turn_manager._process_ai_diplomatic_phase()`. Migrate PL-34 overflow logging into DialogueManager (the 3-turn expiry from `advance_turn:4098` is removed entirely — mailbox items do not silently expire; overflow cap remains). Update all 4 badge formulas in main.py (`build_base_response:170`, `_include_popup_passthroughs:497`, end-turn response `:857`, `get_pending_envoy:1945`) to use `get_mailbox_count()`. Deprecate `get_soft_stop_count()` — it counts all queue items regardless of type and must not be used for badge/mailbox logic after `get_mailbox_count()` exists. Remove `diplomatic_queue` from `to_dict`/`from_dict` (add `from_dict` backward compat: if saved data has `diplomatic_queue`, deliver each item into `dialogue_manager` on load without duplicating already-active/queued items; dedup by source nation + turn since raw proposals lack `mailbox_id`). Suppress `DIPLOMATIC_PROPOSAL` persistent notification for mailbox-eligible proposals (`ai_diplomacy.py:905`) — use transient terminal arrival ping instead; the mailbox badge is the persistent surface. Also update: `_has_pending_proposal_from()` (ai_diplomacy.py:296), `meta_executor.py:2014-2016` cheat fallback, `diplomatic_ledger.py:623`, `turn_manager.py:302-324` import+call, and `world_state.py:4098-4101` inline expiry (see trap warnings above).
1. Add `counter_offer`/`counter_offer_response`/`conflict_alert` to `DIALOGUE_PRIORITY` (suggested: `counter_offer: 3`, `counter_offer_response: 3`, `conflict_alert: 4` — same-urgency as `incoming_proposal` for counter-offers, slightly lower for conflict alerts). Add `get_mailbox_count()` to `DialogueManager` that counts `SOFT_STOP_MAILBOX_TYPES` only (excludes hybrids).
   Use `mailbox_priority` / `mailbox_order` in both `DialogueManager._promote()` and `GET /mailbox`; `DIALOGUE_PRIORITY` is fallback only.
2. Add stable `mailbox_id` ownership (generation via `f"mb-{turn}-{seq}"` with per-turn counter on WorldState, serialization, presence on all mailbox-eligible dialogue types including `counter_offer_response` from advance_turn).
   Preserve mailbox metadata when the active item is replaced in place (`incoming_proposal` → `counter_offer`), and backfill missing mailbox metadata for restored legacy mailbox dialogues before advancing `_next_mailbox_seq`.
3. Add `GET /mailbox` plus `POST /mailbox/activate` (with cache invalidation for `incoming_proposal_popup`, activation guard for `HARD_STOP` / `HYBRID_SOFT_STOP` / `LOCAL_PLANNING`, re-queue with preserved `turn_created`). Lock ordering semantics with tests.
   Treat `incoming_proposal_popup` as active-item-only state: queued arrivals/load migration must rebuild per-item payloads instead of overwriting the active cache.
4. **Add type-based exemption in `clear_stale()` for `SOFT_STOP_MAILBOX_TYPES`:** skip clearing entirely when current dialogue type is in `SOFT_STOP_MAILBOX_TYPES`. Do NOT change the `blocking` field to `False` — that would trigger the non-blocking branch which clears on the very next turn. The `blocking=True` field is legacy; the type taxonomy is authoritative. Also confirm `is_blocking()` is not used in any guard path for soft-stops (it shouldn't be — guards use `is_hard_stop()`). Keep mailbox lifetime semantics inside the inbox contract. If explicit expiry is ever added later, make it per-item, visible in the inbox payload/UI, and logged.
5. Build the Godot mailbox panel/list. Wire mailbox button -> inbox open/close. Replace `_dismissed_proposal_nation` with panel-aware suppression. Add type→popup dispatch for `conflict_alert`.
6. Keep local defer behavior, but make inbox selection the authoritative "open this specific item" path.
7. Fix `/pending_envoy` shape and active-item-only backward-compat semantics so queued-only / hard-stop-plus-queue states are handled through `GET /mailbox`, not arbitrary queue reopening.
8. Fix soft-stop `/command` delayed-reply routing for numeric and keyword responses without widening back to global keyword misroutes. Specifically: add numeric-index matching (e.g. "1" → first option, "2" → second) against the active dialogue's `options` list for soft-stop dialogues (main.py:639-650), alongside the existing label/action text matching.
9. Lock the whole flow with mailbox browse/defer/select/respond-later regressions (including expanded test matrix above) before moving to `PL-32`.

### Session 2 Refactor Follow-Up - Current-Turn Diplomatic Offer Lifetime — COMPLETE

**Items:** follow-up slice under `PL-27` / `PL-34` only. No new PL id.

**Status: COMPLETE** (April 11, 2026). See `docs/DIPLOMATIC_OFFER_LIFETIME_SPEC.md`.

**Goal:** replace the persistent diplomacy mailbox model with current-turn envoy items that can be reopened this turn, lapse automatically at end turn, and block only new diplomacy during that same turn.

**What shipped:**

- `CURRENT_TURN_OFFER_TYPES` constant + `lapse_pending_offers()` + `has_current_turn_offers()` in `DialogueManager`
- `conflict_alert` reclassified from `SOFT_STOP_MAILBOX_TYPES` to `LOCAL_PLANNING_TYPES`
- AI proposals created with `blocking=False` — do not block end-turn or ordinary commands
- End-turn narrowed to hard-stop only (`is_hard_stop()` guard replaces blanket blocking check)
- Diplomacy gating narrowed: `is_hard_stop() or has_current_turn_offers() or is_local_planning()`
- Lapse hook at start of `TurnManager.end_turn()` — offers lapsed before enemy phase / AI diplomacy
- Campaign log `offer_lapsed` event type + morning dispatch `lapsed_offers` section
- Frontend: "Not Now" button rename, lapse warning text, "Envoys" rename (top bar + mailbox panel)
- Client-side end-turn confirmation gate with inline terminal warning
- Dispatch view renders lapsed offers section
- Diplomacy wizard blocked message updated
- Save/load migration: normalize `blocking=False` on offer types, remove legacy `conflict_alert` mailbox items
- 51 new tests in `tests/test_offer_lifetime.py`, 8249 total passing

### Session 3 - Diplomacy Display Contract

**Items:** `PL-32`

**Goal:** make the backend the single owner of player-facing diplomacy labels once the Session 2 follow-up transport contract is stable.

**Status: COMPLETE** (April 12, 2026). Proposal/clause label ownership is centralized in `backend/display_names.py`. `main.py`, `diplomatic_dialogue.py`, `mailbox_payloads.py`, `world_state.py`, `diplomatic_defiance.py`, and `ai_diplomacy.py` now consume shared backend formatters. `incoming_proposal_popup.gd` reads backend `proposal_type_display` instead of keeping its own proposal-type map. Added targeted regressions for raw-token leaks and popup payload display contract coverage.

**Exit criteria**

- Incoming proposal, counter-offer, sabotage, and fallback popup text all come from the same backend formatter.
- Godot stops rebuilding proposal labels from raw identifiers.

### Session 4 - First-Hour Pressure Cleanup

**Items:** `PL-28`, `PL-26`

**Status:** COMPLETE Apr 12, 2026. Audit handoff: `docs/SESSION4_AUDIT_HANDOFF.md`.

**Goal:** remove unfair defeat surprise and make the first combat lesson legible without flattening combat depth.

**Exit criteria**

- Players receive an explicit defeat-imminent warning before the live loss rule fires.
- The obvious early French attack line is no longer a hidden trap with no surfaced counterplay.

### Session 5 - Restart Flow

**Items:** `PL-29`

**Goal:** allow a clean restart from the live client/server flow without manual process kill or stale autosave leakage.

**Exit criteria**

- A supported `POST /new_game` contract exists.
- The pause menu exposes it.
- Autosave/restart behavior is explicit and regression-tested.

---

## Active Bug Specs

### PL-30: Godot crash after a masked proposal result

**Problem statement**

A proposal result can be hidden behind a higher-priority popup, then the next Diplomacy-button interaction crashes Godot with `attempt to call function add_output on a base null instance`.

**Confirmed evidence**

- Playtest Session D reproduction: send a proposal, let a higher-priority popup win, then open Diplomacy on the next turn and hit the crash.
- The current popup pipeline only forwards one winner per response cycle through `_include_popup_passthroughs()`.
- The frontend crash string points at a stale/null `add_output` path rather than a cleanly recoverable deferred result.
- `diplomacy_wizard.gd` has two matching fallback branches: `_render_nations()` and `_render_preview()` both close the wizard and call `get_node("/root/Main").add_output(...)` whenever `dialogue_pending` is true.
- `/command` still has an enemy-phase path that consumes `proposal_result_popup` outside the main response builder, so proposal-result ownership is already split.

**Root-cause notes**

- `_include_popup_passthroughs()` only surfaces one winning popup per response cycle, so lower-priority proposal results can remain pending after a different popup displays first.
- The diplomacy preview contract is too coarse. Step 1 preview in `backend/main.py` and Step 2 preview in `backend/game_logic/diplomacy.py` both collapse multiple states into `dialogue_pending`, even when the real condition is "recoverable proposal result is still pending."
- The frontend wizard treats that coarse flag as a fatal block and routes through a null-prone terminal logging path instead of a structured recovery surface.
- Step 1 and Step 2 are the same failure family and stay under `PL-30`; do not split them into separate work.

**Exact code surfaces**

- `backend/main.py` - `build_base_response()`, `_include_popup_passthroughs()`, enemy-phase `/command` proposal-result handling, `/diplomatic_preview`.
- `backend/game_logic/diplomacy.py` - `get_available_diplomatic_actions()`, `get_diplomatic_preview()`.
- `godot-client/project-sovereign/scripts/main.gd` - `add_output()`, `_on_proposal_result_dismissed()`, `_on_diplomacy_button_pressed()`, `_open_diplomacy_wizard()`.
- `godot-client/project-sovereign/scripts/diplomacy_wizard.gd` - `_render_nations()`, `_render_preview()`.

**Exact failure modes**

- A higher-priority popup wins the current response, leaving `proposal_result_popup` deferred.
- The player reopens diplomacy. Step 1 or Step 2 sees only `dialogue_pending = true`, not the real deferred-result state.
- The wizard closes itself and tries to log via `get_node("/root/Main").add_output(...)`.
- If that node lookup is invalid in the current tree state, Godot throws the observed null-instance crash.
- Even when no crash occurs, the deferred result is still on an ambiguous contract and can be lost or redisplayed incorrectly.

**Edge cases / sibling failure scan**

- Reopen diplomacy from the button and from any shortcut/hotkey path.
- Reopen on the same turn as the masked popup and after a turn advance.
- Reproduce both Step 1 nation-list rendering and Step 2 action preview rendering.
- Verify the flow when a proposal result is pending but a true blocking dialogue is not.
- Verify dismissal does not create double-delivery on the next response cycle.

**State-transition risks**

- Clearing or dismissing the proposal result must happen in one source of truth; otherwise the same popup can reappear after the wizard or after enemy phase.
- `_on_proposal_result_dismissed()` currently refreshes war data and input state only. If proposal-result ownership moves, the dismissal hook must clear the retained result state as well.
- Save/load and turn-advance flows must not resurrect a stale deferred result after it has been dismissed.

**Backend / frontend contract risks**

- `dialogue_pending` is not precise enough for the diplomacy wizard. The fix needs an explicit distinction between a blocking diplomacy dialogue and a recoverable deferred result.
- Wizard-side code should not depend on a hard-coded `/root/Main` lookup to report contract state.
- The fix should not pull full Session 6 popup-registry work earlier; it only needs to restore single-source ownership for proposal results.

**Acceptance criteria**

- Reproducing the original masked-result flow no longer crashes the client.
- A proposal result that loses popup priority remains recoverable until it is displayed or explicitly dismissed.
- Opening the Diplomacy wizard after a masked result distinguishes "blocking dialogue" from "deferred result" instead of treating both as generic `dialogue_pending`.
- Neither Step 1 nor Step 2 of the wizard calls the null-prone `get_node("/root/Main").add_output(...)` fallback for this flow.
- Lower-priority proposal results are not discarded just because another popup displayed first.

**Regression test matrix**

- Backend response test: a lower-priority `proposal_result_popup` survives a higher-priority popup cycle and remains present until dismissed.
- Backend preview test: `/diplomatic_preview` and the Step 2 preview path return a structured non-crashing state when a deferred proposal result exists.
- Frontend smoke: `proposal reply masked -> next turn diplomacy open` via diplomacy button.
- Frontend smoke: the same flow through Step 2 preview and result dismissal.
- Re-run popup contract suites after the ownership change.

**Dependencies / blockers**

- No upstream blocker.
- Re-check this flow after Session 2 if mailbox semantics touch the same proposal-result surfaces.

**Implementation order inside Session 1**

1. Normalize proposal-result ownership so `_include_popup_passthroughs()` and the `/command` enemy-phase path stop diverging.
2. Replace the coarse wizard gating path with an explicit backend/frontend distinction between blocking dialogue and deferred result.
3. Remove the null-prone `add_output()` recovery call from both Step 1 and Step 2 render paths.
4. Add persistence tests for masked results, then rerun the original repro flow manually.

---

### PL-31: Capital-loss instant defeat is still live, and its regression test is broken

**Problem statement**

The game still hard-loses when Paris falls, even though the project history and regression test claim that capital-loss defeat was removed.

**Confirmed evidence**

- `backend/game_logic/turn_manager.py::_check_victory_conditions()` still returns defeat on captured capital.
- `tests/test_playtest_bugfixes.py::TestCapitalLossNotDefeat` targets `Ile-de-France`, which is not a live region key, so the test passes vacuously.
- Direct reproduction with `world.regions["Paris"].controller = "Prussia"` returns `Your capital has fallen!`.
- Historical status text still contains a now-false March 9 claim that capital-loss defeat was removed.

**Root-cause notes**

- `_check_victory_conditions()` still contains the obsolete capital-capture defeat branch even though the intended rule and prior notes say capital loss should be survivable.
- The regression test never exercised the live branch because it points at a nonexistent region key.
- `docs/STATUS.md` inherited the false "already fixed" claim, so code, test, and docs all drifted together.

**Exact code surfaces**

- `backend/game_logic/turn_manager.py` - `_check_victory_conditions()`.
- `tests/test_playtest_bugfixes.py` - `TestCapitalLossNotDefeat`.
- `docs/STATUS.md` - current-phase summary plus the March 9 historical note that now needs a superseded marker.

**Exact failure modes**

- Capturing Paris immediately ends the campaign even while France still has armies and other regions.
- The false-negative regression test allows the obsolete branch to survive future refactors.
- Downstream warning work in `PL-28` would otherwise target the wrong defeat rule.

**Edge cases / sibling failure scan**

- Capital loss with surviving armies and surviving territory must continue the game.
- Zero armies must still lose.
- Zero controlled regions must still lose.
- Time-expiry victory/defeat logic must remain unchanged.

**State-transition risks**

- Removing the capital-loss branch must not weaken the existing `game_over` flow for the real defeat paths.
- Any defeat summary, dispatch text, or end-turn path that referenced capital loss as terminal must be aligned to the surviving rules before `PL-28` starts.

**Backend / frontend contract risks**

- The live defeat rule is backend-owned; frontend and docs must not preserve stale capital-loss wording after the code fix.
- The repaired regression test must target the real live region key so future refactors fail loudly if the branch returns.

**Acceptance criteria**

- Capturing Paris alone does not end the game while France still has territory or armies.
- The regression test targets `Paris` and fails if capital-loss defeat comes back.
- `docs/STATUS.md` no longer implies this bug is already resolved.
- PL-28 warning logic is based on the surviving defeat rules, not the obsolete capital-loss branch.

**Regression test matrix**

- Repair `tests/test_playtest_bugfixes.py` to use `Paris`.
- Add or keep a direct defeat-state test that proves capital loss alone is non-fatal.
- Re-run defeat-condition coverage around zero-territory, all-marshals-destroyed, and time-expiry paths.

**Dependencies / blockers**

- Unblocks PL-28.
- If design direction changes later and capital loss becomes fatal again, reopen PL-31 rather than silently changing the rule.

**Implementation order inside Session 1**

1. Remove the capital-loss defeat branch from `_check_victory_conditions()`.
2. Repair the regression test to target `Paris` and add a direct non-fatal capital-loss assertion.
3. Re-run defeat-path tests to confirm only the intended loss rules remain.
4. Update `docs/STATUS.md` so the historical note is explicitly marked as disproven rather than silently left in place.

---

### PL-27: Diplomacy interrupt contract is broken

**Problem statement**

Soft-stop diplomacy is still treated like a hard-stop crisis. Incoming AI proposals and related items block ordinary commands, the player has no authoritative mailbox/recovery surface, pending counts are wrong, and several popup buttons still route back through stringly parser commands.

**Confirmed evidence**

- `backend/commands/executor.py` and `backend/main.py` both hard-stop on any `pending_diplomatic_dialogue`.
- `backend/game_logic/ai_diplomacy.py` still delivers incoming proposals with `blocking = True`.
- `backend/main.py::build_base_response()` and `backend/game_logic/diplomatic_ledger.py` both derive `pending_envoy_count` from queue length only, ignoring an active pending dialogue.
- `godot-client/project-sovereign/scripts/main.gd::_on_envoy_clicked()` only prefills `Talleyrand, report on the waiting envoy`; it does not open a real recovery surface.
- `backend/campaign_log.py` does not retain proposal-arrival events, so masked or auto-rejected opportunities are not authoritatively recoverable from history.
- Remaining popup handlers still use parser-shaped command text instead of typed dialogue responses.

**Root-cause notes**

- Both backend command paths treat any `pending_diplomatic_dialogue` as a global blocker before ordinary command handling can continue.
- The codebase already has a blocking taxonomy signal (`dialogue.get("blocking")`, `dialogue_manager.is_blocking()`, `meta_executor` special-casing for `end_turn`), but that taxonomy is not enforced consistently across `/command`, executor routing, previews, or UI entry points.
- Incoming proposals are still delivered as `blocking = True`, which collapses mailbox-style diplomacy into crisis-style interruption.
- The pending-envoy badge is not authoritative because it ignores the active pending item and counts only queued items.
- Recovery is not authoritative because the envoy button only pre-fills parser text and several popup responses still synthesize English commands instead of stable option ids.
- Same-family command failures on `status`, `help`, `economy`, `treasury`, and `finances` belong here. Do not create new PL items for those paths unless a post-fix repro survives the contract cleanup.

**Exact code surfaces**

- `backend/commands/executor.py` - pending-dialogue guard in `execute()`.
- `backend/main.py` - `/command` dialogue guard, `build_base_response()`, typed dialogue endpoint.
- `backend/game_logic/ai_diplomacy.py` - incoming proposal delivery, cooldown/frequency behavior, queue handling.
- `backend/game_logic/diplomatic_ledger.py` - pending envoy count and related visibility.
- `backend/models/dialogue_manager.py` and `backend/models/world_state.py` - stale-dialogue clearing and turn-advance behavior.
- `backend/campaign_log.py` - diplomacy event whitelist/history retention.
- `godot-client/project-sovereign/scripts/main.gd` - incoming proposal response handlers, envoy click target, remaining `send_command` fallbacks.
- `godot-client/project-sovereign/scripts/top_bar.gd` and related diplomacy UI entry points - badge/count presentation for the mailbox surface.

**Exact failure modes**

- A soft-stop incoming proposal freezes `status` and other ordinary commands because the guard fires before command execution.
- The active pending proposal is invisible to the top-bar badge if the queue is empty.
- Clicking the envoy badge does not reopen the pending item; it only sends a parser phrase and depends on brittle keyword recovery.
- Popup handlers for incoming proposal, objection, sabotage, and rebellion still route through parser text, which can drift from valid dialogue option ids.
- Queue promotion, dismissal, and stale-dialogue cleanup can all happen without an authoritative mailbox/history record of what the player actually missed.

**Edge cases / sibling failure scan**

- No pending dialogue: normal command execution must remain unchanged.
- Hard-stop dialogue active: command blocking must remain intact for true hard-stop crises.
- Soft-stop dialogue active with no queue: read-only and ordinary non-dialogue commands must still work.
- Soft-stop dialogue active with queued items behind it: badge/count and recovery surface must show both active and queued work.
- `end_turn` remains special: it may still require explicit handling or auto-default behavior for certain dialogue families.
- Same-family nearby commands `status`, `help`, `economy`, `treasury`, and `finances` must all be verified under the new guard split.

**State-transition risks**

- Reclassifying dialogue types without aligning stale cleanup can cause items to clear unexpectedly on turn advance.
- Active-to-queued-to-history transitions must update the badge/count exactly once at each step.
- If only one backend command path is fixed, the parser and direct executor paths will drift and create inconsistent behavior.
- Typed popup responses must not bypass the same world-state transitions used by parser-driven dialogue handling.

**Backend / frontend contract risks**

- The response contract needs more than a coarse `dialogue_pending` boolean. The frontend needs an authoritative distinction between hard-stop dialogue, active soft-stop item, and queued mailbox items.
- The envoy badge must be derived from the same backend-owned count in every response path.
- Recovery should reuse the existing envoy/desk surface rather than inventing a second parallel inbox flow.
- Popup handlers should send stable response ids to `/respond_to_diplomatic_dialogue`, not synthesized English text.

**Acceptance criteria**

- Hard-stop vs soft-stop taxonomy is enforced in both backend command paths.
- For the current fix phase, the minimum taxonomy is:
  - hard-stop: `force_declare_war_confirmation`, `commitment_paradox` (legacy `alliance_paradox` alias still accepted on load)
  - soft-stop mailbox: `incoming_proposal`, `counter_offer`, `counter_offer_response`, `conflict_alert`
  - hybrid soft-stop with end-turn default: `sabotage_confrontation`, `vassal_rebellion_imminent`
  - local planning flow, not global blocker: `proposal_confirm`, `advisory`, `mission`, `terms_guidance`, `ultimatum_demand_wizard`
- Incoming proposals, counter-offers, conflict alerts, and similar soft-stop items no longer freeze ordinary commands.
- Soft-stop diplomacy has a visible mailbox or desk surface with a trustworthy badge/count.
- Pending envoy count includes both the active soft-stop item and queued items.
- Envoy click opens the recovery surface instead of only prefilling terminal text.
- Auto-reject, dismissal, and expiry outcomes are recorded in dispatch/history so the player can tell what happened.
- Popup choices for dialogue-shaped diplomacy flows use typed response ids instead of synthesized English commands.

**Regression test matrix**

- Extend `tests/test_dialogue_manager.py` for hard-stop vs soft-stop classification and stale-clear behavior.
- Extend `tests/test_bugfix_proposal_flow.py` for non-blocking proposals, mailbox recovery, queued visibility, and auto-outcome logging.
- Extend `tests/test_endpoint_wiring.py` or `tests/test_response_pipeline.py` for authoritative pending counts and mailbox payload shape.
- Add command-path regressions for `status`, `help`, `economy`, `treasury`, and `finances` with no dialogue, soft-stop dialogue, and hard-stop dialogue.
- Re-run popup response tests after migrating the affected handlers to typed response ids.

**Dependencies / blockers**

- Root dependency for PL-34 and PL-33.
- Blocks PL-32.
- Blocks diplomacy refinement items that need a trustworthy interrupt model, especially R162.

**Implementation order inside Session 2**

1. Normalize the blocking taxonomy and enforce it in both backend command paths before parser execution.
2. Reclassify incoming proposals and other soft-stop flows so they stop acting like hard-stop crises.
3. Make the pending-envoy count authoritative by including both the active soft-stop item and queued items in one backend-owned contract.
4. Wire the envoy badge to a real recovery surface and migrate the affected popup handlers to typed dialogue responses.
5. Add history/dispatch outcomes for arrival, dismissal, expiry, overflow, and auto-default behavior.
6. Run the `PL-33` duplicate verification pass last, after the guard split and recovery surface are both live.

---

### PL-34: Queued diplomatic proposals can expire unseen behind blockers

**Problem statement**

Queued proposals can age out or get dropped before the player ever sees them, so diplomacy is currently being resolved by hidden queue expiry and overflow rules instead of explicit player choice.

**Confirmed evidence**

- Queue expiry removes proposals after three turns.
- Queue overflow keeps only the top three items and silently drops the rest.
- Queued delivery expires items before attempting delivery.
- Blocking dialogues can linger until the stale-dialogue cleanup path, which lets unseen queued items die behind them.
- The focused reproduction showed a later Prussian proposal expiring before it was ever surfaced because an Austrian blocker remained active first.

**Root-cause notes**

- Queue age currently starts at generation time, not at first player visibility.
- `try_deliver_queued_proposal()` expires queued work before attempting delivery, so a proposal can die on the same turn it would otherwise become visible.
- Queue overflow silently drops lower-ranked items once `QUEUE_MAX_SIZE` is exceeded.
- There is no authoritative mailbox/history record at enqueue time, so "waiting envoy" state is invisible until delivery succeeds.
- This belongs under `PL-27` because the real fix is the mailbox/visibility contract, not a separate proposal subsystem.

**Exact code surfaces**

- `backend/game_logic/ai_diplomacy.py` - `_expire_queue()`, `_enqueue_proposal()`, `_dequeue_best()`, `try_deliver_queued_proposal()`.
- `backend/models/dialogue_manager.py` - stale-dialogue cleanup timing.
- `backend/models/world_state.py` - dialogue clear path on turn advance.
- `backend/game_logic/turn_manager.py` - delivery timing relative to turn flow.
- Mailbox/count surfaces introduced by PL-27.

**Exact failure modes**

- A queued proposal generated behind another blocker can expire before first surface.
- Overflow beyond queue capacity silently discards proposals with no player-visible record.
- Badge/count state does not reveal that proposals are waiting or that they were dropped/expired.
- Clearing a blocker does not guarantee the player can inspect what arrived while that blocker was active.

**Edge cases / sibling failure scan**

- One active soft-stop item plus one queued item.
- One hard-stop item plus queued proposals behind it.
- Queue reaches capacity and receives one more proposal.
- A blocker clears on the same turn an older queued item would otherwise expire.
- Expiry, dismissal, and promotion all occur around turn advance or stale-dialogue cleanup.

**State-transition risks**

- Making queued arrivals visible at enqueue time must not double-count the item when it later becomes active.
- Expiry and overflow outcomes must remove the item from badge counts exactly once.
- Delivery-order policy should stay stable while visibility/accounting changes; do not mix count fixes with a ranking rewrite.

**Backend / frontend contract risks**

- If the mailbox payload only exposes the active item, queued proposals will remain invisible and this bug will survive under a new badge.
- If expiry/overflow are only logged in history but not reflected in the active count, the top bar will drift out of sync.

**Acceptance criteria**

- Queued proposal arrival becomes visible immediately through the authoritative envoy/mailbox contract, even if another item is currently blocking delivery.
- Unseen soft-stop proposals do not disappear silently.
- Expiry and overflow create explicit recorded outcomes; they never remove an item without a player-visible record.
- Delivery after the blocker clears preserves the existing queue policy unless a direct test proves the policy itself is wrong.
- The player can review what arrived, what expired, and what was auto-rejected through the mailbox/history flow introduced by `PL-27`.

**Regression test matrix**

- Extend `tests/test_bugfix_proposal_flow.py` for blocker-behind-queue visibility, hidden-expiry conversion into recorded outcomes, and overflow recording.
- Extend `tests/test_dialogue_manager.py` for promotion and stale-clear timing around queued items.
- Add a regression proving that a queued proposal generated behind another soft-stop item is still visible in the mailbox and is either surfaced or explicitly logged before removal.

**Dependencies / blockers**

- Implement inside the PL-27 batch.
- Depends on the new soft-stop/mailbox contract.

**Implementation order inside Session 2**

1. After the `PL-27` mailbox contract exists, make queued arrivals visible at enqueue time.
2. Convert expiry and overflow into explicit recorded outcomes.
3. Verify badge/count transitions across active, queued, expired, and dismissed states.
4. Re-run the focused unseen-expiry repro before closing the item.

---

### PL-33: `status` is blocked by the diplomacy guard and recovery path

**Problem statement**

The first-hour command most players are likely to try, `status`, is currently being swallowed by the same diplomacy guard/recovery failure that blocks ordinary commands.

**Confirmed evidence**

- The parser already recognizes `status`.
- `_execute_status()` exists and returns a valid intel report.
- The observed failure path happened while an incoming diplomatic dialogue was active.
- Current evidence does not show a clean no-dialogue reproduction.

**Root-cause notes**

- Current evidence points to the same global-guard failure family as `PL-27`, not to a broken `status` implementation.
- `meta_executor._execute_status()` already exists and is valid; the likely fault is that the guard fires before the command reaches it.
- Same-family read-only commands should be verified together instead of patching `status` alone.

**Exact code surfaces**

- `backend/commands/executor.py` - pending-dialogue guard.
- `backend/main.py` - parser-side dialogue guard.
- `backend/commands/meta_executor.py` - `_execute_status()`.

**Exact failure modes**

- `status` is blocked when a soft-stop diplomacy item is pending.
- The same failure family can also swallow other read-only commands that should remain available.
- Shipping a separate `status` patch before the taxonomy fix risks treating the symptom and leaving the family bug alive.

**Edge cases / sibling failure scan**

- `status` with no dialogue pending.
- `status` with soft-stop dialogue pending.
- `status` with true hard-stop dialogue pending.
- The same matrix for `help`, `economy`, `treasury`, and `finances`.

**State-transition risks**

- If `status` is special-cased instead of fixing the guard contract, the next read-only command will fail in the same way.

**Backend / frontend contract risks**

- None beyond the `PL-27` guard split; this item should not create new contract surfaces unless a post-fix repro survives.

**Acceptance criteria**

- After `PL-27` lands, `status` works with no pending dialogue.
- After `PL-27` lands, `status` also works while soft-stop diplomacy is pending.
- True hard-stop dialogue still blocks `status` where intended.
- If a non-dialogue-guard failure still exists after those checks, keep `PL-33` open and split it into a true standalone bug.

**Regression test matrix**

- Add a focused command-path regression for `status` with no dialogue, with soft-stop dialogue, and with a true hard-stop dialogue.
- Add the same verification sweep for `help`, `economy`, `treasury`, and `finances` under the owning `PL-27` test family.

**Dependencies / blockers**

- Blocked on PL-27.
- Duplicate-candidate; do not ship separate code unless a post-PL-27 reproduction remains.

**Implementation order inside Session 2**

1. Leave `PL-33` untouched until the `PL-27` guard split, mailbox contract, and typed-response recovery path are live.
2. Run the focused read-only command matrix.
3. Close as duplicate if the matrix passes; keep open only if a non-guard repro remains.

---

### PL-32: Raw diplomacy labels can leak into popups

**Status:** FIXED (April 12, 2026; audit follow-up added a pause-menu confirmation before `New Campaign` replaces autosave).

**Problem statement**

Proposal and clause display ownership is split across backend and Godot, so raw identifiers such as treaty enums or underscore tokens can leak into popups or degrade wording on fallback paths.

**Confirmed evidence**

- Backend and Godot both keep proposal display mappings.
- `backend/main.py` still formats fallback proposal text ad hoc.
- `backend/game_logic/diplomatic_dialogue.py` rebuilds clause display separately.
- `backend/models/world_state.py` builds counter-offer popup clauses directly from raw clause ids.
- `backend/commands/diplomatic_defiance.py` and `backend/game_logic/ai_diplomacy.py` still own separate formatting paths.

**Root-cause notes**

- Display ownership is split across `backend/display_names.py`, multiple backend helpers, and Godot popup scripts.
- The strongest live raw-leak path is counter-offer popup construction in `world_state.py`, which still builds clauses from raw ids.
- `_include_popup_passthroughs()`, `diplomatic_dialogue.py`, `ai_diplomacy.py`, and sabotage summary code all keep separate fallback formatting logic, so wording can drift even when raw ids do not leak.
- The duplicate Godot proposal-type map is part of the same family and belongs here rather than in a new frontend-only item.

**Exact code surfaces**

- `backend/display_names.py` - canonical display source.
- `backend/main.py` - popup safety-valve formatting.
- `backend/game_logic/diplomatic_dialogue.py` - proposal/clause rendering helpers.
- `backend/models/world_state.py` - counter-offer popup payload construction.
- `backend/commands/diplomatic_defiance.py` - sabotage proposal summary formatting.
- `backend/game_logic/ai_diplomacy.py` - secondary clause display map.
- `godot-client/project-sovereign/scripts/incoming_proposal_popup.gd` - duplicate proposal-type map and underscore fallback.

**Exact failure modes**

- Counter-offer popups can show raw clause ids such as `territory_cede`.
- Proposal type labels can diverge between backend and Godot because both sides keep their own display maps.
- Safety-valve fallback paths can degrade into inconsistent title-casing such as `Open_Borders` or `Non_Aggression`.
- Sabotage and AI proposal summaries can describe the same clause family differently from incoming-proposal popups.

**Edge cases / sibling failure scan**

- Unknown or newly added clause ids should still render through one centralized fallback instead of leaking raw tokens.
- Counter-offer, incoming proposal, sabotage, and fallback popup paths must all be tested together.
- Legacy save data or modded clause ids should degrade consistently through the same formatter.

**State-transition risks**

- Removing the Godot-side map before all backend payloads are normalized can make some popups go blank.
- If one popup path still ships raw ids after the formatter centralization, the bug will survive in a fallback path and be harder to detect.

**Backend / frontend contract risks**

- The backend should ship fully rendered labels plus canonical ids only where machine logic still needs them.
- Godot should render provided display strings, not rebuild labels from ids.

**Acceptance criteria**

- Backend becomes the only owner of human-readable proposal and clause labels.
- Incoming proposal, counter-offer, sabotage, and fallback popup paths all consume the same backend formatter.
- Godot no longer rebuilds proposal labels from enum names or underscore replacement.
- Unknown ids degrade through one centralized fallback formatter instead of leaking raw tokens.
- Popup payload tests fail on raw tokens such as `NON_AGGRESSION`, `territory_cede`, or `Open_borders`.

**Regression test matrix**

- Add backend formatter tests for proposal type and clause rendering.
- Extend popup payload contract tests so raw underscore or enum-style tokens fail.
- Re-run proposal-flow and popup suites after removing the Godot duplicate map.

**Dependencies / blockers**

- Depends on Session 2 transport cleanup so the popup contract is stable before display ownership is collapsed.

**Implementation order inside Session 3**

1. Centralize proposal-type and clause-label rendering in `backend/display_names.py`.
2. Replace backend duplicate formatters in `main.py`, `diplomatic_dialogue.py`, `world_state.py`, `diplomatic_defiance.py`, and `ai_diplomacy.py`.
3. Remove the duplicate Godot proposal-type map and fallback formatting.
4. Re-run popup payload tests, especially counter-offer and sabotage paths.

---

### PL-28: No defeat-imminent warning before game over

**Status:** FIXED Apr 12, 2026.

**Problem statement**

The player can cross from a damaged position into defeat without any clear "you are about to lose" warning in the notification or dispatch layer.

**Confirmed evidence**

- Current defeat-state rules are already inconsistent enough that the player cannot predict what will end the campaign.
- The playtest loss happened without visible warning.
- The fix must follow the surviving defeat rule after PL-31, not the obsolete capital-loss branch.

**Root-cause notes**

- `turn_manager.py` checks terminal defeat only; it has no near-defeat helper that can emit warnings before the loss condition fires.
- After `PL-31`, the live battlefield defeat rules are "all armies destroyed" and "all territory lost." Time-limit warning already has its own system and should stay separate.
- The current item should not expand into predictive enemy-intent simulation. It only needs a deterministic warning tied to the actual surviving defeat thresholds.

**Exact code surfaces**

- `backend/game_logic/turn_manager.py` - defeat evaluation order.
- `backend/models/world_state.py` - any surviving defeat-threshold tracking.
- `backend/notifications.py` - defeat-imminent notification type.
- `backend/game_logic/dispatch.py` - morning-dispatch warning surfacing.

**Exact failure modes**

- The player can step into terminal defeat with no prior warning when only one army or one region remains.
- Warning wording can drift toward the obsolete capital-loss rule if `PL-31` is not treated as the source of truth first.
- If warning logic mixes in time-limit or enemy-intent prediction, the result will spam or mislead instead of clarifying the live loss rule.

**Edge cases / sibling failure scan**

- Exactly one surviving marshal remains.
- Exactly one controlled region remains.
- The player recovers above the threshold after a warning and should not keep stale warning spam.
- Time-limit warning stays on its separate path and is not merged into this item.

**State-transition risks**

- Warning state must persist long enough to appear in both notifications and the next dispatch, but it must also clear if the player stabilizes.
- The warning should fire before defeat resolution, not after a terminal result has already been returned.

**Backend / frontend contract risks**

- The warning should reuse the existing notification and dispatch surfaces, not create a one-off popup path.
- Wording must match the live defeat rule after the capital-loss branch is removed.

**Acceptance criteria**

- After `PL-31`, a high-visibility warning is emitted when France is down to exactly one living marshal and/or exactly one controlled region.
- The player receives the warning before the live defeat rule fires.
- Warning wording matches the actual surviving defeat condition after `PL-31`.
- The warning appears in both notifications and the following dispatch/readout path while the condition persists.
- The warning clears or stops repeating once the player climbs back above the threshold.

**Regression test matrix**

- Add defeat-warning coverage around the surviving loss threshold.
- Add notification/dispatch assertions so the warning is emitted before the actual defeat result.
- Verify that time-limit warnings are unchanged and remain separate.

**Dependencies / blockers**

- Blocked on PL-31.

**Implementation order inside Session 4**

1. Remove the obsolete capital-loss path via `PL-31` first.
2. Add a deterministic near-defeat helper keyed to one remaining marshal and one remaining region.
3. Wire it into notifications and morning dispatch.
4. Add non-spam coverage for warning persistence and recovery above the threshold.

---

### PL-26: Combat feels hopeless because the obvious opener teaches the wrong lesson

**Status:** FIXED Apr 12, 2026.

**Problem statement**

The common early "Ney attacks Wellington" line is punishing before the game has taught bombardment, coordination, or setup counters, so the player learns "attacking is hopeless" instead of learning the system.

**Confirmed evidence**

- Repeated attacks in playtest produced defender victories or punishing stalemates.
- Existing audit synthesis says this is primarily a teaching/setup problem, not proof that the combat system lacks depth.
- The current opener surfaces defender stacking before it surfaces viable French preparation lines.

**Root-cause notes**

- The likely first-hour attack line (`Ney` into `Wellington`) presents stacked defensive advantages before the game teaches the counters.
- The old coordination preview is gone, and the first-time coordination tutorial only fires after the player already achieves combined arms.
- The existing bombardment advisory fires only after the player already used artillery correctly.
- This makes the current problem a teaching/order-of-information failure first. Narrow numeric tuning is the fallback only if guidance plus setup still leave the opener feeling hopeless.

**Exact code surfaces**

- `backend/game_logic/combat.py` - modifier surfacing and common-opener outcome messaging.
- `backend/commands/combat_executor.py` - first-time coordination tutorial, bombardment advisory, and any added opener guidance on the attack flow.
- `backend/models/marshal.py` and region/terrain data only if number tuning is still required after surfacing fixes.
- Any tutorial, advisory, dispatch, or wizard surface used to expose the better line.

**Exact failure modes**

- The naive `Ney, attack Wellington` line produces a punishing result before the player is told about bombardment, combined arms, or defender terrain advantages.
- The game teaches combined arms only after success instead of before commitment.
- The post-bombardment advisory is useful but arrives too late to teach the player what to try first.

**Edge cases / sibling failure scan**

- If `Drouot` is unavailable, advice should still surface a non-artillery preparation line rather than naming an impossible move.
- The added guidance should target the common first-hour opener, not spam every later battle.
- Prepared assaults should improve the outcome materially without making all direct attacks trivially safe.

**State-transition risks**

- Guidance added only after the battle result may still be too late if the first failed assault already ends the campaign.
- Broad stat nerfs or buffs could mask the teaching failure while flattening later combat depth.

**Backend / frontend contract risks**

- Reuse existing advisory, objection, tutorial, or result surfaces; this item does not need a new UI system.
- If the advice is conditional, the trigger conditions must stay deterministic enough for regression coverage.

**Acceptance criteria**

- At least one obvious early French preparation line is surfaced as materially better than the naive direct assault.
- The game exposes the key counters behind the Wellington opener before or at the point the player is likely to commit.
- The prepared line is measurably better in the deterministic regression scenario than the naive line.
- Combat depth stays intact; this item does not flatten the system into guaranteed attack wins.

**Regression test matrix**

- Add a deterministic scenario test for the common opener and one prepared alternative.
- If guidance is added to objections, dispatch, or preview text, add a regression that the surfaced advice names the relevant counterplay.
- If narrow number tuning is required, add a regression proving the prepared line improves while the naive unsupported line is still risky.

**Dependencies / blockers**

- No hard code dependency.
- Intentionally sequenced after Sessions 1-3 so crash/defeat/diplomacy noise does not contaminate first-hour tuning.

**Implementation order inside Session 4**

1. Add or restore pre-commit guidance on the common opener attack path.
2. Reuse the existing tutorial/advisory surfaces instead of adding new UI.
3. Build a deterministic naive-vs-prepared comparison test.
4. Only if guidance still leaves the opener hopeless, apply narrow opener-specific tuning and capture it in tests.

---

### PL-29: No supported new-game / restart endpoint

**Status:** FIXED (April 12, 2026).

**Problem statement**

The player still has no clean restart path from the running build. Starting fresh requires server restarts and sometimes manual autosave cleanup.

**Confirmed evidence**

- No formal `POST /new_game` implementation exists in the live backend route set.
- The client pause flow exposes save/load only.
- Existing tests already call `/new_game` indirectly without making it a real supported contract.

**Root-cause notes**

- The backend world is initialized at startup only; there is no reset helper and no restart endpoint.
- The frontend already has save/load wiring, but the pause menu and API client never expose a restart path.
- The pause menu also needs an explicit destructive-action confirmation so one misclick does not immediately replace the current autosave.
- Local client reset logic already exists in the load flow and should be reused instead of inventing a second partial reset path.
- The test suite already assumes `/new_game` exists, so the current state is a direct contract contradiction rather than a speculative feature request.

**Exact code surfaces**

- `backend/main.py` - new-game endpoint wiring and world reset.
- `backend/save_manager.py` - explicit autosave reset/retention behavior.
- `godot-client/project-sovereign/scripts/api_client.gd` - client call.
- `godot-client/project-sovereign/scripts/pause_menu.gd` and `godot-client/project-sovereign/scripts/main.gd` - pause-menu button and UI refresh.

**Exact failure modes**

- Starting fresh requires a process restart and can inherit stale autosave state.
- Existing tests can call `/new_game` even though the route is not supported.
- Frontend local state such as pending popups, dialogue state, or cached world data can leak across a manual restart unless the reset path is centralized.

**Edge cases / sibling failure scan**

- Restart immediately after unsaved play.
- Restart after a manual save/load round trip.
- Restart while popups or dialogues are active.
- Manual saves must remain intact.
- Autosave from the previous campaign must not resurrect stale state after restart.

**State-transition risks**

- Resetting the world must also reset dialogue/mailbox state, notifications, eliminated nations, and any singleton references kept by `backend/main.py`.
- The client must clear local popup/dialogue caches before hydrating the fresh world response.
- Restart and load should share as much UI reset code as possible to avoid parallel bugs.

**Backend / frontend contract risks**

- `/new_game` should return the same kind of hydrated response shape the client already knows how to consume.
- Autosave behavior must be explicit. For the current fix phase, write a fresh autosave immediately after creating the new world so stale autosave state cannot be restored by accident.

**Acceptance criteria**

- `POST /new_game` returns a fresh world state without restarting the process.
- The fresh world is equivalent to a new campaign start: starting regions and marshals restored, `current_turn` reset, no pending diplomacy/dialogue carry-over, eliminated nations cleared.
- Autosave handling on new game is explicit and consistent, and stale autosave state cannot resurrect the previous campaign.
- The pause menu exposes restart/new game and returns the player to a fresh turn-one state.
- The pause menu requires explicit confirmation before restart/autosave replacement.
- Manual saves are preserved.

**Regression test matrix**

- Add formal endpoint coverage in `tests/test_endpoint_wiring.py` or equivalent.
- Add save/load interaction coverage so new-game does not accidentally reload stale autosave state.
- Add a client smoke or manual verification for the pause-menu flow if no Godot harness exists.
- Update or retain the existing `/new_game`-using tests so they now exercise a supported contract instead of an accidental assumption.

**Dependencies / blockers**

- No upstream blocker.
- Keep last in the fix phase because it is QoL, not game-truth or contract-critical.

**Implementation order inside Session 5**

1. Extract a backend world-reset helper that can be used at startup and by `/new_game`.
2. Implement `POST /new_game` and return a fully hydrated fresh-world response.
3. Persist a fresh autosave immediately after reset.
4. Reuse the frontend load-reset path for new-game hydration, then expose the action in the pause menu.
5. Add endpoint, autosave, and pause-flow regression coverage.

---

## Open Judgment Points

- `PL-30`: the exact null object in the crash stack should still be confirmed if the repro is rerun, but the implementation should harden both wizard render paths now rather than waiting on another trace.
- `PL-26`: if pre-commit guidance plus prepared-line verification still leaves the opener reading as hopeless, approve the narrow numeric tuning inside this item; do not jump straight to broad combat rebalance.

---

## FIXED (July 3, 2026 — CR-0): Parser roster pinning — 5 of 7 French marshals uncommandable by typed text on the shipped 1805 boot (ALL LLM modes)

**Owner: `docs/COMMAND_ROBUSTNESS_SPEC.md` CR-0 — LANDED July 3, 2026.**
Parser rosters now derive from the live world: `parser.py`
`_get_player_marshals(world)` / `_get_known_regions(world)` (hardcoded
legacy lists survive only as the no-world cold-parse fallback);
`llm_client.py` `_parse_with_mock` takes `game_state` and derives marshal
extraction, the target ladder (enemies → regions, camelCase-split aliases
so "archduke charles" finds `ArchdukeCharles`), and nation-keyed vassal
keywords. Also fixed while there: the `Marshal [Name]` regex was
case-sensitive on "marshal" (so "Marshal Soult" never matched); exact
enemy names were fuzzy-rewritten into regions on the 126-province map
("Mack" → "La Mancha"); trailing punctuation broke the word-scan skip
list ("Bernadotte," fuzzy-drifted into region "Bern"); and typed vassal
commands ("invest in saxony") died at the marshal word-scan in EVERY
world — probe-verified pre-existing, now parsing in both. The landing ran
a 4-lens adversarial review (24 confirmed findings, all fixed or pinned —
see the STATUS.md July 3 third entry for the full list incl. the
"Attack Marshal Mack" / "Hold Bern!" / "invest in austria"→Asturias
regressions caught pre-commit). Behavior tests over both worlds:
`tests/test_command_robustness_cr0_parser_rosters.py` (66 tests). The
meta-action silent-marshal-drop class ("Murat, charge") and
unknown-extra-word hard errors remain CR-2 scope.

Originally recorded (Map Slice 8 smoke, July 2, 2026) as the low-severity
mock-only bare-command gap below. The July 2 re-staging audit probe
**disproved the "dev-mode only" framing for marshal-name commands**:

- `parser.py:56` hardcodes `valid_marshals` to the legacy 4 (Ney, Davout,
  Grouchy, Drouot); the mock parser's player-marshal extraction matches
  (`llm_client.py:610-615`). On the shipped `europe_1805.json` boot,
  **"Soult, attack Mack" / "Marshal Soult, attack Mack" / "Lannes, move to
  Swabia" / "Massena, hold Milan" all FAIL in every LLM mode** with
  "Marshal not found — Available: Davout, Drouot, Grouchy" (suggesting
  marshals absent from the 1805 world).
- The failure is invisible to the LLM safety net: the fast parser awards
  0.8 confidence for any recognized action verb (≥ the 0.7 LLM-fallback
  threshold, `llm_client.py:48/:210`), so the LLM is never consulted before
  `_apply_fuzzy_matching` (`parser.py:216-272`) hard-errors.
- Related same-owner gaps: `known_regions` derives from legacy
  `REGIONS_DATA` (19 names on a 126-province map — no typo correction for
  Europe provinces); the mock target-extraction ladder is legacy-hardcoded
  (`llm_client.py:857-911`); meta-actions skip marshal matching so
  "Murat, charge" silently drops the addressee (`parser.py:209`).
- The ORIGINAL entry (kept for lineage): with `LLM_MODE=mock`, bare
  marshal-less commands on Europe names ("scout Swabia", "move to
  Flanders") fail target extraction and fall to Berthier recovery instead
  of `auto_assign_scout`; "Ney, scout Swabia" parses but drops
  `target=None` in mock mode. Graceful (no crash), but the in-game help
  advertises these forms.

Fix direction (CR-0): derive parser rosters from the live world (mirror
`_get_known_enemies(world)` and the E-1 both-roster precedent), regions
from `world.regions`, mock ladder from game_state.

---

## FIXED (July 4, 2026 — EC-0): advance-turn AP reset uses the legacy nation builder

**Owner: `docs/ECONOMY_REVISIT_SPEC.md` EC-0.** ✅ LANDED.

`world_state.py`'s `advance_turn` reset `nation_actions` from
`build_default_nation_actions` (legacy 4-nation builder) regardless of
`sovereign_map`. On the shipped Europe world this squashed **Austria 4 → 3
after turn 1** (nullifying the approved 1805 pre-slice item-8 tuning) and
never reset the 15 Europe-only nations (Naples/Bavaria/Ottoman/…), so their
`ap_per_turn` treaty penalties **compounded permanently**. **Fix:** the
constructor snapshots the world's OWN base AP into `base_nation_actions`
(world-scoped by construction, like `_starting_controllers`; serialized;
from_dict defaults to the loaded `nation_actions` for fresh scenarios +
pre-fix saves), and `advance_turn` resets from that snapshot. Now Europe
Austria holds 4 across turns and every Europe-only nation's penalty
applies-then-releases each turn. Legacy Austria stays 3 (unchanged). No
Slice-8 balance pin moved in the suite; the *prose* verdicts touching
Austrian tempo were measured at 3 AP and now run at the intended 4 — a note
for the next balance pass, not a test fix. Tests:
`tests/test_economy_ec0_ap_reset.py`.

---

## FIXED (July 4, 2026 — MC-0): marshal-overview ability display shows "None" as an active ability

**Owner: `docs/MARSHAL_CONTENT_PASS_SPEC.md` MC-0.** ✅ LANDED.

`marshal_overview._build_ability` gated on marshal NAME only, so
scenario-authored 1805 Ney/Davout — who boot with `ability={"name":
"None"}` via `create_marshal_from_data` — reported `ability_active=True`
with ability name "None" in the management screen. **Fix:** the gate now
also requires a real ability name (`name not in ("", "None")`), so 1805
marshals correctly report no active ability — matching the mechanics (the
combat wiring keys off the ability name too, so no name = no effect). Legacy
marshals with genuine wired abilities (Ney's Bravest of the Brave, Davout's
Counter-Punch Mastery, Drouot's Sage of the Grand Army) still display. The
content half (authoring abilities for the 1805 roster) remains the gated
MC-1. Tests: `tests/test_marshal_content_mc0_ability_display.py`.

---

## Fixed Bug Archive

28 bugs fixed across playtest Sessions 1-12 and Sessions A-C.

| ID | Summary | Fixed In |
|----|---------|----------|
| PL-1 to PL-4 | Early combat/display bugs | Sessions 1-6 |
| PL-5 | Proposal race condition plus no feedback popup | Sessions 7-8 |
| PL-6 | "Harsher" terms on friendship pacts demanded territory | Session 7 |
| PL-7 | Counter-offer accept/reject missing AI cooldowns | Session 7 |
| PL-8 | Counter-offer popup looked like an unsolicited AI proposal | Session 9 |
| PL-9 | Acceptance mismatch between display and resolution | Session 10 |
| PL-10 | "More generous" downgraded proposal type | Session 10 |
| PL-11 | Incoming AI proposals hijacked player diplomatic commands (API-only) | Session 10 |
| PL-12 | Harsher terms increased acceptance estimate | Session 11 |
| PL-13 | Viable proposal falsely rejected as surpassed | Session 11 |
| PL-14 | Ultimatum delivery reworked into a conversational diplomacy tool | Session 12 |
| PL-15 | Ultimatum demand wizard replaced blind escalation | Session A |
| PL-16 | Harsher-demand multiplier retuned | Session A |
| PL-17 | Manpower demand zero-penalty bug absorbed into PL-18 | Session A |
| PL-18 | Typed manpower demands plus `DEMAND_VALUES` key fixes | Session A |
| PL-19 | Dynamic ultimatum relation penalty | Session B |
| PL-20 | Territory cost scaling plus elimination guards | Session B |
| PL-21 | Phantom `connections` attribute | Fixed in code |
| PL-22 | Phantom `income` attribute | Fixed in code |
| PL-23 | Authority-driven pushback, pen nudge, trust removal | Session C |
| PL-24 | Harshness scoring for all demand types | Session C |
| PL-25 | Term novelty: jitter, personality nudge, desire bias, flavor | Session C |
