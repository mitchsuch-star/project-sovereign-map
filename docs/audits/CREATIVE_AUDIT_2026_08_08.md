# Creative Audit — August 8, 2026 (post–tutorial, post–marshal-voice; pre–shippable build)

> **What this is.** A play-first creative audit built from a **26-turn France/1805 campaign** driven
> through the real backend at master `de5af03` — i.e. after ROADMAP positions 4 (Music & Sound),
> 5 (Econ Balance), 6 (Main Menu), 7 (Tutorial), 8 (Voice-to-Text) and 9 (Marshal Voice Tier 1)
> landed. `LLM_MODE=anthropic`, seed `historical`. Evidence:
> `CA9_CAMPAIGN_DIGEST_2026_08_08.md` (player-visible transcript) and
> `CA9_PLAY_NOTES_2026_08_08.md` (the live play log, including every claim I later corrected).
>
> **The question asked was "what's fun and what isn't", so this memo leads with play, not with
> code.** Findings were then put to an adversarial verify→refute fleet against master; claims that
> did not survive are corrected in place, never quietly dropped.

---

## 0. Methodology, and two things that must be read first

**0.1 — The transcript is honest about what the *client* renders.** The Aug-4 audit's governing
caveat was that its digest was assembled from each enemy action's `message` field, which the
shipped Godot client never reads. This audit's harness instead **mirrors
`enemy_phase_dialog.gd::_format_action`'s own key list**, verb by verb, and stamps a
`<<<RAW-FALLBACK>>>` marker wherever the client would fall through to printing a raw internal verb.
Measured across the whole campaign: **zero fallbacks** — CA8-6 is holding.

**0.2 — A contamination event, and what it invalidated.** Mid-session the user's own Godot client
(PID 28048, live on `127.0.0.1:8005`) fired `POST /new_game` and reset my world to turn 1
(`backend.log:792`). Three of my early observations were read from that fresh world and are
**withdrawn** — they are listed as withdrawn in the play notes rather than deleted. The audit then
moved to an **isolated backend on port 8015** so nothing external could reset it, and the campaign
reported here was replayed from turn 1 on that isolated world. Findings dated before the reset were
re-verified on the clean run before being carried forward.

**0.3 — The visual half was not performed, deliberately.** The Godot client is hardwired to port
8005, which the user's own live session owns. Rather than disturb their game or edit the client, I
verified every client-side claim by reading the shipped `.gd` source (quoted inline). A visual
sign-off pass on the surfaces named here is still owed.

---

## 1. What the campaign actually was

Turn 1, one sentence: *"Marshal Ney, march on Mack at Swabia and destroy him."* Ney reports the odds
are bad and asks for orders. I mass instead — Soult gets a written order and answers *"No more and
no less"*; Bernadotte answers *"I move when the need is real, not before."* Six marshals, 107,722
men, converge on Swabia and break Mack's corps for 1,940 casualties. It is a superb opening five
minutes.

The next tick, **8,676 of those men starve**, because the province the game just told me to fill
feeds 40,000 and I put 107,722 in it. Nothing warned me. The number exists — the region panel shows
it once you occupy the province — but no surface in the ordering path mentions supply at all, and
the muster preview that talks you into concentrating is silent about it (CA9-3).

That is the whole campaign in miniature, and it repeats for twenty-five more turns. Murat's
cavalry turns a rout into annihilation and the game stops him at Hesse's border to ask what our war
purpose is — then never renders the question, and silently eats my next two orders. Lannes, hungry
for glory, attacks on his own initiative and drags the same invisible prompt back. Archduke Charles
grinds Massena down at Milan; Soult, one province away and holding a written order to support him,
**refuses**, because the order bound to a location rather than to a man — after the game promised in
so many words that *"Soult will march to Ney's guns."*

By turn 13 Davout, Murat and Massena are standing in **Ottoman Albania**, nine provinces from their
war, having followed a beaten British officer there; Murat's standing order to march on Vienna has
been silently cancelled and no event mentions it. By turn 16 Talleyrand reports the campaign's best
moment: **Austria's national design has flipped to *Revanche* — against Russia**, its own ally, for
holding Bohemia. Nothing scripted that. It is a real, exploitable fracture in the Third Coalition,
reported accurately and actionably.

