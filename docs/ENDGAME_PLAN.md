# The Endgame Program — the fixes, then "The Congress of Paris" (row EP)

> **Status: RULED September 23, 2026 (evening) — BUILD-READY. This document is the routing authority for row EP; `docs/STATUS.md` ▶ NEXT UP points here.** **Progress: ~~F1~~ ✅ LANDED September 23, 2026 (landing record in §1 F1) → ▶ NEXT = F2 "The display-name pass".** Every decision below was taken by Claude under the user's delegated grant (*"create a plan to fix all of these, make all decisions, and for the ending make the decision on how to end — but it should be a challenge to force a new status quo, and you should have to hold the win state for X turns, with a mechanic that makes it fun"*). Each decision carries its argument and, where it matters, its re-open condition. The user has not separately confirmed them.
>
> **Order, by the user's direction:** *start with the fixes, end with the end state.* Slices **F1 → F6** (the live review's 21 defect rows and 5 design rows, `BUG_FIXES.md` §Live Review, `DESIGN_REFINEMENT.md` §Live Review), then **GE-1 → GE-2 → GE-3 → GE-V** (the ending). **The release build (ROADMAP 10) follows GE-V**, then Updates 1–5.
>
> **What it supersedes.** `GAME_END_SPEC.md` §7 was a PROPOSAL with six questions; this document RULES them (§2 below) and adds the mechanic the user asked for. `GAME_END_SPEC.md` §1 (the measured facts) and §2 R1, R3–R9 stand as written; R2 (the Verdict at 44) stands as the epilogue card (§4.4). Where this document and §7 differ, this document governs. `GAME_END_SPEC.md` §8 records the same in one paragraph so the two cannot drift.
>
> **Evidence.** `docs/audits/PLAYTEST_LIVE_REVIEW_2026_09_23.md` (the played campaign, the Steam review, the three end-state probes) and the code research summarized in `GAME_END_SPEC.md` §7.0.

---

## §0 The decisions in one page

