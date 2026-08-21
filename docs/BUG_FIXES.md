# Bug Fixes

> Broken-now implementation document.
> Treat the current findings as frozen truth until the open items below are fixed.
>
> Last Updated: August 21, 2026 (**WO section EXTENDED — rows WO-17..WO-32 from
> the spec-authoring session's defect hunt, incl. three hand-verified new P1s:
> WO-17 the direction-less WIN-D3 evacuation corridor, WO-21 the objection
> channel's free-trust + dead cancel arm, WO-22 auto-end-turn crossing an
> unanswered capture — plus WO-32 (P1, owned by PC15-10). Build contract for
> the whole WO row = `docs/WEIRD_OUTCOMES_SPEC.md`.**) Prior: August 16, 2026
> (**Weird-Outcomes Playtest (WO) section added — 16
> game rows + 3 harness rows, ALL OPEN** (report-only session): 3 game P1s ⛔ — the
> enemy-name addressee executing on your own army, the parser rewriting an unknown
> place into a real one and marching there, and a detachment garrison that can
> never fall — plus a harness P1 that reports campaigns which never happened.
> Verified by a 40-agent find-then-refute fleet: 21 CONFIRMED, 5 REFUTED, 4
> ALREADY_FILED. Memo: `docs/audits/PLAYTEST_WEIRD_OUTCOMES_2026_08_16.md`.)
>
> Last Updated: August 15, 2026 (**Comprehensive Playtest PC15 section added — 18
> game rows + 1 harness row, ALL OPEN** (report-only session): 4 P1 ⛔ Round-0
> gates (silent marshal destruction · the interrupt route swallowing addressed
> commands · the settlement confirm wedge · dead-name silent substitution), the
> neutral-soil family, and the measured petition-firehose number for CA9-D3.
> Memo: `docs/audits/PLAYTEST_COMPREHENSIVE_2026_08_15.md`.)
>
> Last Updated: August 1, 2026, second session (**Live-Playthrough Aug-1 section CLOSED**
> — the 2 routed rows PT-F1 + PT-F6 FIXED under the user's delegated grant, alongside the
> four PT-D design items; the section's 10 defects are now 10/10 FIXED. This session's
> tests: `test_neutral_soil_pursuit_capture.py` (7), `test_ai_square_thrash.py` (6),
> `test_enemy_phase_presentation.py` (13), diorama/digest extensions. Prior session:
> 8 FIXED with pins (`tests/test_playthrough_fixes_2026_08_01.py`, 12). Record:
> `docs/audits/AI_V_SWEEP_2026_08_01.md` §10 + `docs/STATUS.md` top entry.)
>
> Last Updated: July 18, 2026 (**July-18 Playtest Sweep section added — ALL 25 rows FIXED**:
> the two user-reported issues ("give them hell" did nothing; the settle-a-war window ran off
> the screen) plus their families, found by a 34-agent find→verify workflow and hardened by a
> 50-agent pre-commit review that caught a P1 regression before it shipped. Record:
> `docs/STATUS.md` top entry.)
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


## Weird-Outcomes Playtest (WO) — filed August 16, 2026; **EXTENDED August 21, 2026** (WO-17..WO-32 from the spec-authoring session's defect hunt; **build contract = `docs/WEIRD_OUTCOMES_SPEC.md`**; ALL OPEN)

> **Evidence memo = `docs/audits/PLAYTEST_WEIRD_OUTCOMES_2026_08_16.md`
> (authoritative).** Ten scripted campaigns, ~290 turns, each built to push a
> DIFFERENT system past its designed shape rather than to win — a pacifist, a
> deliberate attempt to lose Napoleon, a tyrant, a kingmaker, a merchant, an
> admiral, a parser-torture arm, France at war with all Europe, 45 idle turns,
> and one arm on the live Anthropic parser. Scripts:
> `tools/playtest_scripts/weird_*.json`; digests under
> `tools/playtest_runs/weird-*/` on the dev machine.
>
> **Method note worth keeping:** a 40-agent find-then-refute fleet verified every
> candidate against the code — **21 CONFIRMED, 5 REFUTED, 4 ALREADY_FILED** —
> and it killed five of the session's own candidates plus one of its headlines
> (WO-H1 below). Rows here are code-traced and reproduced, not observed.
>
> **The through-line is the one the NPC cluster closed one commit earlier, at a
> different altitude:** *the player names a thing and the game acts on something
> else* — and this time it EXECUTES rather than misreporting. WO-1 and WO-2 are
> the same defect on two different name registers.

> ### ✅ RE-VERIFIED against master `24a59ed` by WO-EVAL, August 17, 2026 — **`docs/audits/WO_EVAL_2026_08_17.md` §4 is authoritative where it amends these rows.**
>
> **All four P1s and all three harness rows still reproduce.** Suite measured
> **18,178 passed / 3 skipped** (the 18,175 above is stale). Amendments:
>
> - **WO-1 is WORSE than filed** — `Kutuzov, retreat` moves **8 corps including
>   Napoleon**, and **`Kutuzov retreat` with no comma is byte-identical**, so a
>   guard on the leading *addressed* token cannot close it. `Kutuzov, scout
>   Swabia` makes **Soult** scout.
> - **WO-2's filed seam is CORRECT** (a claim that it was misfiled was traced and
>   killed) — but `executor.py:301` is a live **backstop**: gate the parser alone
>   and `move to the Moon` marches **10 provinces to Morocco**. Gate both.
> - **WO-3 fix measured**: `garrison_losses >= 1` collapses the garrison at
>   assault 13. Left alone it is 49 attackers lost by assault 500, garrison still
>   1 at assault 2,000.
> - **WO-13's count is wrong** — **30** boot-live pairs across all nations, not
>   197 (3 from France's view). The real severity argument is that **the ambient
>   AI hits it 17× in 40 turns**. Two more ungated seams found: `executor.py:370`
>   absorbs 16 of 17 when `:433` is gated, and `:230`. **`Brunswick` is both a
>   province and a Prussian marshal at score 100 — an uncloseable exact
>   collision**, so `_plausible_name_typo` cannot be the whole fix.
> - **WO-H3 is a P1, not a P2** — the estate stage is answered `"plunder"`, the
>   executor refuses **without clearing**, and every later command for the rest of
>   the campaign returns *"You must decide the fate of…"*. It is **indivisible
>   with WO-H1**: fixing H1 alone took a run from `completed` at 31 commands to
>   `blocked` at 24.
> - **THREE MORE HARNESS BLIND SPOTS, all P1 for evaluation integrity:** the
>   driver never reads `response["state"]` (blind to **every**
>   `awaiting_clarification` question — this is the whole of WO-D3's measured
>   failure); never reads `envoy_digest` (truthy **134/202**; the Kingmaker arm
>   was offered 22 letters and answered 0); and **never seeds the module RNG**
>   while 20 backend modules use `random` — so the same script at the same seed
>   ends at **30 / 28 / 27** provinces. `tools/playtest_runs/` is also gitignored,
>   so every digest these rows cite is a local artifact.
> - **WO-6 is wider than filed** — overruling the resulting WAIT objection with
>   `trust` made **Ney charge into Swabia**; its `hold on` table row did **not**
>   reproduce end to end.
> - **WO-16's row body repeats a disproved example** — that turn's ledger reads
>   `provinces 29 (+1)`; no vassal defected and no homeland province fell. The
>   corrected charge is at least as damning: a 26-man skirmish beat `region_taken`
>   and `victory_won` on the turn France stormed and sacked a province. WO-16 also
>   now owns the `own_mauled` absolute floor as a **conscious re-open** of the
>   playtest's own killed claim #4.
> - **WO-11 is folded into WO-D6's slice** — after a `capital_lost` split, the
>   direction-blind guard would fire the game's most ceremonial sentence on the
>   morning an **ally liberated Paris for you**.

> ### ✅ SPEC AUTHORED + THIRD VERIFICATION August 21, 2026 — **build contract = `docs/WEIRD_OUTCOMES_SPEC.md`, AUTHORITATIVE for every row's fix design.**
>
> Every seam re-verified at master `bd0be0c` (six-agent read-only pass + hand
> checks; spec §2 is the record). **Five material corrections to the rows
> above:** (1) **WO-1's seam is `parser.py:688-702` + `:1575-1576`** — the
> CR-1 enemy-name demotion (`llm_result["marshal"] = None` at `:700`) followed
> by the marshal-less classification; the filed `executor.py:1794-1805` is
> only the routing hop. (2) **WO-5's story splits:** bare `sue for peace` /
> `make peace` hit the honest FINAL-21 target ask (`llm_client.py:2041`), and
> the *"against which nation shall we declare war?"* line is reached because
> **"end the war ON any terms" contains the war keyword `"war on "`**
> (`llm_client.py:1018`, checked before the proposal keywords) — a peace
> request parsing as a war declaration via a three-word substring. (3)
> **WO-H3 precision:** the driver DOES answer a bare-`True` capture prompt
> (posts `/capture_choice`); what it loses is the sibling `capture_data`
> (stage / `dialogue_id` / detail) — which is exactly what makes the ESTATE
> stage unanswerable. (4) The typo gate has **four** sibling application
> sites, not three. (5) `home_captured` is no longer the weight ceiling —
> **`sovereign_captured: 101`** (NP-4) sits above it, and WO-D6's
> `capital_lost` slice must preserve that ordering.
>
> **The same session's defect hunt filed SIXTEEN new rows (WO-17..WO-32,
> below) — three hand-verified P1s** (WO-17 the direction-less WIN-D3
> corridor; WO-21 the objection channel's free-trust + dead cancel arm;
> WO-22 the auto-end-turn crossing an unanswered capture) plus the P1 WO-32,
> owned by PC15-10. Fix designs = spec §3 slices 13–17; the hunt's CLEAN
> verdicts (bankruptcy priced, DP non-accumulating, no vassal-autonomy
> arbitrage, glory farming excluded, doomstack capped…) are recorded in spec
> §4 so nobody re-hunts them.