And then nothing happens, for eleven turns. Provinces frozen at **31/95 from T16 to T26**. The
headline is a victory at Bohemia on six of eight turns, the same sentence with a different marshal's
name. The line *"Sire — Marshal Davout's household goes unpaid. His patience erodes with his
purse"* appears **fourteen times, verbatim**. At war score +13, holding two Austrian provinces with
Mack captured and his army destroyed, Talleyrand's *recommended* peace terms are to **pay Austria 77
gold a turn and demand nothing.**

Final accounting: France won nearly every engagement it fought. It lost **52,677 men to hunger**
against **38,016 in battle** — hunger killed 1.39 times as many French soldiers as the enemy did.
The army went 189,000 → 86,573. Trust ended at Bernadotte 10, Massena 26, Ney 53. Thirty-one
provinces of 126, and a war with no way out.

*(Correction on record: earlier in the play notes I wrote "4.5× more men died of hunger than of the
enemy". That was wrong — I was totalling lead-corps figures for battles against all-corps figures
for supply, which is exactly the confusion finding F2 describes. I made the same mistake the game
makes. The honest ratio is 1.39:1.)*

---

<!-- ANALYSIS SECTIONS MERGED BELOW FROM THE VERIFY/REFUTE FLEET -->
## 2. Findings — all 14 survived adversarial refutation

Every row was put to an independent skeptic instructed to refute it (wrong path / correct-by-design
/ contaminated world / already fixed / dead code). **12 were NARROWED, 2 survived outright, 0 were
killed.** Where a skeptic narrowed a claim, the row states the CORRECTED version.