| # | Question | Ruling |
|---|---|---|
| **D1** | Order | Fixes first (F1–F6, ~3.25 sessions), then the ending (GE-1..GE-3 + GE-V, ~4 sessions), then the release build. Player-facing first-contact fixes (F1) are the very first slice because the release build ships them. |
| **D2** | How the game is won | **The Congress of Paris (§2).** With **50 provinces held by TITLE** the Emperor may *summon the Congress*; every great power then answers — recognize or refuse — and the Congress **sits for 8 turns** during which refusers are driven to war, the paymaster pays them, coalitions form more easily, the marshals and the satellites present their bills, and the player must hold every titled province, Paris and the Emperor's freedom. It ends in **THE IMPERIAL PEACE** only if every great power recognizes, is shut out, or is gone. A failed Congress dissolves with a cost and a cooldown; the player may summon again. |
| **D3** | "Hold X for X" | X = **50 titled provinces** (39.7% of 126; the boot bloc is 35, so fifteen must be won AND settled) held for X = **8 consecutive turns** of the Congress. Both numbers live in the scenario's `campaign_end` block. |
| **D4** | The mechanic that makes it fun | The **summons is the player's choice** (a fuse they light when they judge themselves ready); the **table is public** (four rows, each court's stance, its reason and its PRICE, re-answered every turn); **refusal has teeth** (a refuser's intent climbs +15 a turn toward war; Britain funds every refuser; the coalition threshold drops); **every refuser can be flipped four ways** (beat them, buy their design, pay their price, court them) and the table says which; the marshals and the satellites present their bills at the summons; the Moniteur runs a Congress column; the clock is on every surface. Failure is legible and recoverable. |
| **D5** | Britain | Britain answers like the others but cannot be *beaten* on land. It is **shut out** (not blocking) when the Continental System closes ≥ 60% of the Continent's ports for the whole window and no British corps stands on the Continent. The Continental System finally has its purpose. |
| **D6** | Stabilization of the new status quo | **Title** (§2.2): a province counts only when it is homeland, ceded by a treaty the loser signed, or held 12 quiet turns after conquest. ONE new serialized record `province_title`. A signed cession *reconciles* that province's Revanche while the treaty holds. |
| **D7** | After the victory | Mark and continue, with a **Retire to the Tuileries** button. The Verdict at 44 still grades. |
| **D8** | Defeat | R1's two warned clocks stand (≤1 province or no free corps and no affordable commission, 5 turns; the Emperor captive 10 turns; Paris alone never). **Plus** "The Humbled Peace": ratifying a settlement that cedes Paris, half the homeland, or makes France a vassal stamps a **marked, non-terminal** defeat. A dissolved Congress is **not** a defeat. No third clock. |
| **D9** | Global elimination | E1–E6 of `GAME_END_SPEC.md` §7.5 RULED as written: the Universal Monarchy fires the Imperial Peace at once when no great power remains; the alarm stops climbing with nobody left to alarm; the dead stay dead (no enemy-phase rows, no fleets, no ports, no trade dominance, decks retired); knocking out a great power is a beat and a verdict input; great powers stay eliminable on the battlefield; the AI roster needs no change. |
| **D10** | Screens | ONE scene `campaign_end.tscn` with four registers — **The Imperial Peace** (gold), **The Fall of the Empire** (crimson, terminal: Load / Main Menu), **The Humbled Peace** (crimson-grey, continue), **The Verdict of History** (parchment, continue) — plus the Congress table as a tab of the Diplomatic Ledger and a one-line clock on the war room, the ledger and the end-turn banner. |
| **D11** | The reward curve (LV-D1) | Expectation rises only on a **decisive victory as lead** or a **glory-rank rise**, at most once per marshal per 4 turns, never before turn 6; the collective petition needs turn ≥ 12, three eroding marshals and ≥ 300g unmet; the dispatch's UNMET block appears only within 2 turns of erosion. |
| **D12** | Bavaria's walk-ins (LV-D2, FA-D13 re-opened) | One undefended capture per corps per turn (its `movement_range`), and a "literal" AI marshal takes the "cautious" strength check before walking into a province adjacent to a stronger enemy. `BASELINE_SERIES` re-recorded once, attributed. |
| **D13** | The strategic-orders recap modal (LV-D3) | Retired as a modal. Its lines join the morning dispatch's MARSHAL STATUS; a modal is raised only for an order that needs an answer (the interrupts already have their own). |
| **D14** | The legitimacy sentence (LV-14, LV-D4) | The whole-war blocker names the unbeaten courts and their scores and offers the separate peace as a chip on the table. The predicate is unchanged. |
| **D15** | Series and harness policy | F4, F5 and GE-3 move AI behaviour and each re-records `BASELINE_SERIES` **once, with a flip-experiment attribution**; every other slice must leave it and M1–M7 byte-identical. |

---

## §1 The fixes — slices F1 … F6

Conventions for every slice: the four-file rule (`STATUS` ▶ NEXT UP struck and advanced, this document's slice table marked, `BUG_FIXES`/`DESIGN_REFINEMENT` rows disposed, `CLAUDE.md` LIVE STATE), a mutation sweep with 0 INERT at close, the XR-1 parse harness + boot smoke on any `.gd` change, and the series policy of D15. Effort is in sessions.

### F1 — "The first ten minutes" (0.5) — LV-1, LV-12, LV-13, LV-7, LV-8 — ✅ LANDED September 23, 2026 (landing record below the table)

| Row | Decision | Seam |
|---|---|---|
| **LV-1** the empty first turn | (a) The boot help moves into `_print_boot_help()` and is printed **after** every world swap that starts or loads a campaign (`_apply_world_swap_response` when `response.new_game` or a load is set), so Begin, Continue and Load all show it. (b) **A turn-1 briefing exists:** `/new_game` calls `build_morning_dispatch(world, boot=True)` — a new flag that runs the *pure* halves (situation, marshal status, the war block, the "what to do today" doors) and **skips every consuming arm** (the sabotage roll, the seen-lists, the once-per-turn beats), so the campaign seed and `BASELINE_SERIES` cannot move. It is stored as `last_morning_dispatch`, so R finds it and the "No dispatch available yet" copy becomes unreachable on a live world (delete it). (c) On Continue/Load the client re-renders the loaded turn's `last_morning_dispatch` in the terminal under "Loaded: …". | `main.gd` (`:799-810`, `:5270-5272`, `:5350`), `dispatch.py:2700`, `main.py:5005-5048`, `dispatch_view.gd:59-61` |
| **LV-12** the swallowed battle report | Reproduce at the command-result seam with a pending `incoming_proposal` AND `incoming_settlement_offer`. Rule: **a command's own result renders before any dialog the same response raises**. The `_post_hud_response_routes` entries that return before `_display_result` must call it first when the response carries `battle_report` / `message` from the player's own order (the BD §14.1 stash-and-raise discipline, applied to the envoy family). Pin: the terminal text contains Berthier's report AND the dialog is raised. | `main.gd` `_on_command_result` / `_post_hud_response_routes` |
| **LV-13** nine fog lines | The no-visible-action branch emits the same collapsed sentence the visible-action branch does: "Nine courts stirred, but their formations remain beyond our sight." Pin: a turn with zero visible actions renders exactly one fog line. | `turn_manager.py` enemy-phase summary builder (the `beyond our sight` producer) |
| **LV-7** "Enemy nations hold 98 regions" | Count only controllers at war with the player (`get_nations_at_war_with`, cached `get_nation_regions`); the line reads "The courts at war hold N regions." Pin on the boot board: 28, not 98. | `dispatch.py:2869-2873` |
| **LV-8** the 28-name war purpose | For a defense objective that covers the homeland, ONE sentence: "the homeland — 28 of 28 provinces held" (`_homeland_held_fraction` + `format_progress`); any other list capped at 8 names + "and N more" (`nation_names.py:91-95`). Sent as a field to the war panel and the war-detail popup; the envoy dialog's War Summary reads the same field. | `dispatch.py:4446-4463`, `war_status_panel.gd:318`, `war_detail_popup.gd:409`, the envoy payload |

Done when: a fresh Begin shows the boot help AND a turn-1 briefing in the terminal and on R; Continue shows the loaded turn's briefing; the LV-12 reproduction renders the report; boot dispatch says 28; the purpose line is one sentence on all four surfaces; `BASELINE_SERIES` + M1–M7 byte-identical.

**✅ Landing record (September 23, 2026 — the commit that carries this record).** Every done-when item is met and driven on the real `main.tscn` (`tools/ep_f1_first_ten_minutes_harness.gd`, fed payloads from the real endpoints; `tests/test_ep_f1_the_first_ten_minutes.py`, 48 tests); rules `SYSTEMS_REFERENCE.md` §56; rows disposed in `BUG_FIXES.md` §Live Review.

- **LV-1, as ruled, plus one addition.** `build_morning_dispatch(world, boot=True)` skips every consuming arm: the expectation latch, the headline-lead memory (`_select_headline(record=False)`), both warnings (they write the rail), Talleyrand's report (its cooldowns), the Session-6 sabotage roll, and the diplomatic-event queue (the next real dispatch reads and clears it). Its only write is `last_morning_dispatch`. **Measured:** the world after `/new_game` differs from a fresh `from_scenario` world ONLY in that field; the next real dispatch is identical with or without it; no module dice are drawn.
  - **Where it is built.** `main.py` `_ensure_first_morning` runs in `_reset_world_state`, so the process boot, `/new_game` and the School are all covered — not only `/new_game`, as the ruling said. It also runs in `/load` for a save written before its first end turn. A stored briefing is never rebuilt.
  - **Where it is read.** `/new_game` and `/load` carry it as `morning_dispatch` through `_readable_dispatch`, which is now also the one reader behind `GET /dispatch`.
  - **The addition, a TODAY section.** "The 'what to do today' doors" became the counsel's own orders (`ai/counsel.what_can_i_do`, at most 4), each sent as printed to `/command` and taken (pinned), plus first contact's `THREE_DOORS` + `CABINET_DOOR`, quoted rather than re-typed.
  - **The client.** `_print_boot_help()` is the one home of the help. The world swap prints the briefing, then the help. The Dispatch screen's empty arm no longer claims "appears at the start of each turn"; it is unreachable on a live world.
- **LV-12, as ruled.** Reproduced for real first: Austria's envoy was delivered, then `Ney, attack Mack`. The response carried both `battle_report` and `incoming_proposal`, and the envoy route returned before `_display_result`.
  - **The fix.** Six `_post_hud_response_routes` entries are marked `result_first`: the paradox, the petition, the proposal, the settlement offer, the sabotage and the rebellion. These are the modals a command does not ask for. `_on_command_result` passes `_render_own_result`, so the order's result prints first.
  - **Out of scope, filed.** The capture route is one the command DID ask for, and it has its own form of the defect. Filed as **LV-22**, owned by F3.
- **LV-13, one refinement.** The fog line is one sentence through PT-E4's `_join_courts` ("Britain, Russia, Prussia and 6 other courts stirred, …"). A single court keeps its own sentence, which names it best.
- **LV-7, as ruled.** The count now reads 28. It stays one region pass, with the at-war set read once; the per-nation cache would read stale on a fixture that re-colours a province without invalidating. Europe-scoped (N1). A new `enemy_regions_are_at_war` flag tells the client which sentence to print.
- **LV-8, as ruled; FIVE client surfaces, not four.** The player's own peace-confirm popup prints the same War Summary. ONE source: `war_status.objective_target_summary`. "The homeland is lost" at none held keeps PR-X1's rule by naming no province. Europe-scoped: the field is absent off the board, so the legacy payloads are byte-identical.
- **Levers:** `dispatch.THE_FIRST_MORNING_HAS_A_BRIEFING`, `dispatch.ONLY_THE_COURTS_AT_WAR_ARE_COUNTED`, `war_status.THE_PURPOSE_IS_ONE_SENTENCE`, `main.THE_FOG_IS_ONE_SENTENCE`.
- **Pins consciously flipped or re-scoped (9):**
  - `test_popup_routing_registry.py::test_on_command_result_uses_route_dispatcher` — the dispatcher call now carries the renderer.
  - `test_iq2_collapse_dispatch.py::TestWarObjectives::test_one_of_many_is_not_held` and `test_iq2_collapse_integration.py::TestTheWarPurposeListsOnlyWhatIsHeld` ×4 — these now run on the list shape that the LV-8 lever-down arm restores. Their levers still govern it. The sentence's PR-X1 guarantee is pinned beside them.
  - `test_pt_f_jealousy_channel.py::TestTheAutonomousAttackIsShown::test_it_is_called_before_the_enemy_phase` — re-scoped, assertion unchanged: it read the FIRST `_display_jealousy_attacks(response)` in the whole file, and `_render_own_result` now calls it earlier; it reads `_on_command_result`'s own call.
  - `test_ux23b_the_desk_is_quiet.py::TestTheDispatchReReadIsNotStale` ×2 — the copy-and-overlay moved verbatim into `_readable_dispatch`; the pins read it there, pin that `GET /dispatch` goes through it, and the never-rebuild guard now covers the shared reader too.
  - `test_wo_slice15_capture_question_holds.py::test_the_world_swap_handler_raises_it_client_side` — its body-length sanity ceiling 4000 → 6000 (the handler grew to 4,101 chars by the briefing and help it now prints).
- **Series:** `BASELINE_SERIES` + M1–M7 byte-identical — neither harness boots through `/new_game`, and every non-boot dispatch arm is unchanged. **Gates:** ruff clean, full suite green, Godot parse harness EXIT=0 (the harness registered in `TOOL_SCRIPTS`), boot smoke 0 `SCRIPT ERROR`, mutation sweep `tools/_sweep_ep_f1.json` **38/38 killed, 0 INERT, 0 BROKEN** (nine of them `.gd` mutations killed by the driven pins).

### F2 — "The display-name pass" (0.75) — LV-2, LV-3, LV-4, LV-6, LV-9, LV-10, LV-11, LV-18, LV-19 (NPC-12's first slice)

| Row | Decision | Seam |
|---|---|---|
| **LV-2** raw marshal keys | `humanize_entity_name` (+ `formed_display_name` for the controller) at the three scout sites and the covering/shield lines; the client's diorama nameplate and war-table piece label pass names through a new `Utils.display_marshal_name` (the marshal-name sibling of `humanize_nation_keys_in_text`). NPC-12's census gains an AST pin over `movement_executor.py` and the covering builder: no `{m.name}`/`{enemy_marshal.name}` reaches a player string un-humanised. | `movement_executor.py:1085/1087/1150`, `combat_executor.py:6183-6192`, `battle_diorama.gd`, `war_table_piece.gd` |
| **LV-3** raw states and tags | `STATE_DISPLAY` for every diplomatic state in prose (`_ratify_treaty` `:12051`, the downgrade refusal `:11149`); courts through `with_definite_article(formed_display_name(world, n))`; the popup payload gains `from_nation_display` and `choice_display`, which `main.gd:5942/5946` render. The client's tag-skipping list (`utils.gd:265-274`) is left alone — the backend owns the article. | `world_state.py`, `diplomatic_executor.py:7001/5881`, `mailbox_payloads.py:399-415`, `main.gd` |
| **LV-4** the strategic dialog's copy | Every report row carries `command_display = get_strategic_display(cmd)` from the single return (`strategic.py:1294`); `turns_remaining` is sent as an int and rendered with `str(int(...))`; `STATUS_ICONS` gains `active` and `consumed`; `turn(s)` → the plural helper; `[HINT]` → a sentence ("Hungary lies undefended — an attack takes it."). The modal itself is retired in F3 (D13); this slice fixes the copy the dispatch will inherit. | `strategic.py:1236-1262`, `strategic_report_popup.gd:19-90` |
| **LV-6** inverted envoy hints | For an INCOMING offer both hints are blanked (the client-petition arm's pattern, `mailbox_payloads.py:431-432`); the counter-offer path likewise. The player's OWN previews keep them. Pin: an incoming payload carries no `acceptance_hints`. | `mailbox_payloads.py:317-377`, `diplomatic_executor.py:7355-7362` |
| **LV-9** `(s)` everywhere | `display_names.plural(n, noun)` on the backend (absorbing `emergent_designs._turns` and `diplomatic_dialogue._plural`) and `Utils.plural(n, noun)` in the client, applied at all fourteen sites. A census pin forbids the `(s)` literal in player strings. | the fourteen sites listed on the row |
| **LV-10** whom it was taken from | The capture and field-battle branches print " (was X)" like the movement branch. | `enemy_phase_dialog.gd:336-347`, `:510-524` |
| **LV-11** the advance attrition | `advance_losses` recorded at `combat_executor.py:7802`; the report's strength line and the diorama's lead card show "22,181 → 21,863 after the advance" when it is non-zero. The lock point stays. | `combat_executor.py:7798-7812`, `battle_report.py`, `battle_diorama.py:185-188` |
| **LV-18** the bundled defence term | The defence line prints each component `get_defense_modifier` already computes with its own label ("Defensive stance +15%, Personality (cautious) +5%, Outnumbered +11%"). Pin: the labelled sum equals the applied modifier. | `battle_report.py`, `marshal.py` |
| **LV-19** ASCII arrows | One arrow (`→`) in the materiel and route lines. | `combat_executor.py`, `strategic.py` |

Done when: NPC-12's census lists these sites as CLOSED; every string above is pinned by a driven `/command` test rather than a source grep; zero `BASELINE_SERIES` movement.

### F3 — "The client layout pass" (0.75) — LV-5, LV-14(b), LV-15, LV-16, LV-20, LV-22, LV-D3

| Row | Decision | Seam |
|---|---|---|
| **LV-5** the clipped petition | The body label sizes to `get_content_height()` and is marked `relax_last`, so `clamp_centered_panel` shrinks the options list before the body; a disabled arm's reason renders **above the fold** as one line under the header ("The command arm is closed: no enemy within his reach") — IQ10-X2's pattern — and the duplicate `detail == reason` line is dropped. This modal joins the IQ-10 capture set at both Interface Scales. | `marshal_petition_dialog.tscn/.gd`, `utils.gd:595-661`, `tools/iq10_capture_payloads.py` |
| **LV-14(b)** the settlement overlap | The per-court Press/Ease/Drop rows become their own scroll block under the "Allies and Standing" heading; the third court is never clipped. Shot through the IGR-G harness with the turn-6 payload (Vienna held, three courts). | `settlement_review` panel, `tools/settlement_popup_screenshot.gd` |
| **LV-15** the wizard's chips | Chip labels autowrap; the gate reason moves to a second, smaller line; the horizontal scrollbar goes. Step 2 joins the IQ-10 capture set. | `diplomacy_wizard.gd` |
| **LV-16** the log's letters | The glyph font is bound on `campaign_log.gd`'s row prefix (the letters are the fallback); pinned by the IQ-10 frame. | `campaign_log.gd` |
| **LV-20** the wizard's gap + one chip | The prompt sits directly above the list (the spacer was the old nation-count block); "Sponsor Their Design" for a court whose design is against France reads "Fund the design they already pursue against us" and is hidden while at war with that court. | `diplomacy_wizard.gd` |
| **LV-22** the capture swallows the report (filed by F1) | The rule F1 applied to the envoy family, applied to the one route a command DOES ask for that also discards a result: `_show_capture_choice_dialog` prints `response.message` only, so a battle that ends in a capture loses Berthier's report; the muster road prints the message twice. The capture route renders the order's result first (`_render_own_result`) and its renderer skips the message a rendered result already printed; the muster road's second print goes. Driven like F1's LV-12 pin, on an attack that captures. | `main.gd` `_route_capture_choice_response` / `_show_capture_choice_dialog` / `_on_interrupt_response` |
| **LV-D3** the recap modal | `strategic_report_popup` is no longer raised at turn start. Its rows render inside the morning dispatch's MARSHAL STATUS ("Soult — marching to Vienna, arrives next turn"), and the popup class is kept only for reports that carry a question (an interrupt) — those already route through their own dialogs. The end-turn response drops `strategic_report` from the popup whitelist and adds it to the dispatch payload. | `main.gd` popup whitelist, `dispatch.py`, `strategic.py:1294` |

Done when: the four IQ-10 frames at 1.0 and 2.0 show no clipped text; a turn with three standing orders and no interrupt raises no modal at turn start; parse harness EXIT=0, boot 0 `SCRIPT ERROR`.

### F4 — "The fuse is longer" (0.5) — LV-21 / LV-D1 (the reward curve; UX23-D1..D4 closed by this ruling)

- **Rises.** `expectation` rises only on (a) a decisive victory with the marshal as LEAD, or (b) a rise in his glory RANK; never on a reinforcement, never on a stalemate. At most one rise per marshal per **4 turns** (`EXPECTATION_RISE_COOLDOWN = 4`, serialized `last_expectation_rise_turn` — one new marshal field, `to_dict`/`from_dict`, `SAVE_FORMAT_REFERENCE`). No rise before turn **6**.
- **The collective petition** (ESP-1 Fontainebleau) needs turn ≥ **12**, ≥ 3 eroding marshals and ≥ **300g** unmet (all in-band constants).
- **The dispatch's UNMET MARSHALS block** appears only for a marshal within **2 turns** of erosion; the per-victory "Ney's victories raise his expectation" line stays (it is the tell).
- **GR5:** the AI grant rung reads the same predicates, so `BASELINE_SERIES` moves — re-recorded once with a four-arm attribution (rises / cooldown / petition gate / dispatch gate).
- Measured before landing on the historical seed, played as in the live review (Ulm turn 1, Vienna turn 6): the first expectation rise on or after turn 6, no collective petition before turn 12. Re-open: if a 40-turn commanded campaign never sees a collective petition, lower the gate to turn 9.

### F5 — "Bohemia is not empty" (0.5) — LV-D2 (FA-D13 re-opened) + LV-14(a) / LV-D4

- **Walk-ins.** `_find_undefended_capture` honours a per-corps per-turn cap of `movement_range` captures (one for infantry); the AI's action loop cannot hand a second walk-in to a corps that already took one this turn. A "literal" marshal runs the "cautious" strength check (`enemy_ai.py:5502-5513`) before entering a province adjacent to an enemy corps stronger than his own. **Measured on three seeds:** Bavaria takes at most ONE Austrian province on turn 1, and the Austrian REVANCHE against Bavaria fires on turn 1 on zero of three. `BASELINE_SERIES` re-recorded once, attributed (the cap alone; the strength check alone; both).
- **The legitimacy sentence.** The whole-war blocker's copy names the courts: "London and St Petersburg are unbeaten — a whole-war peace needs their consent (Austria 32/50, Britain 24/50, Russia 24/50). Press Austria alone: the separate peace." The review panel gains a **"Separate peace with <court>"** chip for any covered court at ≥ 50, routed to the existing pair-substitute tier. The predicate is unchanged; the counsel rung says the same thing. Pin: the turn-6 payload renders the named sentence and the chip.

### F6 — "Settled once, reopened" (0.25) — LV-17

- Reproduce turn 5 of the historical seed (two attacks on Archduke John; Davout the reinforcer). If the confrontation was generated by the end-of-turn pass from a `jealous_of` the battle had already resolved, the pass re-reads the relationship at **delivery** (the IGR-2 re-price pattern) and drops a petition whose grievance no longer stands. If it is the ladder's next rung, the petition's first line says so: "Settled once at Vienna — and reopened by …". Either way the two lines cannot contradict on consecutive turns; a pin drives the reproduction.

---

## §2 The ending — "THE CONGRESS OF PARIS" (RULED)

### §2.1 The shape

Napoleon's problem was never conquest; it was that Europe would not *recognize* the conquest. Amiens lasted a year, Pressburg was undone at Wagram, Tilsit was undone at Moscow. The ending is that problem made playable: **the Emperor must force a new status quo and then make Europe sign it, and hold everything while Europe decides.**

1. **Title.** Conquests count only when settled (§2.2).
2. **The summons.** With 50 titled provinces in the bloc the player may **summon the Congress of Paris** — a deliberate act, priced, and reversible only by failure.
3. **The table.** Every great power answers — *recognizes* or *refuses* — and keeps answering every turn, with its reason and its price on a public table.
4. **The sitting.** The Congress sits for **8 turns**. Refusal has teeth; recognition has a price; the marshals and the satellites present their bills; every titled province, Paris and the Emperor's freedom must be held.
5. **The Imperial Peace.** If, on the eighth turn, every great power recognizes, is shut out or is gone, and the hold never broke — the ending. Otherwise the Congress dissolves, at a cost, and can be summoned again later.

### §2.2 Title — the stabilization of the new status quo (RULED as `GAME_END_SPEC.md` §7.2, with the rider)

A province in the French bloc is **titled** when it is: **homeland** (in `nation_starting_regions` for France or for a satellite that is loyal ≥ 40); **ceded by treaty** (a `territory_cede` / settlement clause the loser signed — title is immediate); **held in quiet possession** (captured by force and held `title_turns` = **12** consecutive turns with no hostile army entering it and the loser not at war with France); or **a client's soil** (a court France created). Everything else is *held*, shown, and not counted.

**The record:** ONE serialized field, `province_title: {region: {"kind": "treaty"|"conquest", "since": turn, "from": nation}}`, written at `capture_region` (conquest) and the three ratify seams (treaty); a hostile army entering a `conquest` province resets `since`. GR5: written for every nation, read only for the player's ending. `Region` is not changed.

**Reconciliation (RULED in):** a court that signs a cession has that province's Revanche weight read 0 while the treaty holds; breaking the treaty re-arms it. Zero new fields.

### §2.3 The summons

- **Verb:** `summon the congress` (typed) and a **"The Congress of Paris"** row at the top of the Diplomacy wizard's step 1 with honest-availability gate terms: `50 titled provinces (43 of 50)` · `Paris held` · `the Emperor free` · `no satellite in rebellion` · `no Congress dissolved within 10 turns`. Cost **2 DP + 1 admin action**. Not a standing order; it cannot be undone.
- **What happens:** `world.congress = {"summoned_turn": t, "ends_turn": t+8, "answers": {...}, "held": true}` — ONE serialized field. A dispatch beat and a Moniteur special ("THE EMPEROR SUMMONS THE POWERS TO PARIS"). The marshals' collective petition fires **at the summons** if any marshal is eroding ("the peace dividend": estates before the peace); every satellite with a pending ask presents it.
- **The great powers** are `_CANONICAL_MAJORS` minus France (Britain, Russia, Austria, Prussia). A great power that is eliminated or a French vassal is counted as recognizing by construction.

### §2.4 The table — how a court answers, every turn

Each great power's stance is **re-derived every turn** of the sitting from `congress.answer(world, court)`:

- **at WAR with France** → *refuses*, unless its war score against France is ≤ **−40** (then it *sues*: the existing P1 sue seam generates its peace offer, which now carries recognition; ratifying it flips the court to *recognizes*). A refuser whose capital France holds sues at once.
- **at peace** → the acceptance formula for a new proposal type `recognition`, threshold **50**: base = relation; `agenda_acceptance_mod` (a deny design unsatisfied −12, an acquire design targeting French-held soil −12, a satisfied or bought-off design +12); hegemony fear −(bloc share − the court's `share_floor`) × 100 (Russia's `arbiter_of_europe` bites here); war weariness ≥ 60 → +10; beaten by France within 15 turns → +10; an alliance +20, a defensive alliance +10, a non-aggression pact or open borders +5; a **sweetener** the player attaches (gold: +10 per 1,000g, cap +20 — a new `recognition_sweetener` clause on the existing instrument transport); seeded jitter ±3 through the campaign-seed helpers. ≥ 50 → *recognizes*, else *refuses*.
- **Britain** answers like the others and additionally reads *shut out* (not blocking) when the Continental System closure is ≥ **60%** for every turn of the sitting and no British corps stands on the Continent. Talleyrand names it: "London will not sign; London need not — close the ports and she is a spectator."
- A recognizer **flips back to refusing** if France declares a new war, takes a province by force, or denies its design further (annexes soil it covets) during the sitting.

The table (a new **CONGRESS** tab on the Diplomatic Ledger, and the same rows in the war room) shows for each court: the flag, the stance (RECOGNIZES / REFUSES / SUES / SHUT OUT / GONE), the reason sentence from the formula's top negative term, and **the price** — the cheapest lever that would flip it, derived from the same terms: "Vienna: Savoy by right — buy the design (300g/turn), or beat Charles (war score −40)"; "London: 4 more ports of 26 shut, or 12,000g"; "St Petersburg: our share frightens the arbiter — a guarantee to Sweden, or Finland to the Tsar"; "Berlin: Hanover — cede it to Prussia's client, or 6,000g". The price is display-only counsel; it is never a bargain the court is bound to.

### §2.5 The sitting — the challenge

While the Congress sits (turns `summoned+1 … summoned+8`):

- **Refusal has teeth.** Each refuser's intent weight against France rises **+15 a turn** (the AI-3 ladder climbs to `fight`; beat 2 fore-warns; a declaration follows within 3–4 turns unless it recognizes) — the "War of the Congress". A refusing Britain sponsors every other refuser at **+200g/turn** (the paymaster generalized). The coalition alarm's formation gate drops from 60 to **40** while any two great powers refuse. Refusers' Revanche designs get +weight.
- **The hold.** Every turn ALL of: titled ≥ 50 · Paris held · the Emperor not a prisoner · no satellite in rebellion · no titled province lost (a titled province taken and retaken the same turn still breaks it) · **France has declared no war since the summons** ("the Emperor who summons the Congress and then draws the sword has answered for Europe") · alarm < 80. A broken hold dissolves the Congress that turn.
- **The bills.** The marshals' collective petition at the summons (§2.3); during the sitting the reward rail's rows are priced ×1.5 (the "peace dividend"); an eroded marshal's refusal to march is likelier (existing trust arms). Satellites: a client petition during the sitting carries double loyalty stakes; a rebellion dissolves the Congress. These are the existing systems with the Congress's multiplier, so the player is juggling four fronts with the scoreboard in view.
- **Counter-play, all existing verbs:** beat a refuser to −40 (or take its capital); buy its design (`buy_off_design`); pay its price (the sweetener); court it (missions, `improve relations`); guarantee a third party (`guarantee_nation`) to satisfy an arbiter; cede a titled province to its client by settlement (title moves, the count drops — a real trade); close ports for Britain (the CS surface); create a client that satisfies a deny design (the formables).
- **Narration.** Beats: 1 the summons; 2 a refuser's fore-warning/declaration ("Vienna answers the Congress with cannon"); 3 a recognition won ("Berlin signs"); 4 the eighth turn. The Moniteur runs a *Congress column* every turn of the sitting; Talleyrand's rung names the biggest blocker and its price; the clock line (`THE CONGRESS SITS — turn 3 of 8 · 50 of 50 titled · Austria REFUSES (Savoy) · London SHUT OUT · Berlin, St Petersburg RECOGNIZE`) rides the war room, the ledger's Territories tab and the end-turn banner from ONE source, `congress.state_line(world)`.

### §2.6 Resolution

- **Eighth turn, hold intact, every great power recognizing / shut out / gone → THE IMPERIAL PEACE.** `record_ending(world, "victory", "imperial_peace")`; the gold register of the end scene (§4); the Moniteur's final special; **Continue the reign** or **Retire to the Tuileries**. Stamped once; a second Congress can never fire it again.
- **Otherwise → the Congress dissolves.** Alarm **+15**; a **10-turn** cooldown before another summons; each refuser gains a 10-turn grudge (the `agenda_grudge` contributor, +1 threat, cap 2, existing); the marshals' expectation rises by one rung (they were promised the peace); a dispatch beat names the courts that would not sign. Not a defeat (D8).
- **E1, the Universal Monarchy:** if no great power stands (all eliminated or French vassals), the Imperial Peace fires **without a Congress** on the first end turn — nobody is left to contest the order.

### §2.7 Numbers (all in `campaign_end`, all in-band tunable; the SHAPE is the ruling)

`hold_titled: 50` · `congress_turns: 8` · `title_turns: 12` · `recognition_threshold: 50` · `refuser_weight_per_turn: 15` · `congress_alarm_gate: 40` · `hold_alarm_ceiling: 80` · `cs_shutout: 0.60` · `sue_score: -40` · `sweetener_per_1000: 10 (cap 20)` · `dissolve_alarm: 15` · `congress_cooldown: 10` · `verdict_turn: 44`.

### §2.8 Measurement before landing (GE-V)

- The commanded-accept arm must never be able to summon (35 titled); pinned on the archive.
- The fiat arm must never win (alarm 97, at war with everyone); pinned.
- A scripted **"Pressburg" arm** (Ulm → Vienna → a Pressburg that cedes Tyrol, Carniola and Venetia by treaty, vassalizes Bavaria, Saxony and Hesse → Hanover held twelve quiet turns → summon) reaches 50 titled between turns 25 and 40 and, with Austria and Prussia recognizing and Britain shut out at 60%, wins between turns 33 and 48. If it cannot reach 50 by turn 40, `hold_titled` comes down to 45 before anything else moves.
- A scripted **"Premature" arm** (summon at exactly 50 with two refusers and no preparation) must LOSE the Congress on 3 of 3 seeds — the fuse is the player's judgement.
- The global-elimination probe fires E1 on the first end turn after the last great power falls.
- The played campaign (GE-V) confirms the table reads, the prices are true (each named lever flips the court when applied), and the sitting FEELS like a crisis: at least one declaration of war, one bill, one flip.

---

## §3 Defeat (RULED)

- **R1 stands:** "The Empire Without Soil or Sword" — ≤ 1 province, or no free corps and no affordable commission, for **5** consecutive turns; "The Eagle in Chains" — the Emperor captive **10** consecutive turns unfreed (with the purse-priced exit guaranteed, GE-1). Both warned on the existing defeat-imminent channel with the clock and the exits named; Paris alone never triggers them (PL-31). Terminal: the crimson register, Load / Main Menu, GET endpoints alive (R3).
- **The Humbled Peace:** ratifying a settlement that cedes Paris, or ≥ half the homeland, or makes France a vassal → `record_ending(world, "defeat", "humbled_peace")`, the crimson-grey register, **continue**. The Verdict grades it as an eclipse.
- **A dissolved Congress is not a defeat**; a lost titled province is not a defeat. **No third clock** (grip and treasury already reach R1 through attrition). Re-open: a played campaign showing a hopeless state neither arm reaches within ten turns.
- **GR5:** `fall.get_fall_state(world, nation)` answers for any nation; only the player's ends the game; AI courts keep losing by elimination and by suing.

## §4 Screens (RULED)

- **One scene, `campaign_end.tscn` (CanvasLayer 122), four registers**, fed by ONE builder `build_campaign_summary(world, ending)`:
  - **THE IMPERIAL PEACE** — gold, the Proclamation style: the four flags with SIGNED / SHUT OUT / GONE, the titled count, the sitting's eight turns as a strip, the campaign totals (battles fought / won / lost, men lost and inflicted, provinces taken / lost, coalitions faced), the Verdict tier, a final Moniteur line; buttons **Continue the reign** / **Retire to the Tuileries**.
  - **THE FALL OF THE EMPIRE** — crimson: the cause line ("No soil and no sword remain to the Emperor" / "The Emperor, a prisoner these ten turns, is deposed"), the totals, the tier; buttons **Load a campaign** / **Main Menu**; input disabled.
  - **THE HUMBLED PEACE** — crimson-grey: the treaty's terms, the totals, the tier; **Continue**.
  - **THE VERDICT OF HISTORY** — parchment: the tier and its three lines, at turn 44 if no ending has fired ("the reign, unfinished, is judged as it stands"), and as the epilogue block inside the other three; **Continue**.
- **The Congress table:** a CONGRESS tab on the Diplomatic Ledger (stance / reason / price per court, the sitting's clock, the hold's seven conditions with ✓/✗), and the same rows in the war room while the Congress sits.
- **The clock line** on the war room, the Strategic Ledger's Territories tab and the end-turn banner (one source). Before a summons it reads the gate: `THE CONGRESS OF PARIS — 43 of 50 titled (7 held, unsettled: Vienna, Bohemia …) · summon from the Cabinet (F1)`.
- **Saves:** the ending stamped in `metadata.ending`; a defeated save loads onto the end screen; the autosave after a fall is the pre-fall turn plus a "Final — <date>" save (R6).
- **Raised** from every end-turn flow, from `/load`, and from the settlement ratify path (the Humbled Peace) by the NA-6b stash-and-raise discipline; never blocks the turn; `/mailbox/activate` gets the "The war is over." guard (R6).

## §5 Global elimination (RULED — E1–E6)

E1 the Universal Monarchy · E2 the alarm producers early-return while `get_qualifying_nations` is structurally empty and Talleyrand says "There is no Europe left to alarm" · E3 the dead stay dead (enemy-phase rows, fleets, ports, trade dominance, decks) · E4 a great power's knockout is a beat and a verdict input · E5 great powers stay eliminable on the battlefield · E6 the AI roster needs no change. All as written in `GAME_END_SPEC.md` §7.5; pinned in GE-1.

---

## §6 The ending slices

| Slice | Contents | Effort |
|---|---|---|
| **GE-1** backend | `backend/game_logic/fall.py` (R1's two clocks, ONE serialized `fall_clock`, the defeat-imminent copy with clock and exits, the captivity-exit reachability proof); `game_end.py` (`record_ending` + the serialized `ending`, `campaign_totals`, `build_campaign_summary`, the Verdict tiers, the `campaign_end` scenario block + validator + `MODDING_FORMAT`); **`province_title`** at the four seams + reconciliation; the Humbled Peace stamp at the three ratify seams; E2/E3/E4 with pins; WO-D10 (exile commissioning, flip lever, series attribution if it moves); saves (R6); the three end-turn exits and `/load` carry the ending; `first_contact._is_open_ended` re-pointed; tests. | ~1 |
| **GE-2** client | `campaign_end.tscn/.gd` with the four registers, raised from every end-turn flow, `/load` and the ratify path; keep-playing after a marked ending, Load / Main Menu after the Fall; the legacy `_show_game_over_screen` text kept as fallback and de-legacied; the clock line on the three surfaces; XR-1 harness + boot smoke; a Mode-A driver arm that reaches each fall and the verdict; the IQ-10 frames for all four registers. | ~1 |
| **GE-3** the Congress | `backend/game_logic/congress.py` (`can_summon`, `summon`, `answer`, `price`, `tick`, `resolve`, `state_line`; ONE serialized `congress`), the `summon_congress` verb through the shared executor (2 DP + 1 admin; corpus rows; the wizard row with gate terms), the `recognition` proposal type + sweetener clause on the instrument transport, the refuser pressure hooks (intent weight, paymaster, alarm gate, Revanche weight), the recognition clause on the sue seam, the hold predicate, the dissolution, E1; the CONGRESS ledger tab + war-room rows; beats 1–4 + the Moniteur column + Talleyrand's rung; the Pressburg and Premature driver arms; `BASELINE_SERIES` re-recorded once (the pressure hooks are dormant with no Congress — attribution must show arm 0 byte-identical); `tests/test_congress_of_paris.py`. | ~1.5 |
| **GE-V** the played campaign | The user (or Claude driving the client) plays a campaign to a Congress: the table reads, the prices are true, the sitting is a crisis; the §2.8 measurements published; the pillar "the ending" re-scored (3.0 → target ≥ 7). | ~0.5 |

## §7 Build order and the routing rule

**~~F1~~ ✅ (Sept 23, 2026) → ▶ F2 → F3 → F4 → F5 → F6 → GE-1 → GE-2 → GE-3 → GE-V → the release build (ROADMAP 10) → Updates 1–5.** ≈ 7.25 sessions before the build. A player report never re-orders the ending; it may re-order F2–F6.

Every slice's commit carries: this document's §6/§1 table marked (✅ + date + commit), `STATUS` ▶ NEXT UP struck and advanced, the rows disposed in `BUG_FIXES` / `DESIGN_REFINEMENT`, `CLAUDE.md` LIVE STATE. A slice is not landed until those four are in the commit.

## §8 Done when (falsifiable, the whole program)

1. A fresh Begin shows the boot help and a turn-1 briefing; no player-facing string in the F2 census carries a raw key, state, enum, float turn count or `(s)`; the four F3 frames are clean at both scales; a winning historical-seed campaign sees no collective petition before turn 12; Bavaria takes at most one province on turn 1.
2. `summon the congress` is refused with named gate terms below 50 titled and accepted at 50; every great power answers every turn; each price on the table, applied, flips the court (driven pins per lever).
3. The Pressburg arm wins between turns 33 and 48; the Premature arm loses 3 of 3; the accept and fiat arms cannot summon or win; E1 fires on total elimination.
4. Both fall clocks warn on turn 1 and fire on the 5th/10th; retaking a province, commissioning, or ransom stops them; Paris alone never triggers; the tutorial and the bare flag world never arm.
5. Every ending is stamped once, survives save/load, and raises the right register; a defeated save never loads onto a silent board.
6. `BASELINE_SERIES` and M1–M7 byte-identical except the three attributed re-records (F4, F5, GE-3).

## §9 Pins consciously flipped (to be named per commit)

- The IQ-2 "never terminal" pins (`_dispatch`, `_economy_status`, `_war_room`, `_chronicle`, `_client`) — GE-1.
- `test_first_contact_keyless` (the open-ended answer, 2 tests) — GE-1.
- `test_economy_ec6_sandbox::test_1805_no_end_screen_at_turn_60` — re-blessed (the verdict never sets `game_over`).
- The strategic-report popup whitelist pin — F3.
- The UX23-A/UX23-B expectation timing pins that assume a rise per victory — F4.
- The FA-D13/PT-D4 display pins that assume three walk-ins — F5.
- Legacy: 0.