| # | Sev | Finding | Seam | Status |
|---|---|---|---|---|
| **WO-1** ⛔ | **P1** | **Naming an ENEMY marshal executes the order on the FRENCH army.** `Kutuzov, retreat` → *"General retreat ordered! Ney falling back! Davout falling back!…"* and it executes — every French corps changes province, Massena Milan→Munich **losing 2,100 men**. Identical for `Mack, retreat` / `Buxhowden, retreat` / `Moore, retreat`, and byte-identical to the bare word `retreat`. `Mack, attack Vienna` sends the whole army at **Swabia**; `Kutuzov, defend` puts every corps on the defensive. **The guard exists and works for names the game does NOT know** (`Zorblax, retreat` → *"There is no Marshal 'Zorblax' in the order of battle"*); it fails for known names belonging to the enemy — the addressee is recognised, stripped, and the command degrades to its bare army-wide form. Verbs with no bare form (`fortify`/`drill`/`wait`/`form square`) correctly ask *"Which marshal, Sire?"* | the pre-parse addressee guard — the third member of the family **PC15-4** opened (invented names guarded; fallen names guarded in the PC15 slice; **enemy names not**) | **OPEN** |
| **WO-2** ⛔ | **P1** | **The parser rewrites an unknown target into a real place and the executor marches there.** `Ney, move to Avalon` → *"Ney begins marching to **Leon** (distance: 8). Route: Lorraine → Orleanais → Burgundy → Limousin → Gascony → Bordelais → Galicia → Leon."* — a 2-AP standing order across eight provinces into Spain, no confirm, no did-you-mean, and the word *Avalon* never appears. Partial-ratio junk auto-corrects at 75: `Moon→Moore`, `Troy→Deroy`, `Mars→Damas`, `Hell→Hohenlohe`, `Eden→Buxhowden`, `Avalon→Leon`. Runs in the AI direction too — **Britain spent 13 consecutive turns ordering two field armies to take an adjacent province and being told it was 8 provinces away**, because the province name resolved to a French marshal. | `parser.py:983` + `:985` — the two **ungated** `auto_correct` arms of the target precedence ladder (sibling gap at `:1421`). The project already owns the gate: `parser._plausible_name_typo` (`:349`), applied to three sibling arms whose comments name this same failure. ⚠ **this disproves NPC-7's "its three siblings are gated" claim — correct that row** | **OPEN** |
| **WO-3** ⛔ | **P1** | **A detachment garrison stalls at one man, forever.** Garrison losses are floored at `int(garrison × 0.10)`, which truncates to **0** below ten men, while the attacker keeps paying a 2% floor; a detachment collapses only at `<= 0`. Sequence: `3000 → 1500 → 750 → … → 3 → 2 → 1 → 1 → 1 …`. Measured: *"Wellington assaults the Normandy garrison! Garrison: 1 → 1 (-0). Wellington loses 364 troops. Garrison holds — 1 defenders remain."* — 40 assaults, no collapse, attacker 40,000 → 17,843. **This is the terminal state of EVERY detachment garrison** (`_execute_garrison` places exactly 3,000; the 0.50 cap halves it each assault), not an exotic state. Seen in the wild: a Bavarian marshal spent **21 consecutive assaults and 10,152 men** on a garrison that could never fall. | `combat_executor.py:2697` (the truncated floor) paired with `:2715` (detachment collapse requires `<= 0`); amplified by `enemy_ai.py:3537` (P4.25 has no futility guard) and `:1220` (the futility tracker reads `type == "battle"`, which a garrison hold never emits) | **OPEN** |
| **WO-4** | P2 | **A player who only types cannot declare war at all.** After the war purpose is answered, Talleyrand's objection is live in the response as `diplomatic_objection`, but typing `proceed` answers *"Berthier: There is no pending diplomatic matter to respond to, Sire."* Every following answer (`confirm`/`1`/`yes`) bounces off the generic fallback; France stays at PEACE and **is never told the declaration was abandoned**. Verified against Prussia, Bavaria and Saxony. The popup channel (what the Godot client uses) works — it is the typed route that dead-ends, which is the route the game advertises in its own error text (*"For diplomacy: 'declare war on Prussia'"*). | the typed dialogue router vs the `diplomatic_objection` popup key | **OPEN** |
| **WO-5** | P2 | **"End the war on any terms" offers to start one.** → *"Sire, against which nation shall we declare war? Specify: Britain, Prussia, Austria, or Saxony."* Reproduces in **mock** mode, so it is the fast parser, not the LLM. Answering with a nation declares **nothing** (checked — it falls through to the generic shrug), so no destructive action is reachable; the player is told to specify and then punished for specifying. The reason it is P2: of nine natural ways to ask for a war to stop, **one works** — `peace with Britain` ✅; `sue for peace` / `make peace` ask which nation; `end the war`, `end this war`, `stop the war`, `I want peace`, `end the war with Britain` all return *"I cannot interpret that order."* | fast-parser action routing | **OPEN** |
| **WO-6** | P2 | **A leading English filler outranks the real verb and never escalates.** `no wait, Ney, retreat` issues **WAIT** at confidence 0.8 and reports success — the bare `"wait" in command_lower` / `"stand by"` substring test is sited ABOVE retreat/move/scout/build/restrain/drill in the `elif` chain. | `llm_client.py:1313` | **OPEN** |
| **WO-7** | P2 | **A pending soft-stop dialogue walls off all three parse-failure recovery arms** — PARSE-NEG's honest refusal and CR-2's did-you-mean are replaced by an unrelated "no marshal named" shrug. This is the cause of most of the *"I cannot make sense of this"* noise in the Kingmaker arm, and it made an identical typed command appear non-deterministic. | `main.py:2594` — the `else:` enclosing the CR-2 clarification (`:2660`), the PARSE-NEG refusal (`:2685`) and the Berthier recovery (`:2749`) | **OPEN** |
| **WO-8** | P2 | **Vassal courting has no per-vassal cap.** All 19 AI courts fire on ONE satellite in a single tick — including **the vassal courting itself** and its lord's other satellites — for −95 loyalty, after which the rebellion-imminent modal is raised for a war that has already started. Both throttles are keyed per-COURTIER (`court\|{nation}\|{vassal}` cooldown; the `break` is per-call), never per-TARGET. | `vassal.py:1976-2040` (loop head `:1977`, per-nation `break` `:2038`), driven by `turn_manager.py:525-528` | **OPEN** |
| **WO-9** | P2 | **An AI capture of the player's own province via the `attack` verb is dropped from the enemy-phase report.** PT-E5's own-soil carve-out keys on `captured_from`, which only the MOVE producer stamps; both `conquest` producers in the combat executor omit it although `old_controller` is live three lines above each. This is why provinces vanished from the digests with no line — a fog-shaped hole in the report, against PT-E5's own recorded ruling that these must be shown. | `main.py:1734` vs `combat_executor.py:2806` + `:4698` | **OPEN** |
| **WO-10** | P2 | **The briefing reports enemy strength at 2% of French forces when the true at-war total is 107%**, and the same screen leaks Britain's *unscouted* exact national aggregate as "51,238 men". Two seams: the ratio sentence is rendered unqualified although the estimator's own docstring records deliberate under-estimation as the cost of poor intelligence; and `_format_army_strength` has no LAST_KNOWN branch, falling through to the FULL exact-aggregate return. | `dispatch.py:2152` + `:2226` · `diplomatic_ledger.py:183-203` | **OPEN** |
| **WO-11** | P2 | **`home_captured` (weight 100) is direction-blind** — it fires whenever ANY non-French power takes a French homeland province, **including an ALLY liberating it from a third party**, while its own sibling arm two lines below correctly requires France to have been the loser. | `dispatch.py:432-434` (guard); contrast `:435` | **OPEN** |
| **WO-12** | P2 | **The under-capacity concentration tax is reported as starvation.** A corps at 18.1% of Paris's capacity reads *"Starving — supply has failed at Hungary 6 turns running."* The death-ball stacking penalty falls into the same event builder as genuine over-capacity attrition and narrates with its words. | `world_state.py:6233-6235` (branch), message at `:6249-6258`; second surface `dispatch.py:1587` | **OPEN** |
| **WO-13** | P2 | **A province name silently resolves to an enemy marshal** — `_fuzzy_match_enemy` runs FIRST and auto-corrects with no typo gate; 197 boot-live collapses, executing on both sides. Same class as WO-2, a different matcher. | `executor.py:433` (ungated `match_with_context` → `auto_correct`), reached from `combat_executor.py:4224-4249` | **OPEN** |
| **WO-14** | P2 | **The blockade order names the one court it cannot pin** and promises a drill the blockaded fleet can never get. The "currently:" set is *at-war courts with any naval row*, computed before the posture's effect and never compared against `blockaded_nations`. | `naval_executor.py:107-115`; `naval.py:1276-1280` | **OPEN** |
| **WO-15** | P3 | **A captured marshal is labelled "(dead)"** in the player-facing recruit refusal — contradicting the honest prisoner refusal the same world gives for the same man (a prisoner is a strength-0 marshal who stays in `world.marshals`; `destroy_marshal` explicitly refuses prisoners). | `world_state.py:4908` | **OPEN** |
| **WO-16** | P3 | **"Mauled" prints a number that contradicts it.** *"Sire — Ney was mauled at Bohemia: 29 men lost in a single action."* The predicate is proportional and CORRECT (`casualties >= 0.25 × pre`, Ney was at ~87 men) — the sentence publishes the absolute figure, which reads as trivial, and withholds the proportion that earned the word. It also led the briefing on a turn a vassal defected, a homeland province fell, and the army was at 24% of boot strength. | `dispatch.py:255` (template) + `:666` (predicate) | **OPEN** |
| **WO-H1** ⛔ | **P1** (harness) | **The playtest driver reports campaigns that never happened.** The World Burns arm ran **fifteen complete declare-war ceremonies** and declared war on **ZERO** nations; every one is logged as a success. The ally-entry review's options carry `action` keys and no `id`, so `_option_id` returns `None` for all, `find()` cannot match, and the arm falls back to the literal `"confirm"` — a word whose keyword list does not include the ally-entry actions. `1`, `proceed`, `ally_entry_proceed_without` and `Proceed Without Allies` **all declare the war**. ⚠ **The BACKEND IS CORRECT here** — this session first filed it as a game inconsistency and that reading is struck. ⚠ **It also falsifies the recorded refutation** in §Napoleon Campaign harness rows calling `_option_id`'s blindness *"causally inert"* on `proposal_confirm` — proven load-bearing by experiment. | `tools/playtest_driver.py:449-451` (`_option_id`), fallback `:120` + `:659-660`, blind chain `:726-730` | **OPEN** |
| **WO-H2** | P2 (harness) | **The `battles` counter reads 0 for a campaign the world logged 12 battles in.** The driver counts only top-level `response["battle_report"]` (`:519`) while autonomous jealousy attacks ship on `result["jealousy_attacks"]` (`turn_manager.py:405`) — a key it never reads. The Pacifist arm's centrepiece (11 autonomous attacks, 12 battles) was structurally invisible to its own digest. | `playtest_driver.py:519` | **OPEN** |
| **WO-H3** | P2 (harness) | **`pending_capture_choice` arrives as a bare `True`**, so `_as_dict(response["pending_capture_choice"])` yields nothing and the capture payload is unreachable — the third known-bad-digest class, and **not yet in `docs/PLAYTESTING.md`**. Add all three (WO-H1/H2/H3) to that document's *Known-bad digests* section. *(Aug 21 precision: the driver still POSTS an answer — what it loses is the sibling `capture_data` with stage/`dialogue_id`/detail, which is what wedges the estate stage.)* | `playtest_driver.py:569-579`; `main.py:3413-3415` ships the detail on `capture_data` | **OPEN** |
| **WO-17** ⛔ | **P1** | **"The Trojan Corridor" — the WIN-D3 evacuation grant is pair-scoped and direction-less** (hand-verified): `has_evacuation_grant` is a bare `(pair_key → expiry)` compare consumed by the ONE `can_enter_territory` arm — no marshal, no direction, no stranded check — and it opens on ANY WAR→non-WAR edge **including ARMISTICE**. Park one corps deep on enemy soil (depth sets duration, cap 12 turns), sign a 1-DP armistice, march FRESH corps INTO enemy sovereign territory all truce long (walked-in corps register "stranded" and HOLD the corridor open), let the armistice collapse — war auto-resumes free — with the army beside Vienna. The enemy legally cannot contest (attack gates on `is_at_war`). Player-exclusive in practice: the AI's only consumer (P1.2) walks home. Compounding: the player has NO truce floor (`PAIR_EXIT_TRUCE_FLOOR_TURNS` skips player pairs; leaving ARMISTICE pops the 5-turn hold). | `withdrawal.py:133-149` + `diplomacy.py:9452-9455` (permission), `:2815-2817` (creation), `:2839-2845` (cooldown pop), `settlement_third_party.py:453` (player skip) | **OPEN — spec slice 13** |
| **WO-18** | P2 | **Pension churn: pay the rente one turn in three, never erode.** The bill reads the LIVE pension at income time; the erosion reconcile fully resets the grace clock on any met turn; neither grant nor revoke carries churn memory — grant/revoke/revoke/regrant pays `ceil(1.5×face)` on one turn of three with zero trust bleed, while the revoke copy promises erosion "after its grace expires." | `world_state.py:5376-5379` (bill), `:5908-5946` (reconcile), `economy_executor.py:1174-1373` (no memory) | **OPEN — spec slice 14** |
| **WO-19** | P2 | **The repeat-sack guard re-arms on any change of hands.** `plunder_yield`'s docstring promises the flag holds until stability >50 / ≥9 unguarded turns, but three sites clear `region.plundered` in ONE turn on any hand-change (secure, AI-secure, own-soil recapture) — abandon a sacked province, let the AI secure it, retake it, and the prompt quotes the FULL `income×4` again. IGR-X6 covered only re-sack while the flag stands. | `combat_executor.py:7639-7643`, `world_state.py:3966-3969`, `:3928-3933` vs the documented clear `:6122-6123` | **OPEN — spec slice 14** |
| **WO-20** | P2 | **"break the alliance with Austria" PROPOSES an alliance** — `_break_keywords` are treaty-phrasings only, so the addressed form falls into the proposal arm and `extract_proposal_type` reads "alliance" as the thing to CREATE. One-line hardening (`break alliance`/`end the alliance` into `_break_keywords`); the G1 redirect covers the player surface. | `llm_client.py:1003-1008` | **OPEN — spec slice 11** |
| **WO-21** ⛔ | **P1** | **The strategic-objection trust arm pays trust for nothing, and the SUPPORT-cancel arm is dead** (hand-verified): `modify_trust(v2_trust_gain)` fires BEFORE the `preferred_action` existence check (the bail returns success=False, cost 0 — trust kept), and the relationship-SUPPORT objection's trust option carries `"action": "cancel"`, an id the post-objection dispatch has no arm for → *"Unknown action: cancel"*, AP uncharged, the SUPPORT order still standing. +2..+12 trust per press, repeatable. | `strategic_executor.py:1627-1635` (credit-before-check), `:994-996` (the dead option), `meta_executor.py` dispatch tail | **OPEN — spec slice 16** |
| **WO-22** ⛔ | **P1** | **Auto-end-turn crosses an unanswered capture choice** (hand-verified): the defer at `executor.py:1966` checks only `has_current_turn_offers()` while the typed `end turn` BLOCKS on `pending_capture_choice` (`:597-602`) — a last-AP capture auto-advances, the enemy phase can retake the province, and the answer dies on the holder-re-validation lapse; the plunder/estate decision silently forfeited. | `executor.py:1965-1975` vs `:597-602` | **OPEN — spec slice 15** |
| **WO-23** | P2 | **A mid-turn save/load refreshes the objection budget** (hand-verified): `save_manager` wipes `objection_popups_this_turn` on load while `from_dict` restores it — the only live limiter on the +3..+12/popup trust channel (no per-marshal cooldown exists; the global cap constant is dead code). | `save_manager.py:191` vs `world_state.py:7303` | **OPEN — spec slice 16** |
| **WO-24** | P2 | **The charge/auto-charge ADVANCE has no frontier halt** — the victor relocates with only `_naval_advance_allowed`, no `can_enter_territory` (both implementations; the reckless-cavalry pass even checks its MOVE arm but not its charge arm) — victorious cavalry stands illegally on a neutral court's soil, the CA9-F13 shape. | `combat_executor.py:7362-7370`; `world_state.py:12033-12035` vs `:12288-12292` | **OPEN — spec slice 17** |
| **WO-25** | P2 | **The "autonomous war-purpose theater dead" rider covers 2 of 4 staging sites** — the glorious-charge site takes no command and `respond_to_glorious_charge` drops it on both branches, so an auto-charge the player never ordered stages the HARD_STOP `war_purpose_selection` (mounted with `replace()` — can destroy the active dialogue). The census pin's docstring is falsified by the auto-charge site. | `combat_executor.py:7421-7432`, `:7605-7614`, auto-charge `:4022-4047`; pin `test_pc15_d_rulings_2026_08_15.py:141-150` | **OPEN — spec slice 17** |
| **WO-26** | P2 | **Attack-capture and occupation-completion CLOBBER an unanswered capture choice** — bare writes to the single slot; only the move path carries the PF-3 save/restore guard. Reachable inside multi-marshal strategic loops. The first province keeps `capture_region`'s effects but never runs secure/estate/log. | `combat_executor.py:7853`, `world_state.py:3937-3938` vs `movement_executor.py:546-551/589` | **OPEN — spec slice 15** |
| **WO-27** | P3 | **The dotation prune lacks the `_capture_choice_pending` carve-out its three siblings have** — an estate question crossing the boundary is pruned and the *respect* answer becomes a paid no-op (never re-added to `dotation_regions`; the +5 acceptance term never fires). | `world_state.py:5891-5896` vs `dotation.py:325/345/405` | **OPEN — spec slice 15** |
| **WO-28** | P3 | **The jealousy beat narrates autonomous attacks that were REFUSED** — the order is voided, the attack executes into a live refusal (recklessness popup et al.), and the beat logs anyway with no success check; the order stays lost. | `jealousy.py:3575-3626` | **OPEN — spec slice 17** |
| **WO-29** | P3 | **Typed capture answers never carry `dialogue_id`** — the W6-0 stale guard is inert on the typed path; composed with WO-26 a typed `plunder` for province X can apply to province Y. | `main.py:2263-2264` vs `:3407-3408` | **OPEN — spec slice 15** |
| **WO-30** | P3 | **`/load` never re-attaches a restored pending capture question** — no capture entry in `PopupQueue.RESPONSE_KEYS` (the queue's own `to_dict`/`from_dict` are dead code; it round-trips via hand-enumerated keys). Self-healing after one refused command; the player is told nothing at load. | `main.py:3947-3971`; `main.gd:1421-1422` | **OPEN — spec slice 15** |
| **WO-31** | P3 | **A HOLD-sortie suppresses the advance but not the capture** — a sally that "returns to hold position" can flip an at-war province the marshal never stood on. Decide at build: block it for `_sortie`, or keep it and say so. | `combat_executor.py:6327` vs `:6376-6416` | **OPEN — spec slice 17** |
| **WO-32** ⛔ | **P1** | **The vassal-rebellion-imminent popup destroys the crisis decision on a refused arm** — the dialogue is popped UNCONDITIONALLY, then `invest_in_vassal` runs with reachable refusals (3-turn cooldown / gold / DP); on those turns "Invest" charges nothing, changes nothing, and deletes Garrison/Accept-Risk too, on a vassal one tick from rebellion, re-fired every turn at loyalty ≤10. The jealousy channel documents-and-fixes this exact failure; the pattern was never ported. | `diplomatic_executor.py:5448-5480`; contrast `jealousy.py:2490-2497` | **OPEN — owner = PC15-10** (`PETITION_POPUP_REVISIT_SPEC.md` popup-lifecycle family; checked at row WO's exit) |

> **Killed this session, recorded so a later reader knows they were tested:**
> ~~"two campaigns soft-lock on `end turn` forever"~~ (hand-driving the blocked
> save resolves it — three answers reach *"Talleyrand departs for the Britain
> court"*; already owned by **WIN-H5**, and the driver's guard simply gives up
> after two identical answers) · ~~"`invest in bavaria` is non-deterministic"~~
> (deterministic five for five; the noise was **WO-7**) · ~~"the cede refusal
> names the wrong party"~~ (correct on a clean boot) · ~~"the mauled threshold is
> broken"~~ (**WO-16** is presentation only) · ~~"the Grand Diversion fires
> repeatedly despite being once-per-war"~~ (quote-then-confirm; it never fired).
> The fleet's verifiers additionally killed: the double `proposal_confirm` as the
> alliance-paradox hard stop · `guarantee_nation`'s missing covet gate (design) ·
> `marshal_destroyed` losing its headline to `home_captured` · Talleyrand calling
> a vassal one point from revolt "steady" · and **"tyranny has no meter"** (false
> — trust collapsed 62 points and the V2a triggers did read it).


## Win-Attempt Campaign (WIN) — filed August 16, 2026 (**✅ ALL 7 ROWS FIXED same day, + the WIN-D2 design ruling BUILT**)

> **Evidence memo = `docs/audits/PLAYTEST_WIN_CAMPAIGN_2026_08_16.md`
> (authoritative).** A France/1805 campaign driven to WIN — 23 world turns,
> four scripted phases (`tools/playtest_scripts/win_campaign_p{1,2,3,4}.json`),
> digests under `tools/playtest_runs/win-p*/` on the dev machine. Austria's
> army was annihilated at Ulm on turn 1 and Austria knocked out of the war by
> turn 13; Russia signed by turn 21.
>
> **The shape of this batch:** the four harness rows are one theme — **the
> unattended harness could not see what it was measuring**, and two of them
> had silently degraded EVERY prior evaluation. The three game rows are the
> CA9 through-line again: a surface offers or narrates one thing while the
> executor does another. Design consequences (no victory condition; the ally
> collecting the player's conquests) are NOT here — they are
> `DESIGN_REFINEMENT.md` §Win-Attempt Campaign.

| # | Sev | Defect | Fix / seam |
|---|---|---|---|
> **✅ FIX PASS, same day (user: "make any fixes needed").** All three
> game rows are FIXED, **WIN-H1 closed both halves**, and the **WIN-D2
> design question was RULED and BUILT** — see `DESIGN_REFINEMENT.md`
> §Win-Attempt Campaign for the gate record. Pins:
> `tests/test_win_campaign_fixes_2026_08_16.py` (25) +
> `tests/test_playtest_harness_win_campaign_2026_08_16.py` (17).
> Suite **18,099 / 3**; `BASELINE_SERIES` and M1–M7 byte-identical
> **without re-record** — which is a fact about the harness (the ambient
> 40-turn run never puts a stronger co-belligerent beside an undefended
> province), not proof of safety; the behaviour is pinned directly.
>
> **Found and fixed in the fix pass itself:** the WIN-H3 cycle guard as
> first written was too coarse — its signature was `(key, choice)`, and
> every dialogue family rides the key `diplomatic_dialogue`, so
> "decline a settlement offer, then decline a proposal" tripped it and
> stopped a chain that was making progress. Signature now carries the
> summary, and non-answers (`(left standing)`, `display-only`) never
> count at all.

| ✅ **WIN-H1** | **P1 (evidence)** | **NPC-16 CLOSED — both halves FIXED.** ⚠ **NPC-16's routed fix is incomplete as written and the row is amended:** promoting the report to `response["pending_interrupt"]` *alone* regresses the client, because that key is a registered `_post_hud_response_routes` matcher (`main.gd:1360`) whose router runs at `main.gd:1909` — BEFORE the strategic-reports branch at `:2000`, in the same function, and returns; the client would fire the popup and SKIP the summary narrating the turn. **The fix is a PAIR:** the backend promotes, and `main.gd`'s `_response_has_interrupt_route` now DEFERS whenever the response also carries a report awaiting input, so the reports flow keeps its own interrupt while a synchronous blocked-path interrupt still routes as before. Neither half ships alone; both are pinned, and the client pin was mutation-checked. Harness half: an interrupt raised during END-TURN rides only `strategic_reports[i].requires_input`; the driver scanned only the top-level `pending_interrupt`, answered nothing, and step 0a returned `awaiting_response` forever — freezing the marshal and then the turn loop. Measured on NPC-16's own input (`Napoleon, attack Mack`): before, `current_turn` stalled at 7; after, the run reached 10 and **the pursuit resolved and took Swabia on turn 6**. ~~⚠ the PRODUCTION half stays OPEN~~ **— STALE, corrected August 16, 2026.** This clause was written of an earlier draft; the commit that landed the client guard landed the backend promotion WITH it (`_include_command_strategic_reports`, guarded on `if not response.get("pending_interrupt")`, carrying the comment that explains the pair). Nothing is open here, and the stale clause is what scoped NPC-16 into the Aug-16 P1 cluster before it was re-measured. | FIXED, BOTH HALVES: `tools/playtest_driver.py` `_interrupt_report()` + the arm-2 fallback; `main.py` promotion + `main.gd` deferral guard |
| ✅ **WIN-H2** | **P1 (evidence)** | **The enemy-phase attack counter has ALWAYS read 0.** The verb lives at `row["ai_action"]["action"]` (`turn_manager.py:964`); PC15-H's fix read `row["action"]`, a key that does not exist, so the substring test ran against `None` on every row. **Every digest ever produced reported "0 attacks" no matter what the AI did.** After the fix the next turn read `3 actions, 3 attacks`. ⚠ **any prior digest-derived conclusion about AI attack frequency is unsupported**, including this campaign's own phases 1–2 | FIXED: new `_verb()` reading the nested key with the flat ones as fallbacks; verbs tally + capture lines + full action list now recorded to jsonl |
| ✅ **WIN-H3** | P2 (evidence) | **An answer cycle reported a healthy engine as `blocked`.** `settlement_confirm` option 1 stages a pair substitute; the chooser's `keep_joint_settlement` is DOCUMENTED to restore the prior dialogue (`settlement_actions.py:3209`). Each step is correct — together they loop forever. The run spun **97 popups** and finished `blocked`, which reads exactly like an engine hard-lock. **This was written up as a P1 against the game before being checked and killed** | FIXED: cycle guard in `drain()` — the same (surface, choice) answered twice in one post stops the chain, notes it, and records an `unknown_blocker`; `--strict` raises. Pair-substitute answer now follows the diplomacy policy instead of always cancelling |
| ✅ **WIN-H4** | P2 (evidence) | **The province scoreboard read `None`.** `GET /ledger` wraps its body under `"ledger"`, so `territories` was never found. Without it a campaign can annihilate an empire and never notice its own map did not grow — which is what happened here for 16 turns | FIXED: unwrap the envelope; the digest's LEDGER row now carries `provinces N (+d)` |
| ✅ **WIN-1** | P2 — **FIXED** | **A peace option is offered that can never succeed.** `Talleyrand, propose peace with Austria` drafts terms and offers *"Send as suggested"* as the FIRST option; execution then refuses — *"Making peace with Austria while allied with Bavaria (who is still at war with Austria) creates a diplomatic contradiction"* — and the dialogue is re-presented **identically and indefinitely** (6/6 in a probe; organically across two courts, Austria t8–t11 and Britain t15). Non-blocking, with a `Reconsider` exit, so not a lock — but it violates this project's own honest-availability discipline | the alliance-contradiction check runs at execution; it should gate the OPTION at build time — arrive disabled with its reason stated, as the vassal-wizard gate rows and NV-6 naval chips do. **FIXED** at the mount seam that already computed the block (`diplomatic_dialogue.py`, the Gate-4 E-2 honest-preview): the `execute_proposal` arm now arrives `enabled: False` with the reason on it, while modify/adjust/Reconsider stay live so the player is never dead-ended |
| ✅ **WIN-2** | P2 — **FIXED** | **Talleyrand's commentary contradicts the terms he drafted.** One payload carries `demands: [{"type": "gold_per_turn", "value": 187}]` and `talleyrand_commentary: "Border territory provides strategic depth. A prudent demand."` — no territory is demanded at all. The CA9 through-line (compute one thing, say another) alive in the peace generator | **FIXED**: the easing ladder's first rung drops territory demands, but `border_territory_demanded` was tagged before easing. The tag is now re-checked against the FINAL demands before stage-4 commentary selection. Only this tag needs it — the sibling territory tags describe SWEETENERS, which the ladder never touches |
| ✅ **WIN-3** | P3 — **FIXED** | **Out-of-range refusals name a distance but never a place.** *"Lannes cannot reach Mack from Swabia! Range: 1, Distance: 8"* never says where Mack is, so the player cannot act on it. The project already fixed this class for regions (*"Region 'Venetia' not found. Nearby: …"*) | **FIXED**: the refusal now names the place it actually resolved to (`cannot reach Mack (La Mancha) from …`), which also makes the NPC-7 misresolution visible instead of silent. Fog-safe — the branch is only reached for a region target or a non-player marshal |
| ⚠ **WIN-H5** | P2 (evidence) | **The p4 acceptance digest no longer reaches its own scenario, and blocks.** Re-run at HEAD `b33a029` through the p1→p2→p3 chain (Aug 16, 2026, during the WIN-D3 build), the campaign never reaches the Russian peace the script is written around — the same-day §7 fix pass changed the board — and instead terminates at world turn 22 in a `settlement_confirm` loop: the driver answers `1` ("Make peace with Britain only"), the dialogue does not clear, and every subsequent command including `end turn` is refused with *"The terms on the table awaits your answer, Sire — nothing was relayed"* until the run stops. **Reproduced BEFORE any WIN-D3 code was written, so it is not caused by that slice.** Two consequences: `win_campaign_p4.json` cannot serve as acceptance evidence for anything until it is re-authored, and a settlement dialogue that consumes a valid answer without clearing is a live player-facing hazard in its own right | OPEN — needs its own session. Digest: `tools/playtest_runs/win-p4-BEFORE/digest.md` (regenerable via the p1→p2→p3 chain). The WIN-D3 slice reproduces the §5.3 stranding deterministically instead — `tests/test_win_d3_road_home.py::TestTheMeasuredDefect` |

**Checked and cleared, recorded so it is not re-filed:** Napoleon's
`Paris → Artois` first step toward Swabia is NOT a pathfinding fault
(Artois and Champagne are both 5 provinces from Swabia — a legal tie);
and `keep_joint_settlement` restoring the prior dialogue is documented
behaviour, not a defect.

Pins: `tests/test_playtest_harness_win_campaign_2026_08_16.py` (15).


## Row NP — the promise audit (August 15, 2026) — **18 FIXED, 11 ROUTED**

> **Record = `docs/audits/NP_PROMISE_AUDIT_2026_08_15.md` (authoritative);
> landing record = `docs/NAPOLEON_SPEC.md` §15.9.** Every commitment in the
> spec and in the 13 NP commit messages, extracted and verified against
> code — 450 promises extracted, 297 LANDED, 60 non-LANDED rows put to
> independent refuters (23 REFUTED, 22 downgraded, 15 confirmed/upgraded),
> alongside a hand pass deliberately not told what the fleet was doing.
> The eighteen fixed rows are in the landing record; these eleven are
> ROUTED with owners, per GR9.

| ID | Sev | Summary | Owner / landing |
|----|-----|---------|-----------------|
| NP-X1 | P3 | **The trailing self-marker still reaches the destination extraction in SOVEREIGN-FREE worlds.** `"Ney, march to Belgium myself"` parses the phantom province `Belgium Myself`. The audit's strip is inside `normalize_sovereign_address`, which is content-gated by design (the NP dormancy pin), so it cannot run on a board with no Emperor. NP-1's claim that adding "myself" to the two fuzzy skip lists closed this family is false by construction — the destination regex reads to end-of-string and never consults them. The general fix belongs at the destination-extraction seam and is corpus-moving. | **CR-6 *proper*** (the parser gate). Completion: a trailing reflexive never becomes a destination token on ANY board, pinned by a corpus row in the sovereign-free arm. |
| NP-X2 | P3 | **The general prisoner-rescue rule was routed nowhere.** NP-4 scoped "storm the city and free him" to sovereigns deliberately — "a general prisoner-rescue rule would change ambient behavior" — and its commit says "routed as a follow-up". It was not routed. Today an ordinary marshal is NOT freed when his own nation retakes the city holding him. | **EC-2 pass 2 / the Victory gate**, whichever reaches prisoners first. Completion: either ordinary prisoners are freed by recapture (with a measured ambient delta) or the sovereign-only rule is CANONIZED at the resolver head with its reason. |
| NP-X3 | P3 | **`sovereign_takes_field` still notes a war DECLARED while the Emperor is already afield.** The per-war-instance re-fire is fixed (one beat per departure), but a fresh war instance created later is unnoted and fires once. | **ACCEPTED, not deferred** — the sentence is true news for that war. Pinned in `test_napoleon_promise_audit_2026_08_15.py`; re-open only if a played campaign finds it reads wrong. |
| NP-X4 | P2 | **The test suite can reach the live Anthropic API.** `.env` sets `LLM_MODE=anthropic` and `conftest.py` does not pin it, so any phrasing the fast parser scores below 0.7 escalates for real — observed during this session (`AnthropicProvider: request_id=…` inside a pytest run). Pre-existing and unrelated to row NP, but it makes every parser test non-hermetic and costs money on a full run. | **position 10 (the shippable build)** — it already owns the key/mock-default surface. Completion: `conftest` pins `LLM_MODE=mock` suite-wide with an explicit `live_only` opt-in, and a pin asserts no provider call escapes a default run. |
| NP-X5 | P3 | **The §10 "modding reference" fails the validator.** `mods/examples/battle_of_waterloo.json` errors on two capitals missing from its scenario regions. **Verified pre-existing and byte-identical before row NP** (`git show 4550ccb`), so NP-5's sovereign upgrade did not cause it — but §10 names this file as the reference a modder reads. | **DEF-1 / the modding-docs row.** Completion: the example validates clean, or the validator's partial-scenario mode is documented and the example is marked as one. |
| NP-X6 | P3 | **The marshal card claims "He never objects and never asks."** Half true: objections are structurally gone, but in LIVE-LLM mode a delegated order ("Napoleon, deal with Mack") routes to the CR-5 ASK arm and raises a `command_clarification` modal — friction on the one commander the card promises has none. Mitigated: Berthier voices the question, not the Emperor, so §2 pillar 1 holds. | **DEF-1 / the next copy pass.** Completion: the card's sentence states the true half without promising the false one, or the CR-5 table gains a sovereign row that resolves rather than asks. |
| NP-X7 | P3 | **`display_names.marshal_honorific`'s docstring says "Single source for EVERY surface that prefixes a rank" — it is used at 3 of 49 such sites.** The reachable remainder renders the Emperor as a rank-less marshal, and one clarification prompt asks the player where the player shall march. | **DEF-1 (roster voices owns the copy backlog).** Completion: either the callers are migrated, or the docstring stops claiming a coverage it does not have. |
| NP-X8 | P3 | **The CR-4 first-person SUPPORT anchor set is wider than the parser.** 5 of its 9 anchors resolve a reference and return a rewrite the parser then cannot act on — the same advisory-diverges-from-executor shape §15.8 item 4 retired four verbs for, one file over. No test iterates the anchor set the way `test_every_sovereign_order_verb_actually_parses` iterates the verb set. | **CR-6 *proper*.** Completion: an anchor-set iteration guard mirroring the verb guard, and the inert anchors retired or made parseable. |
| NP-X9 | P3 | **The Emperor-lead rewrite claims 38 inflected forms and breaks on 6** ("the Emperor moves to X" parses; some inflections do not) — the mock parser's verb regexes are not inflection-tolerant (`move`, not `moves?`). Fixing it at the parser helps every marshal, not only the Emperor. | **CR-6 *proper*.** Completion: the standing verb guard iterates inflections, not just bare stems. |
| NP-X10 | P3 | **`parser._find_player_sovereign`'s `game_state` fallback is production-dead** — nothing emits the payload shape it reads (it looks for a `personality` key the LLM game-state marshals dict does not carry), so it would return None even if it fired. | **CR-6 *proper*** (it is parser-internal). Completion: the branch is deleted or the payload it reads is actually produced. |
| NP-X11 | P3 | **`pending_interrupt["sovereign"] = True` is a production-dead payload key** — written by the NP-4 last-stand builder, read by nothing. The distinct sovereign copy is carried entirely by the `message` string, which does work. | **ACCEPTED for now, pinned as dead**; re-open with NP-6, which is the row that would give a second sovereign a reason to branch on it. |


---

## Napoleon Campaign (NPC) — filed August 16, 2026 (**✅ THE P1 CLUSTER IS FIXED — same day; NPC-16 REFUTED**)

> **Evidence memo = `docs/audits/PLAYTEST_NAPOLEON_CAMPAIGN_2026_08_16.md`
> (authoritative).** Found by the played campaign owed since row PT: four
> scripted arms, 68 turns, one on the live Anthropic parser
> (`tools/playtest_scripts/np_campaign_*.json`, digests under
> `tools/playtest_runs/` on the dev machine). Each row was produced by a
> verifier that had to point at `file:line` with a reproduction; the two
> P1s marked ⛔ were additionally reproduced **by hand, independently**.
>
> **The shape of this batch, stated once:** almost every P1 and P2 here is
> the same defect wearing different clothes — **the player names a thing the
> way the game printed it, and the game acts on something else.** An enemy's
> display name, an honorific, a prisoner's name, a dead man's name, a
> compound sentence: five separate seams, each resolving the player's words
> to a different referent, and only one of them refusing out loud. None is
> sovereign-specific except where marked.


> ### ✅ LANDING RECORD — the P1 cluster, August 16, 2026
>
> **All four P1s are FIXED** (NPC-1, NPC-2, NPC-3, NPC-5), together with the
> two rows that are mechanically part of them: **NPC-20** (the ground the
> NPC-1 guard could not see — its correctness PRECONDITION: fixing the
> needles without it would have INVERTED the bug, so that an answer naming
> the interrupt's own enemy read as a fresh order) and the pursue/support
> half of **NPC-12** (the surfaces that TAUGHT the player the spelling
> NPC-1 punished him for). Pins: `tests/test_npc_cluster_2026_08_16.py`
> (28); 10-mutation sweep, 10 killed. Suite **18,175 / 3**, ruff clean, no
> `.gd` touched.
>
> **⚠ NPC-16 is REFUTED and struck.** Its production half is NOT missing —
> `backend/main.py::_include_command_strategic_reports` already promotes the
> first `requires_input` strategic report to `response["pending_interrupt"]`,
> paired with `main.gd`'s deferral guard, and both halves carry the WIN-H1
> comment explaining why they ship together. The row (and WIN-H1's trailing
> "the PRODUCTION half stays OPEN" clause) were true when written and were
> closed by WIN-H1 itself. Recorded rather than deleted, because the stale
> clause was the reason this cluster was scoped to include it.
>
> **A 46-agent find-then-refute review round then took SIX more, ALL FIXED
> — two of them P1, and one a regression this slice itself introduced:**
> **(a)** NPC-1's P1 survived one step over — the fix corrected the
> REGISTER and left the MEMBERSHIP premise alone, so a name the game had
> just announced as DEAD (`destroy_marshal` removes the fallen from
> `world.marshals`) was still routed into the interrupt: measured, **Mack
> 52,000 → 0, Austria's army annihilated by an order naming a dead
> Russian.** The needle set now unions `fallen_marshals` and the authored
> `marshal_pool`. **(b)** NPC-5 landed at 1 of 5 destination-resolution
> sites; the four in the per-turn processor — the HOTTER path — still
> re-aimed a player's pursuit at the quarry's true province. Lifted to
> `strategic.pursue_known_location` / `resolve_order_destination`, the
> NPC-2 pattern applied to the same class of drift. **(c)** my own
> NPC-20 derivation silently un-did PC15-2(b) for cannon_fire: with the
> battle province in `own_ground`, an addressed *"march to Swabia"* during
> a *"cannon fire at Swabia"* interrupt stopped being the MARCH the player
> typed and became `investigate` — an AP-free, objection-free ATTACK.
> `battle_location` is excluded, with the reason at the constant.
> **(d)** the raw-key `{target} spotted at …` PURSUE lines. **(e)** the
> stale legacy-ladder comment still citing the deleted alias. **(f)** a
> cluster of vacuity in this slice's OWN pins — an `is None or True`
> tautology, a no-op `monkeypatch.setattr`, an AST census that was a
> per-FILE substring test (so `strategic.py`, the module with 17
> order-ending seams, passed on its own `def` line), a SUPPORT pin
> asserting a name whose two registers are identical, and an end-to-end
> pin whose `options` fixture used a shape **no production builder emits**,
> so it could not reach the branch it named. Each now carries a control
> arm that fails when the fix is disabled.
>
> **Three defects found while fixing, not filed by the campaign:**
> `movement_executor`'s too-far auto-upgrade to MOVE_TO, `tactical_executor`'s
> auto-break-square, and the SECOND forced-retreat copy in `world_state`
> (`_process_reckless_cavalry_turn_start`) all end an order's life and none
> was in NPC-2's list — the "two combat copies" trap this codebase keeps
> hitting. A structural AST census now fails if any module ends a strategic
> order's life without consulting the single source.
>
> **Two conscious flips, and one fixture that was always incoherent:**
> `test_estate_second_pass.py::test_title_grounds_the_target` is inverted and
> renamed (a title owned by two Archdukes must ground NEITHER — it was the
> hole NPC-3 went through); `test_creative_audit_ca9_2026_08_08.py`'s parity
> probe now seeds intel, because a pursue against an unseen quarry is refused
> up front; and `test_strategic_objections.py`'s fixture replaced
> `world.regions` with a seven-province map while leaving the boot intel
> store describing the old one — invisible until PURSUE started pathing to
> the last KNOWN province instead of the live one.

| # | Sev | Defect | Fix seam |
|---|---|---|---|
| ✅ **NPC-1** | **P1** | **Typing an enemy's name the way the game spells it fights a different enemy and wins.** `_addressed_fresh_order_elsewhere` (`main.py:795-802`) builds its needle set from internal marshal KEYS (`ArchdukeCharles`), but the game prints `Archduke Charles` everywhere. Reproduced by hand in two ordinary commands and no state injection: `Ney, march to Swabia` (raises a `contact_bad_odds` interrupt about Mack) → `Ney, march to Frankfurt` (order replaced, interrupt survives) → **`Ney, attack Archduke Charles` → `success: true`, "Ney attacks Mack and wins!", 3,297 casualties, Ney advances into Swabia.** The key spelling `ArchdukeCharles` refuses honestly — so the player is punished for copying the game's own text | `main.py:795-802` — needle set `{key, humanize_entity_name(key)}` (and the last-name token, which `delegation.py` already supports) | **✅ FIXED** — the needle set now carries BOTH registers via the public `llm_client.name_match_patterns`, plus a uniqueness-gated surname pass over the whole enemy SET (`unique_name_tokens`, single source with the parser). NPC-20's derived `own_ground` had to land WITH it or the bug inverted.
| ✅ **NPC-2** | **P1/P2** ‡ | **Re-ordering a marshal who holds an order-bound interrupt leaves the stale question armed.** Measured: after `Ney, march to Frankfurt` replaces the Swabia order, `ney.strategic_order.target == 'Frankfurt'` while `ney.pending_interrupt` still holds `{contact_bad_odds, enemy: Mack, location: Swabia}` — which also freezes the new order at step 0a, and is the ammunition NPC-1 needs. **Root cause corrected by the refutation pass:** it is not "implemented at 1 of ~38 seams" — TUT-F4a's clear IS written, and is **unreachable for strategic orders** because `executor.py:873` excludes `is_strategic_command` before it can run | one `clear_strategic_order()` routed through the reachable seams the refuters enumerated — `strategic_executor.py:1109` / `:1703` (new order), `combat_executor.py:6954` (form_square), `:3199` / `:3285` (forced retreat), `jealousy.py:3575` — clearing only `strategic.ORDER_BOUND_INTERRUPT_TYPES` | **✅ FIXED** — new single source `strategic.clear_order_bound_interrupt`, called at every seam that ends an order's life (~20, incl. three the row missed), with an AST census pin so a new one cannot drift. The old inline copy in `executor.py` now delegates to it.
| ✅ **NPC-3** | **P1** | **`Ney, attack Archduke John` silently attacks Archduke Charles** (with John fogged). The guessed-target guard's substring grounding (`combat_executor.py:134-136 _named_in_raw`) is disarmed by the shared title — "Archduke" matches both — and, per both refuters, the substitution originates one layer up in **the mock parser's world-blind legacy bare-`archduke` alias at `llm_client.py:1675`** — which runs at PARSE time, before either PC15-4 guard, and fires with **nobody dead at all** (`attack Archduke Ferdinand` also lands on Charles). The muster header names Charles, the battle is fought against Charles, and the word "John" never appears | retire/scope the bare-title alias, and ground `_named_in_raw` on the uniqueness rule `llm_client.unique_name_tokens` already implements | **✅ FIXED, both layers** — the world-blind bare-`archduke` alias is retired from the mock parser's legacy ladder (the explicit full-name forms stay, and an `archduke john` arm was added), and `guessed_target_refusal` no longer accepts a word SHARED by two commanders as grounding.
| ~~NPC-4~~ | **REFUTED** | ~~"`attack <marshal>` out of range is a null action — a PURSUE closing at 0 provinces/turn."~~ **FALSE, and struck.** Two independent refuters measured the pursuit *closing*, and a third measurement by this session confirmed it: Paris→Swabia went **4 → 3 → 2** at the pursuer's own `movement_range`, and the refuters' samples terminated in combat 2 times in 5, one with a capture. The observation that prompted it (4 player battles in 22 turns, 0 in 14 live) is real — **its cause is NPC-16, not the pursuit rate.** Recorded rather than deleted because the wrong diagnosis was this session's headline and a later reader deserves to know it was tested and killed | none — do not "fix" the pursuit rate |
| ✅ **NPC-5** | **P1** | **The PURSUE acceptance line leaks an unseen enemy's exact province, then the same order is cancelled for having no intelligence on him.** Issue time reads the live marshal (`strategic_executor.py:1400-1403`, no fog filter); execution reads `get_last_known_location`. `Napoleon, attack Kutuzov` → "pursues Kutuzov (at Podolia)" — a province France has never scouted — then two turns later "Order cancelled: No intelligence on Kutuzov" | `strategic_executor.py:1401-1402` (message) and `:697-698` (the path) — resolve through `get_last_known_location`, refuse up front when there is none, and **gate on `marshal.nation == world.player_nation`** so AI omniscience is untouched. Fires for all four fogged at-war commanders (Carniola / Podolia / Volhynia / London) | **✅ FIXED** — new `_pursue_known_location` resolves through the PLAYER's intel while the AI keeps live truth (the gate is load-bearing, not a courtesy); the order is refused up front and costs 0 AP when the quarry has never been seen; the first-step-blocked reroute (not in the row) was the same live read and is routed through the same helper.
| **NPC-6** | P2 | **A destroyed marshal's display name silently retargets a living one.** `Napoleon, attack Archduke John` with John destroyed → "Napoleon pursues ArchdukeCharles (at Carniola)", a standing order created and AP spent. The PC15-4 guard is correctly scoped to the ADDRESSED marshal; the TARGET side has no twin | the target-side twin of `main.py:_addressed_lost_marshal_refusal`, at the point `_execute_attack` resolves the target |
| **NPC-7** | P2 | **An order to attack a marshal we already hold prisoner answers with a different province's geometry — and has an EXECUTING arm.** Arm 2 hit this organically for fifteen consecutive turns. `get_enemy_by_name_for_nation` requires `strength > 0`, so the name falls through to region fuzzy-matching: "cannot reach Mack from Paris! Range: 1, Distance: 5 … Try 'move to La Mancha'". When the misread province is in range and at war it **proceeds**: a province taken, 432 men lost to march attrition, a plunder/secure prompt *(the refuters split on the executing arm and then found a **worse, boot-reachable** case: `Ney, attack Brunswick` with Brunswick a prisoner **executes** — Hanover flips to France and 432 men are lost to march attrition — because his name is also an exact province name. No controller flip needed. The structural gap is one region seam of four with no typo gate)* | `combat_executor.py:4290-4296` — consult the prisoner/fallen roster before the region branch; gate the auto-correct on `parser._plausible_name_typo` as its three siblings are |
| **NPC-8** | P2 | **An honorific in any strategic TARGET erases the target.** `Napoleon, support Marshal Ney` → *"Napoleon moves to support Bernadotte (at Franconia)"*, 1 AP charged, six-province path committed, substitution never mentioned. Classified GENERIC by naked substring (`strategic_parser.py:625,656` — "marshal" matches inside "marshal ney"), which also bypasses SUPPORT's unknown-name and enemy-marshal refusals. **Not just SUPPORT:** `pursue` and `march to Marshal Ney` too — the latter becomes MOVE_TO **Swabia**, a Bavaria-held province holding Mack, while Ney stands at Rhineland | the bare-form indicators need an exact whole-target test, not a substring |
| **NPC-9** | P2/P3 ‡ | **The Emperor's first-person address fails on a compound sentence, and the phantom province is back.** `I will take the field myself and march to Lorraine` → "Which marshal shall march to Lorraine, Sire?"; `I will march to Lorraine myself and attack Mack` → **"Napoleon begins march to Lorraine Myself."** Cause: `_SOVEREIGN_SELF_MARKER_RE` (`parser.py:137-138`) is **`$`-anchored**, so a mid-sentence "myself" is never stripped, and the first-person arm binds only when an order verb sits adjacent to "I [modal]". ⚠ **the session's "this is *not* the retirement of `take`" was REFUTED for the first input** — restoring `take` to `_SOVEREIGN_ORDER_VERBS` does make that sentence bind (§15.8 item 4 retired it because it does not parse as an action, so the fix is the anchor, not the verb). ⚠ the second input **duplicates NP-X1** and shows that row is under-graded | `parser.py:137-138` — de-anchor the marker (strip anywhere, not only at `$`); the existing strip at `:212-217` then runs before every arm |
| **NPC-10** | P2 | **The A4 verb gate tests for a verb ANYWHERE in the body, not for the sentence being an order.** `I will hold talks with Prussia myself` → "Napoleon, hold talks with Prussia" — a diplomatic sentence handed to the LLM marshal-addressed, the exact A4 shape. Too loose here and too tight on NPC-9 | `parser.py:139-140` `_SOVEREIGN_BODY_HAS_VERB_RE` |
| **NPC-11** | P2 | **The literal marshal's "verbatim" quote is fabricated from internal keys.** `Soult, attack Archduke John` → `"Soult attack ArchdukeJohn." Understood to the letter.` — the comma gone, the display name replaced by the database key, a period added, inside quotation marks that assert these are the player's words. Directly against the W6-5 literal doctrine | `combat_executor.py:4342` — carry the real typed text through the auto-upgrade |
| ⚠ **NPC-12** | P2 | **Raw camelCase enemy keys reach the terminal on at least seven player-facing surfaces** (`Ney pursues ArchdukeCharles`), while the morning dispatch spells the same man `Archduke Charles`. This is *how the player learns* the spelling NPC-1 then punishes | `strategic_executor.py:1403/1410`, `combat_executor.py:1100`; durable fix is `humanize_entity_name` at the interpolation seams | **✅ FIXED at the pursue/support acceptance lines** (the surfaces that teach the spelling NPC-1 punished); two function-local imports that SHADOWED the module-level humaniser were removed. ⚠ **the wider census is NOT closed** — a recon pass measured ~426 enemy-reachable interpolations across the backend, and `game_logic/combat.py` and `ledger.py` have never imported the humaniser at all. That remainder keeps this row OPEN at P2 with an AST pin named as its completion.
| **NPC-13** | P3 ‡ | **The engaged-move refusal offers a retreat that does not exist and prints a dangling empty label**, and never names the enemy it already computed: "You may retreat to friendly territory." / "Friendly regions adjacent:" *(nothing)*. Downgraded P2→P3 on refutation | `movement_executor.py:149` |
| **NPC-14** | P2 | **A fallen homeland province — Paris included — is news for one turn and then vanishes from the briefing.** One turn after Paris fell the lead went to an unpaid household (weight 55). There is no standing producer for "homeland currently enemy-held" | `dispatch.py` — a standing producer alongside the existing state-based ones |
| **NPC-15** | P2 | **Paris gets Nivernais's sentence, and no captor is named.** `home_captured` (weight 100) renders `"Sire — {region} has fallen. Enemy colours fly over French homeland soil."` with no `{captor}` and no capital branch — byte-identical in shape for the capital and for any province. `capital_stormed` (92) is the *mirror* class, for France taking an ENEMY capital | `dispatch.py:415` — pass `captor` as `:433` already does; branch on `get_nation_capital(player_nation) == region` |
| ~~NPC-16~~ | **REFUTED** |  **A strategic interrupt raised during END-TURN processing is never promoted to the top-level response key** — it rides only `strategic_reports[i].requires_input`. An unattended driver cannot see it, so step 0a returns `awaiting_response` forever and the marshal — **and then the turn loop itself** — freezes. **Measured on the ordinary input `Napoleon, attack Mack`:** the pursuit closes 4 → 3 → 3 through turn 4, a `cannon_fire` interrupt is raised on turn 5, and from there Napoleon never moves again and `current_turn` stops advancing at 7. **This, not the pursuit rate, is why all four campaign arms produced so few battles — and it means every battle-count figure in this playtest understates the game.** Only ONE `strategic_interrupt` popup appears across all four digests. The Godot client derives it from `strategic_reports`, so a human player is unaffected: hence P3 for the player and **P1 for anything that evaluates the game unattended** | `main.py:1205-1219` — promote the first `requires_input` strategic report to `response['pending_interrupt']` (what the client already derives); and teach `tools/playtest_driver.py` to read `strategic_reports` | **STRUCK, August 16, 2026.** The production half is ALREADY LANDED — `backend/main.py::_include_command_strategic_reports` promotes the first `requires_input` strategic report to `response["pending_interrupt"]`, paired with `main.gd`'s deferral guard; both carry the WIN-H1 comment. WIN-H1 closed this when it landed the pair, and its own trailing "the PRODUCTION half stays OPEN" clause is stale. Do not re-fix.
| **NPC-17** | P3 | The muster hedges **"if he marches"** when the Emperor is the LEAD ATTACKER — the attack *is* the march. Same screen calls him **"this marshal"** in the hostile-refusal string (`combat_executor.py:974`), the demotion NP-V's `marshal_honorific` was landed to stop. *(The opposite half — audit B1 — is healthy and was falsified: a fortified Emperor prints "WILL NOT — Napoleon: is dug in…" and no presence line. Do not re-open that predicate.)* | `combat_executor.py:1153` — `"" if (_sov_present is marshal or _sov_present.location == battle_region) else …` |
| **NPC-18** | P3 | **"the Emperor" is an address form but never a REFERENT.** `Ney, support the Emperor` → "Cannot find marshal 'Emperor' to support" while `support Napoleon` and `support me` both work — and the refusal then lists the sovereign under **"Available French marshals"** | `strategic_executor.py:553-590` (a sovereign-title arm mirroring PURSUE's) and `:559-562/:586` (route the roster through `marshal_honorific`) |
| **NPC-19** | P3 | Two more answers to "what about our prisoner?": `Ney, pursue Mack` **accepts** and charges 2 AP to chase a prisoner into Paris; the bare `attack Mack` says **"Mack has already been destroyed!"** of a living, unwounded man who is live diplomatic leverage | `strategic_executor.py:599` filter on `strength > 0 and not captured_by`; `combat_executor.py:8080` branch on `captured_by` before the destroyed copy |
| ✅ **NPC-20** | P3 | `own_ground` is always EMPTY for `cannon_fire` — the guard reads `location`/`enemy`/`destination`, the cannon_fire builder stores its ground under `battle_location`, so every cannon-fire interrupt reads as fresh-order-elsewhere and is left armed (NPC-2's ammunition) | `main.py:782-787` — include `battle_location`; audit the other builders' key names | **✅ FIXED** — `own_ground` is DERIVED from the interrupt payload's own string values instead of a hand-kept three-key literal, so a new interrupt type inherits the right behaviour. The census found two more builders the literal missed: `muster_confirm` (stores `target`) and `last_stand` (stores only `enemy`).
| **NPC-21** | P3 | `proposal_confirm` mounts a permanently-dead **"Send as suggested"** button beside an acceptance estimate that contradicts its own "I cannot deliver this" warning; answering it re-serves the identical dialogue un-popped (the HARD_STOP arm returns without `pop()`), which is what made 16 refusals look like a soft-lock | `diplomatic_dialogue.py:866-876` — mark the execute option unavailable with the warning as its reason (the honest-availability convention); `diplomatic_executor.py:3841-3849` for the pop |
| ~~NPC-22~~ | **REFUTED** | ~~"A sovereign inherits the cautious branch of the cannon-fire interrupt — audit finding B4's class at a second seam."~~ **Struck, 2/2 refuters.** The mechanism reproduces, but it is **a recorded, dated, census-pinned NP-V decision**, not a silent inheritance: `marshal_voice.py:361-389` (`interrupt_speaker`) was authored on Aug 15 about this exact family and names cannon fire in its body — *an interrupt is NOT an objection; the decision stays, only the voice changes* — and **Berthier speaks it, not Napoleon**, so §2 pillar 1 holds. This session called it "the only NP-shaped mechanical defect the campaign found"; it is not a defect at all | none — the docstring at `strategic.py:2139-2143` still enumerates three personalities and could note the fourth, but that is cosmetic |
| **NPC-23** | P3 | `"Murat stand in his path"` / `"Lannes and Murat and Napoleon stand in his path"` — no verb agreement, no serial join, and **both fixes already exist in the repo** (`battle_report._join_names`, the `{stand}` idiom at `dispatch.py:255-257`) | `dispatch.py:736` |
| **NPC-24** | P3 | The escalated famine headline prints a bare `"1,351 men."` that reads as the overage collapsing (good news) when it is the men who died — the two sibling templates give the number a verb | `dispatch.py:213` |
| **NPC-25** | P3 | The charge refusal states the stat and never the threshold, and the threshold is **1**: "build momentum … Win battles as attacker" implies a campaign; one victory is enough | `combat_executor.py:7088-7089` |
| **NPC-26** | P3 | Naming an enemy nation and a province is answered about a different nation with no acknowledgement: `Murat, ride down the Austrians at Swabia` → "cannot attack Bavaria — they are our ally" (Swabia is Bavaria's; no Austrian corps stands there). The word Austria never appears | `combat_executor.py:202-222` `friendly_fire_refusal` — say which province is whose |
| **NPC-27** | P3 | The briefing reports **authority 100 / "Strong"** on the same screen that reports 19 French provinces to 107 enemy ones and the capital lost — while `get_imperial_grip`, built for exactly this, reads **52**. The raw tracker is the number the player sees; the derived one is the number the game acts on | `dispatch.py` situation block — surface the derived grip beside (or instead of) the raw authority |

**Harness rows (tools, not game).** Together these are why the digest could
not show that a P3 dead button was a dead button: **NPC-H1** (P3) the driver
never inspects `success` on a popup follow-up and has no repeat-`dialogue_id`
guard, so a refused answer is re-sent identically until the cap
(`playtest_driver.py:607-620`) · **NPC-H3** (P3) the digest records the answer
SENT but never the server's reply, so sixteen refused confirms rendered as
sixteen ordinary ones (`:326-329` + the scan call sites; contrast `:301-306`,
which does record an outcome).

‡ **The refutation pass** (two independent refuters per surviving claim) ran
after this section was first written and judged **29 of ~40 claims** before
the session closed — **two killed, zero downgraded to nothing, and every
remaining row confirmed at or within one grade of its filed severity.** The
corrections are folded in above rather than appended; ‡ marks a row whose
refuters disagreed on severity or moved it (the **higher** is kept as the
filed grade, the disagreement noted in the cell). Where the two split P2/P3
without a ‡ — NPC-6, NPC-11, NPC-12, NPC-15 — the P2 is kept on the same
convention. **Final tally, from the fleet's own synthesis: 33 claims entered
verification, 4 were KILLED, 1 was reduced to no defect, and the surviving
distribution is 4 P1 · 12 P2 · 16 P3 (3 of them harness).** The fleet's four
P1s are NPC-1, NPC-2, NPC-3 and NPC-5; **NPC-16 is theirs at P3** and the
evidence-P1 grade above is this session's own judgement about what it does to
an unattended playtest, stated separately so the two are not confused.

**Two of the four killed rows were this session's own conclusions** —
~~NPC-4~~ (the "null pursuit", the memo's second headline) and ~~NPC-22~~
(the sovereign's cannon-fire ask, written up as the campaign's only NP-shaped
mechanical defect). That is the argument for pointing refuters at your
findings and not only at the code: the code review would never have caught
either, because both were claims *about* the code rather than defects *in*
it. 84 agents, 17.5M tokens, zero errors.

**REFUTED / KILLED, recorded so they are not re-opened:**
- **the third harness row is dead.** `_option_id` genuinely cannot read
  `action`-keyed options — and on `proposal_confirm` that is **causally
  inert**: the `confirm` fallback is what the endpoint wants anyway, so every
  stated consequence was false. Not filed.
- **"the sovereign is listed under Available French marshals" is a duplicate**
  of NPC-18 and half its evidence is production-dead (only the `:586`
  not-found arm is live). Folded into NPC-18; not a separate row.
- the sibling `_mentions_whole` loop over `world.regions.keys()` does **not**
  have NPC-1's key-vs-display mismatch (region names are not camelCase keys —
  do not churn that loop).
- audit finding **B1's predicate is healthy** in both directions: a fortified
  Emperor prints "WILL NOT — Napoleon: is dug in and will not abandon his
  works" and no presence line, on one screen. NPC-17 is the *opposite*
  direction and is copy only. Do not re-open the predicate.
- the muster header calling 20,162 men against a "small force" an "even"
  balance is a **documented deliberate decision** — the band and the printed
  strength come from different sources on purpose, and reconciling them would
  leak fog.

---

## Comprehensive Playtest PC15 — filed August 15, 2026 (**THE FIX SLICE LANDED August 15, 2026 — 13 rows FIXED**)

> **Evidence memo = `docs/audits/PLAYTEST_COMPREHENSIVE_2026_08_15.md`
> (authoritative; per-row digest named below — digests live in
> `tools/playtest_runs/<name>/` on the dev machine, gitignored).** Found by
> the first playtest on the standing harness: 4-seed variance sweep + a
> 24-turn anthropic flagship + naval/diplomacy/tutorial arms + a Mode-C
> visual pass. **The three P1s marked ⛔ are the Round-0 gate** (memo §1).
> Directional score ≈6.7 — the first rise since July.
>
> ### ✅ LANDING RECORD — the PC15 fix slice, August 15, 2026
>
> **FIXED (13): PC15-1** (+ the probe-found prisoner-deletion sibling) —
> `WorldState.destroy_marshal` is now the ONE marshal-removal seam
> (tombstone registry `world.fallen_marshals`, serialized; a
> `marshal_destroyed` campaign-log type, 157→158 pins flipped consciously;
> the dispatch three-arm ladder `marshal_destroyed` w96 /
> `enemy_marshal_destroyed` w89 / third-party-no-candidate per CA8-D6; the
> PT-J4 bench note rides both loss classes; gazette + turn-events rail;
> `marshal_eliminated` retired — it was never in CAMPAIGN_LOG_TYPES; the
> glorious-charge and coordinated-cleanup pops no longer delete a marshal
> the forced-retreat arm just CAPTURED, and a census pin forbids bare pops
> backend-wide) · **PC15-2** — the interrupt route's addressed-other guard
> is roster-FREE (leading address token honoured for dead names) and an
> addressed command naming foreign ground falls through as a fresh order
> (`_addressed_fresh_order_elsewhere`) · **PC15-3** — the pair-substitute
> chooser is a NAMED hard stop answerable by typed word ("confirm"/"keep"
> keyword rows; `dialogue_court` reads `selected_target_nation`;
> `turn_created` stamped at the mount; `clear_stale` now sweeps the QUEUE
> by the same rules — the displaced-stale-dialogue immortality is closed
> structurally) · **PC15-4** — the pre-parse LOST-MARSHAL guard: an order
> addressed to a fallen marshal refuses by name ("lost to us … destroyed
> at {place}", bench named only when `first_affordable_commission` grants
> it), a PRISONER refuses with his captor, and the enemy-side
> `attack <destroyed name>` answers from the tombstone · **PC15-6** —
> request-terms names the leader substitution and its why
> (`settlement_request_terms_sent_for_court_talleyrand`) · **PC15-7** —
> the typed Grand Diversion quote-then-confirms (the expedition's own
> idiom; AI rung untouched, GR5) · **PC15-9** — tutorial beat VI gate 3→2
> (the window was ONE player turn; root cause = ambient combat RNG driving
> Kienmayer's fate, which no campaign-seed pin covers — a 3-seed
> ambient-RNG window pin now binds it) · **PC15-11** — every structural
> request-terms refusal code has its own sentence with a remedy ·
> **PC15-12** — supply-headline subject-verb agreement ({stand}/{have}
> fields) · **PC15-13** — the low-confidence did-you-mean answers with the
> marshal's own roads ("From Paris the roads lead to …") instead of
> string-distance noise · **PC15-14** — the "recovering: 0% (recovered)"
> non-event yields to the completion beat (one `test_mc_q3` pin flipped
> consciously) · **PC15-17** — stale `vassal_rebellion_imminent`
> popups/dialogues naming a non-vassal are retired at load · **PC15-H** —
> the driver's enemy-phase attack counter reads `action`, the
> pair-substitute chooser is answerable by policy ("keep"), and
> PLAYTESTING.md documents the loop-index/world-turn trap.
>
> ~~**PC15-8**~~ ✅ **FIXED August 15, 2026 (the live-probe session, eighth
> that day)** — `tests/test_pc15_8_delegation_nation_arm.py` (14). The
> live probe REPRODUCED the flagship failure (live parse → `attack` at
> 0.85 for literal Soult) and found the root cause was NOT the router:
> `_resolve_target` knew officers and provinces but not NATION references,
> so "the Austrians" made `detect_delegation` return None and the whole
> CR-5 router — literal ASK included — was bypassed. Fix at three seams,
> router untouched (guardrail (e) pinned): (1) the deterministic NATION
> arm — demonym/nation-name → nearest VISIBLE enemy of that nation
> (fog-honest R5, at-war-only so a delegation never hands the aggressive
> arm a friendly officer, region table still shadows "Hanover");
> "the Austrians" now resolves to **Mack at Swabia** — the 1805-exact
> answer — and every personality gets its blessed arm; (2) the prompt's
> literal row gained a concrete no-guess instruction (action "unknown");
> (3) PARSE_TOOL's `action` description had said "One of the Valid
> Actions", OVERRIDING the prompt — it now names the "unknown" escape
> hatch. **Live compliance measured, not assumed** (temp-0 probes: 2/3
> unknown + 1/3 scout on the resolvable case, 2/2 unknown on the
> unresolvable case, never attack; the deterministic router forced ASK in
> every probe) — so no parse-tier live pin is written: the corpus row
> `cr5-deleg-literal-soult-resolves-live` (which pinned success:true off
> the model resolving an action) is RETIRED for a `mock_only` row, and the
> definitive literal→ASK stays deterministic at the endpoint tier.
> Endpoint verified LIVE end to end: the ASK fired for Soult and the
> aggressive PURSUE + bad-odds interrupt fired for Ney, both on the
> nation phrasing; the two surviving live corpus rows re-ran green twice;
> mock corpus 516/516.
>
> **STILL OPEN with reasons: PC15-10** (CA9-D3's owned
> revisit slice — **✅ EVALUATED + SPEC'D August 15, 2026, seventh session
> that day, AND THE §6 GATE RULED THE SAME DAY at the recommended defaults
> under the user's delegated grant: fix design + gate record =
> `docs/PETITION_POPUP_REVISIT_SPEC.md` v1.1**, authoritative for the
> slice; root cause = ~2.3 candidate petitions/turn from 7 hair-trigger
> authored pairs against a serve-per-answer single-slot channel with no
> budget constant; centerpiece fix F1 "The Antechamber" tier-splits
> routine audiences off the modal path; BUILD-READY per §9, no gate
> outstanding) ·
> ~~**PC15-16 + PC15-18**~~ ✅ **FIXED August 15, 2026 (the visual-pass
> session, eighth that day)** —
> `tests/test_pc15_16_18_visual_fixes_2026_08_15.py` (13); all four
> surfaces driven live in the client against
> `saves/flagship_visual_t12.json` on `SOVEREIGN_PORT=8006`, evidence =
> `docs/audits/PC15_16_*.jpg` + `PC15_18_*.jpg` (5 shots). **PC15-16**:
> the CA9-F5 `-1` sentinel extended from `supply_capacity` to
> `income_value` / `effective_income` / `stability` in the hidden-econ
> block of `get_filtered_game_state_summary`, with BOTH `.gd` readers
> branching (region panel + map tooltip now read "Income: Unknown /
> Stability: Unknown" beside Supply; one `test_intel_report` pin flipped
> consciously). **PC15-18(a)**: N had NO special block — every letter
> screen hotkey was dead in the game's dominant state, because the
> client re-grabs command-input focus at every control-return tail and a
> focused LineEdit consumes printable keys before `_unhandled_input`;
> fix = the F1 precedent, `Alt+<screen key>` intercepted in
> `_on_command_input_gui_input` for all six screens (bare letters must
> keep typing — "ney…" starts with n; bare keys still work unfocused),
> nav-button tooltips name the form; verified live (Alt+N opened the
> Moniteur with the input focused). **PC15-18(b)**: the enemy-phase
> dialog got the NV-6 `MOUSE_FILTER_PASS` fix — and the class is now
> CLOSED BY CENSUS: a fit_content RichTextLabel directly under a
> ScrollContainer must let the wheel through (scene-side or
> script-side), enforced over every `.tscn`. The census found and fixed
> **eight more latent members** (diplomatic ledger, dispatch, gazette,
> marshal management, proclamation, region panel, strategic report
> popup, the settlement per-court table, AND the terminal scrollback
> itself — the July-25 R4 fix set `scroll_active=false`, which the
> ledger and enemy-dialog evidence proves was insufficient);
> wheel-scroll verified live on the enemy phase (before/after pair).
> Tests: `tests/test_pc15_fix_slice_2026_08_15.py` (53).
>
> **PC15-5 and PC15-15 CLOSED August 15, 2026 (same day, second slice) by
> the PC15-D gate rulings** — gate record = `DESIGN_REFINEMENT.md`
> §Comprehensive Playtest (D1 "The Closed Frontier" closes the whole
> PC15-5 family: retreat scan obeys the movement law, the glory-hunt
> respects neutrality, the autonomous war-purpose theater never stages,
> the DP-shortage exit is a visible receipt; D4 "The Congress Holds"
> closes PC15-15: truce floor 8 + P3.7's war filter + the unheld-homeland
> return + the congress-beat dedupe). Tests =
> `tests/test_pc15_d_rulings_2026_08_15.py` (34).

| ID | P | Finding | Evidence | Where to look |
|---|---|---|---|---|
| **PC15-1** ⛔ | P1 | **A destroyed marshal vanishes silently.** No event type exists for corps annihilation (`marshal_captured/recovered/released/commissioned` is the entire marshal event vocabulary); Ney and Murat were annihilated in the flagship (T13–18) with no event, no dispatch line, no campaign-log row — the player discovers it when their next order misroutes (PC15-2/-4). The drama/reward economy's protagonists can die unannounced. | flagship-1805 digest + t20 save event-log scan | `combat_executor` marshal-removal seam; `world.log_event` needs a `marshal_destroyed` type + dispatch beat (campaign-log type count pins will move consciously) |
| **PC15-2** ⛔ | P1 | **A pending order-bound interrupt swallows every typed command.** `[INTERRUPT ROUTE] Routing 'Murat, attack Buxhowden' -> Soult destination_blocked response: attack` · `'Ney, march to Vienna' -> Bernadotte cannon_fire response: investigate` · `'Davout, march to London' -> Davout cannon_fire response: investigate`. The route keyword-matches (with an any-text fallback to an answer) and never checks whether the command explicitly addresses a DIFFERENT marshal — the order is consumed, the response describes someone else's battle or a cancel failure. 3 hits in 2 runs once strategic orders stack. | flagship-1805 T19/T21 + naval-descent T8; `server_console.log` lines 10701/12024 (flagship), 4084 (naval) | the `[INTERRUPT ROUTE]` seam (strategic interrupt answer matcher) — an explicitly-addressed command naming a marshal other than the interrupt's must fall through to the parser (the CR-4 invented-marshal-guard idiom, applied here) |
| **PC15-3** ⛔ | P1 | **A stale settlement pair-substitute confirm wedges all later proposals.** From fixture_t20 with accept policy: answering an incoming offer staged `settlement_confirm` → answered "1" → staged `settlement_pair_substitute_confirm` (unanswered); next turn `propose peace to Austria` looped EIGHT `proposal_confirm` popups — every typed "confirm" was consumed by the stale ACTIVE dialogue and the proposal never sent. BUG-CA-7's dialogue-stack family on the settlement channel. Client severity depends on whether `settlement_pair_substitute_confirm` is in the `main.gd` dtype whitelist — verify while fixing. | diplomacy-latewar T21–22 digest ("⚠ answer chain capped at 8") | `dialogue_manager` stack + the typed confirm router; stale-dialogue retirement (clear_stale) or stack-aware confirm targeting |
| **PC15-4** ⛔ | P1 | **A dead marshal's name silently commands a different marshal.** `Ney, attack Archduke Charles` (Ney destroyed) → LLM parse valid → "LLM result failed validation: Unknown marshal: Ney" → fell back to the FAST parser's bare `attack` → `[MARSHAL SELECTED]: Soult` → Soult's muster/battle ran. The fallen-marshal case needs its own refusal ("Ney is lost to us, Sire"), not roster-nearest substitution; the CR-2 invented-marshal clarify covers only never-existed names. | flagship-1805 T23; console 13195–13210 | `validation.py` unknown-marshal arm + the fast-parser fallback path; distinguish fallen/captured names from typos (the roster of the DEAD is knowable) |
| PC15-5 | P2 | **The neutral-soil family.** (a) Forced retreats route broken armies through NEUTRAL territory including foreign capitals — Mack fled Frankfurt→Berlin→Dresden (three neutral courts) with `[RETREAT DEBUG] allies=0, enemies=0` treating neutral soil as valid; (b) autonomous glory-attacks pursue him there (Ney fought at Frankfurt, Lannes stormed BERLIN at peace with Prussia); (c) the resulting war-purpose→Conquest→Talleyrand-objection→proceed→confirm chain produced **no war, no state change, and no receipt** — three modals of theater, in three separate runs, twice re-firing for the same court. Either the declaration should happen or the chain should not start. | variance_jena T17–19 · flagship-1805 T2/T5 · naval-descent T5–6/T10 | retreat destination scan (neutral exclusion or internment rule); jealousy autonomous-attack target filter; the incursion declare-war pipeline's terminal arm |
| PC15-6 | P2 | **`request terms from Austria` answered by BRITAIN.** The named court is silently replaced by the coalition war's leader ("I shall ask Britain's chancery to name its terms for France + … vs Britain + Austria + Russia"). If leader-authored terms are the design, the response must say why Austria cannot answer; today it reads as the typed-router class CA9 fixed for dialogue answers. | diplomacy-latewar T21 | `request_terms` court resolution in `diplomatic_executor`/`settlement_offers` |
| PC15-7 | P2 | **The typed Grand Diversion resolves irreversibly with no quote or confirm.** `order the diversion` at readiness 53 with no staged camp executed instantly: "caught coming home … loses 46 sail." The sibling `naval_expedition` quote-confirms; the client chip warns — the typed path just fires. One line cost the fleet. | naval-descent T5 | `naval_executor.naval_diversion` — the expedition's quote-then-confirm idiom |
| ~~PC15-8~~ ✅ | P2 | **FIXED Aug 15, 2026** (landing note above). The router was innocent — nation references never reached it: `_resolve_target` gained the fog-honest at-war NATION arm ("the Austrians" → Mack@Swabia), plus the prompt/schema no-guess pair for the residual unresolvable case. Live-verified end to end. | flagship-1805 T4 → live probes Aug 15 | `delegation.py` `_resolve_nation_reference` + `prompt_builder`/`providers.py` |
| PC15-9 | P2 | **Tutorial beat IV's anchor is broken.** `Senarmont, bombard Jellacic` → "Target out of range" — Jellacic was not adjacent to Munich when the script's beat fires (he was at Bohemia by T6). The S5 anchor-drift class again (S5 re-authored Jellacic cautious to hold him); the school's suggest chip now teaches a refusal. Round 0 leads with the School. | tutorial-lesson T4 digest | `tutorial_1805.json` choreography + `test_tutorial_scenario` beat arithmetic (why did the pins hold while the live run drifted?) |
| PC15-10 | P2 | **The petition firehose, measured: 19 petitions in 24 turns** (13 jealousy confrontations, 4 rivalry, 2 Fontainebleau) — a modal nearly every turn in a winning multi-marshal campaign. This is CA9-D3's revisit slice (`DESIGN_REFINEMENT.md` §CA9 Design Answers) with its number attached; not a new owner. **Evaluated + spec'd Aug 15, 2026 → `docs/PETITION_POPUP_REVISIT_SPEC.md` (fix design F1–F10; §6 gate ✅ RULED same day at recommended defaults, user-delegated; build order §9, no gate outstanding). Slice B0 ✅ LANDED Aug 15, 2026 (eighth session — F5 latents S1/S4/S6/S9, F4 central guard, F3 narration fallbacks, F7 three drain fixes + route census; landing note = spec §9; `test_pc15_10_b0_petition_channel.py` 24). B1 "The Antechamber" onward remain — B1 is the first `.gd`-touching slice and its own session.** | flagship-1805 jsonl popup counts | CA9-D3 slice → `PETITION_POPUP_REVISIT_SPEC.md` |
| PC15-11 | P3 | "Requesting enemy terms is not available for this pair." names no reason and no remedy (N5 discipline gap on one refusal). | flagship-1805 T15 | `settlement_offers` request_terms gate copy |
| PC15-12 | P3 | Supply-headline grammar: "Massena stand 21,858 men… Massena have been 4 turns over" — plural verb for a single marshal. | variance_austerlitz T3–6, vassal-probe | `dispatch.py` supply-strain headline pluralization |
| PC15-13 | P3 | 'Alsace' did-you-mean offers "Wales, Balearics, Ulster" — string-distance suggestions with no geographic sanity. | flagship-1805 T2 | movement-target nearby suggester |
| PC15-14 | P3 | "Davout's army is recovering. Effectiveness penalty: 0% (recovered)." — a non-event as a dispatch headline. | flagship-1805 T18, naval-descent T4 | recovery-notice producer gate |
| PC15-15 | P3 | The exhausted-pair peace has no weight: Austria↔Bavaria `third_party_peace` and Austria's RE-declaration on the SAME turn (austerlitz T17; jena peace T15 → re-declare T16); plus "Austria and Bavaria have made peace without us" rendered verbatim two turns running (diplomacy-latewar T22–23). | variance_austerlitz/jena saves; diplomacy-latewar digest | pair-peace cooldown vs the AI war ladder; dispatch dedupe |
| ~~PC15-16~~ ✅ | P3 | **FIXED Aug 15, 2026** (landing note above). PARTIAL-intel regions rendered "Income: 0g / Stability: 0%" as facts — the `-1` sentinel now covers income/stability and both `.gd` readers branch. | PLAYTEST_F_SUPPLY_UNKNOWN_PARTIAL jpg → PC15_16_*.jpg | `region_panel.gd` / `map_renderer_base.gd` / `world_state.py` hidden-econ block |
| PC15-17 | P3 | fixture_t20 load pops `vassal_rebellion_imminent: Switzerland` while Switzerland is already NOT a vassal ("invest" refuses); no rebellion narrative existed in the ambient log — the silent-vassal-loss family (IGR-A) plus a stale popup surviving in the save. | diplomacy-latewar boot + T21 | vassal rebellion event narration + popup retirement on serialization |
| ~~PC15-18~~ ✅ | P3 | **FIXED Aug 15, 2026** (landing note above). (a) NO N-specific block existed — all letter hotkeys die under the auto-re-grabbed terminal focus; `Alt+<key>` route added for all six screens. (b) Enemy-phase wheel = the NV-P1 class, now closed by census (10 members PASS + a structural pin). | PLAYTEST_F screenshots → PC15_18_*.jpg | `main.gd` `_on_command_input_gui_input` / the NV-P1 census in `test_pc15_16_18_visual_fixes_2026_08_15.py` |
| PC15-H | — | **Harness (tools, not game):** the driver's enemy-phase "N attacks" counter reads `action_type` which does not exist (real key: `ai_action.action`) so every digest reads "0 attacks"; script `turns` keys are the driver's 1-based loop index, not world turn numbers (undocumented — cost one probe run); `settlement_pair_substitute_confirm` is still unanswerable by policy (left standing by design this session). One fix landed in-session under the blocker exception: `settlement_confirm` added to `DIALOGUE_TYPE_ANSWERS` + pin. | vassal-probe (first run), diplomacy-latewar (first run) | `tools/playtest_driver.py` + `docs/PLAYTESTING.md` |


## Creative Audit CA9 — filed August 8, 2026 (**TIERS 1 AND 2 LANDED August 9, 2026**)

> ### ✅ LANDING RECORD — the CA9 fix queue, tiers 1 + 2, August 9, 2026
>
> **17 commits, `4ab1cc6` … `3764f6f`. Suite 16,634 → 16,820 / 3 skipped, ruff
> clean, Godot parse harness EXIT=0 (46 scripts), boot smoke 0 SCRIPT ERROR.**
> Tests: `tests/test_creative_audit_ca9_2026_08_08.py` (181).
>
> **31 rows closed.** Tier 1 (all ten items, in order): **F6** the war-purpose
> hard stop is DELIVERED (one shared `_attach_staged_war_purpose`; the three
> battle-advance sites staged a HARD STOP and returned without it, so the client
> rendered nothing and every later command — including `end turn` — was
> swallowed; plus the `_unresolved_choice_failure` backstop widened to every
> `HARD_STOP_TYPES` member) · **the typed dialogue router** reads the court the
> player named (new `backend/commands/dialogue_routing.py`; the guard sits inside
> `handle_diplomatic_dialogue_response` behind a `raw_text` parameter so every
> typed route inherits it and the popup route is structurally unreachable —
> *the mutation reproduces the live `PEACE → ALLIANCE`*; the hard-stop
> BARE-SUBSTRING matcher is gone, and all three copies of the option rule now
> make one call) · **N5** every blocking state names the words that clear it,
> free reads pass, and plain English resolves · **F1** symmetric
> `committed_defender` in the muster band (the four CR-5 gate call sites stay
> byte-identical; the ratio reads ground truth by the same doctrine as the
> fort/terrain terms, the printed figures stay fog-legal, and the committed
> figure is qualified *"if all march"*) · **F10** one `region.can_build`
> predicate, so the briefing quotes the executor's own refusal verbatim ·
> **F14** the peace curve is continuous and its sign matches the war
> (**A GATE RE-OPEN** — see below) · **N3 + N17** the rail stops advertising
> expired state (N17's filed root cause named one of THREE clearing seams, and
> the two it missed were the permanent ones) · **F12 + N2** a capture has a
> direction (plus a third arm neither row carried: a THIRD PARTY's capture led
> France's briefing at weight 95) · **N1** one battle, one tally (the whole ES-7
> reward economy was priced off a doubled number) · **the seven narration
> one-liners** N24 N25 N26 N37 N31 N28 N32. Plus **F9's** one-guard defect (a
> prisoner in Paris is not a siege of Paris).
>
> Tier 2 (all six): **N9 + N47** · **F7 + N40** · **N6 + N7** · **F13** ·
> **N27 + F11** · **F8's copy half + F5 + N11**.
>
> **`BASELINE_SERIES` re-recorded TWICE, each consciously and each with the
> cause proved by experiment rather than argued** — F9 by a FOUR-arm run (all
> three fix arms byte-identical, because a prisoner IS the strength-0 case) and
> N6 by a SIX-arm run (N6-P0 alone and N7 alone are both byte-identical to
> control; N6's P4 rung is the whole move). N1 moves `battles_won` 104 → 98 over
> the ambient board and the series is byte-identical anyway — measured, not
> assumed. **M1–M7 byte-identical throughout, without a re-record.**
>
> **⚠ F14 IS A GATE RE-OPEN, not a bug fix**, and the row said so. CA8-D2's
> close-out (`CREATIVE_AUDIT_2026_08_04.md:934-936`) deliberately kept the ≤200g
> gold sweetener on the `relation < -50` arm. CA9 measured what that produces
> over 26 turns — +21 collects 105 g/turn and +20 PAYS 80 — and calls it
> falsified. **The armistice sibling was fixed with it as a DECLARED SCOPE
> EXTENSION** (identical `or relation < -50`, ~20× the magnitude, and the gate's
> language covered only the peace arm's ≤200g sweetener, so that number was never
> before it). Both are the user's to veto.
>
> **Nine pins re-blessed and two fixture defects repaired**, each carrying its
> reason at the seam. **Six inert pins were found by mutation and replaced** —
> including my own first cut of F14's property (monotonicity, which the old gate
> never violated) and N1's `>= 1` predecessor. **Mutation sweeps: 4/4, 4/4, 4/4,
> 6/6, 10/10, 5/5, plus per-row checks on F6, the router, F1, F10 and F12.**
>
> Reported rather than buried: a crashed run of my own mutation script left the
> `coordination_reinforcement_mixed` call site clobbered, and
> `test_live_pass_fixes_2026_07_25`'s grammar pin caught it.
>
> ### ⚠ CORRECTIONS FROM THE REVIEW ROUND (August 9, 2026)
>
> A 38-agent find→refute fleet over the committed tiers-1+2 diff returned **29
> surviving claims**. Six were confirmed against the real endpoint and are FIXED
> in commits `a4bfd57` + the follow-up; **two of them correct statements made
> above, and both corrections are recorded here rather than edited away.**
>
> 1. **"the hard-stop BARE-SUBSTRING matcher is gone" WAS FALSE.** It was gone
>    from main.py's *gate*; `handle_diplomatic_dialogue_response` kept its own
>    `if keyword in choice_lower:` over the same table, and the hard-stop
>    fallback feeds it the whole sentence. Measured over the real endpoint:
>    `Ney, move north` answered "Back Out" and popped a live war-purpose
>    dialogue ("no" is inside "north"); 3 of 12 ordinary orders consumed it; on
>    a `settlement_confirm` the same input discarded a drafted treaty. The
>    resolver now uses the shared word-boundary predicate. **The claim is true
>    as of the review round, and was not true when it was written.**
> 2. **F11 was recorded CLOSED and was not.** The relaxed phrase gate fed only
>    the "Did you mean…?" *suggestion*; `pursue Archduke Charles` still created
>    no order. Now resolved at the seam that makes the order, scoped to an
>    EXACT DISPLAY-NAME match — deliberately not fuzzy, because CA8-28 ruled the
>    strategic arms suggest a typo rather than correct it and scopes that
>    suggestion to what fog reveals. Both rules verified intact: `pursue Macck`
>    still suggests, `pursue Kutuzow` still says nothing, `pursue Charles` is
>    still refused.
>
> Also fixed: **F13 punished the marshals its own guard turned back** (−3 trust
> each, and "could not reach the battlefield in time" for men the engine
> stopped — plus the muster preview promising a march it would refuse);
> **N5's plain-English router had no negation guard**, so "I don't trust him"
> executed TRUST; **N5's objection block offered 'trust' or 'insist' while the
> validator accepted 'compromise'**, because it read an `alternative` key no
> producer writes; and **F1's committed term sat on the wrong side of the
> terrain multiplier** — my justification for the placement was factually
> wrong, and the error hid `committed_defender × bonus` effective defenders
> (measured: a real board read `favorable` at a true ratio of 0.99).
>
> Nine-mutation sweep, 9/9, after three survivors were found by it — two of
> them my own tests mirroring the router's logic instead of driving it, which
> is the third time that shape produced an inert pin in this session.
>
> **⚠ A VISUAL SIGN-OFF IS OWED** on three `.gd` surfaces this queue touched:
> the per-court fog line in the enemy phase (F7), and the `Supply: Unknown`
> sentinel on both the region panel and the map tooltip (F5).
>
> **What was deliberately NOT done is listed in `docs/STATUS.md`'s landing
> entry** — tier 3 stays gated, and eight P2/P3 rows plus the P1 **N4** (the
> petition TTL, which memo §9 Q8 makes a design question) are untouched.

### Rows still open after the tiers-1-and-2 pass

> **STATE AS OF August 14, 2026 (the PT-J landing).** Since this block was
> written: **row PT closed the through-line at all eight measured seams**
> (August 12, `PLAYTEST_FIXES_SPEC.md` §7) and **the four §4 design rows
> were ruled August 12 and BUILT August 14 as PT-J1..J4**
> (`PLAYTEST_FIXES_SPEC.md` §4.2) — which discharges **CA9 row 1's
> deferred option-A retune** (the battle-vs-territory re-weight is live:
> battles ±15 / decisive ±15 / campaign ±10 / blood ±15 on the new
> serialized campaign ledger), the peace-memory complaint (every sample
> "White Peace" — the war now remembers captures and blood), the EB-1
> condition-term row (the pensions of the fallen), and the
> commissioning-surfacing row (three surfaces on the executor's own
> gate). **What remains open below is UNCHANGED in ownership:** the
> **grievances-and-popups REVISIT slice** (user-ruled August 9 — "revisit
> grievances and popups in general … mark it as next, don't code yet" —
> owns **N4 (P1)**, N21, N8, the IGR-X7 family, the PopupQueue-order
> audit, the stash-and-raise centralization and the objection
> module-global leak; starting list =
> `docs/audits/CA9_GATE_ANSWERS_2026_08_09.md` §3), the tier-3 gated
> rows, and the enumerated unranked P2/P3 backlog. **The section does not
> close until those are disposed** — the CA8 precedent closed only when
> every gated row had been ruled.

**Gated (tier 3, needs a design gate — do not build):** F9's leverage question ·
N19 Requisitions · N20 · F4's general form · N10.
**Design questions (memo §9):** **N4** (petition TTL / re-validation — Q8 →
**answered August 9: the grievances-and-popups REVISIT slice owns it**) ·
N21 (drama budget — Q9 → the same revisit slice) · N13 (rename the ENEMY
PHASE — Q7) · N19/N20 (Q3).
**Unranked P2/P3, not in either tier and not attempted:** N8 (→ the revisit
slice) · N12 · N14 · N15 ·
N16 · N18 · N22 · N23 · N29 · N30 · N33 · N34 · N35 · N36 · N38 · N39 · N41 ·
N42 (merges with open S5-2) · N43 · N44 · N45 · N46 · F2 · F3 · F8's mechanic
half.

---

### The finding table as filed (August 8, 2026)

> **Record = `docs/audits/CREATIVE_AUDIT_2026_08_08.md` (authoritative).** Evidence:
> `docs/audits/CA9_CAMPAIGN_DIGEST_2026_08_08.md` (player-visible transcript) +
> `docs/audits/CA9_PLAY_NOTES_2026_08_08.md` (live play log incl. every claim later corrected).
>
> **⚠ These rows SUPERSEDE the first-pass severities committed in `73faf17`.** The play pass filed
> 14 findings; a 42-agent verify → refute → sweep fleet then **narrowed six** of them
> (F1 P1→P2 · F2 P2→P3 · F3 P2→P3 · F4 P1→P2 as scoped · F8 P1→P2 with the *copy* half carrying the
> weight · F9 down to one guard plus a gate question), **killed one sub-claim** (F14b — `modify_harsh`
> round 2 *does* append a territory demand), **ruled one UNDETERMINED and not to be filed**
> ("Even harsher is byte-identical" — the transcript EOFs before round 2, and the code predicts
> escalation, so the observation is evidence that round 2 *never executed*: a separate
> dialogue-routing row), **raised two from P3 to P1** (the typed dialogue router; the objection that
> never states its options), and **found 47 findings the play pass missed**.
> Where the play notes and this table disagree, **this table is correct**.
>
> Directional pillar score **≈6.3** (Aug 4: ≈6.9; Jul 25: ≈7.4). Every scorer independently
> attributed the drop to campaign *length* — these are accumulation failures, not regressions.
> Narration is the only pillar that **rose** (6.0 → 6.5).
>
> **The through-line: every system computes the right answer and then tells the player a different
> one, and the divergence is always in the direction that makes the player commit.** The advisory
> surface and the executor are separate implementations of the same rule and only one is maintained.
> The fix shape that closes most of it: **make the advisory surface call the executor's own
> predicate** — not a copy of it, not a simplified model of it, the same function.
>
> The pillar that regressed hardest is not narration. It is **trust**: six of the campaign's seven
> worst moments were the game asserting something false at the exact instant the player committed
> resources. That class is cheaper to fix than anything on the feature roadmap.

### Recommended order of work

Ordering principle: **restore trust before adding reach.** Every item in tier 1 is a case of the game asserting something false while the player commits; none needs a design gate; several are one line. Feature work on top of a lying advisory layer compounds the problem.

### Tier 1 — unblocked, days, highest trust-per-line

1. **F6 — stamp `diplomatic_dialogue` at the three PT-F1 sites** (`combat_executor.py:4489/5410/6323`, copying `:3176`). One line each. This is a total input lockout that ate `end turn`; it has no defence. Also widen `_unresolved_choice_failure`'s re-attach from the settlement family to all `HARD_STOP_TYPES` as a backstop for the next unwired dialogue type. **Do this first.**
2. **The typed dialogue router (`main.py:2092`)** — read the court the player named, or refuse and say which court is being answered. An unconfirmed permanent treaty with a great power is the most serious correctness defect in the audit. Note the client-side fix for this exact class already shipped (`diplomatic_executor.py:3222-3224`); the typed path — this game's premise — was never given it.
3. **N5 — one helper that prints the live dialogue's own option list**, applied at `executor.py:524` and `main.py:2111-2118`. `choices` is already in the return dict and thrown away. While there: swap the hard-stop substring matcher for the option-matcher twenty lines below it, or `garrison Paris` will keep declaring wars of conquest. Cheap, and it converts six "the game stopped listening" moments into questions.
4. **F1 — symmetric `committed_defender` in the muster band.** One new defaulted parameter; all four `inferred_attack_favorable` call sites stay byte-identical. Fog-safe (the formula already reads ground truth; keep `_fog_banded_strength` on the printed figure). Add a hedge row for unseen adjacent corps, and change `43,778` to `43,778 if all march`.
5. **F10 — extract `can_build(region, type, nation) -> (ok, reason)` and have both `_execute_build` and `_supply_strain_candidate` call it.** The written contract already requires this (`ECONOMY_REVISIT_SPEC.md:175`, *"names whichever remedy is LEGAL"*); it is a recurrence of closed CA8-2 on a different gate arm. Add the `repair` arm for damaged depots.
6. **F14 — drop `or relation < -50` from the sweetener branch** (`diplomatic_templates.py:3584`) and make the demand arm continuous through zero. One `if/elif`; one pin to re-bless as "hostile *and not winning*". *(Caveat: the current behaviour is gate-blessed at `CREATIVE_AUDIT_2026_08_04.md:934-936`, so this is a re-open, not a bug fix — but it is a one-line re-open of a decision the campaign falsified.)*
7. **N3 + N17 — dismiss `DOTATION_EROSION` and `COUNTER_PUNCH_EARNED`.** Two `dismiss_by_type` calls at seams that already exist (`world_state.py:5337`, `:10348`). The tray's own docstring says *"a list of things still true"*; make it true.
8. **F12 + N2 — branch `marshal_captured` on `e["nation"]`**, which the event already carries, and give the Berthier note the same direction. Apply the existing D6 ruling (*"a third party's kill is never our triumph"*). Fixture note: the CA8 pin builds its event with no `nation` key and will red on first run.
9. **N1 — dedupe the double `battles_won` increment** (`combat_executor.py:4950-4967` against `atk_participants`). This one is *not* cosmetic — it doubles the price of the entire reward economy and inverts the fiction. Re-measure the ES-7 band after.
10. **The narration one-liners**: N24 (`{failed_was}`), N25, N26, N37, N31, N28, N32. Each is one line and each is quotable, which means each is disproportionately damaging.

### Tier 2 — unblocked, one slice each

11. **N9 + N47 — cross-turn sub-beat memory, and hoist `_STANDING_ESCALATION` out of its `for…else`.** The best-written lines in `dispatch.py` have never been rendered. This kills both dominant repeats at once.
12. **F7 / CA8-15 §2a — per-nation fog fallback**, under a *new* key rendered after the nation blocks (reusing `fog_hidden_summary` would delete visible actions — `enemy_phase_dialog.gd:68` branches *instead of* the loop). Fix N40's stale `action_count` first, since the honest line will carry it.
13. **N6 + N7 — give the AI a committed-defender estimate and put the futility brake on P0.** Same root as F1; twelve suicide assaults for a 4.7:1 exchange against itself is why Europe is busy and not threatening.
14. **F13 — gate the muster relocation with the PT-F1 predicate**, and emit one event per cleared strategic order naming what it voided. *(Caution: the artillery arm it would copy omits the marshal from `arrived_names`, so extending it to infantry touches committed-strength accounting — measure M1–M7.)* Also read `jealousy_attack_results` in `turn_manager.py:187`; it is assigned and never consumed.
15. **N27 — route the three remaining surfaces through `humanize_entity_name`**, and pair it with F11's `_plausible_name_typo`-gated marshal arm in `pursue`. Note `_plausible_name_typo("Archduke Charles", "ArchdukeCharles")` is already **True** (edit distance 1) while the bare surname is correctly **False** — so the CA8-28 discipline is preserved, and only the `len(token.split()) != 1` phrase gate at `strategic_executor.py:127/152` needs relaxing.
16. **F8's copy half + F5's `-1` sentinel** (both `.gd` sites) + **N11's `treasury_delta`** (read the applied cache, like both banners do).

### Tier 3 — needs a design gate

- **F9's captured-marshal capital inversion** is a one-guard defect and can ship in tier 1; but the leverage question behind it — the flat ±3 battle term, the shared 2-decisive cap, the power-weighted side-pressure average — is all specified, blessed, and documented as anti-farming. That belongs at the **Victory & Objectives** gate with the scope boundary corrected, not in a bug sweep.
- **N19 Requisitions** — the mechanic pays only a stalled invasion. Re-scoping it to reward an army *living off* conquered ground is a design call.
- **N20** — joining "the army starved" to "upkeep fell" is an economy-design decision, not a copy fix.
- **F4's general form** — order-time supply disclosure on *every* path (not just the muster preview, which on this evidence is a post-hoc header) touches the stacking penalty, which is undisclosed even in `SYSTEMS_REFERENCE.md`.
- **N10** — separating jealousy's fire from its escalation is a mechanics change (`_check_escalation` has one caller), and it moves M7.

---


---

### The full finding table

### Confirmed

| ID | P | One-line | Root cause | Verdict |
|---|---|---|---|---|
| **F6** | P1 | The war-purpose hard stop is armed but never delivered — swallows every command incl. `end turn`, four times | `combat_executor.py:4489`, `:5410`, `:6323` discard the staged dialogue; only `:3176` stamps `diplomatic_dialogue` | CONFIRMED |
| **F13** | P1 | A jealousy autonomous attack teleported three corps into neutral Ottoman Albania and voided their orders silently | `combat_executor.py:4288` (relocation, no diplomatic guard) + `:5141-5146` (order clear, no event) | CONFIRMED |
| **F12** | P1 | `marshal_captured` (w=95) has no ownership guard — France's own triumph led as a French disaster, twice | `dispatch.py:444-454` never reads `e["nation"]`, which `combat_executor.py:2498` stamps | CONFIRMED |
| **N2** | P1 | The Berthier note on that headline is direction-blind — *"consider his ransom… or make his captors regret the keeping"* when France **is** the captor | `dispatch.py:275` — flat class→string lookup, no direction | CONFIRMED |
| **N1** | P1 | Every arrived reinforcement banks **two** battle-wins for one battle; the lead banks one — the whole ES-7 reward economy is priced off a doubled number | `combat_executor.py:4668-4674` and `:4950-4967`, no dedupe against `atk_participants` | CONFIRMED |
| **N3** | P1 | `DOTATION_EROSION` is created and **never dismissed by any code path** — a paid marshal's "unrewarded, holds 0g/turn" alert persists for the rest of the campaign | `world_state.py:5337-5351` dismisses only `DOTATION_EXPECTATION`; created `:5420`, dismissed nowhere | CONFIRMED |
| **N4** | P1 | The pending marshal petition never expires, never re-validates, and is answered against **live** state — a turn-11 card served on turn 16 would have spent 1 AP on the wrong quarrel | `jealousy.py:1390` (only clear site), `:1408-1448` never compares `context["target"]` to `marshal.jealous_of` | CONFIRMED |
| **N5** | P1 | A pending objection blocks *everything* including free reads (`status`), never names the two words that clear it, and rejects plain English meaning one of them | `executor.py:520-528` returns `choices` in the payload and omits them from the sentence | CONFIRMED |
| **F10** | P2 | The `supply_strain` headline prescribes a depot the executor will refuse — 6 identical false firings | `dispatch.py:1382-1393` models 2 preconditions; `economy_executor.py:1400-1431` enforces 8 | CONFIRMED |
| **F14** | P2 | The recommended peace pays tribute to a court France is beating, in the entire ±20 war-score dead band | `diplomatic_templates.py:3584` — `elif war_score < -20 or relation < -50:`; every 1805 war boots at −80 | CONFIRMED |
| **F11** | P2 | `pursue` has **zero** typo/display-name tolerance; `attack` is fully tolerant | `strategic_parser.py:537-554` exact-key-only → `:647-653` misfiles as region → `strategic_executor.py:580` | CONFIRMED |
| **F3** | P2 | Every 2-AP strategic order reports `cost=1` while charging 2; four code paths disagree | `executor.py:1788-1789` reassigns `action_result` in the loop instead of accumulating | CONFIRMED |
| **F7** | P2 | The fog fallback is whole-phase, not per-nation — fired once in 15 phases, and named nine courts when it did | `main.py:944-953`; `raw_nations` captured at `:940` and discarded | CONFIRMED |
| **N6** | P2 | The AI's own attack rungs sum their army and divide by **one** enemy marshal; P0 picks the *weakest* present | `enemy_ai.py:2578` (P4), `:1532-1535` (P0) | CONFIRMED |
| **N7** | P2 | The futility brake cannot fire on the shape that happens (gated on `fortified`), and P0 bypasses both brakes | `enemy_ai.py:2620-2632`, `:1575-1583` | CONFIRMED |
| **N8** | P2 | "Separate Them" is a permanent, un-cancellable warning subscription — 5 consecutive byte-identical turns | `jealousy.py:1566-1567`; `separation_flagged` never set False anywhere in `backend/` | CONFIRMED |
| **N9** | P2 | Sub-beats have no cross-turn memory: the Tyrol supply sentence ran 6 consecutive dispatches; T15/T16 are the same three sentences permuted | `dispatch.py:849-858` dedupes against a set built fresh per call | CONFIRMED |
| **N10** | P2 | Jealousy fires and escalates on the same tick — 10 of 10 escalations, 6 of 7 French pairs on fire #1 | `_check_escalation` has one caller, `jealousy.py:750`; gate `stored_rel <= -1` vs the MC-3 authored web | CONFIRMED |
| **N11** | P2 | `treasury_delta` is a fresh forward projection rendered as the turn's change; wrong on all 15 turns, wrong *sign* twice | `dispatch.py:1639` recomputes; `meta_executor.py:283` uses the applied cache | CONFIRMED |
| **N12** | P2 | AI admin actions (build/commission) can never be shown at any visibility — Prussia built three structures invisibly | `main.py:1382-1398` derives region only from `ai_action["marshal"]`; admin actions carry none | CONFIRMED |
| **N13** | P2 | 32% of "ENEMY PHASE" actions belong to France's formal allies; T15's entire enemy phase is Bavaria recruiting | `turn_manager.py:452` loops `enemy_nations` = "not the player"; `enemy_phase_dialog.gd:47` | CONFIRMED |
| **N14** | P2 | A fogged coalition member's exhaustion and treasury render as literal `0` beside a sibling that says "Unknown" | `dispatch.py:2883`, `:2886` | CONFIRMED |
| **N15** | P2 | Voice rotation keys on the **region's** battle count — two marshals said the identical line in consecutive battles | `combat_executor.py:5006`/`:5033` pass `world.battle_counts[region]` as `rotation_key` | CONFIRMED |
| **F9** | P2 | Capturing the enemy commander **subtracts 10** from your own war score — a prisoner in Paris reads as "Austria contests the French capital" | `diplomacy.py:2899-2901`, no `strength > 0` / `captured_by` guard (siblings at `:7040`, `:9671` have it) | CONFIRMED |
| **F5** | P2 | Supply capacity renders as a fabricated `0` at PARTIAL — the exact pre-commitment state | `world_state.py:7612` sentinel; `region_panel.gd:179`, `map_renderer_base.gd:2581` print it bare | CONFIRMED |
| **N16** | P2 | All six `europe_*`/`war_touches_us` arms share one dedupe identity — T16 reported the **wrong** congress | `dispatch.py:351` defaults `identity` to the class name | CONFIRMED |
| **N17** | P2 | `counter_punch_earned` is never dismissed; the rail advertised an expired opportunity for eight turns | Created `combat_executor.py:1508-1514`; `world_state.py:10348-10363` clears the flag, not the notification | CONFIRMED |
| **N18** | P2 | A marshal France announced as its own prisoner stays on the enemy order of battle for six turns | `dispatch.py:1966-2028` `_build_intelligence` has no `captured_by` check; its sibling at `:1823-1825` does | CONFIRMED |
| **N19** | P2 | Requisitions of War paid **0 on all 15 turns** — it requires standing on soil the enemy still controls, and capture is instantaneous | `world_state.py:4577-4591` `region.controller != marshal.nation` | CONFIRMED |
| **N20** | P2 | Starvation reads as an economic *win*: 40,000 dead retired both upkeep surcharges, −1,224g/turn | Post-EC-U1-reversal upkeep on fielded strength; nothing joins the two facts | CONFIRMED |
| **N21** | P2 | The drama channel has no dispatch budget — peak 13 marshal-drama lines in one briefing, flat and unranked | `jealousy.py:1781`/`:1789`/`:1845` cap fires only; resolutions/escalations/crowns/warnings uncapped | CONFIRMED |
| **F2** | P3 | Two "Casualties:" lines a few rows apart disagree ~6× on French losses, distinguished only by an apostrophe-s | `combat_executor.py:1366-1369` (CO-5, lead-only) vs `:1410-1418` (CA8-1, whole-army) | CONFIRMED |
| **N22** | P3 | The crown "passes" to nobody — 2 of 3 `glory_crown_lost` name no successor; the real transfer prints crowning *before* loss | `jealousy.py:376-380` vacancy paths share the transfer wording | CONFIRMED |
| **N23** | P3 | `jealousy_restlessness` has exactly one hardcoded template, rendered 7×, beside a sibling with a 7-variant bank | `jealousy.py:1822-1825` | CONFIRMED |
| **N24** | P3 | `"Davout, Soult and Murat **was** expected"` — the plural fix landed on one of two banks | `battle_report.py:462` hardcodes `was`; sibling `:445` uses `{failed_was}` correctly | CONFIRMED |
| **N25** | P3 | `"again, 1 turns after the last"` — no singular arm | `jealousy.py:687` | CONFIRMED |
| **N26** | P3 | `"Starving — supply has failed at Tyrol two turns running"` ×17, on a famine the headline calls "3 turns" on the same screen | `dispatch.py:1289-1293` hardcodes the phrase; `len(turns)` is in scope | CONFIRMED |
| **N27** | P3 | Raw camelCase marshal keys reach terminal, enemy-phase dialog and diorama nameplate — 135 occurrences to 44 spaced | `humanize_entity_name` (`display_names.py:1147`) called only by `_build_intelligence`; `utils.gd` repairs nation tags only | CONFIRMED |
| **N28** | P3 | `"Our scouts report activity within **Ottoman**'s borders"` — a raw tag the client is documented as unable to repair | `main.py:947-951`; `utils.gd:186` names Ottoman as the documented exclusion | CONFIRMED |
| **N29** | P3 | Berthier can never speak about the treasury — 21 classes, 21 notes, rung 2/3 unreachable | `dispatch.py:2186` short-circuits on `headline_class in _HEADLINE_BERTHIER_NOTES` | CONFIRMED |
| **N30** | P3 | The anti-monotony cooldown keys on the internal P-rule label, not the pact the player reads — Hesse re-raised one pact 5× | `ai_diplomacy.py:322` `_cooldown_keys`; `TYPE_LAPSE_COOLDOWN = 6` | CONFIRMED |
| **N31** | P3 | Vassal loyalty prints a `+2` that a clamp at 100 discarded, 4 times | `vassal.py:577` clamps, `:586` gates on the unclamped delta, `:597`/`:623` print it | CONFIRMED |
| **N32** | P3 | Talleyrand's vassal trend derives from autonomy tier alone — *"Holland: loyalty 100, falling"* against its own `+2` events | `diplomatic_advisory.py:529-531` | CONFIRMED |
| **N33** | P3 | `"Other"` is up to 36% of the revenue side and is the only unnamed line; every drain is itemised | `meta_executor.py:284-288` computes it as a residual; `ledger.py:384-389` already breaks it out | CONFIRMED |
| **N34** | P3 | `[HINT] X is undefended — attack to capture it!` never looks past the target province; contradicted the objection two turns later | `movement_executor.py:661-669` | CONFIRMED |
| **N35** | P3 | The mutual-spiral line says *"is now mutual"* every time it re-fires | `jealousy.py:826-851` | CONFIRMED |
| **N36** | P3 | One grievance resolution narrates twice, back to back, structurally | `jealousy.py:1714-1724` appends after `clear_jealousy` already emitted | CONFIRMED |
| **N37** | P3 | A rout's recovery is `severity: "good"` and missing a sentence terminator: *"penalty: -40% The rout's disorder lingers"* | `world_state.py:10210`; `dispatch.py:2124` | CONFIRMED |
| **N38** | P3 | The Fontainebleau quote says "carry" and computes the *increment* — latent, did not bite (all pensions were 0) | `jealousy.py:1255` uses `get_shortfall`; applied cost uses `compute_rente_face` | CONFIRMED |
| **N39** | P3 | AI-vs-AI rivalry/downgrade events have no persistent surface; 12 sponsorships (all aimed at France) reach only the campaign log | `ai_diplomacy.py:2591-2626` not logged, not a dispatch type; `instruments.py:199-209` carries no `message` | CONFIRMED |
| **N40** | P3 | Per-nation `action_count` is stale after the composition collapse — wrong on 8 nation-turns | `main.py:761` sets `actions` and not `action_count` | CONFIRMED (latent) |
| **N41** | P3 | War exhaustion runs to 200 and stops narrating at 80 — the whole second half of the campaign, raw integer, no denominator | `coalition.py:61` vs `:1447` | CONFIRMED |
| **N42** | P3 | The pursue confirmation narrates the raw key back (`"pursuing ArchdukeCharles"`) — merge with open **S5-2** | `BUG_FIXES.md:1387`, `strategic_executor.py:393` | CONFIRMED (already filed) |
| **N43** | P3 | The `literal_fidelity` beat asserts a cause it never checked — *"per your orders"* when three unrelated mechanics produced the absence | `marshal_voice.py:118-130` is a pure per-turn scan | CONFIRMED |
| **N44** | P3 | Silent retarget: `attack Charles at Bohemia` fought at Franconia; the rejected destination is never echoed | `executor.py:449-459` resolves enemy-first and returns his location | CONFIRMED (executor half) |
| **N45** | P3 | Glory — the number the whole drama system runs on — is readable on exactly one screen | `get_glory_score` has one consumer outside `jealousy.py`: `marshal_overview.py:166-169` | CONFIRMED |
| **N46** | P3 | The rente is a treadmill by construction: face sized at grant time, expectation keeps climbing to 300 | `dotation.py:446-458` vs `get_expectation` | CONFIRMED |
| **N47** | P3 | `_STANDING_ESCALATION` has **never fired** — reachable only via a `for…else` that needs the standing class to be the sole candidate | `dispatch.py:810` | CONFIRMED |

### Corrected or killed

| ID | Original claim | What actually holds |
|---|---|---|
| **F1** | "The muster preview sums only the PLAYER side; is enemy fog ever considered?" | **NARROWED.** The enemy *primary* is in the denominator at ground truth — this is not a fog defect at all. The omission is the enemy's **muster** (`objection_v2.py:880` has no `committed_defender`), violating `COMBAT_OVERHAUL_SPEC.md:155`'s own "Symmetric for a reinforced defender (GR5)". Measured once (+4,800); the *attacker* over-promise is 4–8× larger (Franconia: 54,408 predicted, 18,101 fought). **P2**, and a sub-row of the already-owned VP-D2, not a standalone P1. |
| **F2** | "P2 — the battle report shows lead-only casualties, no label" | **NARROWED to P3.** CO-5's reconciler is a *pinned contract* (`test_combat_overhaul_co5_report_consistency.py`); CA8-1 moved the terminal to whole-army four weeks later and created the collision. Confined to `main.gd` — `_format_berthier_report` prints no casualty numbers, so the enemy phase is unaffected. The intervening ally line closes the arithmetic. The three-number T2 claim is unverifiable (pre-reset). |
| **F3** | "P2 — the action economy's advertised price is wrong" | **NARROWED to P3.** No player-visible number is wrong: `main.gd:2866-2870` uses `cost` only as a `>0` gate and prints the honest post-deduction `remaining`. It is an API-contract defect plus a separate copy gap (non-literal strategic orders quote no price at all) plus a latent arithmetic fragility (the loop conflates iteration count with AP total). |
| **F4** | "The muster preview never mentions supply" | **NARROWED to P2 as scoped.** True, but **all four musters read "favorable"**, so the gate at `:4091` never armed and the block was *prepended to an already-resolved battle* — a `supply_note` in `_build_muster_preview` would print after relocation and after the battle. Also Swabia is 6 of 64 attrition events; the general defect is "no order-time supply disclosure on **any** path". And the dominant term is the undisclosed `(num_marshals-1)×1%` stacking penalty, which fires **under capacity**. |
| **F5** | "Supply capacity is UNLOOKUPABLE off own soil" | **NARROWED.** It is lookupable at FULL (scout, 1 AP, or stand there) on both the region panel and map tooltip. The defect is the fabricated `0` at PARTIAL specifically. Note the proposed `-1` sentinel fix needs both `.gd` sites edited — `format_number(-1)` returns `"-1"`. |
| **F8** | "Soult's SUPPORT order binds to the ally's LOCATION at issue time" | **NARROWED to P2.** It binds to his **name**, tracks him dynamically, and fails on `order.target == primary.name` (`combat_executor.py:1071-1073`) — he must lead the battle. Only **one** of the cited refusals is that defect (T6/Tyrol, where Ney was *in the battle* as a reinforcement); T8 is correct-by-doctrine (Ney absent entirely); T13+ is a second mechanism — silent auto-completion on `ally_safe` (`strategic.py:1935`), which does announce itself. What is genuinely P1-shaped is the **copy**: `strategic_executor.py:1326-1329` states an unconditional guarantee the code scopes twice. |
| **F9** | "P1 — `base_side_pressure` is the root cause; leverage is unconvertible" | **NARROWED.** Three of the four mechanisms are the specification implemented verbatim: the flat ±3 battle term (`DIPLOMACY_SPEC.md:1179-1183`), the 2-decisive cap (`:1190`, *"prevents farming"*), and the power-weighted average (`WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md:218,261` — *"This is intentional anti-farming behavior"*). Only the captured-marshal capital inversion is a defect, and Mack was taken on **turn 8**, four turns after the observation. The bilateral route previewed `COUNTER` at 45, not a wall. Tuning question at the Victory & Objectives gate, plus one guard. |
| **F14b** | "No draft at any harshness can demand territory" | **KILLED as stated.** `modify_harsh` round 2 does append one (`diplomatic_executor.py:3888-3894`), and `_ease_suggestion_until_not_rejected` (`:3519-3529`) is the stronger suppressor. |
| **CA9-P2** | "Even harsher is byte-identical" | **UNDETERMINED — do not file.** The digest EOFs at the initial confirm; the two harsher rounds are absent. Code predicts escalation to 450g + territory, so the observed 300 is evidence round 2 *never executed* — a dialogue-routing defect, a separate row. |
| **CA9-P2 (parser)** | "`accept Portugal's proposal` → fuzzy Por→Pru" | **CORRECTED, and worse.** No nation matching happens at all. `main.py:2092` substring-matches the *option label* against the raw text and applies it to whichever dialogue is **active** (`diplomatic_executor.py:3218`). Prussia **was** ACTIVE (`digest:637`), contradicting the note. Any court name in an accept/reject sentence is ignored, including the correct one. Three copies of the rule: `main.py:2092`, `main.py:1901`, `diplomatic_executor.py:3380`. **P1.** |
| **CA8-15** | "still unbuilt" | The prune half **is** live (`main.py:764-780`). The unbuilt half is the §2a remediation — route suppressed nations to the fog line. |
| **CA8-12** | (Aug-4) digest doesn't latch | Remains **REFUTED** against the shipped client. |
| **Play notes T7-T8** | "13 actions across Austria, Bavaria and Spain by T8" | Turn **7**, and the third nation is **Britain**, not Bavaria. |
| **CA9-P3** | "AI never commissions a marshal" | **UNDETERMINED.** By T13 Austria met both visible gates (roster 2 < 3; treasury 4,577 ≥ 3,500+1,000) and never fired. Which downstream gate blocked it — manpower, AP, or admin-rung contention — I could not determine. Worth measuring. |

---


### Open questions for the developer

1. **Should the muster preview be a *decision* surface at all?** Today all four musters read "favorable", so the gate at `combat_executor.py:4091` never armed and the block was prepended to an already-resolved battle. Fixing the arithmetic (F1) makes more previews read unfavorable, which arms the confirm modal — is that the intended texture, or should the preview move to a pre-commit seam (the `support`/`move` response) where it can be acted on?

2. **Is 6% attrition on a six-corps stack a trap or a lesson?** The stacking term (`(n-1)×1%`, fires under capacity) is documented as intentional (`SYSTEMS_AUDIT_V2_FIX_PLAN.md:334`, "intentional design") and is disclosed nowhere — not in the ledger, not in the region panel, not in `SYSTEMS_REFERENCE.md`, which describes the formula without it. Disclose it, or reduce it? Both are defensible; the current state is neither.

3. **Should conquest pay?** France took four provinces and income moved +4.2%. With `Requisitions` structurally unreachable for a winning army (N19) and 16,000g idle, the war has no economic payoff and the treasury has no sink. Is the intent "war is a money pit and that's the point", or should taking Vienna feel like taking Vienna?

4. **What is the war-score → terms curve meant to look like?** At +19, seven wins, zero losses, the game recommends paying tribute. At +30 it would demand territory. Is the ±20 dead band deliberate, and if so what is the player supposed to do with a war they are winning but not winning *enough*?

5. **What should a national design change cost in credibility?** Austria shifted design three turns running (Revanche → survival → Revanche), each a MEDIUM dispatch beat. The content is excellent; the churn devalues the beat. Hysteresis, a cooldown, or accept it?

6. **Does the player need a verb for a foreign war they can see coming?** Talleyrand reported Austria at weight 72 against Russia — one rung and thirteen points from the first AI-initiated war in the game's history — and the assessment surface offered no action, while `sponsor_design` exists at 1 DP and was never named there.

7. **Should the "ENEMY PHASE" be renamed, or split?** 32% of its actions are France's own allies; T15's entire phase is Bavaria recruiting. It is Europe's phase, not the enemy's.

8. **Is the marshal petition meant to expire?** It currently blocks the whole channel indefinitely (turn-11 card still pending at turn 16, with at least four petition-worthy events unable to queue behind it) and is answered against live state. A TTL, a re-validation at serve time, or a queue?

9. **How much drama per turn?** AI-6 landed a 2-per-dispatch cap on intent narration for exactly this failure mode; jealousy — the noisier producer — has caps on fires only, and peaked at 13 lines in one briefing, unranked. Should the same budget apply?

10. **Was any AI commission blocked, or just not attempted?** By T13 Austria met both visible gates in `find_ai_commission` and never fired. The Marshalate's stated both-sides recovery path produced zero enemy commissions in a campaign that annihilated one enemy marshal and routed two more. I could not determine which downstream gate held — worth measuring before EA, since it is the AI's only path back from attrition.
## Creative Audit — filed August 4, 2026 (**✅ SECTION CLOSED August 7, 2026 — 25 of 28 FIXED, 1 REFUTED, 2 CANONIZED/HOMED**, see landing records below)

> ### ✅ LANDING RECORD — THE CLOSE-OUT GATES, August 7, 2026 (user-delegated)
>
> **Gate record = `docs/audits/CREATIVE_AUDIT_2026_08_04.md` §10 (authoritative).** The
> user directed *"make design gate decisions and finish CA sweep"*; the four gates the
> sweeps left standing were held under that delegation and their rows BUILT the same
> session. Tests: `tests/test_ca8_gate_closeout_2026_08_07.py` (46).
>
> **CA8-D2 → CA8-3 + CA8-24 + CA8-27 FIXED (§10.1).** One new single source
> `diplomacy.calculate_side_war_score` (five pair components summed across the war's
> opposing side, each re-clamped at its pair cap — reduces byte-identically to
> `calculate_war_score` for one opponent, pinned) + the instance-resolving
> `get_side_war_score_for`. Three consumers: the multi-participant HUD collapse row
> (score/breakdown/battles/recent/duration/trend now report the WAR — CA8-24's
> one-screen contradiction dies, no `.gd` change), the incoming settlement-offer
> producer (direction + EC-W4 amount read the war France is actually fighting — the
> audit's measured white-peace-from-the-winning-side dies, with the pairwise 0 pinned
> as the falsifiable control), and `_build_base_terms` (Talleyrand prices the war, and
> **territory cession now requires `war_score < -20` STRICTLY** — the `relation < -50`
> arm keeps only the ≤200g gold sweetener; "France cedes Nivernais at +2" is
> impossible by construction). Scope boundary recorded: the §6.3 side-pressure
> acceptance machinery and the Stage-D third-party peace seams are untouched.
>
> **CA8-D6 → CA8-26 FIXED (§10.2).** Four success classes from EXISTING events (no new
> campaign-log type, the 156 pins hold): `enemy_eliminated` 93 (gated on France having
> OPPOSED the fallen court in a war instance — a third party's kill is not our
> triumph) · `capital_stormed` 92 · `victory_won` 73 (annihilation outcomes stand
> alone; a tactical win counts only when joined to an enemy corps' forced rout on the
> same field, so an AI-vs-AI rout never reads as French news) · `region_taken` 68
> (with a homeland-liberation arm: "X is French again"). The weight principle replaces
> the retired "an opportunity never outranks a wound" comment: **at equal scale the
> wound still leads; a triumph outranks only a wound of smaller scale than itself** —
> pinned as arithmetic. The victory absorbs the bare conquest of its own field
> (CA8-5's discipline); elimination + stormed capital may both appear (distinct facts).
>
> **CA8-17 FIXED at the reduced scope (§10.3) — Voice Bible §16.1a AMENDED.**
> `SPOKEN_BLOCKER_PHRASES` (the **nine** negative-capable acceptance components as spoken
> clauses — the audit row said 8; the §10.6 review proved `war_objective_alignment`
> negative-capable too) + per-register leaning/holds-out framings on the LIVE ally-petition suffix
> idiom (`_castlereagh/_hardenberg/_metternich/_einsiedel` + `_chancery` fallback
> re-lookup; the unsuffixed templates survive as last resort). The per-court rows now
> carry `top_blocker_component` beside the label; Talleyrand's review/blocked/
> white-peace headings speak the same clauses (templates re-formed to colon/em-dash so
> the label fallback still scans — the "spoken three times on one screen" repeat dies).
> Labels stay in tables; phrases go in mouths. Named-envoy registers beyond the four
> cast suffixes remain DEF-1's scope — zero per-court banks added.
>
> **CA8-D4 answered → CA8-16 bounded build LANDED (§10.4).** The gate question — what
> may `hegemony_pressure` sound like besides fear — is answered with three frames
> (arithmetic/interest, opportunity, history/law; Castlereagh's line is the model),
> and every one of the 24 hegemony banks gained a THIRD variant in a non-fear frame
> (24 authored lines; the measured 72%-exact-repeat lever moved by bank size, the only
> lever the row's own analysis admits). The single `len == 2` pin consciously flipped
> to `>= 2` with the depth pinned in the close-out file. Full roster authoring across
> the other four reasons stays DEF-1's.
>
> **CA8-19 RULED (§10.5) — full parity REJECTED as design, the row CLOSED.** Garrison
> assault stays its own resolver (no opposing commander, no morale to break, no
> maneuver — the rule now stated at the resolver head and pinned structurally); the
> repulsed-attacker glory divergence is **CANONIZED** (JEALOUSY_SPEC §1 gains the
> exemption: the ladder prices reputation between COMMANDERS) with the no-glory pin
> in the close-out file; and the garrison half of CA8-25 is **HOMED at the Battle
> Gallery gate** (`BATTLE_DIORAMA_SPEC.md` §12.5 rider: a garrison contingent —
> piece + coat, no locket, no standard-take — with its completion definition).
>
> **Final section accounting: 28 rows → 25 fixed · 1 refuted (CA8-12) · CA8-19 closed
> by ruling (its three latent defects were fixed in sweep 4; the parity ask is
> rejected design, not deferred work) · CA8-25's garrison half homed with an owner,
> landing, and completion definition per GR9. Nothing in this section remains open.**

> ### ✅ LANDING RECORD — CA8 sweep 4 (the last ungated rows), August 4, 2026
>
> **Fixed and landed: CA8-28, CA8-20, the three latent defects inside CA8-19, and
> CA8-16's two gate-free halves.** Four commits (`9ca0374`, `412204e`, `f132d2e`,
> `e97b1f9`). Tests: `tests/test_creative_audit_ca8_2026_08_04.py` (+55, now 160)
> plus a rewritten `TestGarrisonCombat`. Suite 16,281 → **16,334 / 3 skipped**,
> ruff clean, corpus 514/514, no `.gd`. **`BASELINE_SERIES` re-recorded once,
> consciously, with attribution proved by experiment (below). M1–M7 byte-identical
> throughout.**
>
> A 16-agent find→refute fleet verified every filed claim against master before a
> line was written. **It corrected five of them, and two corrections changed what
> got built.**
>
> **CA8-19 stays GATED, and its three latent defects are landed separately.**
>
> **(i) is the live one, and it is a MECHANICS defect, not the hygiene item it was
> filed as.** `_resolve_garrison_combat` recomputes coordination (added July 2026)
> while both its pipeline calls still passed `skip_coordination_clear: True` — a
> flag written in March, when this path computed no coordination at all, and never
> revisited when the recompute arrived. So every garrison assault stamped an attack
> bonus on every eligible marshal in the origin province, and **nothing in the game
> ever removed it**: not `advance_turn`, not the tactical tick, and the fields are
> not serialized, so a save/load was the only reset. It is read back through
> `_committed_reinforcement_strength` — **measured +16.0% committed attacker
> strength with no marshal's strength changed** — which feeds combat resolution,
> the CO-2 odds band and the CR-5 bad-odds modal the player decides on. **Two more
> seams of the same class, neither in the filed row, both proven by probe:** the
> auto-bombardment-kill exit of `_execute_attack` advances the attacker *before*
> calling the pipeline, so `{attacker.location, battle_region}` had already lost
> the origin; and `Marshal.clear_combat_transient_state` held **none** of the
> eleven coordination fields despite its own docstring promising to hold every
> combat-transient field — which is why the reckless-cavalry auto-charge, the one
> `resolve_battle` call site with no recompute on either side, could fight on
> leaked numbers. The names now live on `Marshal`, so the executor's clear and that
> method cannot drift again.
>
> **(ii) was decided, not left in a third state.** The garrison-stomp glory
> exemption was production-dead: `record_battle_glory`'s `is_garrison` argument
> could never be true, because the garrison path passes `battle_result: None` and
> the same guard already excluded it — the spec's rule was satisfied *by accident*,
> and its only test was a direct unit call carrying a fifth argument the game
> cannot produce. **DELETED**, and the rule it implemented is now **stated** at the
> guard, which is stronger than a flag every caller must remember. Behaviour is
> byte-identical and pinned end-to-end for the first time. **Divergence on record
> for the CA8-19 gate:** spec §1's DEFEATS block exempts only "Garrison defense",
> so a marshal *repulsed* from a garrison should read −1 and reads 0. Wiring that
> arm means ungating step 9.5 as well, which **mutates `jealous_of`** — the derived
> −1 that coordination, objections, reinforcement, muster and the enemy-AI ally
> filter all read. That is drama behaviour with M7 exposure and it belongs with the
> parity work, not in a copy sweep.
>
> **(iii)'s stated consequence is FALSE, and that is the headline correction.** The
> `elif` is indeed unreachable — a garrison hold is a defender victory and its ctx
> says so, so `elif defender_won:` always claims it first. But "an AI army repulsed
> from a French garrison accrues no war exhaustion at all" is wrong: the arm above
> it already charges him, **measured Austria +6**, and the full 3×2×2 matrix
> accrues on every cell of the running board. Two independent agents reproduced it;
> a third contradicted them and was itself refuted (its probe ran on a bare
> `WorldState`, i.e. the legacy map, where the third-party arm is deliberately
> Europe-gated). Deleted as dead code rather than repaired: flipping the hold ctx
> would **suppress** the defender's `battle_win` threat, `decisive_victory`,
> coalition shock and war-score record that the live arm grants.
>
> **Found while pinning (iii): `TestGarrisonCombat` has never tested anything.** Its
> fixture looks up `"London"`, which does not exist in the 19-region legacy world,
> so all seven tests returned at `if not london: return` and garrison combat was
> invoked **zero** times. Re-sited, with the escape hatch replaced by an assertion.
> **On their first real run two of them failed**: the authority test, because boot
> authority sits at its 100 ceiling so a +5 capital bonus is unobservable; and the
> war-exhaustion test was a tautology (`>= initial_we`, which cannot fail because
> exhaustion only ever rises — deleting the mechanic kept it green, mutation-
> verified). Both now pin exact numbers, plus the AI-repulsed mirror the filed row
> said was broken. **Drive-by:** `test_attack_auto_move_refreshes_fog` gated on bare
> success, which also admits the ATTACK→PURSUE upgrade where nothing moves — a
> **~12% flake on clean master** (36/300 seeds, reproduced in a detached worktree),
> now gated on the marshal having moved.
>
> **CA8-28 — and the naive fix is a trap whose regression is invisible to the pin
> that exists to catch it.** `_fuzzy_match_region` auto-corrects `Pass`→Nassau,
> `Line`→Berlin, `Guns`→Brunswick **silently** — no error, no prompt — so
> delegating to it straight would give "Ney, hold the pass" a real 2-AP standing
> HOLD on a province 200km away: the exact defect PARSE-NEG landed to kill. It
> would not have been caught. `test_parse_negation.py` and the golden corpus both
> call `CommandParser.parse` and never construct an executor, so under the naive
> delegation the parser's target stays `"Pass"` in both arms, the assertion
> (`target != "Nassau"`) passes, and the order exists anyway — measured on the
> counterfactual. Hence: `_plausible_name_typo` gates the auto-correct arm; only
> single **tokens** reach the fuzzy pass (phrases stay with the existing scan —
> aiming a fuzzy matcher at a sentence is how that family got in); the arm sits
> *after* the IGR-A3 nation check so "march to Austria" never suggests Asturias
> again; and every pin is executor-level. PURSUE offered nothing and SUPPORT
> offered an unranked dump of the whole roster; both now rank, and PURSUE suggests
> only from `get_visible_enemies` — a ranked guess at a hidden army is free
> intelligence. **Fixed in passing:** `_resolve_region_from_phrase`'s marshal
> fallback scanned *every* marshal in the world, so naming a fogged foreign army
> answered with the province it was standing in (R5).
>
> **CA8-20 — the row's fix shape was right for the wrong reason, and its cost was
> understated.** A sort-key change cannot fix it (the list is already sorted on
> that metric and on fresh conquest every candidate is 0), and a bare `> 0` filter
> is insufficient (the eligibility list has no disruption term, so a 200g province
> with a hostile army on it sorts first and still pays nothing). One predicate,
> `dotation.estate_yield`, now carries `get_estate_income`'s own two terms narrowed
> to a region. The row's *stated* reason for siting it at the AI call site — that
> two named tests would red on an in-`dotation.py` change — **is false; neither
> would.** The real reason is the player's choice: three player surfaces share that
> list, estates appreciate, and the reward dialog already discloses "covers 0g of
> 120g". Also wired at the erosion notification, which told the player to endow
> whenever the list was non-empty — the same lie the §0.6.8 item-4d contract two
> lines above it forbids. Measured cost of the defect: **6 of 9 ambient grants
> closed 0g of the gap**, and since arm 1 returns unconditionally on a non-empty
> list, the rente was unreachable while any worthless province remained — Austria
> ended **1,761g/turn** in household bills with one marshal endowed to **1,137g**
> against a 300 cap.
>
> **`BASELINE_SERIES` re-recorded once, consciously.** A reshaped tail, not a time
> shift: divergence at index 12 (63 → 79), anti-France alarm ending at 36 rather
> than 0, because Austria stops bankrupting herself (treasury 1,334 → 10,485) and
> stays a live belligerent. **Attribution verified by experiment, not by argument:**
> with the filter clause alone disabled the prior series reproduces byte-for-byte.
>
> **CA8-16 is NOT built as filed, and the gate row is corrected on three counts.**
> Two gate-free defects were split out and fixed — Hardenberg's first
> `hegemony_pressure` line was the generic hawk line with `{nation}` pre-filled as
> "Prussia" (a named override delivering a copy of the register line it exists to
> replace), and a **named envoy lost his authored attribution** whenever his reason
> had no bespoke bank (`Araujo, measuring the room:` → `Araujo:`), which is 16 of 19
> courts on `agenda_pursuit`, i.e. the common path. **The re-key is refused as
> cosmetic churn:** with two variants the key's image is `{0,1}`, so any
> turn-independent term is a phase shift, and the 19 courts hold *disjoint* banks so
> the existing name term decorrelates nothing. `DESIGN_REFINEMENT` CA8-D4 now
> records that the surface is **38 bespoke lines, not 19**; that it is pinned
> **once**, on one bank, not twice (a third variant injected into all 24 banks runs
> the full suite at 1 failed / 16,280 passed, so every bespoke bank grows with zero
> pin flips, and the row's "growing the banks is a conscious flip" cost model was
> false); that its question aimed at `enemy_phase_dialog.gd`, which is CA8-6/21's
> surface; and the measurement that settles it — **72% of all diplomat lines
> composed in a 40-turn campaign are exact repeats**.
>
> **The sweep-3 review's four unexamined areas, closed.** Two were clean (the
> save/load round trip is lossless; the double `_build_marshal_arcs` call is pure
> and costs 0.39ms). Two hid real defects, **both inside the function that review
> declared clean**: the retreat/rout branch was the *only* unguarded branch in
> `_build_marshal_arcs`, and vassal assimilation is the live path — measured, a
> marshal who routed three times under Bavaria's flag, was assimilated, and was
> crowned under France **led the French dispatch at weight 91**; and `hunted_by` was
> **outcome-blind**, so winning two defensive battles on consecutive turns narrated
> as "hunted across the frontier" — verbatim the shape the CA8-9 review believed it
> had killed for `crown_lost`, surviving on a different term and spared the headline
> only by the accident that `fall_turn` stays None for a pure win-hunt. Its line
> invented its own evidence too: `max(fled, 1)` reported "across 1 frontier" for a
> marshal who never withdrew. Plus three dead names — one of them
> `marshal_captured`, the **highest-weight headline in the file (95)**, rendering
> "Kingdom Of Italy holds him prisoner." — a missing definite article the same
> sentence already uses, a raw `target` in the campaign log, and a CA8-8 comment
> that asserted `level` was absent on old saves, which is false.
>
> **Mutation sweeps: 4/4, 7/7, 9/9, 6/6 killed. TWO INERT PINS FOUND AND REPLACED,
> both by mutation rather than by review.** The multi-word CA8-28 test drove
> "march to the Bavarian frontier" through the parser and passed with the guard
> **deleted**, because the parser resolves that phrase upstream and the arm was
> never reached — it now pins the helper directly and asserts the unguarded matcher
> really would have answered "Did you mean 'Oran'?". And every CA8-20 test pinned
> the *helper* while reverting the AI call site to the unfiltered list left all of
> them green — the rung is the entire row, and two tests now drive
> `_find_dotation_grant` itself in both directions.
>
> **NOT BUILT, with the reason recorded rather than deferred vaguely: CA8-17.** The
> honest sizing is not the row's. The full per-diplomat build is **90 authored
> strings** (9 phrase slots × 5 registers × 2 bands) — 2.4× the entire Slice-H ally-
> petition arc — and it **cannot be completed anyway**, because 11 of the 19
> reachable courts have named envoys whose registers the Voice Bible explicitly
> homes to **DEF-1 Roster Voices**, so a "full" CA8-17 would silently annex another
> row's scope. Worse, the fix contradicts its own normative source: **Voice Bible
> §16.1a records the four current templates verbatim as committed exemplars**, so
> the row requires a Bible amendment, not merely conformance. Two of the row's own
> justifications are also wrong — the string is **not** title-cased (it is a hand-
> authored sentence-case label; the `.title()` call is unreachable), and the "no
> jargon" rule it invokes is scoped to bloc-naming lines. Found in passing and
> worth more than the row: the same label is spoken **three times on one screen**
> (Talleyrand's own popup heading says "the largest pressure remains Settlement
> legitimacy" directly above the per-court table), and `_MissingSettlementSlot`
> renders raw `{braces}` to the player with **no exception and no test failure**.
> A reduced build — one spoken-register vocabulary over the 8 negative-capable
> components plus per-register framings, ~19–21 strings, two files, no `.gd` — is
> specified and buildable, but it needs the Bible amendment and therefore a gate.
>
> **Also routed, not fixed:** `strategic_executor`'s `dest`-only rebind leaves the
> raw phrase on `order.target`, which `strategic.py` uses as HOLD's arrival
> predicate — so that write-back is a change to the per-turn strategic tick, not
> the display-only tidy it looks like. And nothing caps an AI grant at the
> remaining shortfall, so the AI can still over-endow as provinces appreciate —
> a sibling defect CA8-20's filter surfaces rather than solves.
>
>
> ### ⚠ ADDENDUM — the sweep's own 59-agent review, same day (`a2a9e0c`)
>
> Held after the four commits, on a pre-snapshotted diff. **52 findings: 27
> confirmed, 14 partial, 11 refuted. Four changed shipped behaviour, and two of
> those were introduced or claimed by this sweep.**
>
> **Introduced here.** CA8-20 narrowed the erosion notice's predicate to "pays"
> and left the else-branch copy written against the old one, so a player holding
> four freshly-conquered provinces was told *"no conquered province remains to
> endow"* while his own marshal card offered all four **by name on the same
> tick**. Three arms now; the middle one covers both of `estate_yield`'s terms
> and deliberately does not promise that waiting is enough, because a disrupted
> province does not settle — it drains.
>
> **A claim in the CA8-19 commit message is FALSE and the review proved it.**
> That message says moving the eleven field names onto `Marshal` means the
> executor's clear and `clear_combat_transient_state` "cannot drift again". The
> drift is not in the NAME list, it is in the REGION set: `_calculate_overwatch`
> stamps `overwatch_penalty` on every attack participant, and artillery
> reinforcing from an ADJACENT province deliberately never relocates, while the
> attack path's clear is keyed on three regions that cannot contain his.
> **Measured −9% attack, permanent** — same class, same read path, one field
> over. The clear is now seeded from the participants, which is the general form.
>
> **The narration commit fixed one hunt line and left its twin** — the weight-91
> HEADLINE, which is the string the player actually reads, since `reversal_line`
> supersedes `line` whenever it exists. **The sweep's own test asserted the
> fabrication.**
>
> **CA8-28's R5 guard keyed on WAR STATUS rather than visibility**, so an ALLIED
> marshal drawn on the player's own map at full visibility stopped being a legal
> destination and *"march to join Deroy"* degraded to a shrug. Worse: the R5 pin
> sampled `hidden[0]`, which boot dict order makes **Deroy — an ally at full
> visibility** — so the pin exercised the ally case while its name claimed the
> opposite, and **locked the regression in rather than catching it**. Now keyed
> on the fog directly, which subsumes `get_visible_enemies` at the same PARTIAL
> line.
>
> **Pre-existing, fixed because the sweep made it self-contradictory:** two
> player surfaces quoted an estate's income without the EC-W1 disruption term, so
> the button that endows a province priced it at 200g/turn while an enemy army
> stood on it and it paid 0.
>
> **THE LEDGER PARAGRAPH FOR THE `BASELINE_SERIES` RE-RECORD WAS FALSE**, and the
> correction is kept visible rather than quietly swapped. *"Recruits on 13 turns
> instead of 22"* compared one arm with itself — 13 and 22 are two different
> metrics of the UNPATCHED run — and *"stays a live belligerent"* is inverted:
> Austria is at WAR on all 40 turns in **both** arms and ends **larger**
> unpatched. The series literal itself was re-verified correct, independently.
>
> **Three more inert pins closed:** the dead-name structural guard killed **1 of
> 7** reintroductions (now an AST walk allow-listing the two slots that
> legitimately carry a marshal name — 7/7); the reckless-charge defender clear
> was an `inspect.getsource` substring match, which cannot tell whether the line
> RUNS; and the register-bank duplicate guard walked **5 speakers of 19**, so
> Hardenberg was covered by luck. Plus a dead loop shipped inside the CA8-20
> fixture. **8-mutation re-check, 8/8 killed — including the two that survived
> the first pass** (the overwatch leak had no test at all, and one mutation
> string was wrong so that pin went unverified).
> **Still at their gates: CA8-3 + CA8-24 + CA8-27 (CA8-D2), CA8-26 (CA8-D6),
> CA8-16's authoring and CA8-17 (a narration/voice gate), CA8-19's parity work.**


> ### ✅ LANDING RECORD — CA8 sweep 3 (the narration pillar), August 4, 2026
>
> **Fixed and landed: CA8-9, CA8-8, CA8-25.** Tests:
> `tests/test_creative_audit_ca8_2026_08_04.py` (+33, now 83). Suite 16,221 →
> **16,281 / 3 skipped**, ruff clean, corpus 514/514. **M1–M7 and `BASELINE_SERIES`
> byte-identical without re-record.** No `.gd` touched.
>
> Narration had missed its 6.5 target at three separate measurements (Jul 10, Jul 25,
> Aug 4). The previous two sweeps fixed sentences; these two rows change how the arcs
> are BUILT.
>
> **CA8-9 — the arc builder could narrate a fall and never a rise.** The played campaign
> told a five-beat tragedy (crowned T3 → ennobled Duke of Carniola T8 → broken at Bohemia
> T10 → estate confiscated the same turn → "the laurels have passed" T12) and not one
> line referred to any other. The blindness was **one `if`**: the four victory outcomes
> arrive on the same `battle` event `_build_marshal_arcs` already parsed and were thrown
> away, and `glory_crowned` / `dotation_granted` / `estate_confiscated` were all already
> in `world.log_event` and simply never read there. A new `_compose_reversal_line` joins
> the acts into one sentence, and it reaches the **headline** — not the roster table cell
> the arc had been confined to.
>
> Three findings that changed the build, all from the pre-build seam map:
> - **The crown loss has no event to read.** Only the crown *gain* branch writes a
>   `log_event`; `glory_crown_lost` is not a campaign-log type and its message names only
>   the loser. It is therefore **derived from live serialized state** — crowned inside the
>   window plus `marshal.glory_crowned` now false. Zero new event types, so none of the
>   five files pinning `len(CAMPAIGN_LOG_TYPES) == 156` move.
> - **The headline route needs no Godot change** (the client reads only `text` and
>   `sub_beats`), whereas wiring the existing `arc_note` — which ships on the wire and
>   which **no `.gd` file reads** — would have needed two client edits to reach the very
>   table cell that was the complaint.
> - **`region_captured` names no marshal** in any of its six producers, so "he took the
>   province" is not derivable and no ascent arm was written expecting it.
>
> The reversal **absorbs** the plain `own_broken`/`own_mauled` candidate for the same man
> rather than outranking it: CA8-5 dedupes on `(class, identity)`, so a new class at
> weight 91 above `own_broken` at 90 would have led with the joined sentence and restated
> the bare one as its own sub-beat — the exact duplicate-beat shape CA8-5 was landed to
> kill. Absorption is keyed on the marshal, pinned by a negative (another marshal breaking
> the same turn keeps his beat). **A rise with no fall builds no arc at all**, which is
> what keeps **CA8-26 gated rather than accidentally built**.
>
> **CA8-8 — no recurrence register, a monoculture, and a starved rung.**
> - The triple ("cooled with time" / "appears envious" / "entrenched" in one dispatch) is
>   **legal state**, confirmed by reading: step 1 expires the timer and clears
>   `jealous_of`; step 3's only exclusion is `if marshal.jealous_of: continue`, so the man
>   just cleared is re-evaluated in the same pass. **This landed as a display fix only** —
>   no trigger, ordering, rate limit or timer was touched, because those feed `jealous_of`,
>   which M7 (slack `1 <= first <= 8`) and `BASELINE_SERIES` both read through combat's
>   reinforcement and coordination math. The register is derived from
>   `jealousy_history[target]`, a list of fire turns already serialized and already read by
>   `_lifetime_fires`: **zero new fields**, pinned by a test that names four plausible
>   invented ones and asserts their absence.
> - Expression **variant banks** replace the three fixed strings, selected RNG-free via
>   `campaign_variance.seeded_int` keyed on the pair and the recurrence index.
> - **"The wound will not close on its own" was falsified two turns later** when the timer
>   expired and the game said the resentment had cooled. Both sentences were true of
>   different things — the grievance timer expires, the permanent −1 between the two men
>   does not — so the cooling line now says which one cooled.
> - **The campaign log is a second PRODUCER, not a consumer** (jealousy's `log_event`
>   payloads carry no `message`; the log composes its own sentence from structured
>   fields), and the two channels had already diverged: the payload has always carried
>   `level` and the formatter ignored it, so a tier-1 escalation read "a matter of concern"
>   in the dispatch and "entrenched" in the log **on the same turn**. Fixed, with the
>   pre-CA8-8-save fallback pinned.
>
> **The starved rung.** Berthier closed 7 of 11 dispatches on the byte-identical "The
> marshals' rivalries demand attention, Sire" and never once mentioned Murat idle at
> Rhineland with 19,312 men for nine turns. The spec ordering is **unchanged** (Jealousy
> §5 puts a grievance above `idle_restless` deliberately); what changed is that rung 3.5
> now names the rival and, when the aggrieved man is also the idle one, says so in the
> same sentence — being passed over is what the grievance *is*.
>
> **The brief framed the arc note as destroying the idle count. It is not the bug** —
> `status_note = arc_note` is pinned deliberate design (`test_arc_upgrades_the_status_note`).
> The defect is that a ladder rung **parsed prose at all**: two of three arc shapes raised
> and were swallowed, and the third, `"4 defeats in as many turns"`, **parsed cleanly and
> compared a defeat tally against an idle threshold** — so a marshal beaten four turns
> running was reported to the Emperor as growing impatient for action. The row now carries
> a structured `idle_turns`. Also: below rung 4 the ladder reached "Your armies stand
> ready, Sire. The initiative is ours." — not a silent default but an **active false
> reassurance** about an army standing still; `idle_restless` joins the non-ready set.
>
> **CA8-25 — the diorama was built and then DISCARDED.** Filed as "no diorama is built"
> for the `press on` resolution (the campaign's largest battle, 82,072 massed); that is
> **refuted**. Every `attack_anyway` arm re-enters `_execute_attack` and sets the payload.
> `muster_confirm` returns the inner result verbatim and it survives; the blocked-path arms
> rebuild a fresh dict through `_COMBAT_PASSTHROUGH_FIELDS`, which carried `battle_report`
> and not `battle_diorama`. **One tuple entry.** Returning the inner result raw is not an
> option — those arms deliberately rewrite `message`/`order_cleared` — so the allowlist is
> the correct seam, pinned by a negative that `new_state` still cannot travel.
>
> **21-mutation sweep, one INERT pin found and replaced:** the ladder-docstring test
> asserted `"3.5" in doc`, which the explanatory paragraph below the list also satisfies,
> so it passed with the ladder entry deleted. Re-anchored to the numbered list and to the
> rung's position between the treasury and idle rungs. Final **21/21 killed**.
>
> **Byte-identity is a fact about the harness, not proof of safety** — stated per the
> file's own rule. It is expected here by mechanism: `dispatch.py` and `campaign_log.py`
> are absent from the sweep's import set, the BASELINE runner never builds a dispatch, and
> the only `log_event` change is one added **key** (`fires`), not a change in row volume,
> which is what `agendas.py`'s 500-cap fail-safe is sensitive to.
>
> #### ⚠ ADVERSARIAL REVIEW ROUND 2 — 129 agents, 8 lenses, 2 skeptics per finding
>
> **60 raw findings; 11 survived both skeptics; ALL FIXED, plus 10 corrections to this
> slice's own claims.** The review was run against commit `e5b18c1` and its fixes landed
> in `d912176` + the follow-up. It found more than the slice's own 21-mutation sweep did,
> and its closing critique is recorded because it was fair: *that sweep's mutation set was
> chosen around the tests rather than around the seams*, which is why three separate
> lenses each found a surviving mutation on their first attempt. The round-2 sweep walks
> the seams instead.
>
> **The headline finding, and it is mine to own: `marshal_reversal` re-created the exact
> defect PC-7 was landed to kill.** Every other headline candidate is scored from a
> two-turn event window, or is declared in `STANDING_HEADLINE_CLASSES` so PC-7's cooldown
> governs it. The reversal was neither — it consumed the arc builder's **six-turn** window
> plus live `glory_crowned` state — so both suppressors were structurally unreachable, and
> the July-19 exact-repeat demotion could not catch it either, because `_turns_ago_phrase`
> rewrites the sentence every turn ("last turn" → "two turns ago" → …) so the strings are
> never equal. Measured: **the same reversal led four to six consecutive dispatches at
> weight 91 and froze Berthier's closing note for the whole run**, burying a bankruptcy, a
> declaration of war and a genuinely broken corps. Fixed by gating the candidate on the
> fall being **current news** (the arc keeps its six-turn memory for the roster note), which
> bounds the lead by construction and needs no new cooldown.
>
> **`crown_lost` was not a fall.** `recompute_crowns` clears the flag whenever a
> same-nation marshal out-scores the holder — *on a French success* — and since
> `crown_lost` implies `crown_turn is not None`, which is itself a disjunct of `rose`, one
> event satisfied **both halves** of `rose and fell`. A marshal who fought nothing,
> retreated nowhere and lost no estate produced the top headline because a colleague won a
> battle. It is now the tail clause only. Related: the crown is **vacated** on a
> top-of-ladder tie, so *"the laurels have passed to another"* was a flat falsehood —
> nobody holds them; the line now checks for a successor.
>
> **The absorption deleted beats it never restated.** Keyed on the marshal rather than on
> which act the composer chose, it deleted an `own_mauled` beat for a battle France **won**
> — 12,000 casualties that then appeared nowhere in the dispatch. Now conditional on the
> fall arm: a defeat absorbs the maul, a rout absorbs the break, a dispossession or a hunt
> absorbs nothing.
>
> **The recurrence interval was never correct.** `jealousy_history` records fire turns
> only, so `turn - history[-2]` is fire-to-fire; the first draft called it *"turns after it
> cooled"*, and a grievance stands 2–5 turns before the timer can expire. In the marquee
> case it printed *"again, 2 turns after it cooled"* **directly beneath the line saying it
> had just cooled**. The seam map had warned there is no clear-turn record and I wrote the
> phrasing anyway; the noun is now the one the data supports, and a falsifiable negative
> sweeps every arm for the false one. Same class: *"It has cooled N times"* counted
> **fires**, so an action-satisfied grievance was reported as a cooling — now *"the quarrel
> has flared N times"*.
>
> **The campaign log asserted a mutual feud the engine had skipped.** The escalation level
> advances to 3 whether or not the tier-3 reciprocity applied (it is guarded on the target
> being STANDING, so a marshal mid-rout is skipped), and the formatter branched on `level`
> alone — one reviewer saw the false line on **eight consecutive turns**. The producer now
> stamps `mutual`; absent on old saves, which falls through to the weaker claim.
>
> **Also fixed:** the roster's max-3 display cap was deleting a 4th-ranked reversal before
> the headline could score it (`cap=None` for the headline arm); *"endowed with Duke of
> Carniola"* — `derive_title` returns a **personal honorific**, and the estate noun is now
> single-sourced as `dotation.derive_estate_noun`, back-filling the two hand-rolled
> `.replace("Duke of", "Duchy of")` sites; and the `marshal_reversal` Berthier note
> asserted the crown and *"a fortnight"* as fixed facts when `rose` is satisfied by an
> estate grant alone and the gap ranges 0–5 turns (`"fortnight"` was a hapax in the whole
> backend, against a game that defines no turn length).
>
> **CA8-25 was only half-landed, and the wrong half.** The typed `press on` route works;
> the **popup** route — the one the UI presents, and the only one reachable while the modal
> is up, because `_show_interrupt_popup` disables the command line — never called
> `_stash_diorama`. Clicking the button and typing the same answer gave different outcomes.
> Fixed with one line in `main.gd`, **so this slice does now touch `.gd`**: parse harness
> EXIT=0, 28 scripts.
>
> **Three INERT seams found by the review, all now pinned:** the roster row's `idle_turns`
> could be hardcoded to 0 with all 16,259 tests green (killing the very rung CA8-8 exists
> to cure); the `fires` producer→consumer wire was unobserved and the `fires == 2` boundary
> — the common case — untested in either direction; and the `own_mauled` half of the
> absorption had no coverage at all.
>
> **Corrections to this slice's own claims, recorded in place** (comments and docstrings
> updated at each site): *"a pure ascent cannot reach here"* was true only because
> `crown_lost` was **classified** as a fall — true by definition, not by behaviour, which
> is why four reviewers read the code as contradicting it (CA8-26 itself does remain
> gated); *"the sub-beat never restates the headline"* was keyed on the wrong thing;
> *"a reversal outranks a bare chain"* is false, since `consecutive + fled` is unbounded
> against a constant `+4`; the `gap <= 0` comment named a case that cannot reach that arm
> (the real path is the tier-3 spiral); the rung-3.5 docstring claimed a general
> improvement that is gated on there being exactly **one** aggrieved marshal; a comment in
> `test_dispatch.py` cited a test name **that exists nowhere in the repository**; and the
> `_endow` fixture pinned a title string **no producer emits**, which is why the
> "endowed with Duke of" defect passed its own test twice.
>
> **Refuted by the skeptics and recorded** (the review's own list): CA8-25 is *not* inert on
> the typed route; the "five identical rebuild seams" claim is wrong — the other four
> forward `events` verbatim, which is exactly why only `strategic.py` needed the top-level
> key; `_ORDINALS`' `"21th"` fallback is unreachable (measured ceiling: 2 fires over 60
> ambient turns, 5 over 200) and is pre-existing house style at three sites; and the
> campaign log's recurrence arm **increased** variance rather than replacing one
> monoculture with another (measured 2 distinct rows → 4).
>
> ### ✅ LANDING RECORD — CA8 sweep 1, August 4, 2026
>
> **Fixed and landed: CA8-1, CA8-2, CA8-4, CA8-5** (four of the five P1s — every one that
> is code-proven and gate-free) · **CA8-13, CA8-14, CA8-15, CA8-18** (P2) ·
> **CA8-22, CA8-23** (P3). Tests: `tests/test_creative_audit_ca8_2026_08_04.py` (38).
> Suite 16,171 → **16,209 / 3 skipped**, ruff clean, **M1–M7 and `BASELINE_SERIES`
> byte-identical without re-record**. No `.gd` touched, so no engine boot required.
>
> **What each fix actually was:**
>
> - **CA8-1** — the mass and ally-casualty lines are now emitted for the DEFENDER too
>   (they existed only inside `for r in attacker_reinforcements:`), and the coordinated
>   casualty figure goes back to the whole-army total the campaign log prints. That last
>   part is a **conscious flip of the F1a fix** (Jul 6): F1a rewrote the corps total down
>   to the lead's private share, which is what made the terminal and the log disagree by
>   15×. Both readings were right about the defect and wrong about the fix — the number
>   was never the problem, the possessive was — so the line now names the *army*
>   (`Ney's army 8,141`). A side that fielded one corps is untouched.
> - **CA8-2** — all four defects: current-turn recency (the region must be bleeding in the
>   window's latest turn, not merely have the largest cumulative loss), live-occupancy
>   names (so the sentence describes one instant instead of two), the `"more"` fallback
>   deleted by **yielding the lead when the overage is zero** (there is no honest sentence
>   to write when the strain has ended), and the province's capacity finally stated —
>   it appears on no screen the player can reach, so *"move a corps"* had no target size.
> - **CA8-4** — the muster note names the enemy and its strength through the same
>   fog-banded helper the muster preview uses (extracted as `_fog_banded_strength`, so the
>   two surfaces cannot drift or leak), and the question names all three options the
>   payload has always carried.
> - **CA8-5** — sub-beats dedupe on `(class, identity)`, and `own_broken` is reachable:
>   the four rout sites now stamp `forced: True` on their `retreat` event, which is also
>   what keeps an *ordered* withdrawal from reading as a rout.
> - **CA8-22** — new `region_lost_estate` class at weight 76, one above the bare map fact,
>   because it is the same event told better. Drive-by: `supply_strain` and `levy_open`
>   had no Berthier closing note at all, so the class that led six of twelve briefings
>   ended in silence.
> - **CA8-23** — one `_proposal_label` helper replaces ten hand-rolled
>   `.replace("_", " ")` sites. `armistice_losing` was not the only leak; the same code
>   rendered `design_purchase`, `sell_neutrality`, `offer_vassalage`, `broker_peace`,
>   `ultimatum_demand` and `friendly_gift` as their internal tokens.
>
> **Two pins were found INERT by a 20-mutation sweep and replaced** — CA8-2's recency
> fixture put one of its two attrition turns outside the 3-turn scan window, so the
> region was dropped for an unrelated reason and the filter was never exercised; and
> CA8-4's test asserted the enemy was *named* but not that its *strength* was stated,
> which was the whole finding. A third apparent survivor was an **invalid mutation**, not
> an inert pin: it restored the `"more"` fallback, which the zero-overage guard makes
> unreachable. Recorded rather than silently re-run. Final: **18/18 valid mutations killed.**
>
> **Five test files were re-pinned consciously**, each with the reason in place:
> `test_playtest_bugfixes_2026_07_06.py` (the F1a flip), `test_pc3_pc9_composition.py`
> (the three-option question), `test_igr_b_campaign_log_readable.py` (proposal labels),
> and `test_igr_e_plunder_prompt.py` / `test_plunder_secure.py` /
> `test_supply_movement_contested.py` — those last three all captured a province that is
> **French homeland in the legacy fixture**, i.e. they were exercising CA8-13's own bug
> shape by accident, and now declare the target foreign.
>
> **Still open and why:** **CA8-3** and **CA8-27** are held at gate **CA8-D2** (both move
> blessed acceptance arithmetic; CA8-27's one-line `or`-split is tempting and is exactly
> why it should be gated). **CA8-26** is design call **CA8-D6**. **CA8-6/21** must land
> together and are the only `.gd` work in the set. The rest (CA8-7/8/9/10/11/12/16/17/19/
> 20/24/25/28) are untouched and stay routed to ROADMAP position 13.
>
> ### ✅ LANDING RECORD — CA8 sweep 2, August 4, 2026 (same day)
>
> **Fixed: CA8-6 + CA8-21 (together, as the memo requires), CA8-7, CA8-10, CA8-11.**
> **CA8-12 REFUTED against the shipped client — see below.** Tests: the same file, now 50.
> Suite 16,209 → **16,221 / 3 skipped**; ruff clean; **Godot parse harness EXIT=0**
> (3 `.gd` touched: `enemy_phase_dialog.gd`, `utils.gd`, and the palette constant).
>
> - **CA8-6** — the six fall-through verbs (`grant_dotation`, `grant_pension`,
>   `form_square`, `break_square`, `garrison`, `naval_expedition`) get render arms built
>   from **structured fields**. The memo's two hazards are respected by construction:
>   nothing here reads `message`, so the origin-vs-destination fog gap and the
>   second-person player-addressed prose cannot leak. Pinned by a test that asserts the
>   arms exist *and* that the function body never reads a `message` key.
> - **CA8-21** — `_decree_preamble(world, acting_nation)`. France's wording is
>   byte-identical; a foreign court no longer issues an *Imperial* decree, and
>   Talleyrand's commerce aphorism and the address to "Sire" no longer editorialise
>   inside Vienna's council. Landed with CA8-6, never after it, exactly as filed.
> - **CA8-7** — `enemy_phase_dialog.gd` now renders `enemy_voice`, above Berthier's
>   observation (the enemy speaks on the field; the staff comments afterwards), in a new
>   cool `COLOR_ENEMY_VOICE` so the two narrators are never confused. A falsifiable
>   negative pins that the backend still attaches the key — a render arm over a key
>   nobody sets is worse than no arm.
> - **CA8-10** — the treasury report **stops hand-assembling its net** and reads
>   `ledger._build_economy`, whose Net is pinned to the signed sum of its declared
>   components. That is the defect class, not just the instance: EC-W5b had fixed the
>   same bug for infrastructure alone, one stream at a time, and admiralty (already
>   sitting in the dict this report was reading), blockade, trade, treaty gold and vassal
>   tribute were still missing. New render lines for each. The War Effort explanation is
>   un-guarded, because turn 1 — the only turn the played campaign opened this screen —
>   had `war_effort == 0` and so printed nothing about a drain that reached −1,238g.
> - **CA8-11** — `find_nearest_marshal_to_region` computed the per-marshal reasons and
>   threw them away; they are now stashed and stated ("out of range — 4 regions away,
>   range 1"), with the rule named and a working alternative offered. The `levy_open`
>   headline states the condition it had been advertising a price and a place without.
>
> **CA8-12 is REFUTED against the shipped client, and this is the audit's own method
> caveat firing on the audit.** The finding was measured from an HTTP transcript, where
> the digest payload genuinely does ride every response. In the client it does not
> repeat: `main.gd` latches it per turn (`_envoy_digest_shown_turn` / `_pending_envoy_
> digest_turn`, with the reason written at `_show_pending_envoy_digest`), and `title`,
> `headline` **and** `deadline_note` are all rendered by `mailbox_panel.gd`
> `_build_digest_caption`. Nothing was changed. The corroborating evidence the row cites
> — 17 `offer_lapsed` events and ~60 DP generated against one spent — is real, but it is
> a different finding (the player ignoring the mailbox) and needs its own row rather than
> a fix aimed at repetition that does not occur.
>
> **One inert pin found by the sweep and replaced:** the War Effort test set
> `war_exhaustion` to 4, which made `war_effort` non-zero and quietly exercised the OLD
> branch. The fixture is now the shipped boot — France at war on turn 1 with
> `war_effort == 0` — which is the audit's actual case, asserted rather than constructed.
> Final: **8/8 valid mutations killed.**

## Creative Audit — the remaining rows (filed August 4, 2026)

> Source: a **17-turn live France/1805 campaign** driven over HTTP against the shipped board
> (`LLM_MODE=anthropic`, `SOVEREIGN_SEED=historical`), played actively — the Ulm concentration,
> Mack destroyed, Rhineland lost and retaken, Massena's autonomous glory-attack into the Alps,
> Ney broken and dispossessed at Bohemia, Vienna stormed, Austria eliminated. Run at master
> `e450b02`, i.e. AFTER ROADMAP position 3 (composition slice) and 3.5 (econ) landed.
> Every row was verified against the code by an 80-agent find→refute fleet; **13 candidate
> findings were killed by the refuters and 4 more materially narrowed** — those corrections are
> recorded in the memo §5, not dropped. Evidence pack + full findings:
> **`docs/audits/CREATIVE_AUDIT_2026_08_04.md`** (authoritative).
>
> **⚠ Method caveat that governs every copy row below.** The play pass drove the backend over
> HTTP, and the shipped client does **not** read the enemy-action `message` field
> (`enemy_phase_dialog.gd` `_format_action` rebuilds each line from `action_type`). Any
> enemy-phase copy claim must be checked against that key list, not an HTTP transcript.
> This invalidated three candidate findings and narrowed two.
>
> Pillar re-score (5 pillars exercised): combat 8.0 → **6.5** · narration 6.0 → **6.0** (flat,
> still under its 6.5 target) · marshal drama 8.5 → **7.5** · economy 7.5 → **6.5** · diplomacy
> 7.0 → **6.5**. Directional ≈ **6.9**. **No code regressed** — every scorer independently
> attributed the drop to campaign LENGTH: the failure modes are accumulation failures that a
> 9-turn pass cannot load.

### P1

| id | claim | seam | fix |
|---|---|---|---|
| ~~**CA8-1**~~ ✅ | The defending army is invisible, and the two surfaces that report French casualties disagree by up to **15×** (terminal `Ney 13` vs log `197`). `combat.py:1098` puts the whole stack in the defensive ratio; `combat.py:268-278` sizes casualties on the LEAD marshal alone. The mass line (`combat_executor.py:5539`) and ally-casualty line (`:5552`) are both inside `for r in attacker_reinforcements:` — **attacker-only, no defender equivalent in the file** | `combat.py:268`, `combat_executor.py:5539` | Mirror both lines onto the defender; make the terminal casualty figure the whole-army number the log already prints |
| ~~**CA8-2**~~ ✅ | The `supply_strain` headline is wrong four independent ways on the mechanic that killed ~43,000 men: renders `stand **more men** over` when `over == 0` (`:749` fallback), names marshals from the 3-turn event window not current occupancy (`:744`), mixes live and windowed epochs in one sentence, and can lead with a province the famine has left (`:715` has no current-turn recency requirement). It led **6 of 12** dispatches. Its prescribed remedy was then refused: `build a supply depot at Munich` → `Cannot build in Munich — not controlled by France` | `dispatch.py:699-749` | Current-turn recency predicate; live-occupancy names; drop the `"more"` fallback; state the capacity |
| ~~**CA8-3**~~ ✅ Aug 7 (close-out §10.1) | Twelve turns of victory contributed **zero** leverage: `calculate_war_score` reads `battle_records` for the France\|Britain **pair**, and no French marshal ever fought a British one — so `battles_fought: 0` all campaign. The offer producer reads the same 0, emits a white peace, and the scorer charges that white peace a hard −10; **Talleyrand's advice ("author terms") takes legitimacy −10 → −20** and is not among the four options on screen | `diplomacy.py:2861`, `ai_diplomacy.py:3577`, `settlement_scoring.py:471` | Gate CA8-D2 — leverage should key to the war actually being fought |
| ~~**CA8-4**~~ ✅ | The game's **first modal** states the friendly muster and the friendly lead as if they were two armies (`82,072 in all, against 24,000 of Ney's own`), never prints the enemy's strength, and offers two choices where three exist | `combat_executor.py:919-922`, `delegation.py:349` | Use the MUSTER format that already exists; name the enemy; three options |
| ~~**CA8-5**~~ ✅ | The campaign's climax rendered as headline + both sub-beats being the same marshal/province/phase three times (`Ney was mauled at Bohemia` ×3). `dispatch.py:300` adds `own_mauled` with **no identity**; `:495-501` dedupes on exact text. **Worse:** `own_broken` (weight 90, the right sentence) is structurally unreachable — the ordinary break logs `{"type": "retreat"}`, and `marshal_broken` occurs **0 times in 12 turns** | `dispatch.py:300`, `:495`, `world_state.py:10508` | Dedupe on `(class, identity)`; route the ordinary break to `own_broken` |
| ~~**CA8-26**~~ ✅ Aug 7 (close-out §10.2) | **The dispatch has no headline class for a French success.** `HEADLINE_WEIGHTS` = 15 classes from 17 `_add()` sites; every one is a wound, an opportunity ranked below every wound by comment (`:71-73` *"an opportunity never outranks a wound"*), or another power's business. **14 of 14 headlines this campaign were misfortunes.** On the turn France stormed **Vienna** *and* **Austria was eliminated**, the dispatch led with `stand more men over what Bohemia can feed` and mentioned neither. The material is not missing — it is **mis-filed** in a notification bar where 8 of 20 entries are the same `dotation_erosion` nag | `dispatch.py:55-83` | **Design call → CA8-D6**, not a bug fix |
| ~~**CA8-27**~~ ✅ Aug 7 (close-out §10.1) | **France offers territory in every wartime peace it proposes, winning or losing.** `elif war_score < -20 or relation < -50:` — the branch the comments twice call *"when losing"* is reached by hostility alone, and every war boots at −80/−90. Live: holding Vienna with Austria eliminated and war score **+2**, Talleyrand drafted `France cedes Nivernais` under *"terms appropriate to the current military situation"*; ten turns earlier, `Territory Flanders` under *"Returning it costs us little"*. Both are **boot-income homeland** | `diplomatic_templates.py:3381` | Split the `or` so a cession needs a losing war score — gate CA8-D2 (moves blessed acceptance arithmetic) |

### P2

| id | claim | seam |
|---|---|---|
| ~~**CA8-6**~~ ✅ | Six AI-reachable verbs fall through the client's 15-arm `match` to `action_type.replace("_"," ")` — live-proven here: `Deroy grant dotation Bohemia`, `ArchdukeCharles grant pension`, `Castanos form square` (**9 of 74 actions, 12%**). ⚠ The fix is **not** to pipe `message` through: two verified hazards (the fog filter gates on destination while raw move text names the origin; the prose is second-person player-addressed) | `enemy_phase_dialog.gd:128-181` |
| ~~**CA8-7**~~ ✅ | `enemy_voice` has exactly **one** consumer in the whole client (`battle_diorama.gd:1147`). Charles's arc — *"I trade ground for time. Time is on my side."* — is generated for both directions and dropped in the enemy phase | `enemy_phase_dialog.gd:328-362` |
| ~~**CA8-8**~~ ✅ | Grievance templates carry no recurrence register, so a legal escalation reads as a state bug: one dispatch printed *cooled with time* → *appears envious* → *has become entrenched* for the same pair. `jealousy.py:520-524` holds exactly three expression strings. And an undocumented rung 3.5 (`dispatch.py:1490`) starved the idle-marshal rung below it — Murat sat idle 9 turns, never mentioned | `jealousy.py:520`, `dispatch.py:1490` |
| ~~**CA8-9**~~ ✅ | The campaign told a five-beat tragedy (crowned → ennobled → broken → dispossessed → laurels passed) and **not one line refers to any other**. `dispatch.py:547-601` builds arcs only from defeats/retreats/attackers — the arc machinery can narrate a marshal being beaten and never one rising | `dispatch.py:547` |
| ~~**CA8-10**~~ ✅ | The two screens reporting income disagree by **124%** (report `+926g` vs end-turn `+2073g`, same turn). `economy_executor.py:86-92` omits admiralty, blockade, trade and vassal tribute. War Effort ran −8 → −1,238 with its explanation guarded by `if war_effort > 0` | `economy_executor.py:86` |
| ~~**CA8-11**~~ ✅ | Position 3.5's levy headline advertises `10,000 foot cost 450 gold **at Paris**`; `recruit 10000 infantry at Paris` → *"No marshal is available to receive reinforcements at Paris"*. `find_nearest_marshal_to_region` filters on `movement_range` (1 for infantry) | `world_state.py:4287` |
| ~~**CA8-12**~~ ⚠ REFUTED | The envoy digest re-prints every pending letter in full on **every** response — eleven identical ~60-word paragraphs in one turn, attached to `plunder` and `move` results. Its `title` and `deadline_note` appear in the transcript **not at all**. 17 `offer_lapsed` events; ~60 DP generated against **one** spent | `envoy_digest.py:175-221` |
| ~~**CA8-13**~~ ✅ | Liberating **French homeland** opens a mandatory prompt asking whether to burn it, and blocks the turn. IGR-E's own-soil guard was scoped to the AI branch; its landing record says the player modal was untouched | `build_capture_choice` |
| ~~**CA8-14**~~ ✅ | A retreating AI marshal captures the province he just fled into, same phase, at −35% effectiveness. P-1 "capture current region" sits **above** the `retreated_this_turn` limiter; the player's equivalent guard is nested under a `nation == player_nation` check. *(Two of three legs of the first-pass claim were refuted — the drill lock IS nation-agnostic and the AI does unfortify first.)* | `enemy_ai.py:1448`, `executor.py:809` |
| ~~**CA8-15**~~ ✅ | A bare `[Prussia]` header with nothing under it — **self-inflicted by the composition slice**: `main.py:794-831` rewrites `nation_data["actions"]` with no empty-nation prune, and PC-3's fortify→unfortify arm drops both entries. The fog filter is innocent (`main.py:1346` does prune) | `main.py:794` |
| ~~**CA8-16**~~ ✅ Aug 7 (close-out §10.4 — bounded authoring: a third non-fear variant in all 24 banks; DEF-1 keeps the rest) | `hegemony_pressure` is a monoculture, rotated by `(turn + len(name)) % len(variants)`. **Two of the row's own numbers corrected Aug 4, 2026 (sweep 3 map), and the finding survives both:** it is **19 named speakers + 5 registers, not 8 courts**, and the `"in its path"` count in `diplomatic_templates.py` is **3, not 14** (no scoping reproduces 14). *"2 variants each"* is exactly right and **universal** — the distribution over all 24 banks is `Counter({2: 24})`, i.e. 48 lines. The monoculture survives on an independent metric: across those 48 lines, "power" 13, "rather" 13, "grow" 12, "reach" 8, "greatness" 7, "shadow" 6 — three separate courts independently reach for the same rising-tide image. **NOT built in sweep 3: the cost is authoring, not selection.** `len(variants) == 2` is hard-pinned twice (`test_w6_incoming_voice.py:118`, `test_nation_agendas.py:728`) so growing the banks is a conscious flip, and the rotation contract is pinned both ways. 19 of the 48 lines are bespoke per-court copy a mechanical fix cannot generate. The cheapest genuine improvement was thought to be **re-keying** the rotation — **REFUSED Aug 4, 2026 (sweep 4) as cosmetic churn**: with two variants the key's image is `{0,1}`, so any turn-independent term is only a phase shift, and the 19 courts hold DISJOINT banks so the existing name term decorrelates nothing. **Three more of the row's facts corrected**: the authored surface is 38 bespoke lines, not 19; it is pinned ONCE, on one bank, not twice (a third variant injected into all 24 banks runs the FULL suite at 1 failed / 16,280 passed, so every bespoke bank grows with zero pin flips and the "conscious flip" cost model was false); and the measurement that settles the row is neither lexical nor structural — **72% of all diplomat lines composed in a 40-turn campaign are exact repeats** (Ottoman: 12 asks, 2 distinct lines), so bank SIZE is the only lever. **Two gate-free defects split out and FIXED**: Hardenberg's first `hegemony_pressure` line was the generic hawk line with `{nation}` pre-filled as "Prussia" — a named override delivering a copy of the register line it exists to replace — now re-authored, with a generalised pin rejecting the whole class; and a NAMED envoy lost his authored attribution whenever his reason had no bespoke bank (`Araujo, measuring the room:` → `Araujo:`), which is 16 of 19 courts on `agenda_pursuit`, i.e. the common path. The authoring question goes to the gate with `DESIGN_REFINEMENT` CA8-D4 rewritten | `diplomatic_templates.py:606` |
| ~~**CA8-17**~~ ✅ Aug 7 (close-out §10.3 — the reduced build, behind the granted Voice Bible §16.1a amendment) | Three named diplomats with three authored registers get one identical sentence, and a table label is put in their mouths as speech: *"Settlement legitimacy is the sticking point before they will sign."* **The row's MECHANISM is wrong, and correcting it removes the cheap fix (Aug 4, 2026, sweep 3 map — the player-visible sentence was first reproduced byte-for-byte from production).** Nothing is title-cased: `display_names.py:962` is a **hand-authored sentence-case UI label**, and the `.title()` call lives only in `_fallback_display_name`, which is unreachable because all 11 scorer keys are present. So there is no "un-title-case it" repair — **every** possible value is a deliberate noun-phrase column label being spliced into a diplomat's mouth. The real fix is a second, **spoken-register** vocabulary keyed on the same 11 component names, plus per-diplomat arms — authoring scope, which is where the hidden gate is. **NOT built in sweep 3.** When it is: match the LIVE override idiom (`settlement_offers.py:430-458`, a nation→suffix map with an explicit `_chancery` fallback re-lookup), **not** the five dead families at `diplomatic_templates.py:1562-1641` (no backend reader, and they lack the fallback arm). Tripwires: `test_settlement_refront_slice1.py:724` requires the speaker's name literally in every line; `:772-789` bans "conference"/"congress"/"veto"; and `_MissingSettlementSlot.__missing__` renders raw `{braces}` to the player with **no exception and no test failure** if a template gains a slot the call site does not supply. **NOT BUILT in sweep 4, and the honest sizing is not the row's (Aug 4, 2026).** The full per-diplomat build is **90 authored strings** (9 phrase slots × 5 registers × 2 bands) — 2.4× the entire Slice-H ally-petition arc — and it **cannot be completed anyway**: 11 of the 19 reachable courts have named envoys whose registers the Voice Bible explicitly homes to **DEF-1 Roster Voices**, so a "full" CA8-17 would silently annex another row's scope. It also contradicts its own normative source — **Voice Bible §16.1a records the four current templates VERBATIM as committed exemplars**, so this needs a Bible AMENDMENT, which is a gate. Two further justifications in the row are wrong: the string is not title-cased at all (hand-authored sentence case; the `.title()` call is unreachable), and the "no jargon" rule it invokes is scoped to bloc-naming lines. Found in passing and larger than the row: the same label is spoken **three times on one screen** — Talleyrand's own popup heading reads *"the largest pressure remains Settlement legitimacy"* directly above the per-court table. A reduced build — one spoken-register vocabulary over the **8 negative-capable** components (not 11; only those can ever be a top blocker) *(count corrected Aug 7 at the build: it is **NINE** — `war_objective_alignment` clamps to −20/−15 and the row missed it; only `war_exhaustion` and `concession_credit` cannot go negative)* plus per-register framings, ~19–21 strings, two files, no `.gd` — is specified and buildable behind that gate | `diplomatic_templates.py:2140-2143`, `:2318-2322` |
| ~~**CA8-18**~~ ✅ | `get_threat_tier` has **no Formed arm**, so a coalition formed on turn 1 is labelled "Brewing" for 12 straight turns while the payload carries `coalition_brewing: false`. This is also why position 3.5's `military_establishment` term was **unmeasurable in play** — it fired into a bar already at 91–97 | `coalition.py:1882` |
| ~~**CA8-19**~~ ✅ RULED Aug 7 (close-out §10.5 — full parity REJECTED as design; the repulsed-attacker glory divergence CANONIZED in JEALOUSY_SPEC §1; the garrison-diorama half homed at the Battle Gallery gate) | Garrison assault is a separate, banner-free resolver — no terrain, fort, personality, coordination, muster or reinforcement. **Re-scoped Aug 4, 2026 (sweep 3 pre-build map): this is a combat-system change wearing a copy row's clothes, and it was deliberately NOT built in a narration sweep.** `_resolve_garrison_combat` never calls `resolve_battle` — no dice, no morale, no `defender_bonus`, no variance, no rout machinery, and it composes terrain+fort **multiplicatively** where the field path adds. It returns before the muster gate, so no muster/reinforcement/overwatch/flanking/participant list/casualty distribution runs and every attacker loss lands on the lead marshal. Full parity moves **M1–M7 *and* `BASELINE_SERIES`** (enemy AI P4.25 takes this path), needs a defender object that does not exist (every field helper takes a Marshal or a participant list), and would consume `compose_battle_name` ordinals whose docstring explicitly excludes garrison assaults — shifting every later field-battle name and the PC-4 uniqueness guarantee. **It also owns the garrison half of CA8-25**: this path emits `garrison_assault`/`conquest`, never a `battle` event, and the client's stash-and-link chokepoint is reached only for `events[0].type == "battle"`. **Three separately-landable latent defects found inside it — ALL THREE LANDED Aug 4, 2026 (sweep 4); the PARITY work stays gated.** (i) is a MECHANICS defect, not the hygiene item it was filed as: the stale stamp is read back through `_committed_reinforcement_strength`, **measured +16.0% committed attacker strength with no marshal's strength changed**, and two more seams of the same class were found and fixed (the auto-bombardment-kill exit, which advances before calling the pipeline; and `clear_combat_transient_state`, which held NONE of the eleven fields its own docstring promised — the reason the reckless-cavalry auto-charge could fight on leaked numbers). (ii) was DECIDED rather than left in a third state — the dead discriminator deleted and the rule STATED at the guard; the spec's defeat-side garrison row is a recorded divergence owned by this gate, because wiring it means ungating step 9.5, which mutates `jealous_of`. **(iii)'s stated consequence is FALSE**: the arm above the dead one already charges the repulsed attacker, measured Austria +6, on every cell of the running board — deleted as dead code, not repaired, since flipping the ctx would SUPPRESS the defender's threat, decisive victory, coalition shock and war-score record. **Found while pinning it: `TestGarrisonCombat`'s seven tests had NEVER invoked garrison combat** — the fixture looks up a region absent from the 19-region legacy world — and on their first real run two FAILED: one asserting an authority rise that boot's 100-ceiling makes unobservable, one a tautology that survived deleting the mechanic outright. Original finding text follows — (i) coordination is recomputed and never cleared (both pipeline calls pass `skip_coordination_clear: True`), leaving transients stamped on every eligible marshal; (ii) the garrison-stomp glory exemption is **production-dead** — step 10.5 is gated on a truthy `battle_result` the garrison path always passes as `None`, so `jealousy`'s `is_garrison_stomp` branch has never executed and no call site anywhere passes `is_garrison=True`; (iii) the garrison-hold war-exhaustion branch is unreachable because the hold ctx sets `defender_won: True`, so **an AI army repulsed from a French garrison accrues no war exhaustion at all** | `combat_executor.py:1966-2213` |

### P3

| id | claim |
|---|---|
| ~~**CA8-21**~~ ✅ | Decree actor-branching — FIXED Aug 4, 2026 with CA8-6 (`_decree_preamble`) |
| ~~**CA8-20**~~ ✅, ~~**CA8-24**~~ ✅ Aug 7 (close-out §10.1 — the collapsed war row now reports the WAR: score, battles, duration), ~~**25**~~ ✅ (garrison half homed at the Battle Gallery gate, §10.5) | See memo §4 (estate valued at income 0; war-room battle counter vs "what stirred Europe"). **CA8-25 half-FIXED Aug 4, 2026 (sweep 3):** the *interrupt-resolved* battle now keeps its diorama — the payload was built and discarded by an allowlist, not missing. **The garrison-assault half is NOT fixed and is now homed at CA8-19 below**, where it belongs: `_resolve_garrison_combat` emits `garrison_assault`/`conquest`, never a `battle` event, so it could not render a diorama even if one were built. CA8-24 remains gated with CA8-3 (same pairwise-vs-aggregate root cause). **CA8-20 FIXED Aug 4, 2026 (sweep 4). The shape corrected in sweep 3 was right; its stated REASON was not.** A **sort-key change cannot fix it**: the list is *already* sorted descending on that exact metric, and on fresh conquest every candidate is 0. Only a **filter** makes arm 2 (the rente) fire, closing the gap in one action. A bare `> 0` filter is also insufficient — `get_estate_income` additionally skips **disrupted** regions while the eligibility list has no disruption term, so a 200g disrupted province sorts first and still yields nothing. Place it **at the AI call site (`enemy_ai.py:5406`), not inside `dotation.py`**: that function is shared by three player surfaces and by the listed⇒eligible invariant (`test_w6_estate_confiscation.py:352-354`), and `test_economy_es7_dotation.py:723-730` pins the descending order. **Both of those test claims are FALSE — measured, neither reds on a filter placed inside `dotation.py`.** The real reason to site it at the call site is the PLAYER's choice: estates appreciate, and the reward dialog already discloses "covers 0g of 120g" and lets him take a fresh conquest anyway. Built as ONE predicate, `dotation.estate_yield` (the income term AND the EC-W1 disruption term), read by `list_paying_estates` at the AI rung **and** at the erosion notification — which had been telling the player to endow whenever the list was non-empty, the same lie §0.6.8 item-4d forbids. **`BASELINE_SERIES` re-recorded consciously once** (divergence index 12, 63→79; tail 0→36; Austria's treasury 1,334→10,485 because she stops giving her conquests away — she is at WAR on all 40 turns in BOTH arms, so the tail is reshaped by the fighting, not by anyone leaving it), attribution verified by experiment. **Still open, not claimed fixed:** nothing caps a grant at the remaining shortfall, so the AI can still over-endow as provinces appreciate — a sibling defect this filter surfaces rather than solves. Player half stays homed as XR-4 |
| ~~**CA8-22**~~ ✅ | `region_lost` needed an estate-holder branch — FIXED Aug 4, 2026 as the `region_lost_estate` class at weight 76 |
| ~~**CA8-23**~~ ✅ | `campaign_log.py:2185` → `PROPOSAL_TYPE_DISPLAY` — FIXED Aug 4, 2026 at all ten sites via one `_proposal_label` helper |
| ~~**CA8-28**~~ ✅ | The same unknown province got a suggestion or a shrug by verb: `move to Venetia` → *"Did you mean 'Vienna'?"*; `march to Venetia` → *"I could not make out a destination"*. **FIXED Aug 4, 2026 (sweep 4)** — the split is deliberate at the keyword layer and accidental at the resolver: the strategic path had no fuzzy pass at all. New `StrategicExecutor._suggest_region_for_phrase` runs AFTER the phrase scan and AFTER the IGR-A3 nation arm, and MOVE_TO / HOLD / PURSUE / SUPPORT all answer now. **The naive delegation is a trap, and its regression is invisible to the pin that exists to catch it**: `_fuzzy_match_region` auto-corrects `Pass`→Nassau, `Line`→Berlin, `Guns`→Brunswick SILENTLY, so passing it straight through gives "hold the pass" a real 2-AP standing HOLD on Nassau — and `test_parse_negation.py` plus the golden corpus both stop at `CommandParser.parse`, so the parser's target stays `Pass` in both arms, the assertion passes, and the order exists anyway (measured on the counterfactual). Hence `_plausible_name_typo` gates the auto-correct arm, only single TOKENS reach it, and every pin is executor-level. PURSUE suggests only from `get_visible_enemies` (R5). **Fixed in passing:** the marshal fallback in `_resolve_region_from_phrase` scanned every marshal in the world, so naming a fogged foreign army answered with the province it was standing in. **Routed, not fixed:** the `dest`-only rebind leaves the raw phrase on `order.target`, which `strategic.py` uses as HOLD's arrival predicate — that write-back is a change to the per-turn strategic tick, not the display tidy it looks like |

### Append to existing rows — do NOT re-file

- **XR-3** (`marches from X into X`) — add the cause never diagnosed: `enemy_ai.py:1448` self-targeting,
  and the frequency asymmetry (the AI reaches it after every post-battle advance). Note its stated
  landing trigger already lapsed once at IGR-X5/X6/X8, which were capture-touching slices.
- **XR-4** — the player-facing 0g estate copy is unchanged and still open.

---

## Quiet-France Played Campaign — filed August 3, 2026 (✅ ALL TEN CLOSED)

> Source: a 42-turn live campaign driven over HTTP against the shipped 1805 board
> (`LLM_MODE=anthropic`, `SOVEREIGN_SEED=historical`), France played actively to turn 5 then
> passive — ROADMAP position 1. Every row below was confirmed against the code by a 12-agent
> find→refute fleet; two rows were *corrected* by the refuters and are recorded as corrected.
> Evidence pack: `docs/audits/QUIET_FRANCE_CAMPAIGN_2026_08_03.md`.
> **Second session, same day:** PC-2, PC-3 (display half) and PC-7 FIXED —
> `tests/test_pc2_pc7_enemy_phase_and_headline.py` (20). Before → after, measured on a
> fresh 30-turn drive: verbatim duplicate phase lines **30 → 0**, fortify/wait thrash
> **41 → 0**, `estate_eroding` headline share **51% → 30%**, longest identical-class run
> **7 → 4**. (The re-measure ran in mock mode against the original anthropic run; the LLM
> is parse-only and every mechanism here is deterministic, so the metrics are comparable —
> stated rather than assumed.) M1–M7 and `BASELINE_SERIES` byte-identical, **no re-record**.

| # | P | Defect | Status |
|---|---|--------|--------|
| **PC-0** | P1 | **The `/command` interrupt router re-opens PARSE-NEG.** `main.py`'s pending-interrupt router matches raw substrings and RETURNS before the parser, so the `clause_guards` that landed the previous day never reach it. (a) No negation guard, and the `attack` branch is tested before `hold` — so `hold your position, do not attack`, PARSE-NEG's own headline sentence, resolves to HOLD at the parser and **to ATTACK here**. (b) No word boundaries, and `"flee"` ⊂ `"fleet"` — so **every naval order in the game** answers a cornered marshal's last stand as `attempt_breakout`. Observed live at turn 42: typing `set the fleet to raid commerce` with Massena cornered logged `[INTERRUPT ROUTE] … Massena last_stand response: attempt_breakout`, failed the escape roll and **lost Massena to captivity**; the fleet posture never changed. `raise a fleet` is a golden-corpus utterance and is hijacked identically. Invisible to the corpus because `parser_eval` calls `CommandParser.parse` directly and never traverses this router. | ✅ **FIXED** — mapping extracted to one pure `_interrupt_choice_from_text`, word-boundary matching, `strip_negated_clauses` applied first, stand-down routed to cancel/hold. `avoid` carved out (it is both a negation marker and this option's own affirmative label). `tests/test_pc0_interrupt_router_guards.py` (34) incl. a negative control that re-runs the old rule and asserts it fails. |
| **PC-1** | P1 | **A province falls and the game announces a MARSHAL was captured.** `combat_executor.py` built the battle event with `"region_name": resolved_target`, but `resolved_target` is reassigned to a region only in the fuzzy-region branch; when the target is a marshal the `enemy_by_name` branch takes `target_location` and leaves `resolved_target` holding the *man's* name. The enemy AI targets marshals by name at every attack rung, so **every AI conquest shipped the wrong noun** — measured **8 of 8** conquest events in the campaign carried `Ney` / `Deroy` / `Massena` / `Paget` / `Bernadotte`. Both clients render the key as a place (`enemy_phase_dialog.gd:291`, `main.gd:1977-1978` → `⚑ Ney captured! ⚑`), so a player reading it concludes he lost a marshal. The comment ten lines above the capture block already warned against this exact substitution; IGR-X8 edited this same event dict without noticing the sibling key. | ✅ **FIXED** — one token, `target_location`. `tests/test_pc1_conquest_names_the_region.py` (4), mutation-tested (2 of 4 fail against the old token). |
| **PC-2** | P2 | ✅ **FIXED** — **The enemy AI spends two of its actions saying nothing.** `enemy_ai.py`'s P8 catch-all `else` returns `wait` unconditionally and never `None`; `wait` costs 0 AP so the loop re-selects the same marshal, and the only brake is a `_consecutive_waits >= 2` latch — i.e. the design *requires a second wasted no-op to detect idleness*, and that second no-op ships to the client. Message is a pure function of (name, location, stance), so the two lines are byte-identical. **30 verbatim duplicate lines across 41 phases**, 23 of them `Deroy holds position at Swabia…`. Concentrated on Deroy because he is authored `literal` and `_evaluate_marshal` has no literal arm — only the aggressive and cautious branches have a "nothing to do → `None`" exit. | ✅ **FIXED at the view layer**, beside PT-D4's move-chain collapse and by its precedent — the producer's `action_count` and `max_total_actions` break are computed *before* the append, so pruning inside the loop would desynchronise the budget and reach `BASELINE_SERIES`. The view fix also covers all **five** `wait` producers rather than the one that was loudest. Measured **30 → 0** duplicate lines. |
| **PC-3** | P2 | **Fortify immediately followed by unfortify, same marshal, same phase** — 41 thrash occurrences (incl. `wait×2`); Brunswick on turns 14, 16, 18; `ArchdukeJohn: move, attack, fortify, unfortify, attack`. Burns 2 of 4 AP for a net-zero state change. **PT-F6 fixed form/break square only** and does not cover fortify. | ✅ **FIXED (balance half)** — at the **fortify** side, not the unfortify side. `_check_threats` (P3) explicitly folds same-region enemies into its "adjacent" list and was **the one fortify site in `enemy_ai.py` without the engaged guard** its three siblings already carry (P5 `:3703`, both P8 arms `:4174`/`:4274`), while P0's engaged-while-fortified arm unfortifies **unconditionally** — so the pair was self-cancelling *by construction*, exactly the S5-1 argument written one line below it. **This is NOT the reverted latch.** That one blocked the *unfortify*, removing the AI's escape from a fortified position, and its measurement stands: it diverged `BASELINE_SERIES` and collapsed the AI-V §4.7 variance signature. Blocking a fortify P0 was always going to undo removes no reachable state — only the round trip to it. M1–M7 and `BASELINE_SERIES` **byte-identical, no re-record**. |
| **PC-4** | P2 | **Battle names collide and ordinals skip.** Swabia produced, in order: *The Great Battle of Swabia* (t1), *Second* (t1), *Third* (t3), ***The Great Battle of Swabia* again** (t3), *Fifth* (t3), *Sixth* (t3). The namer prefers the "Great" form on a significance predicate while the ordinal counter counts all battles in the region, so a later great battle silently duplicates an earlier name and the sequence loses "Fourth". | ✅ **FIXED.** Two defects from one line, and the same line caused both: the Great tier *replaced* the ordinal but still *consumed* the counter. The ordinal now always names the battle's place in the region's series and "Great" modifies it — "The Great Battle of Swabia" then "The Great Fourth Battle of Swabia". **Uniqueness is structural** (the counter is strictly increasing), not a de-duplication pass. The W6-2 pin `test_great_tier_replaces_ordinal` was flipped **consciously** and renamed. |
| **PC-5** | P2 | **The diorama observation contradicts its own contingent list.** Turn 1: defender side lists Lannes/Davout/Ney all `engaged`, `committed_total 64,943`; the observation over that tableau reads *"Lannes held the field alone — reinforcement never came"* and names two marshals absent from the tableau entirely. The "held the field alone" phrasing is not gated on any count of arrivals. | ✅ **FIXED.** The bank is split: `coordination_reinforcement_failure` keeps the lines that are true whoever else was present, and a new `..._alone` bank holds the solitude claim, reachable only when our side's participant list is exactly the primary. Gated on new display-only `attacker_participants`/`defender_participants` on `coordination_context` — the same lists the diorama's fought line is built from, so the two surfaces cannot drift. **A missing list is not evidence of solitude**: when we cannot check, we do not claim it. |
| **PC-6** | P2 | **The flanking line names a province the attacker's side does not hold.** t1 `Mack flanks from Swabia while allies attack from Rhineland!` — Rhineland was French. t3 `ArchdukeCharles flanks from Swabia…` while attacking *into* Swabia. | ✅ **FIXED — and it was not a copy bug.** The flanking tracker keyed on the contested REGION alone and was side-blind, so two armies fighting over one province **pooled their approaches and each was awarded a coordination bonus for the other's march**. `record_attack` now carries the attacker's nation and `calculate_flanking_bonus`/`get_flanking_message` filter on it (omitting it keeps the legacy pooling, so 40+ pre-existing `test_true_flanking` pins are untouched). Second half: a marshal already standing IN the contested province is the anvil, not the hammer — "holds them at Swabia" replaces "flanks from Swabia". M1–M7 and `BASELINE_SERIES` byte-identical. |
| **PC-7** | P3 | ✅ **FIXED** — **The dispatch headline is a stuck record.** `estate_eroding` led **21 of 41 turns (51%)**, longest run **7 consecutive**, and the identical sentence about Davout's household appeared **12 times** with a byte-identical Berthier note — while the treasury held 39,000g and the nag was trivially affordable. No repeat-suppression, cooldown or variety rule exists on the headline scorer. The first line the player reads every turn is the most repetitive text in the game. | ✅ **FIXED.** The cause was a category error in the weight table: most classes are **event**-derived off a one-turn window, so on a quiet turn they do not exist — but `estate_eroding` and `enemy_on_our_soil` are **state** predicates that re-manufacture their candidate every turn. Weight 55 then won by walkover forever, and the July-19 anti-repeat guard had two holes (it compared exact rendered *text*, not class, and was gated behind `len(candidates) > 1`, so the sole-candidate turns — exactly the seven-turn run — skipped it). Now: `STANDING_HEADLINE_CLASSES` + `STANDING_LEAD_MAX = 2`; a standing class that has led its allowance **yields to any other candidate and falls to a sub-beat** (never suppressed — `CREATIVE_AUDIT_2026_07_19` §308 and its pin), and when it is genuinely the only news it keeps the lead but **escalates its wording** and names the remedy. ONE new serialized field `headline_lead_memory` — its own field, not a read of `last_morning_dispatch`, because `_build_headline` returns `None` on a candidate-free turn and a nested memory would be wiped by exactly the quiet turns a passive campaign is made of. Berthier's note arm — priority 0, short-circuiting the whole ladder — hands back once the streak passes the allowance, so the closing line can say what the opening line did not. Selection tail extracted to `_select_headline` so the rule is one testable source; the `test_creative_audit_2026_07_19` body-scrape pin was updated **consciously** to follow it and made stricter. Measured over 30 fresh turns: headline share **51% → 30%**, longest run **7 → 4**, and turns 3 and 4 of a run now read *"Marshal Ney has now gone unrewarded 3 turns…"* then *"4 turns without settlement on Marshal Ney. A rente would close it today."* |
| **PC-8** | P3 | **The strategic first-step bad-odds interrupt prices solo strength**, while the *attack* path's muster preview (PT-D1) prices the committed joint figure. t1: "Odds unfavorable" at Ney 24k vs Mack 52k → on `press on`, Davout and Lannes auto-reinforced and it was fought at ~68k vs 52k. Refuter correction: the interrupt shows **no figures at all**, so there is no on-screen contradiction — severity P3, not PT-D1's P2. Any fix must carry the `player_nation` guard the muster preview's existing call site uses, and the mechanical variant provably breaks a CR-5 pin (solo ratio 0.6705 → joint 1.0297). | ✅ **FIXED as legibility, not as arithmetic.** The gate stays solo-priced and that is correct, not merely constrained: it is the acting marshal weighing *his* corps against a dug-in enemy, and re-pricing it on the joint force flips the canonical case from unfavorable to favorable and makes the gate unreachable. What was wrong is that the modal said "in greater strength" and stopped, while `press on` committed two more corps. New `CombatExecutor._bad_odds_muster_note` appends Berthier's addendum — who would march and the figure they make together — read off the SAME muster ladder the attack path's preview uses (`_muster_reason` → `_committed_reinforcement_strength`), so the two surfaces cannot drift. Carries the `player_nation` guard. Wired at all four `describe_inferred_bad_odds` call sites; the no-muster case is byte-stable and pinned. |
| **PC-9** | P3 | **Player tutorial copy inside the enemy's report** (`Any order — even one that fails — will break the discipline required to hold square.` under `[Austria]`); **`The Switzerland has ceased to exist.`** (hardcoded definite article); **`en_route` to the province the marshal is standing in**; and the notification tray reaching **50 alerts with 7× "Ney is cornered"** duplicated and a turn-3 alert still live at turn 42. | ✅ **FIXED, all four.** (a) The square rule is addressed to the reader ("any order *you* give"), so it is player-nation-scoped; the mechanic stays symmetric. (b) New `display_names.with_definite_article` / `takes_definite_article` resolve the article per NAME at the render seam — a carved client may be an institution ("the Duchy of Warsaw") or a bare state ("Switzerland") and one sentence serves both; `carved_name` in the event payload stays the RAW tag for mechanical readers. (c) A MOVE_TO whose destination is where the man stands reports `arrived`, not `en_route` — the status line was reading the order rather than the man. (d) The tray collapses an un-dismissed repeat of itself, keyed `(type, headline, SUBJECT)` — subject-scoped because PF-5 pins that two proposal results sharing a title must both survive, which a bare `(type, title)` key broke immediately; the survivor keeps the newest message/turn, takes the higher priority, and carries `(xN)` in its title. Plus the actual cause of the stale row: the last-stand notice is an ASK and was never retired when answered — now dismissed at **both** seams (the answer path and capture), each pinned by a path the other cannot reach. |

### The composition slice — ROADMAP position 3, landed August 4, 2026

**Every OPEN row above is closed.** Tests: `tests/test_pc3_pc9_composition.py` (34)
plus 2 net-new W6-2 pins in `tests/test_w6_battle_naming.py`. Suite
**16,100 → 16,136 / 3 skipped**, ruff clean, golden corpus 514/514, **no `.gd`
touched**. M1–M7 **and** `BASELINE_SERIES` byte-identical — **no re-record**,
including across PC-3's producer change and PC-6's mechanical one.

**A 12-mutation sweep ran over the new pins and found one inert.** The
last-stand notification test passed with the `strategic.py` dismissal disabled,
because `_capture_marshal`'s own sweep cleaned up behind it — `fight_to_the_last`
ends in capture on every path. It is now two tests: a *successful breakout*
(never captured, so only the answer seam can clear it, escape roll forced) and a
capture. Both mutations are caught; 12 of 12.

**Two claims in the filed rows were wrong and are corrected here, not buried:**

- **PC-6 was filed as a copy defect and is a mechanics defect.** "The flanking
  line names a province the attacker's side does not hold" is the *symptom*; the
  cause is that `attacks_this_turn` keys on the contested region and nothing
  else, so an enemy's attack on the same province counted toward YOUR pincer and
  paid YOUR side a coordination bonus. The message was telling the truth about a
  number that was wrong.
- **PC-3's "largest single contributor to the farce reading" is spent.** The
  display half already took thrash 41 → 0 in the transcript; what remained was
  purely the 2 wasted AP, and it is fixed on the fortify side rather than the
  unfortify side precisely so the reverted latch's measured cost is not re-paid.

**Recorded, unmeasured:** all three behaviour-touching fixes (PC-3, PC-6, and
PC-9's tray) leave the 40-turn ambient trace byte-identical, which means the
ambient harness never exercises them — it has no same-province two-sided battle
and no repeated cornering. Their reachability is proven deterministically by the
unit pins above, not by the sweep. The same honesty the NV-4 and IGR-X3 records
carry: byte-identity here is evidence about the harness, not about the fix.

**Corrected by the refuters, recorded so the corrections are not re-lost:**
- My first reading of PC-1 was *"a forced-retreat capture prints no capture line"*. Half wrong: the capture is real and one-phase (attacker wins → defender forced out → `_attempt_region_capture` takes the vacated province, and the code comments say so), and the loss **is** announced — the next turn's dispatch headlines it at weight 100. The actual defect is the wrong noun, above.
- My reading of *"one marshal takes five actions"* as a defect is **WORKING-AS-DESIGNED**: the action budget is per **nation**, not per marshal (`ENEMY_AI_REFERENCE.md:35`), full round-robin is an explicit Post-EA row (`:899`), and the AUD-e behaviour half was **dropped** at 8.EVAL. My count was also inflated — `grant_dotation` entries come from the nation's separate *admin* phase and are concatenated into the same array. What is genuinely wrong inside that observation is PC-2 and PC-3.

---


## ~~PARSE-NEG — the fast parser is confidently WRONG above the LLM escalation gate~~ (filed August 3, 2026 — ✅ **FIXED August 3, 2026**)

> **✅ FIXED August 3, 2026.** The whole family, plus eight more defects the
> fix's own evaluation turned up. **Landing record = §PARSE-NEG landing below**
> (immediately after the filed analysis, which is kept verbatim because its
> reasoning about *why the confidence gate shields negation* is the design
> constraint the fix had to satisfy). New module `backend/ai/clause_guards.py`;
> tests `tests/test_parse_negation.py` (94) + 26 golden-corpus rows.

> **P1. Not a mock-mode gap — an API key does not fix it.** Found by the
> EA-scope refund panel; **reproduced first-hand** on the shipped 1805 board
> through the production `LLMClient.parse_command` call, keyless.

`llm_client.should_use_llm` escalates to the LLM only when fast-parse
confidence is **below** `LLM_FALLBACK_CONFIDENCE_THRESHOLD = 0.7`. Every row
below lands **above** it — so the LLM is never consulted, in any mode, with
or without a key. The golden corpus never caught it because these phrasings
are not in it.

| typed | parsed as | conf | escalates? |
|---|---|---|---|
| `Ney, attack Mack` *(control)* | attack, Ney | 0.90 | no — correct |
| `Davout, fortify` *(control)* | fortify, Davout | 0.90 | no — correct |
| **`Ney, never attack Mack`** | **attack**, Ney | **0.90** | **no** |
| **`Ney, don't attack`** | **attack**, Ney | **0.90** | **no** |
| **`Ney, hold your position, do not attack`** | **attack**, Ney | **0.90** | **no** |
| **`how do I attack?`** | **attack** | **0.80** | **no** |
| **`Ney, hold until Davout arrives then attack`** | **attack** immediately | **0.90** | **no** |
| **`Ney, if Mack advances fall back to Alsace`** | **move** to Alsace, condition dropped | **0.95** | **no** |
| `Soult, dig in where you are` | fortify, conf 0.55 | 0.55 | yes — correctly escalates |

**Four distinct defects, one shared cause** — keyword presence outranks
sentence meaning, and the confidence score does not know it:

1. **Negation inverted.** `never attack` / `don't attack` / `do not attack`
   all issue the attack. This is the severe one: a player loses an army for
   using a word correctly.
2. **Interrogatives read as imperatives.** `how do I attack?` issues an
   attack at 0.80 — a help question becomes an order.
3. **Sequencing collapsed.** `hold until Davout arrives then attack` attacks
   now. (CR-2 handles `then` for *two clauses*; the `until X` precondition
   is dropped.)
4. **Conditionals dropped.** `if Mack advances fall back to Alsace` moves
   immediately at 0.95 — the highest confidence in the set, on a sentence
   whose entire meaning is the condition.

**Why the confidence gate makes it worse rather than better.** The gate
exists so cheap parses skip the LLM. But confidence is computed from
keyword-match strength, and a negated sentence contains the *same keywords*
as its affirmative — so negation SCORES HIGHER, not lower, and is
structurally shielded from the one component that could catch it. The fix
must lower confidence (or refuse) on these shapes, not add another
downstream guard.

**Scope of the fix (bounded, no gate needed):**
- a negation pre-check ahead of action selection — `never`, `don't`/`do not`,
  `stop`, `cancel`, `no longer`, `rather than`, `instead of`;
- an interrogative pre-check — leading `how`/`what`/`why`/`can I`/`should I`,
  or a trailing `?`;
- treat `until` / `if` / `unless` / `when` as the CR-2 clause-boundary family
  already handles `then`, and demote confidence below 0.7 so the LLM is
  actually consulted;
- **golden-corpus rows for every line in the table above**, since step 12 of
  the new-action checklist exists precisely to stop this class from
  regressing.

**Do NOT "fix" it by raising the threshold.** That escalates everything and
makes the game LLM-dependent — the opposite of the EA framing, where mock
is the shipped default.

Reproduction: `LLMClient(); parse_command(text, world)` against
`europe_1805.json`, `LLM_MODE=mock`, no key. Verified August 3, 2026.

**Owner:** the plan's position 11 (CR-6 proper) is where this class of work
lives, but this defect is a correctness bug and should not wait for a gate.
Recorded in `docs/audits/ROAD_TO_EA_REPLAN_2026_08_03.md` §amendments.


### PARSE-NEG landing record — August 3, 2026

**What ran first.** A full evaluation of the parse pipeline before any fix:
~130 utterances across nine families driven through the production call shape
`CommandParser.parse(text, llm_game_state, world=world)` on the shipped 1805
board, keyless. It confirmed all five filed rows and found **eight more
defects of the same class**, three of them worse than anything filed.

**The severest finding is not in the filed table.** `don't declare war on
Austria` **declared war**, at confidence 0.95 — an irreversible, nation-level
act, from a negation. So did `Talleyrand, do not propose peace with Austria`
(proposed it) and `do not invade Prussia` (declared). The filed table sampled
only the military verbs; the diplomatic routes sit *above* them in the same
keyword chain and were never checked.

**The second class the evaluation exposed: phantom provinces.** The free-text
target scan fuzzy-matched ordinary English into real places and shipped the
result as the province a marshal was ordered to take — **not** →
Brabant, **how** → Buxhowden, **able** → Naples, **happens** → White Russia,
**lost** → Ulster, **thinking** → Wales, **more** → Moore (the British
marshal), **relieved** → Rhineland, **square** → Normandy, **rente** → Crete,
**pass** → Nassau. `Ney, form square` and `Ney, hold the pass` — plain orders,
no negation anywhere — were affected. All at 0.8–0.9.

**And two plain gaps.** `Ney, go to Alsace` was **unparseable** (the move
keyword list carried "head to", "proceed to", "travel to" and "ride to" but
never "go to"); and the destination regex anchored on the FIRST preposition,
so `Ney, I want you to move to Lorraine` marched on the phantom province
"Move To Lorraine".

**The fix, and why it is not the one the row prescribes.** The row asks for the
confidence to be demoted "so the LLM is actually consulted". Confidence *is*
demoted — but escalation is **declined for a refusal**, deliberately
(`_should_fallback_to_llm`, commented in place). Under forced tool-use every
model reply must name an action from the enum, and the one sentence we would
be handing over is the one whose only verb the player forbade. The guard is
what makes that safe: it does not refuse whenever it sees a negation, it
**removes the negated clause and re-reads what is left**, so
`Ney, hold your position, do not attack` now parses as HOLD and never reaches
the refusal at all. What remains is only the case where there is no order for
a model to find. Mock is the shipped EA default, so a live-only escape hatch
could not have been the primary fix either way.

| # | Fix | Seam |
|---|---|---|
| 1 | **Clause guards** — negated and conditional clauses are blanked with SPACES (never spliced, so every position-aware rule downstream keeps its indices) before any routing reads the text | NEW `backend/ai/clause_guards.py`; wired at the top of `llm_client._parse_with_mock`, after cheat/debug so literal arguments are never blanked |
| 2 | **Negation refusal** when the negation consumed every word that could name an order — checked once before diplomatic routing (which returns early) and once after action selection | `llm_client._refusal_result`, new `ParseResult.refusal` |
| 3 | **`until` scoped, not refused** — it is the one condition `StrategicCondition` implements, so its clause runs to end-of-utterance and the keyword inside it stops outranking the main verb | `clause_guards._UNTIL_CLAUSE_END_RE` |
| 4 | **Conditional refusal** for `if`/`unless`/`when`/`once`/`after`/`as soon as`/`should <third party>` — gated on a **two-word clause**, which is what keeps the corpus pin `cr2-when-ready-then-retreat-not-split` green | `clause_guards.strip_condition_clauses` |
| 5 | **Stand-down → cancel** — "stop attacking" / "attack no more" are unambiguous, so they route to the existing cancel action rather than a refusal | `clause_guards.mentions_stand_down` |
| 6 | **Question → help** — sited AFTER diplomatic routing so Talleyrand's advisory desk keeps its own, better answer | `clause_guards.is_question` |
| 7 | **Phantom-province gate** — a general English stopword list *plus* an independent typo-shape gate (same first letter, edit distance ≤2), because neither alone catches both "square"→Normandy and "relieved"→Rhineland | `parser._NON_TARGET_WORDS`, `parser._plausible_name_typo`, applied to the free-text scan AND the strategic region fuzzy |
| 8 | **Destination = the LAST preposition**, with a widened tail-cutter | `llm_client` Sweep-5 fallback |
| 9 | **`go to <region>`**, guarded against "go to war" | `llm_client` move keywords |
| 10 | **`pass` the noun ≠ pass the turn** — "hold the pass" was answered with WAIT | `llm_client` wait branch, article lookbehinds |
| 11 | **Target never spans a sentence or subordinate clause** | `strategic_parser._clean_target_text` |
| 12 | **A refusal is a finished verdict** — fuzzy matching returns early, or it replaced the verdict ("Talleyrand, do not propose peace" became *"Did you mean 'Ney'?"*) | `parser._apply_fuzzy_matching` |
| 13 | **Berthier says what he read** — a specific line per refusal kind, never the generic shrug, and it bills 0 AP | `main.py` |

**Two of the fix's own regressions were caught by its own counter-example
pins, not by review:** the should-inversion rule fired on "should **we**"
(taking `Talleyrand, should we declare war on Prussia?` — a working advisory
request — down to a bare address and a marshal-typo error), and the guards were
blanking a question's clauses *before* diplomatic routing could read them. Both
are now regression rows in the corpus and in
`TestGuardsStayNarrow::test_talleyrands_desk_keeps_its_own_answer_for_questions`.

**Falsification.** Every guard trades safety for reach, so the counter-examples
are pinned as hard as the defects: polite orders still march
("would you have Ney attack Mack"), `no quarter` is still an attack idiom,
"Talleyrand, stop the war with Britain" is still a peace proposal, "stop
Davout's pension" is still a revoke, "go to war with Britain" is still a
declaration, typos still auto-correct ("viena" → Vienna, "Mac" → Mack), and
cheat arguments are never blanked. Across the **324 pre-existing corpus
utterances only four trip a guard**, all of them questions, and three of those
are Talleyrand's and keep their advisory answer.

**Consciously flipped pin (one).** `how-is-the-war-going` pinned
`success: false, error_contains: "Unknown action"`. Its source test asserts only
`action != diplomatic_declare_war`, which `help` satisfies; the shrug was
incidental. Flipped to `action: "help"`, source test unchanged and green.

**Accepted, pinned, NOT ideal.** `Ney, retreat if outnumbered` still retreats
now — the two-word floor that protects `when ready then retreat` also lets a
one-word elliptical condition through. Pinned as
`parseneg-retreat-if-outnumbered-executes` so the trade-off is visible rather
than discovered later. A real conditional-order system is CR-6/CR-7 scope.

**Verification.** Suite **16,042 passed / 3 skipped** (was 15,901/3), ruff
clean, golden corpus **514/514**, and live-verified over HTTP against a fresh
backend on the 1805 board (refusal lines, the recovered HOLD, `go to Lorraine`
marching Rhineland→Lorraine, `stop attacking` cancelling). No `.gd` touched.

**Routed, not fixed (new row).** `executor.py:300` answers an unknown province
with *"Nearby: Wales, Balearics, Ulster"* — the list is fuzzy **name**
similarity, not geography, so the word "Nearby" is a lie. Left alone because
that exact wording is the documented Sweep-5 contract in three places
(`SWEEP_5_LIVE_EVIDENCE_2026_07_16.md`, `STATUS.md`, `generic_targets.py`);
re-labelling it belongs to whoever next opens that contract. **PARSE-NEG-X1**,
P3.


## Live-Playthrough Findings (August 1, 2026 — the played-world creative-audit re-measure)

> Source: `docs/audits/AI_V_SWEEP_2026_08_01.md` §10 (the full ledger and the scored
> addendum live there). **ALL 10 DEFECTS FIXED.** F2/F3/F4/F5/F7/F8/F9/F10 in the
> re-measure session itself (`tests/test_playthrough_fixes_2026_08_01.py`, 12); PT-F1 +
> PT-F6 in the second Aug-1 session under the user's delegated grant — struck rows below
> carry the landing records.

### ~~PT-F1 — Pursuit-battle capture of neutral/allied soil has zero diplomatic consequence~~ (✅ FIXED August 1, 2026, P2)

> **✅ FIXED August 1, 2026 (second session).** The one-question gate was delegated
> ("make the decision yourself") and **decided as the row recommended: (i) for neutral
> courts, (iii) for allies/vassals.** Landing record = this block; tests
> `tests/test_neutral_soil_pursuit_capture.py` (7) cover both live shapes.
>
> **What shipped.** ONE predicate — `combat_executor._pursuit_capture_guard`, keyed on
> the region's CONTROLLER at the moment of transfer — now guards all four capture doors:
> the main battle-advance, the auto-bombardment advance, the glorious charge, and the
> reckless auto-charge's bare controller assignment in `world_state.py` (the V2-53
> simplified path, which bypassed the executor funnel entirely). Attacking the enemy ARMY
> standing on a third party's soil stays legal — the annexation is what needs a war.
> - **Neutral court (PEACE, attackable)** → the pin-15 War Purpose flow: the advance
>   halts at the frontier ("Ney halts at the frontier of Nassau — Hesse's soil"), nothing
>   transfers, and the player is offered the declaration through the SAME
>   `war_purpose_selection` dialogue the undefended-territory gate stages (the closure's
>   core hoisted to `_stage_war_purpose_selection`, shared verbatim). The Ansbach moment,
>   as a choice.
> - **Ally/vassal (`can_attack_nation` False)** → pursuit ≠ conquest: the victor advances
>   as a LIBERATOR (driving Mack off Bavarian Swabia is the alliance working), the
>   province stays its owner's, no plunder/secure prompt, no threat accrual for a
>   province that never fell (the `+15 capital_capture` was already gated on `conquered`;
>   the honest `+3 battle_win` stays).
> - **GR5** — same predicate both sides; the AI's answer is RESTRAINT (no capture, no
>   auto-declaration): its war decisions belong to the Stage-D machinery, never to a
>   pursuit's momentum. Pinned: Mack destroying a French corps in Nassau leaves Hesse at
>   PEACE and Nassau Hessian.
>
> **Both live cases pinned:** the Nassau shape (halt + staged dialogue + no threat spike)
> and the literal boot-Ulm board (Mack occupies BAVARIAN Swabia; the strike now liberates
> it for Bavaria), plus the at-war control arm (Tyrol still falls, plunder prompt intact).
> Out-of-scope, noted for a future owner: a fortified-occupation timer that started at war
> and completes after a peace is a different (pre-existing) shape and was not touched.
>
> **`BASELINE_SERIES` RE-RECORDED CONSCIOUSLY ONCE** (the IGR-X4 discipline; record at
> the constant, `test_ai_intent_threat_migration.py`): a live spy on the guard found the
> OLD baseline world contained exactly two silent third-party annexations — **turn 5,
> Austria's Mack pursuing into BERLIN, Prussia's CAPITAL, at peace with Austria** (the
> standing baseline had Prussia's capital flipping Austrian, unremarked), and turn 6,
> Britain's Moore seizing Hanover's Brunswick. Both now halt at the frontier; Prussia
> keeping Berlin is a structurally different (and finally sensible) Europe, so the series
> diverges from index 5. Attribution is clean: PT-F6 was measured in isolation FIRST
> (byte-identical, 72/72); every other fix this session is presentation-only. M1–M7 held
> byte-identical throughout.

### ~~PT-F6 — The AI square-thrash: form/break/re-form in one enemy phase~~ (✅ FIXED August 1, 2026, P3)

> **✅ FIXED August 1, 2026 (second session), in its own commit per the row's
> harness discipline.** The live shape — Moore forming square THREE times in one phase,
> breaking it himself each time (stance change, then counter-punch, then re-form) — was
> reproduced deterministically before the fix (the reproduction lives on as the test's
> control arm) and cut to ≤1 formation per marshal per phase.
>
> **Mechanism confirmed:** the P2.5 break rung sets `ai_square_cooldown`, but
> `_auto_break_square` (fired when the AI's own attack/move/stance change breaks the
> square) set nothing — so the planner re-formed the square it had just broken. Two
> halves, both at EXECUTION seams (never inside `_evaluate_marshal` — the
> evaluation-time `ai_square_cooldown` stamp is the documented anti-pattern):
> - **The latch** — `self._squares_formed_this_turn`, initialized with the per-phase
>   state block, written on the executed formation, read in P2.5's form condition: a
>   marshal forms square at most ONCE per enemy phase.
> - **The stance guard** — the central candidate filter now skips `stance_change` for a
>   marshal standing in square (the S5-1 fortify guards' missing sibling): the square IS
>   the posture; P2.5's break rung owns the deliberate exit. Attack/move breaks stay
>   legal — abandoning a square for a counter-blow is a choice, fidgeting out of it is
>   farce. Production transcript now reads "forms square → counter-punches (square
>   broken) → fortifies" — one formation, the break a choice.
>
> **Harness verdict (the conscious-re-record discipline): M1–M7 AND `BASELINE_SERIES`
> byte-identical, 72/72 green before and after — NO re-record needed.** The ambient
> 40-turn world never assembles the adjacent-cavalry-with-self-break conjunction; the
> thrash was a played-world artifact. Tests: `tests/test_ai_square_thrash.py` (6 — the
> phase-transcript ≤1 pin with a neutered-latch control arm that must still reproduce
> the thrash, the stance-guard pin with its not-in-square positive control, and the
> rung-level latch pin in the existing cooldown test's idiom).

### PT-observations routed to owners (✅ ALL FOUR LANDED August 1, 2026, second session)

- ~~**Muster one-voice odds (CO-6 finisher)**~~ ✅ PT-D1 LANDED — struck row in
  `DESIGN_REFINEMENT.md` §Live-Playthrough carries the landing record.
- ~~**Diorama contingent taxonomy**~~ ✅ PT-D2 LANDED — ditto.
- ~~**Letter-book label coherence**~~ ✅ PT-D3 LANDED — ditto.
- ~~**Move-chain presentation**~~ ✅ PT-D4 LANDED — ditto; the naval gate itself stays
  owned by **DEF-5**, whose urgency the re-measure upgraded (Spain besieged London on
  turn 5 — "the believability ceiling").

---

## ~~IGR-X3 — The player can never end a boot war bilaterally, in EITHER direction~~ (✅ FIXED July 26, 2026, P1)

> **✅ INVESTIGATED, PUT TO THE USER, AND FIXED July 26, 2026.** The user chose the full
> scope ("Everything, incl. armistice thaw") after a 24-agent verify→refute investigation.
> **Landing record = this block.** Tests `tests/test_igr_x3_peace_relation_floor.py` (33).
>
> **What shipped.** `STATE_RELATION_REQUIREMENTS["PEACE"]` is now `None`. Ending a war is
> not an act of friendship; what prices a peace is war score, position and exhaustion,
> which `calculate_acceptance` already weighs. **The rows above PEACE are untouched** —
> `validate_transition` permits any upward jump, so they are the only thing preventing
> `WAR → ALLIANCE`. Nobody has to like you to stop shooting; somebody does have to like
> you to march beside you. The dead `TRANSITION_RULES[...]["relation_req"]` copy of the
> number was cleared with it so the spec table cannot contradict the live rule.
>
> **The truce now actually cools tempers.** `_process_relation_decay` no longer lumps
> ARMISTICE in with WAR: a truce thaws at `ARMISTICE_THAW_PER_TURN = 3`, WAR still
> freezes. Measured: Britain −90 → −75 over one five-turn truce, and a second carries it
> to −60 and `armistice_expired_peace`. The authored expiry fork is reachable by the
> passive route the game already advertised.
>
> **Plus the two P1s that were independent of the floor:**
> - `_handle_accept_ai_proposal` ignored a `diplomatic_treaty_failed` result, so a
>   refused ratification was reported as an acceptance. Measured verbatim: `success: true`
>   with *"You have accepted Britain's proposal. Relations with France are insufficient for
>   PEACE."* — the offer consumed, the cooldown applied, the war carrying on. It now
>   reports honestly, in the same vocabulary as the sibling counter-offer guard that has
>   had this check since G4F-13, and does **not** burn the acceptance cooldown (nothing was
>   accepted, so the court stays free to raise it again).
> - The one place the game taught the escape said *"five turns of quiet may cool tempers
>   enough to sign"* while decay skipped ARMISTICE outright. **That advice is the likely
>   proximate cause of this bug report** — follow it literally and the war resumes in five
>   turns. Deleted rather than reworded, and the mechanism it described is now real.
>
> **⚠ THREE OF THE CLAIMS BELOW WERE WRONG, and one of them was mine.**
> 1. **"Can they recover? **No**"** — refuted. `mission_improve_relations` IS offered, in
>    the ARMISTICE branch. The war was endable; the route was undiscoverable, monopolised
>    the single world-wide mission slot, and was taught by copy that described a
>    non-existent mechanism. "Impossible" was the wrong diagnosis of a real defect.
> 2. **The IGR-D residual's −95/−100/−95 boot relations** are wrong; this row's
>    −90/−80/−80 are right, measured on the shipped board and NOT seed-dependent (the
>    scenario deliberately leaves `starting_wars` pairs unbanded). Corrected in
>    `INGAME_REVIEW_FIXES_SPEC.md`.
> 3. **The floor was never gate-blessed and its enforcement was an accident.** It was
>    authored as the armistice-EXPIRY branch condition — a job `ARMISTICE_AUTO_PEACE_RELATION`
>    still does — and `check_relation_requirement` was DEAD CODE for three days before a
>    cleanup commit ("4 unwired functions wired") switched it on. The player/AI asymmetry
>    is scaffolding from the commit that unified AI-AI ratification, not a designed rule.
> 4. **Option (b), war-score-aware relief, is INERT and was not built.** `cleanup_war_end`
>    pops the pair's war score on any WAR→non-WAR transition, so relief at ARMISTICE would
>    always be 0. The costing that recommended it had measured a hand-set fixture.
>
> **Byte-identity: M1–M7 and the 40-turn `BASELINE_SERIES` are unchanged — and the honest
> reason is that the ambient harness never enters ARMISTICE at all** (measured: 0 armistice
> turns in 40). The thaw is symmetric and WILL move AI-AI relations in a played game; the
> harness simply cannot see it. Recorded rather than treated as evidence of no effect.
>
> **Five tests consciously flipped or re-sited**, each with its reason written at the
> assertion: the two floor-value pins, the counter-offer gate pin and the failed-ratification
> pin (both re-sited off PEACE onto `non_aggression`, where the guard is still
> load-bearing), and `test_conflict_alert_accept_anyway_ratifies` — which turned out to
> have been asserting a lie since it was written: its fixture never cleared the ALLIANCE
> floor, so the treaty it claims to ratify was refused and the handler reported success
> anyway. Its name says "ratifies"; now it does.

<details><summary>The original bug row, kept for the record</summary>

## IGR-X3 — The player can never end a boot war bilaterally, in EITHER direction (was OPEN, P1)

**Found July 25, 2026** while landing IGR-D, which hit it as a hard residual: a
`create_client` carve can only travel on the bilateral peace route, and that route is
unreachable for the three wars the campaign opens with. Measured, not argued — every
number below is from a live probe on the shipped `europe_1805` board.

**The rule.** `STATE_RELATION_REQUIREMENTS["PEACE"] = -60` (`diplomacy.py:86-93`), enforced
at `world_state.py:7950-7959` under `if is_player_treaty:`.

**Why it is unreachable.**

| | |
|---|---|
| Boot relations | France/Britain **−90**, France/Russia **−80**, France/Austria **−80** |
| Can they recover? | **No.** `_process_relation_decay` (`diplomacy.py:9698-9700`) explicitly skips `WAR` **and** `ARMISTICE`, so the +1/turn drift toward the neutral band never runs while the war is on |
| The armistice escape | `ARMISTICE_DURATION = 5`, and armistice also skips decay — a treadmill, never a path to PEACE |
| Scope | `is_player_treaty = (proposer == player OR target == player)` (`world_state.py:7915`) — **both directions** |

**Three things make it a defect rather than a difficulty:**

1. **Accepting the AI's OWN peace offer fails.** Probed: Austria proposes peace to France,
   France accepts → `diplomatic_treaty_failed`, *"Relations with France are insufficient
   for PEACE."* The AI offers a treaty the engine will not let the player take.
2. **The AI is exempt (GR5).** Probed: an AI↔AI peace at relation **−95** ratifies
   normally (`ai_ai_treaty`, state → PEACE). Two courts that hate each other may end their
   war; the player may not. Golden Rule 5 exists to forbid exactly this.
3. **The joint settlement route does not apply the check at all** — `settlement_ratify`
   never calls `check_relation_requirement`. So the identical peace is legal or illegal
   depending only on which surface the player used. The gate is a route artefact, not a
   rule.

**The design argument (user, July 25, 2026):** *"relation shouldn't impact war, people in
war hate each other anyway."* Historically exact: Pressburg (1805) and Tilsit (1807) were
signed at the maximum of mutual hatred, *because* of the war's outcome. War score,
military position and exhaustion are what should price a peace — the acceptance formula
already models all three. A relation floor on top double-counts the hostility and then
makes it absolute.

**Not fixed in IGR-D, deliberately:** removing or reshaping the floor re-prices every
bilateral peace in the game and touches the AI counter-offer path
(`ai_diplomacy.py:1926`). It needs its own investigation and a decision.

**Owner:** the next session (investigate + propose; see `docs/STATUS.md` Next Steps).

</details>

---

## IGR-E — routed in passing, July 26, 2026 (X4–X8 ✅ FIXED July 31, 2026; X9 stays homed at the econ gate)

Found by the IGR-E ground-truth pass (the plunder-multiplier slice) and **deliberately not
absorbed into it** — each is either a *shape* change to an already-blessed number or a
separate pre-existing path. Landing record for the slice itself:
`docs/INGAME_REVIEW_FIXES_SPEC.md` §2 IGR-E.

**July 31, 2026 — X4/X5/X6/X7/X8 ALL FIXED in the IGR-G session under the user's
delegated grant** ("complete the igr work … feel free to go off spec if something is bad
wrong or poorly designed"); X9 is decision-shaped and stays with the econ gate. Landing
notes per row below; build summary in `INGAME_REVIEW_FIXES_SPEC.md` §6.

| ID | Sev | Item | Owner / landing |
|---|---|---|---|
| ~~**IGR-X4**~~ | **P2** | **The W6-8 estate confiscation windfall is always exactly 0 gold** — both branches, both sides. `capture_executor._maybe_mount_estate_choice` computes `windfall = int(CONFISCATION_INCOME_MULT × region.get_effective_income())` **after** stage 1 has left stability at 10 (plunder) or 25 (secure); `Region._get_stability_modifier` returns **0.0** at `stability <= 25`, so the product is 0 on every province in the game. The player is shown *"CONFISCATE (+0 gold, Austria will not forgive it)"* and asked to pay −10 relations plus −1 trust on every cautious marshal, and to forfeit the +5 respect bonus, **for nothing**. The docstring at `capture_executor.py:152-154` ("a plundered estate is worth confiscating less than one kept whole") describes behaviour that does not exist — both are 0. The W6-8 tests pass tautologically (`0 == 0`). This is IGR-E's own pathology one stage deeper, and worse. | **Owner: the next econ tuning gate** (`ECONOMY_REVISIT_SPEC.md`, alongside EWC-D1). **Landing:** a slice that re-bases the windfall on `income_value` (as IGR-E did for plunder) or explicitly re-prices it. **Done when:** confiscating a just-captured estate pays a non-zero, stated sum, and a test asserts a *specific* value rather than `0 == 0`. **Escalates** because it changes which income base a blessed W6-8/ES-7 number reads — a shape change, not a tuning. **Test:** `tests/test_w6_estate_confiscation.py` (the tautological pins are the ones to replace).  **✅ FIXED July 31, 2026 (escalation decided under the user delegated grant):** one single source `dotation.confiscation_windfall` = `int(2 × income_value × (1 − war_damage))` — the blessed 2× and its 1.5–3× band stand; only the structurally-zero income BASE was re-keyed (the IGR-E precedent), and the `(1 − war_damage)` term makes the "plundered estate worth less" docstring TRUE (plunder's +0.35 lands before the read). Player prompt, player payment and the AI arm all price through it; the tautological `0 == 0` pins replaced with specific values + a monkeypatch falsifiability pin (`test_w6_estate_confiscation.py`). **The 40-turn `BASELINE_SERIES` was re-recorded consciously once**: four live AI-vs-AI confiscations by turn 9 (Britain stripping Castanos ×3, Spain stripping Moore) now pay 184–400g instead of 0, so the ambient trajectory legitimately diverges from turn 15 — bisected to this one line, and counted by a live spy because the 500-cap event log had EVICTED all four rows (the IGR-B trap, hit again). |
| ~~**IGR-X5**~~ | P3 | **A strategic-march capture never asks the question and never secures.** `movement_executor.py:483-498` restores `_prior_choice` over the freshly-set `pending_capture_choice`; the comment says "AUTO-SECURE this province" but **`_apply_secure` is never called** — so buildings stay *undamaged*, construction is neither continued nor cancelled, and **no `region_captured` event is logged**. Marching in is therefore strictly better than capturing and securing. IGR-E raises the value of the branch being skipped. | **Owner: row IGR-G** (the remaining IGR slice) or the next movement/capture pass. **Landing:** call `_apply_secure` and log the event on the march-capture path, or state in the code why the asymmetry is intended. **Done when:** a march capture and an attack capture leave the province in the same state given the same choice, pinned by a test. **Test:** `tests/test_pf3_uncontested_occupation.py`.  **✅ FIXED July 31, 2026:** the strategic-march capture now calls `_apply_secure` and logs `region_captured` (method secure) before restoring `_prior_choice` — "AUTO-SECURE" is code, not a comment; the W6-8 estate question deliberately does NOT mount mid-march (stated in the code: the holder keeps his title, indistinguishable from respect minus the goodwill entry). The vacuous "auto-secured" pin now asserts stability/buildings/events (`test_pf3_uncontested_occupation.py` +2). |
| ~~**IGR-X6**~~ | P3 | **`region.plundered` is serialized and has no mechanical readers.** Writers at `combat_executor.py` and `world_state.py`; the only reader is its own clear condition in `process_stability_growth`. It costs a save field and reads as meaningful state. **The post-landing review adds the natural consumer (its C-3):** `_apply_plunder` has no repeat-sack guard — a province that changes hands repeatedly pays the full yield each time; a `plundered`-flag check would be both the guard and the flag's first real reader. | **Owner: the next econ tuning gate**, with IGR-X4. **Landing:** either give it a consumer (the repeat-sack guard above, or an occupation-cost/unrest modifier) or delete it with its save-format row. **Done when:** the flag either changes something measurable or no longer exists. **Test:** `tests/test_serialization_enforcement.py`.  **✅ FIXED July 31, 2026:** the repeat-sack guard IS the flag's first reader — `plunder_yield` returns 0 while `region.plundered` stands (clears at stability > 50), so the modal honestly QUOTES 0 on an already-stripped province (shown=applied through the one expression) and `apply_plunder_effects` reads the yield BEFORE setting the flag (GR4, load-bearing, pinned). `test_plunder_secure.py` +1; three pre-existing pins re-ordered to pre-sack reads. **Accepted residual (post-landing review, refuter-sized P4, stated not hidden):** a July 26–31 save holding a LIVE stage-1 question over an already-flagged province keeps its stored full quote (the IGR-E backfill fires only when `plunder_gold` is MISSING) while the answer now pays 0 — a version-migration staleness confined to a 5-day window on a compound-rare state (AI plunder → player recapture → mid-question save), self-healing once answered; re-pricing stored quotes at load would risk the round-trip pins for one modal's worth of exposure. The refuter also proved the in-session direction CANNOT occur (capture resets stability to 25; max same-turn growth reaches 40, below the >50 clear; the pending question then blocks end_turn). |
| ~~**IGR-X7**~~ | P2 | **Capture-choice responses drain the PopupQueue** (pre-existing; surfaced by the review's dialogue-id lens, attribution to IGR-E refuted — behaviour is byte-identical pre-slice). `main.py`'s `build_base_response`/`_build_result_response` default `include_popup_passthroughs=True` on the `/command` capture early-return and on `/capture_choice`, which POPS a queued popup into keys `main.gd`'s capture route never reads — the popup is discarded. A ready-made fix exists: `_fill_popup_keys_without_draining`. | **Owner: row IGR-G** or the next popup-pipeline pass. **Landing:** the capture early-return and `/capture_choice` fill popup keys without draining, or the client route learns to read them. **Done when:** a popup queued behind a capture question is still delivered after the question resolves, pinned by a test. **Test:** extend `tests/test_response_pipeline.py`.  **✅ FIXED July 31, 2026:** all three capture arms (`/command` typed-token router, the capture early-return, `POST /capture_choice`) fill popup keys via `_fill_popup_keys_without_draining` — a popup queued behind a capture question now rides the player's next ordinary `/command` (the IGR-F letter-book discipline); `_build_result_response` gained `drain_popups=False`. E2E pins in `test_response_pipeline.py` (+4). |
| ~~**IGR-X8**~~ | P3 | **The capture surface is uneven across its six routes** (pre-existing, bundled from review C-4/C-5/C-6/C-2): three of five AI-visible capture sites drop `capture_choice` from the conquest event so `enemy_phase_dialog.gd` shows a bare `" CAPTURED!"`; four routes print a literal conquest sentence instead of `capture_choice_prompt` (transcript-only — the priced modal still raises); the command-block message in `executor.py` is unpriced and nameless while its estate sibling names holder and region; and `handle_capture_choice` applies an answer without re-checking who holds the province (reachable when a jealousy autonomous attack's `_strategic_execution` bypasses the pending-choice block). | **Owner: row IGR-G** (capture legibility belongs with its two sibling fixes) or the next capture pass. **Landing:** one sweep that routes all six sentences through `capture_choice_prompt`, attaches `capture_choice` to all five events, and re-validates the holder at answer time. **Done when:** the six routes render identically for identical state, pinned. **Test:** extend `tests/test_igr_e_plunder_prompt.py` route-parity pins.  **✅ FIXED July 31, 2026:** the priced `capture_choice_prompt` sentence now rides EVERY player capture route (field battle, auto-bombardment — which also never flagged the response at all, glorious charge, manual move; garrison/unopposed already had it); `capture_choice` rides every AI-visible conquest event incl. the battle event + `occupation_complete` (and `enemy_phase_dialog.gd`'s bare `" CAPTURED!"` arm renders the suffix); the command-block message states region + price through the same one home; and `handle_capture_choice` re-validates the holder at answer time on BOTH stages — a retaken province lapses the question instead of being sacked in absentia. `test_igr_e_plunder_prompt.py` +10. |
| ~~**IGR-X9**~~ ✅ **DECIDED + FIXED Aug 7, 2026 at the Econ Balance gate** (EB-3.2, `ECON_BALANCE_GATE_2026_08_07.md` §3: **a ruin bills nothing** — damaged buildings and damaged watchtowers are exempt from infrastructure upkeep until repaired; repair (150g) restores function AND the bill, so Secure preserves an OPTION instead of a liability and razing no longer strictly dominates at every multiplier. The razing pin flipped WITH the fix; the plunder acceptance test re-ran GREEN at ×4 — the dissent counter untouched. `test_economy_sink_reachable.py::TestEB3TierScaleAndRuins`) | P3 | **Razing sheds the EC-U2 bill, and no multiplier can change it** (found by the review's balance lens): Secure keeps enemy structures DAMAGED — yielding nothing until a 150g repair yet billed 40g/turn — so on a built province the gold favours Plunder at ANY multiplier, including ×0 (one building's 30-turn bill of 1,200g exceeds the whole 581g revenue gap at the median). Multiplier-invariant by construction, so it can never trigger the IGR-E dissent counter; published in `test_on_a_built_province_razing_pays_and_is_multiplier_invariant`. The counterweight gold cannot price is the structures' function (forts defend, depots supply). | **Owner: the next econ tuning gate**, beside IGR-X4/X6 (all three re-price what conquest does to a province's assets). **Landing:** either bless the interaction as design (razing enemy works is historical) with a doc note, or re-shape (e.g. secure keeps structures undamaged at a ransom, or damaged structures bill nothing). **Done when:** the gate records a decision and the test's docstring points at it. **Test:** the published test above. |

---

## In-Game Review — July 25, 2026 (5 FIXED in-session; 4 routed OPEN)

Found by playing the real client for the queued NA-6c/6d + AI-3r review (France, 1805,
`LLM_MODE=anthropic`, turns 1–9 + a 5-turn `austerlitz` variance pass). Memo:
`docs/audits/INGAME_REVIEW_2026_07_25.md`. Fixed in commit `bdeb17c`,
tests `tests/test_ingame_review_fixes_2026_07_25.py` (29).

**FIXED in-session** — IGR-F1 declare-war-on-a-treaty-partner infinite modal soft-lock (P1);
IGR-F2 every AP-priced marshal-petition arm arrived permanently disabled (P1);
IGR-F3 beat-7 `exposed`/`outmatched`/`penniless` rendered as the `starved` phrase (P2);
IGR-F4 the command terminal swallowed the mouse wheel (P2);
IGR-F5 the separate-peace "your drafted terms carry" promise dropped identity clauses (P2, copy).

**OPEN — owned by row IGR, `docs/INGAME_REVIEW_FIXES_SPEC.md` (v1.0, ✅ GATE BLESSED July 25, 2026 —
build may proceed; gate record = spec §5, authoritative).** IGR-3's question is DECIDED: `create_client`
carries into a separate peace (the Tilsit case), while vassalage/liberation stay settlement-tier and the
bilateral route is disabled with a stated reason instead of dropping them silently.
Slice mapping: IGR-2 → **IGR-A1**; IGR-1 → **IGR-B** (Q1); IGR-4 → **IGR-C** (Q3); IGR-3 →
**IGR-D** (Q2). IGR-X1/X2 were found in passing by the spec's verification fleet and are
standalone.

**The v0.2→v0.3 verification + refutation pass re-measured every row and corrected seven claims.**
Most consequentially: a per-category log filter (a tempting fix for IGR-1) is *wrong*, because the
buried payload shares category "diplomacy" with the noise; the region-vs-nation item is **P3, not
P1** (`move to Austria` does resolve to Asturias, but `movement_executor.py:186-203` already names
the substitution three times — and the real seam is `parser.py:99 _is_nation_demonym`, not the
executor, which never sees the word "Austria"); and **IGR-4 is WITHDRAWN** — see its row.

| ID | Sev | Item | Owner / landing |
|---|---|---|---|
| ~~**IGR-1**~~ | P2 | ~~**Campaign log drowned in AI-AI refusal spam.** Turn 9 carried 25 events; **24** were `D <X> rebuffs <Y> (open borders / non aggression)`. The one dramatic line — `The court of Russia takes up a new design: The Gulf and the Straits` — sat at the bottom of the wall in identical styling.~~ **FIXED July 25, 2026 by IGR-B.** Pure `campaign_log.collapse_refusal_family`, called from `GET /campaign_log` after `filter_campaign_log`, buckets by `(turn, proposal_type)` **within the refusal family only** and renders one aggregate sentence. Measured on the deterministic 20-turn ambient run: **the burst turn's page 26 rows → 5, its refusals 23 → 2, and its `agenda_shift` rises from index 25 to index 4.** Producer untouched — `world.diplomatic_refusals`, `len(event_log)` and AI-3's `_ladder_climbed` all pinned unchanged. **Two corrections to this row's own evidence:** the burst is **turn 3**, not turn 9 (turn 9's 21 refusals are 100% fog-filtered; the spec's raw table was read off a 500-capped `event_log` that had already evicted turn 3's **69** emissions), and a category filter would have been *wrong* — `agenda_shift` shares category "diplomacy" with the noise. | ✅ LANDED — `tests/test_igr_b_campaign_log_readable.py` |
| ~~**IGR-2**~~ | P3 | ~~**Raw internal key in player copy.** The ally-entry proposal renders `Spain cannot join against Prussia: no_participation_path.` verbatim — an R7 display-names violation.~~ **FIXED July 25, 2026 by IGR-A1.** One helper `display_names.ally_entry_block_line` renders the WHOLE sentence for all six emittable keys (prefix-matching the three that carry a dynamic nation suffix), consumed at the review dialogue, the campaign-log one-liner, and the latent `resolve_join_opportunity` site. The raw key stays on the machine fields (`hard_block_reason` is what the log arm re-renders from, incl. out of old saves, and `ai_should_propose_bargain` does exact-literal membership tests on it). **The second surface was DEAD** — `filter_campaign_log` had no branch for `hard_block_surfaced` and no default-include fallthrough, so the event never reached the overlay; it now does. | ✅ LANDED — `tests/test_igr_a_honest_copy.py` |
| ~~**IGR-3**~~ | P2 | **✅ FIXED July 25, 2026 by IGR-D** (landing record `INGAME_REVIEW_FIXES_SPEC.md` §2 IGR-D, commits `32ff834` + `99121ff`): the gate's SPLIT — `create_client` **carries** into the pair-substitute bilateral peace (the Tilsit case, riding `demands` because that is what `_ratify_treaty` converts), while vassalage / liberation / forced-alliance stay settlement-tier and the bilateral route is **disabled with a stated reason** rather than dropped silently. The Proclamation was sighted in-client (`docs/audits/IGR_D_PROCLAMATION_2026_07_25.png`). *Row struck late — the slice landed July 25 and this table was not updated in that session.* ~~Design question — should identity clauses survive the bilateral substitution?~~ `_pair_substitute_seed_terms` translates money + taken territory only; `create_client`, vassalage, liberation and forced_alliance are settlement-tier and dropped by design. Played live: authored *"Erect Duchy of Warsaw from Prussia's lands"*, took the "Make peace with Prussia only" route the game itself offers, and got a bare white peace with the clause gone. The copy is now honest (IGR-F5), but the *only* route the game steers a blocked player toward still silently discards the marquee NA-6 clause. Either carry identity clauses, or have the settlement steer back to the joint route when one is drafted. | Also filed as `DESIGN_REFINEMENT.md` IGR-D3 |
| ~~**IGR-X1**~~ | **P1** | ~~**Save/autosave crashes after an AI marshal finishes recovering.** `enemy_ai.py:2039` does `del marshal._recovery_destination`, permanently removing the attribute; `marshal.py:1485` then reads `self._recovery_destination` directly in `to_dict()` → `AttributeError`.~~ **FIXED July 25, 2026** alongside IGR-A, as its "take before IGR-A" routing directed: the `del` became an assign-`None`, the form `world_state.py:9233-9234` already used at its own clear site. | ✅ LANDED — `tests/test_igr_a_honest_copy.py::TestX1RecoveryDestinationSurvivesSave` |
| ~~**IGR-X2**~~ | P3 | **✅ FIXED July 31, 2026 (IGR-G session):** `get_region_intel` is a PURE READ (missing key → transient UNKNOWN, never stored); the four persistence writers (`calculate_visibility`, the `update_intel_from_*` family) go through the new write-through `_intel_entry`. A `GET /campaign_log` no longer perturbs the intel key set and a save carries no read-created rows (`test_fog_of_war.py::TestX2IntelReadPurity`, 7). ~~**A read path mutates the world.**~~ `WorldState.get_region_intel` (`world_state.py:1937-1943`) lazily *inserts* an UNKNOWN `RegionIntel` on read, so `filter_campaign_log` — pure-looking — mutates `world.intel`; an in-session `GET /campaign_log` perturbs the intel key set. Silently diverged a measurement run. **Found in passing.** | Standalone; matters most to IGR-B's harness |
| ~~**IGR-4**~~ | — | **WITHDRAWN July 25, 2026 by the IGR verification pass — not a defect.** The "designs held in check" rung is the *third* surface of the exposure mechanic; the other two (`_build_france_exposure`, `_build_exposure_line`) render at boot and were verified **PASS** in the review itself. The AI-vs-AI silence already has an owner, landing slice and tracking line in `AI_WAR_DECISION_SPEC.md` §8.2-1 (**AI-V arm (a)**), so GR9 is satisfied. The proposed broadening was additionally measured to render **0 rows while France remains the hegemon** (all 37 rows land only in the collapse case) and would have shown Sweden's authored anti-Napoleon design as held in check *against Britain*. | Closed — no work |

---

## July-18 Playtest Sweep — ALL FIXED July 18, 2026

Two user-reported issues, both real, both with a family behind them. Found by a
34-agent find→adversarially-verify workflow (28 confirmed of 30 raw), fixed, then
put through a 50-agent pre-commit review of the fix itself (15 confirmed of 23,
each double-refuted). Full session record: `docs/STATUS.md` top entry. Tests:
`tests/test_playtest_command_and_ui_2026_07_18.py`, `tests/test_ui_visual_foundation.py`.

**REPORTED (verbatim):** *"when is ay ney give them hell he doesnt do anything it
just give options then i said ney gives charlkes hell and a popup appeared. also
the dplo window is too big for the screen when in settle a war."*

| ID | Severity | Issue | Status |
|----|----------|-------|--------|
| PS18-1 | P1 | **The reported divergence.** The ESP-EV-4 guessed-target guard sat AFTER the range-check block, which returns early with a strategic PURSUE — so an out-of-range guessed target marched off unguarded and opened a bad-odds popup over an enemy the player never named, while a target that grounded nothing got a flat terminal refusal. Same intent, two surfaces, one a dead end. | ✅ FIXED — guard extracted to `guessed_target_refusal` and hoisted above the range/PURSUE block; the reckless-cavalry early return (a second lethal seam) consults the same implementation |
| PS18-2 | P1 | **"give … hell" was unrecognized by every parse layer** — absent from the fast-parser keyword chain, the CR-5 delegation verb allowlist and the golden corpus. It fell to the live LLM to freelance a lethal order. | ✅ FIXED — new single source `backend/ai/attack_vocabulary.py`; 14 golden-corpus rows |
| PS18-3 | P1 | **Colloquial attack idioms all resolved to `unknown`** — crush/smash/destroy/engage/assault/storm/rout/defeat, no quarter, put them to the sword, wipe them out, finish him, and **"give battle"**, which is copy the game itself prints in the CR-5 delegation ASK. | ✅ FIXED |
| PS18-4 | P1 | **The vocabulary had drifted three ways.** `_TARGETING_ANCHORS` listed smash/crush/destroy/engage/assault/storm/rout — verbs the parser had no branch for — so "Ney, attack Mack" then "Ney, crush him" resolved the pronoun perfectly and still shrugged. | ✅ FIXED — the anchor set is now a superset of the routed vocabulary **by construction** |
| PS18-5 | P1 | **Silently WRONG actions at confidence 0.9** — above the LLM-fallback gate, so live mode could never correct them. "cover/screen the retreat" ordered the marshal himself to retreat and spent the AP; "fix bayonets" and "restore order in Vienna" executed masonry repairs. | ✅ FIXED — `_mentions_screening_idiom` / `_mentions_abstract_restore` guards, mirroring the existing `_mentions_pension` idiom |
| PS18-6 | P2 | **Junk words fabricated real provinces.** "hell" auto-corrected into the province **Algiers**, which rode into Berthier's live recovery prompt as a fact the Emperor had stated — so his suggested rephrasing could name a province 1,500km from the marshal. | ✅ FIXED — extraction gated on a resolvable action + idiom filler skip-listed |
| PS18-7 | P2 | **"Ney, deal with Charles" lost the delegation entirely** (generic Berthier shrug) while "deal with ArchdukeCharles" produced the correct CR-5 ASK. Same marshal, verb and enemy; two surfaces. | ✅ FIXED — uniqueness-gated last-name tokens; an ambiguous token ("archduke", owned by two Archdukes) is declined, never guessed |
| PS18-8 | P2 | **"head FOR Vienna" shrugged while "head TO Vienna" marched** — a one-word difference the player cannot see is significant. | ✅ FIXED — destination-bearing + possessive-object forms, anchored so they cannot shadow the SUPPORT family |
| PS18-9 | P3 | **Berthier recited raw internal action ids** ("break_square, change_autonomy"). The live prompt was fixed for this in the F5 pass; the mock template was not. | ✅ FIXED — one filtered vocabulary, two surface forms |
| PS18-10 | P1 | **The settle-a-war window ran off the screen.** `proposal_confirm_popup`'s `FooterLabel` was `fit_content=true` outside any ScrollContainer — the one unbounded contributor. Centre-anchored with `grow_vertical=2`, so overflow split across both edges and carried the action buttons away. | ✅ FIXED — footer bounded, tier-2 affordance rail moved to its own bounded scroll, per-court floor made viewport-derived, panel clamped |
| PS18-11 | P1 | **No ESC and no overlay click-to-close on that popup**, and `main.gd`'s ESC ladder refuses to act while a modal is open — off-screen buttons meant an **unrecoverable soft-lock**. | ✅ FIXED — option-derived escape hatch (`dismiss` is a proposal-family action with no settlement arm; hard-coding it would desync the dialogue) |
| PS18-12 | P1 | **`Utils.clamp_centered_panel` reached only 5 of ~30 surfaces**, and adding the call alone fixes nothing: Godot clamps a Container's size UP to `get_combined_minimum_size()`, so rewriting offsets is inert until the content is bounded. | ✅ FIXED — both halves applied across the sweep; clamp on all 27 centre-anchored surfaces, derived (not hand-listed) in the test |
| PS18-13 | P1 | **`proclamation_popup` authored no offsets at all** — only a 680px `custom_minimum_size` — so it had no design rect to clamp against and a hard width floor that defeated the clamp. A blocking modal whose single [Acknowledge] can leave the screen is unrecoverable. | ✅ FIXED — body scrolled, flag + button pinned outside, offsets authored, minimum released |
| PS18-14 | P2 | **`reward_dialog`'s ES-7 explainer** was unbounded `fit_content`; a marshal with both a shortfall and an active rente pushed "Not now" off the bottom. | ✅ FIXED |
| PS18-15 | P2 | **The diplomacy wizard's own minimum chain (~543px) exceeded its authored 520px box** before any content. | ✅ FIXED — floors lowered, expand flags do the work, both open paths clamp |
| PS18-16 | P3 | **`war_detail_popup`'s button row grew LEFT off the viewport** — an HBox's minimum width is the SUM of its children, one ~130px Target button per coalition member, on a right-anchored panel with `grow_horizontal=0`. | ✅ FIXED — HFlowContainer wraps instead; the clamp deliberately skips this panel (anchor guard), so bounding its content was the only lever |
| PS18-17 | P3 | **`enemy_phase_dialog` / `strategic_report_popup` had no non-mouse dismissal**; both are modal, so a clipped [Continue] cost the player the turn. | ✅ FIXED — floors lowered + `ui_accept`/`ui_cancel` routed through the existing handler |

### Caught by the pre-commit review, before shipping

| ID | Severity | Issue | Status |
|----|----------|-------|--------|
| PS18-R1 | P1 | **A regression the first cut introduced.** The guard rewrite refused any order whose descriptive words grounded nothing — "attack the weakest enemy", "attack the enemy vanguard", "attack the British army" would all have bounced to a popup. The set of words a player may use to describe a foe **is not enumerable**, so a filler denylist is the wrong instrument. | ✅ FIXED — split on WHO chose the target: a PARSER substitution still ASKS (the original ESP-EV-4 case, unchanged); an ENGINE pick **proceeds and DISCLOSES** |
| PS18-R2 | P1 | **`_relax_child_minimums` was a one-way ratchet** — it measured against the already-shrunk minimums it left last time and never wrote back, so one open at Interface Scale 2.0 pinned the per-court table near the floor for the rest of the session. | ✅ FIXED — restore-then-measure (a pure function of viewport and content), then iterate, because one proportional pass under-delivers when a share lands on a text-derived minimum |
| PS18-R3 | P2 | **The clamp cache clobbered a caller that re-derives its own floor** — `proposal_confirm_popup` recomputes the per-court floor from the live viewport every open, and a write-once cache would replace it with a stale value, undoing the scene-level half of the fix. | ✅ FIXED — the pass records its own output (`relaxed_min_y`) so a caller's re-derivation is recognised and adopted |
| PS18-R4 | P2 | **Six modals got the clamp call while keeping an unbounded `fit_content` label** — covered-looking, not covered. A `fit_content` label imposes height through rendered text, a minimum the clamp cannot see. | ✅ FIXED — all bounded; the ten remaining `fit_content` labels are all inside ScrollContainers (verified) |
| PS18-R5 | P2 | **The settlement preamble laid out at height ZERO** once the relax pass ran — it was the only zero-minimum expanding sibling, so the regions that declare minimums exactly filled the budget. | ✅ FIXED — given a real floor, so the pass's 48px floor protects it like every sibling |
| PS18-R6 | P2 | **R7 leak:** raw camelCase keys ("ArchdukeJohn at Tyrol") in the clarification's player-facing labels, on a surface this change makes far more reachable. | ✅ FIXED — labels humanized; `target`/`command` stay raw (machine fields); both forms ride `aliases` so a player who types back what he READ resolves by design, not by luck |
| PS18-R7 | P2 | **Three new tests were vacuous — proved by mutation.** Deleting the relax call site left all three green. | ✅ FIXED — rewritten to pin the WIRING, scoped to the function body; whole set re-mutation-tested, **all 14 mutants caught** |
| PS18-R8 | P3 | **The clamp coverage list was hand-maintained** and named 12 of the 22 touched scripts. | ✅ FIXED — derived from the scenes (27 surfaces), with a paired negative pinning the two deliberately-excluded edge-anchored panels |


---

## EC-W Review Findings — July 17, 2026 (2 routed OPEN)

> From the Econ War-Coupling pre-push find→verify review (memo
> `docs/audits/ECON_WAR_COUPLING_RESEARCH_2026_07_17.md` §6 holds the full
> disposition — findings #1/#2/#3/#4/#6/#9/#10h were FIXED or recorded-with-pins
> in-session; these two carry real design work and are routed with owners).

| ID | Pri | Finding | Fix design | Owner / landing |
|----|-----|---------|-----------|-----------------|
| EWC-F1 | P2 | **A winning-arm settlement offer can stage un-ratifiable:** the AI's purse-priced indemnity (it pays the player) is scored as accepting-side HARSHNESS at ratification (saturating −45 at ≥1,875g), so a marginal court can refuse the AI's own offer after the player accepts — a dead-end click. Pre-existing at the old 2,000 cap; EC-W4's bigger amounts hit it more often. Mitigant: the PROPOSE surface lets the player edit the amount down. | Pre-score the offer package at emission and step the indemnity down until the payer court carries it (`_emit_settlement_offer_for_war` seam); add a winning-direction ratifiability test | Next diplomacy/settlement batch |
| ~~EWC-F2~~ ✅ **FIXED Aug 7, 2026 at the Econ Balance gate** (EB-5.2: `get_estate_income(..., ignore_disruption=True)` for `compute_rente_face` ONLY — satisfaction and every display keep the disruption rule; `test_econ_balance_eb.py::TestRenteFaceIgnoresTransientDisruption`) | P3 | **Rente face can size against disruption-zeroed estate income:** `grant_pension` auto-sizes face = expectation − estate income; a one-turn hostile presence on the estate at grant time (EC-W1) locks an oversized pension, double-counting after liberation. AI auto-grant rungs can trigger it. Pre-existing for captured estates; EC-W1 makes it transient-triggerable. | `ignore_disruption` flag on `get_estate_income` for FACE COMPUTATION only (satisfaction display keeps the disruption rule) | ✅ landed |

---


## EA-SCOPE findings — filed August 3, 2026 (the refund-test panel)

> Companion rows to **PARSE-NEG** above. Same panel, same session; each
> verified first-hand by the orchestrator before filing.

| id | sev | defect | disposition |
|---|---|---|---|
| **EAS-1** | **P2** | **Making mock the shipped default ARMS THE CHEAT CONSOLE.** `meta_executor.py:2037-2043` computes `live_client_armed = key_source != "none"` and refuses cheats only when armed, so a **keyless build leaves the cheat surface OPEN** — and `parser.py` routes any typed `cheat ` prefix. This is not a code bug: the assumption "mock means developer" was true when mock was a test mode. **Position 4's own decision to make mock the shipped default is what invalidates it.** | Re-gate on **explicit debug alone**, in the same slice that makes mock the default (ROADMAP position 4, ~1 hour). Do not fix earlier — today's behaviour is correct for today's build. |
| **EAS-2** | P3 | **The campaign log has no importance tier.** `campaign_log.gd` renders every row at the same size, coloured by *category*, never by weight. IGR-B fixed the VOLUME half of the July-25 complaint (26 rows → 5); the other half — *"the one dramatic line sat at the bottom in identical styling"* — is still literally true. | Files against the **enemy-phase composition** work, NOT against the gazette (cut) and NOT into the pre-EA queue. If ROADMAP position 1's re-measure sends a composition slice to position 3, this rides it. |
| ~~**EAS-3**~~ | ✅ **FIXED Aug 3, 2026** | **`main.gd:663` shipped a player-facing command that fails.** The unreachable-backend error told the player *"Start the Python server: python backend/main.py"* — wrong since the real-map cutover, which requires the module form (`CLAUDE.md:38`: *"Run the backend as `-m backend.main`"*). It is the ONE message a stuck player reads, and it sent them to a command that errors. | Fixed in place → `python -m backend.main`. **`docs/ADDING_CONTENT.md:1329` carries the same stale command** and is fixed with it. |
| **EAS-4** | P3 | **`test_ai_intent_assurance.py::TestArmAAmbientDoD::test_pair_peace_is_exhaustion_driven` is intermittently flaky.** Failed three times in one session, then would not reproduce across eight consecutive targeted re-runs *including under deliberate mutation*. Passes in the full suite. An `LLM_MODE`-inheritance hypothesis was raised and **DISPROVED** — `ai_v_sweep.run_one` already forces `LLM_MODE=mock` before importing the backend, so the proposed pin was a no-op and was **reverted rather than shipped as a fix for something it does not fix**. | Real, pre-existing at HEAD, **unexplained**. Belongs to whoever next touches the AI-V sweep. Full account: `NAVAL_SPEC.md` §15.15. |

**Checked and dismissed as non-gaps** (verified, not assumed): save/load UI
exists (`load_dialog.gd` + pause menu) · save migration is sane
(`FORMAT_VERSION=3`, hard-reject with a clear message) · turn latency 23.1ms
under a 15× tripwire, so no frozen-UI problem · main menu is ROADMAP position
4(f) · tutorial is 12 · SmartScreen/code-signing is 13 · difficulty and
achievements are explicitly cut with owner rows.


## Sweep-5 Findings — July 16, 2026 (P0 FIXED; **S5-1/2/3/5 FIXED in Batch Q Chunk 1, July 16**; only **S5-4** remains, deferred to the Pre-EA Dialogue Robustness row)

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

**Current routed-open set (August 3, 2026)** — the Creative-Audit rows below are ALL FIXED and are kept as a record: **IGR-X9** (razing sheds the EC-U2 bill — homed at ROADMAP row **EC-P3**) · **EWC-F1** / **EWC-F2** · **UI-2d-1** · **S5-4** (Pre-EA Dialogue Robustness) · **NV-P1's live wheel check** (§NV-P1 — evidence, not code). Historical note: BUG-CA-7 (dialogue-stack misroute) was the priority item. Overall routing lives in `docs/ROADMAP.md` §Current Phase Queue.

---

## Creative-Audit Findings (July 10, 2026) — ✅ ALL TEN FIXED (Wave 6, July 10, 2026)

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
| XR-5 | P4 | ✅ **FIXED Aug 8, 2026 (ROADMAP position 9, its named owner slot)** — bank growth APPEND-ONLY in `enemy_voice.py` (index 0 is pinned by the W6-6 tests and the serialized `battle_counts` rotation): every named-marshal bank ≥2 lines, all four of Mack's ≥3 (the measured offender), every personality bank 3; a three-battle grind now yields three distinct Mack lines (`test_marshal_voice_tier1.py::TestXr5QuipVariety`). The per-region battle count IS the cooldown analog — bank SIZE was the missing lever (the CA8-D4 lesson). | Mack's post-battle quip pool is 2 lines; across the 7-battle Ulm grind "The position was sound. It is always sound." repeated verbatim 3×. Delicious once, mechanical by the third — 8.5's marshal-voice tiers should give recurring-battle quips a cooldown/variety bank like W6-10 gave diplomats. |

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

### ~~NV-P1: the Strategic Ledger panel ignores the mouse wheel~~ ✅ FIXED August 2, 2026 (NV-6) — ⚠ **live wheel check still OPEN**

**Cause, confirmed:** the ledger's content area is a `RichTextLabel`
inside a `ScrollContainer`, and a `RichTextLabel` defaults to
`MOUSE_FILTER_STOP` — it consumed the wheel event before its own parent
ever saw it. Dragging the thumb worked because the drag lands on the
scrollbar, not on the label. Fixed in `strategic_ledger.gd::_ready()` with
`content_area.mouse_filter = Control.MOUSE_FILTER_PASS`: PASS still
delivers `_gui_input`, so `meta_clicked` and every chip on the screen keep
working, and then lets the parent scroll. Guessed correctly in the row
below ("likely one `mouse_filter` line") — recorded because the guess was
worth something. Landed with the NV-6 Admiralty chips, which is what made
it bite hardest.

<details><summary>Original report</summary>

**Problem statement.** In the live client the Strategic Ledger's content
area does not scroll on mouse wheel. During the naval visual pass the
ECONOMY tab's content (income-by-region, then THE ADMIRALTY block at the
bottom) could only be reached by DRAGGING the scrollbar thumb — 60 wheel
clicks with the cursor squarely inside the content area moved nothing,
while a thumb drag scrolled instantly.

**Why it matters.** THE ADMIRALTY block renders at the END of the economy
tab, so on a France with many provinces the whole naval surface sits below
a long income list that a player will instinctively try to wheel past.
Same family as the IGR fix "the command terminal swallowed the mouse
wheel" — this is the ledger's turn.

**Scope.** PRE-EXISTING, not caused by the naval slices (the naval work
appended a render arm to `_render_economy`; it added no scroll handling
and changed none). Reproduced on `strategic_ledger.gd`'s panel.

**Owner / landing.** The next UI pass (or a standalone fix — it is likely
one `mouse_filter` / `ScrollContainer` focus line). **Completion
definition:** wheel scrolling works in every ledger sub-tab.
**Behavior test:** a `.gd` source pin that the scroll container accepts
wheel input, plus a live wheel check in the next in-client review.
</details>

⚠ **Still open:** the live wheel check in the client — the fix is a
one-line filter change with no headless test that can prove a wheel event
reaches a `ScrollContainer`. Verify on the next play session.

### NV-P2 (recorded, working-as-designed): a blockading Britain stops tinting a crossing it owns outright

Observed in the same pass: once Britain captured Normandy, the
London–Normandy sea link's map tint went from crimson (SHUT) to the
neutral/uncovered dash. That is `naval._fleet_covers_link` behaving
exactly as `NAVAL_SPEC.md` §3.3/§4.1 specify — a **blockade** posture
covers links touching an at-war ENEMY's provinces, and with Britain
holding BOTH ends neither endpoint qualifies (a **guard** posture, which
covers links touching its own provinces, would still cover it). It reads
correctly in fiction too: an internal ferry between two British-held
shores is not a contested strait. **Recorded so it is never re-filed as a
bug**; re-open only if a played session shows a player exploiting an
own-both-ends crossing.

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