| ID | P | Finding (as corrected) | Root cause |
|---|---|---|---|
| **CA9-1** | P1 | **The war-purpose hard stop is created and never delivered.** All three PT-F1 pursuit-capture sites call `_stage_war_purpose_selection(...)` and **discard the return value**, so the dialogue lives only on `world.dialogue_manager` and no key reaches the result dict. The client renders modals from `response.diplomatic_dialogue`, and `war_purpose_selection` *is* whitelisted (`main.gd:32`). Result: total input lockout — `end turn` itself is swallowed — until the player guesses a token never shown. Fired **4x** in 26 turns, twice from marshal actions the player never ordered. | `combat_executor.py:4489`, `:5410`, `:6323` discard the wrapper at `:3165-3178`; `_stage_war_purpose_selection` at `:6543-6571` returns a payload nobody reads |
| **CA9-2** | P1 | **The muster preview's verdict is asymmetric by construction.** The attacker side gets `+= committed_attacker` (the whole mustered joint force); the defender side is `max(1, enemy.strength)` — the single named marshal, with no `committed_defender` term at all. "The balance of force looks favorable" is computed against one man while the player's whole army is counted. The same wrong word also suppresses the confirm modal. | `objection_v2.py:867-883` (`inferred_attack_effective_ratio`), driven from `combat_executor.py:828-832` |
| **CA9-3** | P1 | **The muster preview never mentions supply, and the muster physically relocates every joiner onto the battle square.** `_build_muster_preview` is holding `region` and the full `will_join_marshals` list and never reads `region.supply_capacity`. Massing 107,722 men at Swabia (capacity 40,000) on the game's own advice cost **8,676 men the next tick** against 1,940 taking it. | `combat_executor.py:834-844` (preview), `:4288` (relocation) |
| **CA9-4** | P1 | **"Soult will march to Ney's guns" is false as written.** The Grouchy Rule accepts a SUPPORT order only when `order.target == primary.name` — only when the supported marshal *leads* the battle. Soult refused 3x while holding the exact order the muster preview prescribes; 28,202 men sat out the fall of Milan. | `combat_executor.py:1071-1073`, mirrored at `:725-726`, `:596`, `:663`; copy at `strategic_executor.py:1326-1329` |
| **CA9-5** | P1 | **The default peace offer pays tribute to the court you are beating.** The arms are `if war_score > 20` (demand) / `elif war_score < -20 **or relation < -50**` (offer gold). The Aug-7 CA8-27/D2 fix sits *inside* the second arm and guards only the **territory cession** — the gold sweetener above it is still reachable via the `relation < -50` disjunct, true in every war. Measured at **+13 in my favour**: offer Austria 77g/turn, demand nothing. There is also a ±20 dead band where neither arm fires. | `diplomatic_templates.py:3581-3588`; cession guard at `:3598` |
| **CA9-6** | P1 | **The conquest→leverage→terms loop is dead — four mechanisms, none of them `base_side_pressure`.** Headline two: the war-score *contested-capital* arms count marshals with `strength <= 0` and captured marshals, missing the `strength > 0 and not captured_by` guard their two siblings carry; and the decisive-victory cap is not keyed per winner. Net: 26 turns of victory, an enemy army annihilated and its commander captured, and territory remains undemandable at every harshness. | `diplomacy.py:2892`, `:2899`, `:9060`; `settlement_scoring.py` 11-component pipeline |
| **CA9-7** | P1 | **The dispatch leads with third parties' prisoners.** The `marshal_captured` branch reads only `marshal` and `captor`, never `e["nation"]` — which `_capture_marshal` already stamps. At **weight 95**, the highest class in the game. Led 3x in 16 turns; once it was Spain taking a British officer, above a French victory and 10,718 French dead. | `dispatch.py:444-454`; event field set at `combat_executor.py:2452`, `:2496-2498` |
| **CA9-8** | P1 | **Auto-reinforcement crosses into neutral countries and silently voids written orders.** Reinforcer relocation has **no diplomatic-ownership guard**, and the arrival path then nulls `strategic_order` with no event, notification or message. Three corps ended in Ottoman Albania; Murat's live MOVE_TO Vienna was destroyed and nothing said so. | `combat_executor.py:4288` (relocation), `:5141-5146` (silent order clear) |
| **CA9-9** | P2 | **Berthier's casualty figure is lead-only and unlabelled.** `_reconcile_report_survivors` (CO-5) *overwrites* `casualty_summary.attacker_casualties` with `attacker_original − lead.strength` **after** casualties were distributed across all participants. Two lines a few rows apart, both headed "Casualties:", differ ~6x (1,940 vs 316). | `combat_executor.py:1366-1369` |
| **CA9-10** | P2 | **`action_info.cost` under-reports multi-AP orders.** The charge loop reassigns `action_result` each iteration instead of accumulating, so the reported cost is the last single call's base cost (1), never the loop total (2). AP is deducted correctly; the API contract lies, and the player budgets on it. | `executor.py:1788-1789` → `:1803`; same shape at `meta_executor.py:2003-2011` |
| **CA9-11** | P2 | **Fog defaults are rendered as facts.** Below FULL visibility the filter substitutes `supply_capacity: 0` (and income/stability/war_damage 0) as crash-safe defaults, and **both** client render sites print the sentinel as a literal number. A province that feeds 40,000 reads `Supply: 0`. A `-1` "unknown" sentinel already exists twelve lines below for garrisons and is already handled by both clients. | `world_state.py:7612`; `region_panel.gd:179`, `map_renderer_base.gd:2581` |
| **CA9-12** | P2 | **The fog fallback is whole-phase, not per-nation.** `fog_hidden_summary` is only reachable when *every* enemy action on the continent was suppressed, so one visible action anywhere hides all of Europe. This is the Aug-4 CA8-15 remediation — chosen independently by both the narration and aliveness scorers — still unbuilt. The fix cannot reuse the existing key: the client branches on it *instead of* the nations loop. | `main.py:944-953`; also `:1400`, `:778-780` |
| **CA9-13** | P2 | **The supply headline prescribes a build the executor refuses.** The remedy clause models depot legality with **two** predicates; `_execute_build` enforces **nine**. Stability is one it never asks about — and securing a conquest sets stability to 25, so a just-taken province can never accept a depot. | `dispatch.py:1382-1393` vs `economy_executor.py:1400-1431` |
| **CA9-14** | P2 | **`pursue` only accepts the raw internal key.** The strategic parser matches the roster by exact key only; on failure the target is misclassified as a region, routing it to the wrong fuzzy list. The UI prints "Archduke Charles" 28x and `ArchdukeCharles` 105x; only the latter works. `attack` resolves it correctly — the two verbs use different resolvers. | `strategic_parser.py:537-554`, `:647-653`; `parser.py:1161-1196` |

### Corrected or killed — recorded, never silently dropped

| Original claim | Outcome |
|---|---|
| "Supply capacity is unlookupable off own soil" | **Refuted by me before filing.** The region panel *does* show it at FULL visibility, which a marshal's presence grants. Replaced by CA9-11, which is the real defect. |
| "`capital: -20` is a bug" | **Withdrawn.** Correct behaviour — my vassal Kingdom of Italy's capital is Milan and Austria has held it since turn 3. Leaves a P3 legibility note: the term is unlabelled. |
| "Typed 'Portugal' fuzzy-matched to 'Prussia'" | **Root cause corrected.** No fuzzy nation match exists. The dialogue router matches an answer verb against the *active* dialogue and **never consults the nation the player named** (`main.py:2046-2110`). Broader and simpler than claimed. |
| "The mis-routed accept destroyed two pending letters" | **Withdrawn** — the mailbox was empty because the user's client had reset the world. |
| "~40,000 to hunger vs ~12,000 to the enemy (4.5:1)" | **Corrected to 52,677 vs 38,016 (1.39:1).** I had totalled lead-corps battle figures against all-corps supply figures — the exact confusion CA9-9 describes. I made the game's own mistake. |
| "The Fontainebleau petition was not delivered" | **Withdrawn** — it arrives deferred on the next command, the documented PopupQueue contract. |
| "The campaign log dropped three battles" / "Davout frozen by a stale engagement" | **Withdrawn** — both read from the contaminated post-`/new_game` world. |

### Found in passing, outside the 14

- **P1 (latent): the hard-stop dialogue router does bare-substring matching.** `main.py:2067-2071`
  scans `_DIALOGUE_RESPONSE_KEYWORDS` — containing **"no", "yes", "send", "more", "garrison",
  "invest", "demand", "review", "consider", "side", "start", "begin"** — as raw substrings, first
  match wins. While an *invisible* war-purpose stop (CA9-1) is pending, `Ney, march on **No**rmandy`
  contains "no". The soft-stop branch was hardened against exactly this (its comment names
  "garrison"); the hard-stop branch was not. Verified the soft path is safe.
- **P2: the standing-headline cooldown demotes but never suppresses.** PC-7 works — `estate_eroding`
  yields the lead after `STANDING_LEAD_MAX`. But the code's own comment says it "falls to a
  **sub-beat** … reported, never deleted", and there it repeats verbatim forever. Measured: **the
  same sentence 14 times in 25 dispatches.** `_STANDING_ESCALATION` variants exist but are consulted
  only on the keeps-the-lead branch. `dispatch.py:789-815`.
- **P2: three "should I attack?" advisors use three different neighbourhoods.** `[HINT] X is
  undefended` reads marshals in the **target region only** (`movement_executor.py:661-669`) and
  ignores adjacent reinforcement; the muster preview reads the player's side only; the marshal's
  objection reads adjacent strength and was *correct*. All three fired on Tyrol and disagreed.
- **P3:** `mailbox.summary` renders the raw key `"PapalStates — Open Borders"` (the envoy digest
  correctly says "Papal States"). **P3:** "Even harsher" produces byte-identical terms to "Harsher".
  **P3:** objections expose `choices: ["trust","insist"]` and never show either word; plain English
  is rejected, and a pending objection blocks the free read-only `status`.

---

## 3. The through-line

**Every one of these is the same defect wearing a different hat: a producer and a consumer that
disagree about what a number or a promise means, with no seam forcing them to agree.**

The muster preview counts my army and the enemy's *one man* (CA9-2). Berthier's report counts the
lead corps while the line above it counts the army (CA9-9). The AP charge loop counts to two and
reports one (CA9-10). The supply advice models depot legality with two predicates while the executor
enforces nine (CA9-13). The `[HINT]` looks at one province while the objection looks at two. The
support order binds to a place while its confirmation text promises a man (CA9-4). The war-purpose
dialogue is created by one function and delivered by another that never runs (CA9-1). The fog filter
writes `0` meaning "unknown" and the client reads `0` meaning "zero" (CA9-11).

The game is not short of systems, and its systems are not badly designed — the emergent Austrian
*Revanche* against Russia is as good as anything in the genre. What it is short of is **single
sources for the handful of quantities the player actually decides on**: how strong is the enemy,
how many men will this cost, what will this order actually do, and what is my victory worth. Four
questions; each currently has two or more answers in the shipped build.

The most expensive instance is the last one. **26 turns of unbroken victory could not be exchanged
for one province** (CA9-5, CA9-6), so from turn 16 the map froze at 31/95 and the campaign became
the same battle at Bohemia with a different marshal's name in the headline. That is not a missing
victory condition — `sandbox_mode` disabling the endgame is deliberate and already owned by the
Victory Pass at ROADMAP 12-13. It is that **the one remaining way for the world to change — the
negotiating table — is wired to a number that battlefield success barely moves.** Remove the ending
*and* the ability to convert winning into anything, and a sandbox becomes a treadmill. The Victory
Pass will not fix that on its own.
## 5. What is genuinely excellent — do not touch this

Ranked by how much delight they produced at the keyboard.

1. **The muster preview naming who will and will not march, and why.** Nothing else in the genre
   does this. *"WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support
   Ney' and he will march"* / *"WILL NOT — Bernadotte: will not lift a finger for this marshal."*
   It converts a relationship graph into a decision. The one caveat is that the fix it advertises
   does not work (F8), which is a bug against the best thing in the game.

2. **Soult.** The literal marshal is the most successfully realised character in the build. He
   costs 1 AP instead of 2 *"— Soult executes precise orders with fewer couriers"*, answers
   *"Understood to the letter. No more and no less"*, and then stands one province from Milan and
   **refuses to save Massena** because his written order named a place. The system, the price, the
   voice and the disaster are all the same idea. When Milan fell, the order of battle read
   `Massena 32,962(routed); Soult 34,876(refused)` and I felt it.

3. **Austria declaring Revanche on Russia.** Talleyrand: *"Austria's design: Revanche — Their court
   will not rest while Russia holds Bohemia."* I had taken Bohemia from Austria; Russia then took
   it from me; Austria's national design flipped to revenge **against its own coalition partner.**
   Nothing scripted it. This is the emergent-politics promise actually delivered.

4. **Talleyrand's "assess our situation."** Per-court design, weight, and how far each will go;
   the coalition's leader and posture; the turn's threat accounting (*"Natural threat decay (-3);
   Hegemony Passive (+1)"*); vassal loyalties; and then executable counsel: *"Britain's war has a
   purpose we can price — 'The Low Countries'. We hold what their court wants; offer it at the
   table and their reason to fight goes with it."*

5. **The Fontainebleau petition.** *"The marshals come together: Ney, Davout, Soult, Lannes, Murat
   and Bernadotte stand unrewarded while the Empire feeds on their victories... 1340g/turn of
   expectation stands unmet. The army does not march on glory alone."* Three options, each stating
   its exact terms. I conceded, and my net income fell from **+2,316 to +98 in one turn**, with a
   signed "Rentes: −2010g" line in the ledger. A narrative beat with a real balance-sheet
   consequence is the hardest thing on this list to build, and it works.

6. **The jealousy recurrence register.** *"Bernadotte resents Ney's laurels **again, 2 turns after
   the last**"* → *"...has become **entrenched**. The wound will not close on its own."* And the
   fore-warning: *"Murat is eyeing Mack's position at Nassau. I cannot guarantee he will wait for
   orders, Sire — any command would restrain him."* Then Lannes actually did it.

7. **Character expressed as mechanics.** Soult's envy makes him *"throw himself into his post with
   obsessive diligence"* and four provinces light up with
   `intel_updated ... source: "obsessive_patrols"`. Murat's *"First Horseman of Europe"* turns a
   rout into annihilation (+5,000 pursuit casualties). Davout's objection at Tyrol was
   **substantively correct** and heeding it was the right call.

8. **The war-purpose halt as an idea.** *"Murat halts at the frontier of Nassau — Hesse's soil, and
   we are not at war with Hesse. To seize it is to make war on Hesse — choose our purpose, or let
   the province stand."* The concept is excellent. It is undone entirely by never being rendered.

9. **The supply headline when it fires.** *"Sire — Ney, Murat and Massena stand 56,647 men at
   Tyrol, which feeds 30,000. 26,647 too many. 2,922 men lost in 2 turns."* Names the marshals, the
   mass, the capacity, the overage and the cumulative cost. A model of its kind.

10. **The per-court acceptance breakdown.** Eleven named components, each with a display label and
    a signed value, plus `top_blocker_display`. The surface is excellent; only one of the numbers
    feeding it is wrong.

11. **Small courts with real voices.** Reis Efendi: *"The Porte has outlasted a hundred
    ascendancies by trading with each at its noon; France's noon has come, and the bazaar is
    open."* Araujo, Consalvi, Bernstorff, Hardenberg — all distinct, none padding.

12. **Honest refusals.** *"Cannot build in Tyrol — region stability too low (35/100). Need 51+."*
    *"Murat cannot reach Vienna from Albania! Range: 2, Distance: 3."* The game says why, and says
    the number. That discipline is everywhere and it is worth protecting.

## What is not fun

- Winning every battle and watching the army die of hunger anyway, with no order-time warning.
- Being told to concentrate, concentrating, and being punished for it.
- An invisible question that silently eats your orders — including `end turn`.
- The same sentence fourteen times.
- Twenty-six turns of victory that cannot be exchanged for one province at the table.
- Turn 16 onward: the map stops moving and only the marshal's name in the headline changes.
