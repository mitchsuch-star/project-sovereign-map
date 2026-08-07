# Creative Audit — August 4, 2026 (post–composition slice, pre–shippable build)

> **What this is.** A play-first creative audit of a live **France/1805 campaign** driven through
> the real backend (`LLM_MODE=anthropic`, `seed=historical`), run at master `e450b02` — i.e. *after*
> ROADMAP position 3 (the composition slice) and position 3.5 (the econ spec review + levy/drill build)
> landed. **The review fleet analysed the first 12 turns**; the play pass then continued to turn 17
> (Vienna stormed, Austria eliminated), which is where CA8-26/27/28 come from. Evidence:
> `campaign_digest.md` (player-visible transcript, 1,526 lines), `campaign_log.md`,
> `transcript.jsonl` (raw payloads).
>
> **Output discipline.** Every claim is backed by a verbatim transcript line or a code reference I
> opened. First-pass claims that did not survive refutation are **corrected in place in §5, never
> quietly dropped** — of 59 candidate findings put to adversarial refuters, **13 were killed and 4
> more materially narrowed** (§5 carries all 14 rows, including the two the play pass corrected
> against itself).
>
> **⚠ One methodological correction governs everything below and must be read first.** The digest is
> assembled from each enemy action's `message` field. **The shipped Godot client never reads that
> field** (`enemy_phase_dialog.gd` — verified: the token `message` appears in that file only as
> `reinforcement_messages` and `fog_hidden_summary`). So the evidence pack **systematically
> over-reports the quality of the enemy phase**. Several candidate findings were quoting prose the
> player never saw. Any future claim about enemy-phase copy must be checked against `_format_action`'s
> key list, not the digest.

---

## 1. The one-paragraph verdict

**France won every battle it fought, lost 83,000 men to hunger, ended the campaign 44× richer than it
started, and could not end the war — and the game narrated none of those four facts as connected to
each other.** The systems are in excellent health: the composition slice's six rows are all
demonstrably live in this transcript, the muster preview and the per-court acceptance review are the
best surfaces in the game, and Archduke Charles ground Marshal Ney down over three turns like a
character in a novel. What has broken is the **reporting layer between the simulation and the
player.** The single variable that decided every battle in this campaign — massed committed strength —
is printed only for the attacker, so the defending army is invisible and the terminal and the campaign
log disagree about French casualties **by up to 15×**. The mechanic that actually destroyed the army
is announced in a headline that renders `stand **more men** over what Munich can feed`, names marshals
who left two turns ago, and prescribes a building the game then refuses to let you construct there.
The war score that would convert twelve turns of victory into terms is keyed to a France↔Britain
*pair* that never fought, so it read **0** all campaign and Britain's own foreign secretary told the
player, by name, that Britain would not sign Britain's own free peace offer. **Nothing here is a
regression — it is the first campaign long enough and quiet enough to load the reporting layer past
its limits.** Fix the reporting, not the simulation.

---

## 2. Pillar scores

| Pillar | Prior | Now | Δ | Why it moved |
|---|---|---|---|---|
| **Combat** | 8.0 (Jul 25) | **6.5** | **−1.5** | Inputs still an 8 (every modifier named in character). Outcomes a 5: two surfaces disagree by 15×, the deciding variable is attacker-only, France lost **one** engagement in twelve turns |
| **Narration / enemy phase as theater** | 6.0 (Aug 3) | **6.0** | **flat** | The slice removed noise (0 duplicate `wait` lines, 0 fortify/unfortify pairs, forced marches collapsed). Removing noise is not adding theater; 4 of 12 phases contain no combat and 2 are pure no-ops |
| **Marshal drama** | 8.5 (Jul 25) | **7.5** | **−1.0** | No code regression — a measurement effect. Nine turns hid what twelve show: **nothing accumulates.** Murat's rival changed four times; one petition fired, on turn 1, and was re-served fifteen times |
| **Economy** | 7.5 (Jul 25) | **6.5** | **−1.0** | Model reconciles to the digit and prices are live. But **88% of everything France earned was unspendable**, the lifetime conquest-free sink is 13 building slots, and the one new affordance was refused at the place the dispatch named |
| **Diplomacy** | 7.0 (Jul 25) | **6.5** | **−0.5** | Everything added since July is presentation, and it presents well. First campaign long enough to show the fight→leverage→terms loop never connected once in 17 turns |

**Diplomacy sub-scores:** agendas & designs **8.0** · instrument/aliveness layer **7.5** · settlement
**4.5** · state-of-Europe legibility **4.0**.

**Not re-scored** (this campaign did not exercise them): parsing, vassals, UI/UX, naval, formables.
Carry the Jul 25 / Aug 2 readings forward. **Directional overall ≈ 6.9**, from five pillars only —
not a full re-score.

---

## 2a. What raises each pillar

§2 says why each score moved. This says what moves it back. Each row is the **scorer's own answer**
to "name the single change that would move this pillar most", quoted from its scoring pass, mapped
to the finding rows in §4 that it discharges.

**Two independent scorers — narration and aliveness — arrived at the same edit** (per-nation fog
fallback). That convergence is the strongest routing signal in this memo and it is not the §8
recommendation, which is a different edit for a different pillar.

| Pillar | Now | The one change | Discharges | The scorer's case |
|---|---|---|---|---|
| **Combat** | 6.5 | **Report the defending army as an army.** Mirror `combat_executor.py:5539` (massed strength) and `:5552` (ally casualties) onto the defender in the enemy phase; make the terminal `Casualties:` figure the whole-army number `campaign_log.py` already prints | **CA8-1** | *"Does four things at once: kills the 15× contradiction; names the variable that decides every battle; converts an invisible dominant strategy into a visible player choice; and finally lets the supply headline read as the **price** of the wall instead of unrelated nagging. **No balance retune required to land it, and it is the prerequisite for judging whether the ratios need one at all.**"* |
| **Narration** | 6.0 | **Make the fog fallback per-nation, not per-phase.** Move `fog_hidden_summary` (`main.py:890-898`) inside the nation loop and emit it for any nation whose actions were suppressed *or* collapsed away | **CA8-15**, and the I1/I3 floor | *"Turn 4 stops being `Brunswick holds position at Berlin` and becomes 'Our scouts report movement within Austria's and Bavaria's borders, but their formations remain beyond our sight.' A small edit to a sentence already written. It converts the pillar's worst failure mode — silence that reads as 'nothing happened' — into its best asset, dread, and **raises the floor, which is where all the score is being lost: the ceiling (turns 5/9/12) is already at 8.**"* Runner-up, nearly free: dedupe sub-beats on `(class, identity)` at `dispatch.py:498` (**CA8-5**) and branch the decree on `marshal.nation` (**CA8-21**) |
| **Aliveness** | 7.0 | **Same edit**, plus letting AI-vs-AI *outcomes* the campaign log already carries (province changed hands, capital stormed, court sued for peace) surface as a short "elsewhere in Europe" block | shares **CA8-15** | *"A player who reads 'Bavaria's colours are over Vienna; Austria's court is in flight' on turn 12 believes in a living continent. A player who reads 'Brunswick holds position at Berlin' on the turn three provinces changed hands does not. **This is an editing fix, not an AI fix, and it is far cheaper than making Prussia march.**"* |
| **Marshal drama** | 7.5 | **Give the grievance object permanence.** Bias `find_jealousy_target` toward the marshal's own history so a prior rival wins ties; and let a petition re-fire for a pair whose **escalation level has risen**, instead of burning the pair permanently at `jealousy.py:562` | **CA8-D3** (gate), **CA8-8** | *"Murat should hate **Davout**, for the campaign, deepening — not hate whoever topped the table on Tuesday. Then 'entrenched' arrives as a second audience with the same man, and the word means something. Everything else on the against-list is copy, worth maybe **+0.3** together; **this one is worth the whole point back and more**, because the pillar already generates the material and only lacks a reason to remember it past turn five."* |
| **Economy** | 6.5 | **Make the field levy the player's affordance and tell the truth about the proximity gate.** Wire the levy headline to the marshal the army actually has, not the capital nobody is near; make the refusal name the distance | **CA8-11** | *"It already exists, fully priced — the AI used it on screen. Wire it to 'Soult stands at Bohemia; 3,000 foot there cost 600 gold, or 450 at Paris if you send him home', and make the refusal say `Paris is 4 marches from your nearest corps`. That converts a dead 29,496g into a live decision **every turn**, and finally gives the supply crisis a gold-denominated answer. One honest sentence in `dispatch.py` and one in `world_state.py:4287` — **worth more than any new mechanic, because the machinery is already excellent and the loop is the only thing missing.**"* |
| **Diplomacy** | 6.5 | **Key the counterparty's leverage to the war actually being fought.** Point the war-status row and the offer producer at `compute_side_pressure_score`'s aggregate, which *already knew* Austria was 43 | **CA8-3**, and via **CA8-D2** also **CA8-27** | *"One change makes victory legible, makes Britain's offers stop contradicting Britain's own court, and lifts the package off the `white_peace` tier so the −10 legitimacy penalty stops being the answer to every question."* Runner-up at a fraction of the cost: a **Formed** arm on `get_threat_tier` (**CA8-18**) |
| **Command** | 7.0 | **Route strategic destinations through the tactical region chokepoint**, resolving against the FULL command text rather than the post-keyword fragment | **CA8-28** | *"One change, four of the six observed parse failures. Both halves already exist in the codebase — `executor.py:281`'s fuzzy matcher and `_resolve_region_from_phrase` — they are simply not wired together, and the strategic side is fed a truncated string."* Runner-up, and the more *damaging* single failure: a guard on `_interrupt_choice_from_text` — if the command also names a target or a province, it is a new order, not an answer |

### What this table does not cover

- **Four pillars were not exercised** by this campaign and carry no remediation here: **vassals**,
  **UI/UX**, **naval**, **formables**. Carry the Jul 25 / Aug 2 readings forward; a remediation for
  them needs a campaign that plays them.
- **Only CA8-1, CA8-11, CA8-15 and CA8-28 are unblocked.** The marshal and diplomacy changes need
  gates (**CA8-D3**, **CA8-D2**) because they move blessed numbers; the narration/aliveness edit is
  unblocked but its companion **CA8-26** is a design call (**CA8-D6**).
- **No scorer quantified its own post-fix number** except marshals (*"the whole point back and
  more"*, i.e. ≥8.5) and the copy backlog (*"maybe +0.3 together"*). The rest name a direction, not
  a target — do not read this table as a promise of a score.
- **§8's recommendation is CA8-1, and it is deliberately not the most-converged edit.** Two scorers
  chose the fog fallback; §8 argues combat instead because it is simultaneously a correctness,
  legibility, balance-visibility and narrative-joint defect, and needs no gate. If you want the
  cheapest broad lift rather than the deepest single one, do the fog fallback first — it raises two
  pillars' floors and discharges CA8-15 as a side effect.

---

## 3. What the campaign actually was

Turn 1, one typed sentence: *"Marshal Ney, take your corps and deal with Mack at Swabia."* Ney charges;
Davout, Lannes and Murat march to the guns; Soult holds to the letter of his written orders; Bernadotte
*"weighed its own ambitions and did not march."* Mack loses 12,319 men and answers back: *"A temporary
derangement of the arithmetic. Vienna will understand."* Turn 2 Austria takes Rhineland — French
homeland. Turn 3 Murat retakes it, alone (*"Murat stood alone, Sire. Soult never came."*), and the game
asks whether to sack it. Turn 3 Ney is **crowned** the army's most celebrated commander. Turn 5 Britain
offers peace at zero cost and all three courts refuse it — including Britain. Turn 8 Ney is made **Duke
of Carniola**. Turns 9–10 Archduke Charles unfortifies and attacks Ney three times through his own
−10%/−20% exhaustion penalties, breaks him at 21% morale, takes Bohemia; **Austria confiscates the
duchy.** Turn 12 Davout is crowned instead, and Ney stands at Munich with **5,632 men, morale 16**,
*"Hunted by Archduke Charles across 1 frontier."* Behind all of it, the army fell 189,000 → ~106,000 —
**~43,000 to hunger in Tyrol against ~15,600 to the enemy** — while the treasury climbed 671g → 29,496g.

That is a complete tragedy. The game logged all five beats and joined none of them.

---

## 4. Findings

### P1

---

#### **CA8-1 · P1 · Combat**
**The defending army is invisible, and the two surfaces that report French casualties disagree by up to 15×.**

> Terminal, turn 11: `ArchdukeCharles's forces press forward aggressively. Ney holds the line. Casualties: ArchdukeCharles 7,377, Ney 13.`
> Campaign log, same battle: `Third Battle of Tyrol: Archduke Charles (Austria) attacked Ney (France) — Ney holds the field (7,377 / 197 casualties)`

Same pattern every time: terminal `13,255 / Ney 113` vs log `13,255 / 514`; terminal `Kutuzov 9,020,
Davout 56` vs log `9,020 / 280`; terminal `ArchdukeJohn 7,276, Lannes 26` vs log `7,276 / 186`.

**Code.** `backend/game_logic/combat.py:1098` adds `effective += max(0.0, committed)` — the whole
friendly stack — into the defensive ratio, but `combat.py:268-278` computes casualties from
`self._calculate_casualties(defender.strength, …)`, **the lead marshal's own strength**, then
distributes. Massing five corps at Tyrol drove the ratio into the 0.6 casualty cap
(`combat.py:1141`) while the casualty base stayed Ney's 5,688. The four supporting corps paid nothing:
Soult 27,779 → 26,292 is *exactly* the reported `-1,487` supply attrition.

**And the game never says the word.** `backend/commands/combat_executor.py:5539` prints
`Massed effective strength: 24,000 (lead) + 58,072 committed (Davout, Lannes, Murat) = 82,072.` — but
it sits inside `for r in attacker_reinforcements:` (`:5508`) and is gated on `arrived_names`, as is the
ally-casualty line at `:5552`. **Both are attacker-only. There is no defender equivalent anywhere in
the file.**

**Cost.** The single variable that decides every battle in this campaign is printed only for the side
that does not need it. France lost **one** engagement in twelve turns. Massing is an invisible dominant
strategy; the player cannot see it, cannot price it against the starvation it causes, and when he reads
two casualty figures for the same battle he learns to distrust both.

*Correction to candidate F1: the ratios are real but **3–15× less extreme than filed** — the candidate
quoted terminal figures, which are lead-only shares.*

---

#### **CA8-2 · P1 · Dispatch** *(merges B1, B2, B3, first-hour-2, drama-5)*
**The game's lead sentence is wrong in four independent ways, on the mechanic that killed most of the army.**

> `HEADLINE [supply_strain w72]: Sire — Davout, Lannes, Massena and Ney stand **more men** over what Munich can feed.` (turns 5, 8, 12)
> Turn 8 headline: `Bernadotte, Davout, Lannes, Massena and Soult stand more men over what **Tyrol** can feed` — the roster ten lines below on the same dispatch reads `Soult @ Carniola … Massena @ Milan … Bernadotte @ Franconia … Lannes @ Munich … Davout @ Tyrol`. **Four of five named men are elsewhere.**
> Turn 12 headline names **Tyrol** and five marshals while the same dispatch's own warnings read `Supply shortage at **Bohemia**`.

**Code**, all in `backend/game_logic/dispatch.py`, all read:
- **(a) grammar/falsity:** `:749` `"over": f"{over:,}" if over > 0 else "more"` into the template at `:174` `"stand {over} men over what {region} can feed"`. The word fires precisely when `over == 0`.
- **(b) stale names:** `:744` `names = sorted(slot["marshals"]) or [m.name for m in here]` — `slot["marshals"]` accumulates from the 3-turn event window (`:704-713`); the live-occupancy fallback `here` is unreachable when a candidate exists.
- **(c) split epochs in one sentence:** `over` is computed live from `here` (`:723-729`) while `who`/`region`/`losses` come from the window. One sentence, two moments.
- **(d) stale province:** `:715` requires `len(s["turns"]) >= 2` over `turn >= current_turn - 2` (`:699`) and `:718` picks by **cumulative** loss — with no requirement that one of those turns be *this* one. Turn 5 led with Munich, quoting turn 4's frozen 11,251, while every attrition line on that dispatch read Tyrol.

**And the prescribed remedy is refused.** `Munich already has its depot` for five turns; then turn 9,
the player tries the other named remedy — `build a supply depot at Munich` → **`Cannot build in Munich
— not controlled by France`**. The province's capacity is never stated on any screen the player can
reach (`ledger.py:160-165` skips regions the player does not control), so *"move a corps"* has no
target size.

**Cost.** This led **6 of 12 dispatches**. ~43,000 men — three times the combat losses — vanished into
a sentence with a missing number, about a place whose limit cannot be looked up, recommending a
building the game refuses to construct there. The rational response is to stop reading the headline,
and the transcript shows the player did.

---

#### **CA8-3 · P1 · Diplomacy** *(merges first-hour-3, D1, D2, and the war-score root cause)*
**Twelve turns of victory contributed literally zero to the pressure on the court that owned the settlement, so a free peace was refused by its own proposer for a reason given as two undefined words.**

> Turn 17 war status: `"opponent": "Britain", "war_score": -5, "breakdown": {"territory": -5, "battles": 0, "decisive": 0, "capital": 0, "ticking": 0}, "battles_fought": 0, "recent_battles": []`
> Turn 5 settlement review, all three courts, verbatim and consecutive:
> `court Austria: Holding out 24/50 blocker=Settlement legitimacy`
> `court Britain: Holding out 13/50 blocker=Settlement legitimacy voice=Castlereagh holds Britain back from the table — Settlement legitimacy is the sticking point before they will sign.`
> `court Russia: Holding out 13/50 blocker=Settlement legitimacy`
> Talleyrand: `a white peace for France vs Austria + Britain + Russia cannot be sealed as it stands: Settlement legitimacy. **Author terms or hold until the field shifts.**`

**Code.** `calculate_war_score` (`backend/game_logic/diplomacy.py:2861`) reads `battle_records` for the
**pair** France|Britain — no French marshal ever fought a British one, so the campaign contributes
nothing. The offer producer reads the same pairwise number (`ai_diplomacy.py:3577`), sees 0, and emits a
white peace; the scorer then charges that white peace a hard −10
(`settlement_scoring.py:471`, `TIER_LEGITIMACY_BASE["white_peace"]`) and adds a further −10 mismatch
(`:480`) the moment terms are authored. **So Talleyrand's remedy — "author terms" — takes legitimacy
from −10 to −20**, and it is not among the four options on screen (`seek_bilateral_peace` /
`seek_armistice_instead` / `open_war_detail` / `back_out_settlement`).

Both exits deadlocked in one sitting. The bilateral substitute returned
`Making peace with Britain while allied with Spain (who is still at war with Britain) creates a
diplomatic contradiction.` — `severity: HARD_STOP` — and re-presented the identical five options, none
of which resolves it.

**Cost.** The game's central strategic loop — fight well → gain leverage → dictate terms — did not
connect once in seventeen turns. This is where a first-time player concludes diplomacy is decorative,
and in this campaign that is exactly what happened.

**Honest counterweight, and it matters:** the deadlock was **not total.** Austria sat at
`direct_score: 43` with an armistice on the table paying **218g/turn**. A *demanded* bilateral package
against Austria lifts the tier off `white_peace`, kills the −10, and 43 + exhaustion 20 very likely
clears 50. The model is sound. What failed is that the game routed the player to Britain and gave him
counsel so abstract it read as "nothing to do" while the field had already shifted enormously.

---

#### **CA8-4 · P1 · First hour**
**The game's first modal states the friendly muster and the friendly lead as if they were two opposing armies, never states the enemy's strength, and offers two choices where three exist.**

> `Ney reads this as a call to give battle, Sire — but Mack stands dug in and in greater strength. He will charge on your word. Berthier adds: Davout, Lannes and Murat would answer the guns — **82,072 in all, against 24,000 of Ney's own.** Confirm the assault, or hold him back?`
> `"options": ["attack_anyway", "hold_position", "cancel_order"]`

Read cold, *"82,072 in all, against 24,000 of Ney's own"* says the enemy has 82,072. The preceding
clause — *"in greater strength"* — confirms the misreading. **Both numbers are French**: the result
screen four lines later reads `Massed effective strength: 24,000 (lead) + 58,072 committed (Davout,
Lannes, Murat) = 82,072.` **Mack's number is never printed.** The player typed `press on`, a phrase in
none of the three option ids and in none of the prose.

**Code.** `backend/commands/combat_executor.py:919-922` — `joint = int(marshal.strength + committed)`
rendered as `"{joint:,} in all, against {int(marshal.strength):,} of {marshal.name}'s own."` The enemy
is not a term in the string. The two-option question is `backend/commands/delegation.py:349-350`.

**Cost.** The game's first decision is presented in a form that inverts its own meaning. And the
readable format already exists — `MUSTER — Massena (21,606; 48,765 with the muster committed) vs
ArchdukeJohn (16,543 men) at Bohemia`. The opening screen uses the unreadable one.

---

#### **CA8-5 · P1 · Dispatch** *(merges B4, drama-2)*
**The campaign's climax renders as a triplicate arithmetic report, and the sentence written for the moment is structurally unreachable.**

> `HEADLINE [own_mauled w85]: Sire — Ney was mauled at Bohemia: 2,218 men lost in a single action.`
> `· Sire — Ney was mauled at Bohemia: 2,099 men lost in a single action.`
> `· Sire — Ney was mauled at Bohemia: 2,269 men lost in a single action.`

Those are three genuinely distinct battles (`campaign_log.md`: Third/Fourth/Fifth Battle of Bohemia,
2,218 / 2,099 / 2,269) — but all three headline slots, the only editorial judgment in the briefing, go
to one marshal in one province in one phase, on the turn the player most needed the game to speak.

**Code.** `dispatch.py:300` adds one `own_mauled` candidate per battle with **no identity**; `:495-501`
seeds `seen_texts = {top["text"]}` and skips only on exact text — three casualty figures, three
strings, all survive. The identity key that would fix it is computed four lines above at `:487-489`
and used only for streak memory.

**Worse:** `own_broken` is weighted **90 — above `own_mauled`'s 85** (`dispatch.py:58-59`) and carries
the right sentence (`:170`): *"Sire — {marshal}'s corps has been broken at {region}. He must reform
before he fights again."* It did not fire. `marshal_broken` occurs **zero times in
`transcript.jsonl` across all 12 turns** — the ordinary break (`combat.py:815`) logs
`{"type": "retreat"}` (`world_state.py:10508`); `marshal_broken` is emitted only on the rare
no-retreat-route SHATTERED branch. **The narration cannot say "Ney's corps has been broken" in
ordinary play at all.**

**Cost.** What the stutter displaced is measurable: `estate_eroding` and `levy_open` both lost their
slots and reappeared as turn 10's sub-beats.

---

#### **CA8-26 · P1 · Dispatch**
**The morning dispatch has no headline class for a French success. Not one. The good news is exiled to the notification bar.**

`backend/game_logic/dispatch.py:55-83` — `HEADLINE_WEIGHTS` holds **15 classes**, raised from
**17 `_add()` sites** (`:270, 272, 275, 283, 285, 300, 308, 316, 321, 325, 330, 342, 345, 369, 384,
396, 408`). Every one is a wound (`home_captured`, `marshal_captured`, `own_broken`, `own_mauled`,
`enemy_on_our_soil`, `region_lost`, `supply_strain`, `war_touches_us`, `ally_broken`,
`estate_eroding`), an opportunity deliberately ranked below every wound (`levy_open` 54, with the
comment at `:71-73`: *"an opportunity never outranks a wound"*), or somebody else's business
(`europe_at_war` 52, `europe_crisis` 50, `europe_congress` 48, `europe_crisis_passed` 46).

**There is no `region_taken`, no `battle_won`, no `capital_stormed`, no `enemy_eliminated`.**

Measured over the campaign: **14 of 14 headlines were misfortunes** — `supply_strain` ×8,
`home_captured` ×2, `estate_eroding` ×2, `own_mauled` ×1, `region_lost` ×1.

**The illustrative case is turn 15.** France stormed **Vienna** (`The Great Second Battle of Vienna`,
`great_battle: true`, `region_conquered: true`, four contingents, Buxhowden routed) **and Austria was
knocked out of the war** (`Austria has been eliminated from the war.`). The dispatch led with:

> `HEADLINE [supply_strain w72]: Sire — Davout, Lannes, Massena and Soult stand more men over what Bohemia can feed.`

Neither Vienna nor Austria appears anywhere in that dispatch. Talleyrand's assessment likewise stops
listing Austria — turn 1 *"Against Britain + Austria + Russia"*, turn 15 *"Against Britain + Russia"* —
with no sentence marking the change.

**And the material exists.** This is the load-bearing correction to the first-pass reading: the game is
not silent, it is **mis-filed**. `/notifications` carries the events, and the writing there is the best
in the campaign:

> `p1 [estate_confiscated]` — *"Austria has seized Carniola, the estate that funded Marshal Ney's honor. **He will not forget it, Sire.**"*
> `p1 [nation_eliminated]` — *"Austria has been eliminated from the war."*
> `p1 [counter_punch_earned]` — *"Davout earned a free attack from their defensive victory."*

That Carniola sentence is better than anything in that turn's dispatch, which led with the flat
`region_lost` template *"Sire — Carniola has been taken by Austria."* and never mentioned that the
province was a marshal's duchy.

The valence split is visible on a single mechanic: the **loss** of the Counter-Punch is written into
Berthier's prose at the top of the screen (`[!] Davout's Counter-Punch opportunity has expired!`); the
**gaining** of it is a bare notification title. And the channel holding the good news is itself
saturated — **8 of 20 live notifications are `dotation_erosion` "grows bitter"**, one for every marshal
in the army, the same nag the dispatch is leading with.

**Cost.** The one screen the player reads every turn is architecturally a complaints department. It is
why the narration pillar keeps scoring 6 while the event generation scores 8: the events are good and
the editor only publishes bad news. A player who storms Vienna is told his men are hungry.

*(This is a design call, not a bug — the weighting is deliberate and commented. Routed to a gate.)*

---

#### **CA8-27 · P1 · Diplomacy**
**France offers territory in every wartime peace it proposes, winning or losing, because the "when losing" branch is reached by hostility alone.**

Two observations, two targets, ten turns apart.

Turn 5, against **Britain** — who had just offered France a free status-quo peace:
> terms: `Peace Treaty` + `Territory Flanders`
> commentary: *"Flanders is the very object of Britain's design. **Returning it costs us little** and buys their court's goodwill."*

Turn 15, with **Vienna taken and Austria eliminated**, against Russia — whose two marshals France had
just routed:
> preamble: *"I have prepared terms **appropriate to the current military situation**."*
> terms: `["Peace Treaty (end state of war)", "**France cedes Nivernais**"]`
> commentary: *"I've selected our least valuable border territory for cession. We lose little of strategic worth."*

Flanders (200g) and Nivernais (50g) are both in France's **boot income table** — homeland, not conquest.

**Code.** `backend/game_logic/diplomatic_templates.py:3381`, in `_build_base_terms`:
```python
elif war_score < -20 or relation < -50:
    # If losing or deeply hostile, offer gold to sweeten
    ...
    # R147: Offer territory cession when losing
    for region in non_capital[:max_cede]:
        terms["sweeteners"].append({"type": "territory_cede", ...})
```
The branch the comments twice call *"when losing"* is reached by **`relation < -50` alone**. Measured
live at turn 15: `France|Russia = -80`, `Britain|France = -90` — and per the IGR-X3 record every war in
this game boots at −80/−90. The France|Russia war score was **+2**.

⇒ **The `war_score` half of that condition can essentially never be the deciding term.** Being at war
*is* being deeply hostile, so every peace France proposes to an enemy offers territory.
`max_cede = 1 if war_score >= -40 else 2` then scales the giveaway, and stage 2's `smart_cession`
(`:3136`) re-ranks *which* province is surrendered — which is why the commentary sounds so confident
about a decision that should never have been reached.

**Cost.** This is the outgoing mirror of CA8-3 and it closes the trap from the other side. Twelve turns
of victory contribute nothing to the incoming leverage (CA8-3), and when the player gives up and
proposes terms himself, his own foreign minister drafts a partition of France and calls it appropriate
to the military situation. The fight→leverage→terms loop does not merely fail to connect — it runs
**backwards**.

*(One-condition fix, but it moves blessed acceptance arithmetic — gate it with CA8-D2.)*

---

#### **CA8-28 · P3 · Command**
**The same unknown province gets a helpful suggestion or a shrug depending on which movement verb the player used.**

Reproduced twice, fresh AP, same marshal, same turn, same non-existent province:
```
Murat, move to Venetia         -> Region 'Venetia' not found. Did you mean 'Vienna'?      [good]
Murat, go to Venetia           -> Region 'Venetia' not found. Did you mean 'Vienna'?      [good]
Murat, march to Venetia        -> I could not make out a destination in that order, Sire  [weak]
Murat, march south to Venetia  -> I could not make out a destination in that order, Sire  [weak]
```
`move`/`go` route to the 1-AP tactical move (*"Need 1"*); `march` routes to the 2-AP strategic order
(*"Need 2"*). The strategic path does not carry the tactical path's unknown-province resolution.

**Correction to the first pass:** I originally filed this as "`return to X` / `march south to X` fail
to parse". **That is wrong** — `Murat, return to Paris`, `go to Paris`, `return to Milan` and
`march south to Milan` all parse and execute. The phrasing is fine; only the *error quality* differs,
and only by verb.

---

### P2

---

#### **CA8-6 · P2 · Enemy phase** *(merges NEW-two-narrators, NEW-raw-action-verbs)*
**The enemy-phase dialog rebuilds every line from a stale key list, so it prints the debug token while the authored sentence sits unused one key away.**

`godot-client/project-sovereign/scripts/enemy_phase_dialog.gd:128-181` — I read it — matches
attack/move/forced_march/defend/fortify/unfortify/drill/stance_change/retreat/wait/recruit/scout/build/repair,
then `_: action_str += action_type.replace("_", " ")`. **Six AI-reachable verbs fall through**:
`grant_dotation`, `grant_pension`, `form_square`, `break_square`, `garrison`, `naval_expedition`.
Three are live-proven here — `transcript.jsonl` idx 50 renders `- Deroy grant dotation Bohemia`
(twice) and `- ArchdukeCharles grant pension`; idx 152 renders `- Castanos form square`. That is the
exact failure CLAUDE.md's Don't-Do list names.

Meanwhile the server *did* write, for that same action:
`By Imperial decree, Marshal Deroy is endowed with Bohemia and styled Duke of Bohemia. Its revenues
(0g/turn) now sustain his household, not the treasury.` — and the client discards it. Confirmed
losses: the AI-side reward economy is invisible; fortify shows no bonus and no personality clause;
retreat drops the substitution note, the recovery estimate and the orderly-withdrawal clause;
single-hop march attrition is dropped entirely.

**Narrowed from the first pass, and the narrowing matters:** the dialog is **not** bare. Battle name,
casualties, outcome, ARMY DESTROYED, region-captured with plunder/secure suffix, forced retreat, fort
degradation, the diorama link, bombardment, reinforcements, and Berthier's full labelled modifier
breakdown and observation **all render**. Combat is the least affected surface, not the most.

**Six other verbs named in the first pass are structurally unreachable** (`invest_vassal`,
`grant_region_to_vassal`, `change_autonomy`, `recruit_marshal`, `naval_diversion`, `build_fleet`) —
their `ai_action` dicts carry no `marshal`, and `main.py:1331-1344` suppresses marshal-less actions as
the fog-safe default.

**⚠ The fix is NOT to pipe `message` through.** Two verified hazards: `_filter_enemy_phase_by_visibility`
(`main.py:1334-1341`) gates on the marshal's **destination** while a raw move message names the origin
unconditionally — PT-D4 deliberately withholds origin below FULL intel; and the prose is
second-person player-addressed feedback reused for the AI (*"Sire"*, *"Use 'unfortify'"*), which is the
PC-9(a) defect class. Land per-action render arms sourced from **structured fields**, or an explicitly
enemy-voiced fog-checked narration key.

---

#### **CA8-7 · P2 · Enemy phase**
**`enemy_voice` has exactly one consumer in the entire client, so the campaign's only real antagonist is mute in the phase where his story happens.**

Charles's arc is unmistakable and the lines are written at the right moments:
> `— Archduke Charles: "France pays full price for every Austrian mile now."`
> `— Archduke Charles: "Your marshals are bold. Boldness is not a plan."`
> `— Archduke Charles: "I trade ground for time. Time is on my side."`

None appears in the enemy-phase narration. `battle_diorama.gd:1147` is the only `enemy_voice`
reference anywhere in `scripts/`; `enemy_phase_dialog.gd:328-362` `_format_berthier_report` renders
`modifier_breakdown` and `observation` and stops. `combat_executor.py:4833-4855` generates the line for
**both** directions — the enemy-phase case is produced and dropped. On the player's own battles it
surfaces fine: `[enemy_voice] Archduke John: "Noted. The next position will cost you double."`

**Cost.** The one AI character who behaves like a character across twelve turns never gets to be one on
screen. His taunts are the game's best-written enemy content and reach the player only if they open a
diorama or scroll a log.

---

#### **CA8-8 · P2 · Marshal drama** *(merges B5, voice-4, H1)*
**Every grievance is byte-identical to the last, nothing signals recurrence, and an inserted rung starved the one below it.**

> Turn 8, one dispatch, in this order:
> `[good] Murat's resentment of Davout has cooled with time.`
> `[warning] Berthier reports that Murat appears envious of Davout's laurels — he has grown restless for glory.`
> `[warning] The rivalry between Murat and Davout has become entrenched. The wound will not close on its own.`

The *state* is legal — `jealousy.py:1450-1453` expires the timer and emits the cooling line; step 3
(`:1460-1499`) re-evaluates every marshal with no `jealous_of`, including the one just cleared; the
escalation at `:593-607` fires because `_lifetime_fires >= 3` is now true *precisely because of the
fire two lines earlier*. There is no same-turn re-fire suppression. **The defect is that no template
carries a recurrence register** — nothing says "again", "has returned to", "a second time" — so a legal
escalation is indistinguishable from a state bug on the page. Two turns later it cools again, and *"will
not close on its own"* is falsified in front of the player.

Volume compounds it. `jealousy.py:520-524` holds **exactly three** expression strings keyed on
personality, so an aggressive marshal *always* says "grown restless for glory". Digest counts: *"appears
envious of"* ×9, *"has not seen laurels while"* ×6, *"cooled with time"* ×6, *"rivalries demand
attention"* ×7.

**And an inserted rung starved a better line.** `dispatch.py:1490-1505` (jealousy, rung "3.5") sits
above `:1507` (aggressive marshal idle 4+ turns) — and the function's own docstring at `:1461-1468`
still lists six rungs and never mentions 3.5. So Berthier closed 7 of 11 dispatches on *"The marshals'
rivalries demand attention, Sire"* and **never once** mentioned `<marshal> Murat @ Rhineland 19,312
status=idle_restless note=9 turns idle` — the Empire's cavalry standing unemployed for nine turns while
the army bled.

---

#### **CA8-9 · P2 · Marshal drama**
**The campaign told a complete tragedy in five beats and joined none of them.**

Rise: `- [glory_crowned] Ney (France) stands crowned with glory` (T3). Ennoblement: `By Imperial
decree, Marshal Ney is endowed with Carniola and styled Duke of Carniola.` (T8). Ruin: `[!] Ney's
troops are BROKEN (morale 21%)! FORCED RETREAT! Bohemia has been captured by Austria!` (T10).
Dispossession: `- [estate_confiscated] Austria confiscated Ney (France)'s estate at Carniola` (T10).
Fall (T12), a bare warning bullet wedged between a supply note and a congratulation:
`[warning] Ney is no longer the army's most celebrated commander — the laurels have passed.`
immediately followed by `[good] Berthier notes that Davout's recent victories have made him the most
celebrated commander in the army.`

**Not one of these five lines refers to any other.** The engine even knows the connection at battle
time: the Third Battle of Bohemia diorama payload carries `"name": "Ney" … "crowned": true` while
reporting him losing 2,218 men.

**Code.** `dispatch.py:547-601` builds arcs only from `defeats`, `retreats`, `attackers` — no glory,
estate or crown input, **so the arc machinery can narrate a marshal being beaten and never a marshal
rising**; and `dispatch.py:1150-1153` writes `status_note = arc_note` into a roster **table cell**,
never the headline or sub-beats.

---

#### **CA8-10 · P2 · Economy**
**The two screens that report France's income disagree by 124%, structurally — and the fastest-growing drain has its only explanation suppressed exactly when the player reads it.**

> Turn 1 treasury report: `Upkeep: -2524g` … `Over force limit (186,025 / 130,000): -1052g surcharge` … **`Projected net: +926g`**
> Turn 1 end-turn, same turn: `Income: 3400g | War Effort: -8g | Admiralty: -90g | Blockade: -175g | Upkeep: 2374g (incl. 204g over-limit, 738g Grande Armée) | Other: +1320g | **Net: +2073g**`

Different net, different upkeep, different surcharge, plus a Grande Armée line and an `Other: +1320g`
the report does not contain. `economy_executor.py:86-92` omits **`admiralty`** — which sits in the same
`income_data` dict and *is* subtracted by the real net — and omits blockade, trade and vassal tribute
entirely. War Effort then ran `-8g` → `-122g` → `-538g` → `-1,238g` with no explanation on any surface
the player saw: the explanatory line exists at `economy_executor.py:144-147` but is guarded by
`if war_effort > 0`, and on turn 1 — the only turn the player ran the report — it was 0.

**Cost.** A new player cannot answer *"how much money do I make."* This is the identical class of defect
to the `EC-W5b` infrastructure fix whose comment sits three lines above it.

---

#### **CA8-11 · P2 · Economy**
**Position 3.5's new affordance was refused at the place its own headline advertises it.**

> Three dispatches: `Sire — the establishment stands 26,519 men under the ordinance, and the depots hold 100,000. 10,000 foot cost 450 gold **at Paris**.`
> `recruit 10000 infantry at Paris` → `Berthier scans the dispatches. 'No marshal is available to receive reinforcements at Paris, Sire.'`

`find_nearest_marshal_to_region` (`world_state.py:4287-4327`) filters `distance > m.movement_range` — 1
for infantry. Every French marshal was in Germany or Italy. The refusal never names the reason and the
headline never says a marshal must be standing there.

**Cost.** The affordance built to give the treasury a use is unusable at the place it names, in the
state a Napoleonic campaign is normally in.

---

#### **CA8-12 · P2 · UX**
**The envoy digest re-prints the full text of every pending letter on every response — eleven identical ~60-word paragraphs in one turn.**

Turn 5, entries [39]–[49] each end with the byte-identical paragraph beginning
`Ottoman (secondary) open_borders/Open Borders Agreement :: Reis Efendi, serene and unhurried: "The
Sublime Porte has learned across many centuries…"` — attached to responses that have nothing to do with
diplomacy (`[47] plunder`, `[48] Ney, move to Bohemia`, `[49] Davout, fortify at Munich`).

`backend/game_logic/envoy_digest.py:175-221`, docstring at `:178-180`: *"Called from
``build_base_response`` so it rides every gameplay response."* The payload's `deadline_note` (`:215-219`)
and `title` (`:201-205`) — the parts that would tell a player what to do — appear in the transcript
**not at all**.

**Cost.** The first hour teaches the player that the block at the bottom of every response is noise.
That block is the only place minor-court diplomacy happens, and it carries a one-turn deadline he is
never shown. Corroborating: **17 `offer_lapsed` events across 9 turns**, and ~60 diplomatic points
generated against **one** spent.

---

#### **CA8-13 · P2 · UX**
**Liberating a French homeland province opens a mandatory prompt asking whether to burn it, and blocks the turn until answered.**

> Turn 1 treasury, France's own income list: `Rhineland: 150g`
> Turn 3: `Rhineland has been captured by France! … Plunder it for **600 gold** — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')`
> `end turn` → `You must decide how to handle the captured region first!`

IGR-E's own-soil guard was scoped to the AI branch; its landing record says the player modal was
untouched. The offer is also mispriced against the province the same session values at 150g/turn.

**Cost.** The prompt tells the player Rhineland is foreign, forty lines after the treasury told him it
is his. He cannot decline to have an opinion about sacking his own country.

---

#### **CA8-14 · P2 · Enemy AI** *(merges A4, ai-skips-state-guards)*
**A retreating AI marshal captures the province he just fled into, in the same phase, where the player would be refused by name.**

> `Deroy retreats from Hungary to Bohemia. No friendly ground lies open, Sire — Deroy falls back on Bohemia through hostile country. (44 lost to march) Army begins recovery (currently at -35% effectiveness)`
> `Deroy marches from Bohemia into Bohemia unopposed! (88 lost to march) Captured: Austria → Bavaria`

**Code, all read.** `enemy_ai.py:1448` PRIORITY -1 "CAPTURE CURRENT REGION" sits **above** the
`retreated_this_turn` limiter at `:1485` — and Deroy's 3rd and 4th actions that phase
(`stance_change → defensive`, `wait`) are that limiter's own signature returns, proving it was live and
P-1 jumped it. `executor.py:809-810` nests the player's retreat guard (`:946-954`,
*"is recovering from retreat and cannot attack"*) inside `if should_check_objection:` → `if marshal and
marshal.nation == world.player_nation:` — doubly unreachable for AI marshals.

**Two of three legs of the first-pass claim are refuted and the scope is narrower than filed:** the
drill lock **is** enforced nation-agnostically (`combat_executor.py:3071-3078`,
`movement_executor.py:136-142`), and the AI unfortifies first at every rung — the transcript shows the
honest two-step `'ArchdukeCharles: unfortify', 'ArchdukeCharles: attack → Bohemia'` with zero
counterexamples in 12 turns. P-1 also requires `not enemies_here` and garrison < 5,000, so the bypass
yields only an unopposed occupation of the tile the marshal already stands on. And the player-facing
half was never exercised: `grep -c "recovering from retreat" transcript.jsonl` = **0**.

**Cost.** A routed army at −35% effectiveness annexes the province it just fled into, one line after
the game said it was falling back through hostile country. It is the shape most likely to read as *"the
AI cheats"* — and it is the mechanical cause of the `marches from Bohemia into Bohemia` sentence.

---

#### **CA8-15 · P2 · Enemy phase**
**An empty nation header is printed, because the composition slice's own collapse pass can empty a nation without removing it.**

`campaign_digest.md:781` and `:965` both show a bare `[Prussia]` with nothing under it. Reproduced in
the payload: `transcript.jsonl` entries 50 and 60 carry `Prussia` with `actions: []`.

The fog filter is **innocent** — `main.py:1346` `if filtered_actions:` drops nations that filter to
empty (I read it). The offender runs after: `main.py:794-831` rewrites `nation_data["actions"] = kept`
with **no empty-nation prune**, and PC-3's fortify→unfortify arm drops *both* entries. Godot then prints
the header before touching the list: `enemy_phase_dialog.gd:75-89`.

**Cost.** A great power is announced by name in the enemy phase and says nothing, on a screen whose
entire job is to tell you what Europe did — and it is self-inflicted: PC-3 removed the lines without
removing the heading they lived under.

---

#### **CA8-16 · P2 · Voice**
**`hegemony_pressure` is a monoculture: eight courts deliver the same speech with the proper noun changed.**

> Portugal: *"A kingdom as modest as ours does not measure itself against the Empire's shadow… would far rather reach an understanding than be caught standing **in its path**."*
> Hesse: *"Hesse **has watched France grow** very great, and a court so small knows better than to stand **in the path** of such a power…"*
> Papal States: *"France has grown so vast that her shadow now falls even upon the altar…"*
> Ottoman: *"The Porte watches the star of France climb ever higher… would sooner arrange itself gracefully beneath so great a light than stand **across its path**."*

Reading the bank adds Hanover, Helvetia, Naples, Sardinia. **Three of eight literally begin "has
watched France grow"; five use "in its path"; `grep -c "in its path\|in the path"` on the digest = 14.**
`diplomatic_templates.py:606` selects `variants[(turn + len(nation_name)) % len(variants)]` — a
2-element rotation, so each court alternates between exactly two lines forever.

**Cost.** DEF-1's landing note says each line was adversarially verified against *"could this be
mistaken for another diplomat?"* — per court, in isolation. The player reads them **stacked, two per
turn, in one panel.** Strip the place names and no reader can sort them. The prose is genuinely good;
this is a selection and thematic-variance failure, not an authorship one — and a France-hegemon
campaign shows the player exactly the one motive on which every small court has the same thought.

---

#### **CA8-17 · P2 · Voice**
**Three named diplomats with three sharply authored registers get one identical sentence, and a raw scorer key is put in their mouths as speech.**

Quoted in full under CA8-3. Compare the Voice Bible's own authored rejections: Castlereagh — *"The
proposal is not of a character to merit reply."* Metternich — *"Austria regrets that the current
proposal does not align with our interests."*

`diplomatic_templates.py:2140-2143` `settlement_multi_court_court_holds_out` is a single
`{speaker}` / `{top_blocker}` template with no per-name override map. *"Settlement legitimacy is the
sticking point"* is not speech — it is a title-cased component key wearing quotation marks
(`display_names.py:962`), which the Bible's no-jargon rule forbids.

**Cost.** The resolver does the hard part — it correctly names Metternich, Castlereagh and Czartoryski
instead of an anonymous chancery — and then hands all three another man's sentence. The moment the
player finally gets three great powers at one table is the moment the cast collapses into one voice.

---

#### **CA8-18 · P2 · Diplomacy**
**The one gauge the player steers by is saturated *and* mislabelled, for twelve consecutive turns.**

> `<coalition> threat=97 tier=Brewing active=Third Coalition leader=Britain posture=cautious formed_turn=1` — on all 12 dispatches.

`get_threat_tier` (`coalition.py:1882-1891`) has **no Formed arm**, so a coalition that formed on turn 1
is permanently labelled "about to happen" while the payload itself carries `"coalition_brewing":
false`. Threat moved 97→91→97 across a campaign in which France conquered Tyrol, Carniola and Bohemia
and lost 44% of its army. This is also why position 3.5's new `military_establishment` threat term
(`coalition.py:729-762`, +1/+2 per turn on strength share) was **unmeasurable in play** — it fired into
a bar already at the ceiling.

---

#### **CA8-19 · P2 · Combat**
**Garrison assault is a separate, banner-free resolver.**

> `Ney assaults the Vienna garrison! Garrison: 25,000 -> 17,493 (-7,507). Ney loses 5,225 troops.`

`combat_executor.py:1930-1975` — no terrain, fort, personality or coordination lines, no muster, no
reinforcement. Four corps stood one province away and could not be brought. Vienna, which cost Ney
5,225 men against its 25,000 garrison on turn 9, later fell for 516 lead casualties because a field
marshal happened to be standing on it.

---

### P3

| id | claim | evidence / code | cost |
|---|---|---|---|
| **CA8-20** | The estate rung measures a province at its momentary book value, so on fresh conquest it **over-endows** | `Deroy … endowed with Bohemia … Its revenues (0g/turn) … the endowment falls short.` then the same for **Hungary**, one phase. `dotation.py:329-366` sorts by `get_effective_income()` with no `> 0` filter; `region.py:256-258` returns 0.0 at `stability <= 25`; satisfaction cannot move, so `enemy_ai.py:5385-5393` re-fires on the second admin AP | AI-side only: two provinces alienated to close one 80g gap, one admin AP wasted. **Player half already homed as XR-4** |
| **CA8-21** | Reward decrees have **no register at all** — one f-string, no actor branch | `economy_executor.py:1109-1114`; `acting_nation` is in scope at `:1099` and ignored. Bavaria (an electorate) issues an *Imperial* decree; Austria's court addresses Napoleon as *"Sire"*; Talleyrand's commerce aphorism editorialises inside Vienna's council | **Latent, not live** — the client does not render it (CA8-6). It goes live the instant CA8-6 is fixed the wrong way. Fix them together |
| **CA8-22** | The dispossession headline chose the map fact over the human one | T10 notification (HIGH, 71 payload occurrences): `"Austria has seized Carniola, the estate that funded Marshal Ney's honor. He will not forget it, Sire."` T11 dispatch led with `HEADLINE [region_lost w75]: Sire — Carniola has been taken by Austria.` `dispatch.py:264-273` + `:173` read only `region`/`captor` | The better sentence was generated on the same turn and routed to the notification bar |
| **CA8-23** | Raw internal key on the most consequential diplomatic event | `An envoy from Austria has arrived with an **armistice losing** proposal`; dies as `Austria's **armistice losing** offer lapsed unanswered`. `campaign_log.py:2185` does `.replace("_"," ")` instead of `PROPOSAL_TYPE_DISPLAY`, which maps it at `display_names.py:265` | Forbidden by the project's own Don't-Do list |
| **CA8-24** | The war room contradicts itself on one screen | `the war hangs in the balance (+0) — **0 battles across 0 turns**` printed above `What stirred Europe this turn: **Won a decisive battle (+5); Won a battle (+3)**` | Same pairwise-vs-aggregate root cause as CA8-3 |
| **CA8-25** | No diorama on two reachable battles | The `press on` interrupt resolution (idx 4) — the campaign's largest battle, 82,072 massed — carries `"events": []` and no `battle_diorama` key; the Vienna garrison assault (idx 70) emits only a bare `garrison_assault` event | *Correction to F3: the player's normal attack path **does** build dioramas — idx 29, 79, 136* |

---

## 5. Corrections — claims the refuters killed or narrowed

The project's convention is that a first-pass claim that did not survive is corrected in place.

| Candidate | Verdict | Why |
|---|---|---|
| **A1** "marches from X into X" | **Killed as duplicate** | Already open and homed at `BUG_FIXES.md:826` as **XR-3** (P4, July 11), whose own text already states both halves: *"an in-place capture should neither narrate a march nor charge march attrition."* The P4→P2 escalation is unsupported — the string never reaches the shipped client, the toll is symmetric (GR5), and it changed no outcome in 12 turns. **New and worth appending to XR-3:** the cause (`enemy_ai.py:1448` self-targeting, never diagnosed) and the frequency asymmetry (the AI reaches it after every post-battle advance). Process note: IGR-X5/X6/X8 were capture-touching slices and passed without discharging XR-3 |
| **A2** French register in enemy decrees | **Killed as filed; re-filed as CA8-21** | The seam is misidentified and the population is 243, not 2 — `grep -rc "Sire" backend/commands/*.py` = 243, because `message` **is** the acting player's response text by contract. Two lines above the cited evidence, same phase: `Deroy retreats from Hungary to Bohemia. No friendly ground lies open, **Sire**…` — Bavaria's marshal calling the French player Sire, from `movement_executor.py:1025`, a file the finding never mentions. Also: `"By Imperial decree"` is *correct* for Austria, whose sovereign in 1805 is an Emperor |
| **A6** `[HINT]` register break | **Killed** | The uniqueness premise is false. Its Session-31 sibling `[WARNING] Morale dropped to {n}% — consider drilling before battle.` (`economy_executor.py:611`) has the identical shape, and its `[DANGER]` variant appeared **on the same screen in this campaign** (`campaign_digest.md:1469`). `[!]` appears ~14 times and `[Materiel]` on nearly every battle line. Acting on the finding as filed would re-voice one line and leave three siblings, making the screen *less* consistent |
| **B7** Counter-Punch never announced | **Refuted** | It **is** announced — `combat_executor.py:1451-1466` creates a `COUNTER_PUNCH_EARNED` notification at HIGH priority, and the payload carries `"title": "Davout — free attack!" … "turn_created": 2`. The digest renders no notifications at all, for any type, in twelve turns. **Residual, real and smaller:** the grant arrives in the notification bar and the expiry in the dispatch — a channel-consistency defect |
| **C3** "nothing narrated the dispossession" | **Partly refuted → CA8-22** | A HIGH-priority notification narrated it with a strong line. The defect is that the *next* dispatch chose the territorial fact |
| **D3** unmarked Flanders cession | **Half wrong** | The payload carries `"annotated_terms": [{"term_direction": "concession", "display_label": "France cedes Flanders to Britain"}]` and Talleyrand names the reason. The real defect is the *journey* — "Review" on a free peace, four clicks, now you are ceding a homeland province — with no screen saying *their offer failed; this is now yours* |
| **D4** Saxony labelled three ways | **Overstates** | `friendly_gift` as the rule label while `terms["type"]` maps to the legal treaty is a documented W6-10 decision (`ai_diplomacy.py:802-813`). Only the campaign log leaks the rule name — the same `.replace("_"," ")` bug as CA8-23 |
| **E3** levy re-opened because the army starved | **Needs correction** | The framing is half true. Boot absorption held its blessed anchor **exactly**: 2,630 / (3,400+350+937+50) = **55.5%**, dead on the EC-U3 record. What failed is that by turn 13 it was **16.6%** — the anchor is purely a function of army size, and the army halved for reasons the player never chose |
| **F1** extreme exchange ratios | **Confirmed, overstated** | 3–15× less extreme than filed; the candidate quoted lead-only terminal figures. See CA8-1 |
| **F4** two figures for one army | **Refuted** | `24,000` and `82,072` are both stated with their meanings on the same screen, and `delegation.py:337-342` records the solo framing as a deliberate PC-8 decision. The real defect is smaller and is CA8-4: the note names the French figure twice and never names Mack's |
| **NEW-standing-cooldown-region-key** | **Killed** | Identity scoping is a **blessed pin** (`test_pc2_pc7_enemy_phase_and_headline.py`, *"Identity, not just class"*), and `BUG_FIXES.md:44` already records PC-7's measured post-fix state as *"longest identical-CLASS run 7 → 4"* — the play pass measured 4. The four leads are not one sentence (different province, marshal set, figures, remedy). Class-keying would hand the top line back to the weight-55 household nag PC-7 was built to demote |
| **NEW-defensive-muster-silence** | **Refuted** | `reinforcement_messages` **is** attacker-only, but two other channels carry the same content on defence and both render: `battle_report.py:629-631` selects `reinforcement_data["attacker" if we_are_attacker else "defender"]` — nine defender-reinforced battles here, all naming both halves (*"Ney stood alone, Sire. Soult and Bernadotte never came."*), rendered by `enemy_phase_dialog.gd:212` → `:357-359`; and the defensive diorama carries per-corps committed/casualties/status incl. `"refused"` with `absence_reason`. The digest's silence is a **harness artifact** |
| **NEW-silent-defensive-trust-dock** | **Refuted** | Both docked marshals were named on screen in the observation. Exactly **two** French docked no-shows in 12 turns (Davout, Murat, both turn 2), both disclosed |
| **NEW-fog-summary-misplaces-the-army** | **Killed** | The code fact is true but the harm mechanism is impossible: the same PARTIAL rule that suppresses the action **also** puts the enemy in `intel.known_marshals`, and the very next screen names him — `{"name": "Castanos", "location": "Artois", "strength_display": "small force", "visibility": "partial"}`, repeated T5/T10/T11/T12. And `grep -c "fog_hidden_summary" transcript.jsonl` = **0**: it never fired |

**Two findings survived but were materially narrowed** — CA8-6 (twelve verbs → six; the dialog is
*not* bare) and CA8-14 (three legs → one). Both narrowings are recorded in the finding bodies above.

---

## 6. What is working

Be as specific about the good as about the bad.

**The composition slice landed exactly what it promised, and all six rows are verifiable in this
transcript.** PT-D4: `Deroy drives a forced march — Franconia → Tyrol → Franconia → Swabia (3 stages,
103 lost on the march)` — one line where three used to be. PC-2/PC-3: **zero** verbatim duplicate
`wait` lines and **zero** fortify-then-unfortify pairs across twelve phases. PC-4: names are unique and
escalate — `Second` → `Third` → `Fourth` → `Fifth` → `The Great Sixth` → `The Great Seventh` →
`Eighth` → `Ninth Battle of Bohemia`. PC-5: the solitude claim is gated correctly —
`[observation] Murat stood alone, Sire. Soult never came.` against, when help arrived,
`Davout and Lannes arrived to reinforce Massena, but Soult failed to reach the field in time.` PC-6:
`Kutuzov flanks from Hungary while allies attack from Vienna! (+1 coordination)`.

**Turn 1 is a character piece and every line of it is mechanical.** One order produced four different
men behaving four different ways — Davout arriving, Soult holding to the letter, Bernadotte *"weighed
its own ambitions"* (his authored MC-1 Eyes-on-a-Crown ability, unprompted, in the opening move) — plus
the warrant (`Ney acted on your word: "Marshal Ney, take your corps and deal with Mack at Swabia"`), the
loser's voice, and the consequence seeded forward (`Victory raises Marshal Ney's expectation of
reward`). **This is the model the rest of the campaign should be measured against.**

**The muster preview remains the best surface in the game.**
`WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Murat' and he
will march.` A gate that states the exact command that opens it.

**Combat inputs are excellent.** Every modifier is named, in character, at the moment it applies —
`[Shield] Davout's methodical defense is exemplary! (Cautious: +20% total) Outnumbered bonus: +10%` —
and the repeated-attack rule teaches itself as it bites: `(2nd attack: -10%)`, `(3rd: -20%)`, `(4th:
-30%)` across Charles's four assaults.

**The per-court acceptance review is the best thing in the game's diplomacy** — eleven named signed
components per court, each with a named foreign minister, and Britain refusing *harder than the
arithmetic* because a status-quo peace advances nothing of `low_countries` (`agenda_settlement_mod: -8`,
"National design"). That is NA-2 coupling working live.

**The agenda layer is alive.** Talleyrand, turn 1: *"Britain's design: The Low Countries — They will not
suffer France's bloc in Flanders. Their price: prepared to go as far as war (weight 84)."* Two
**emergent** designs fired unprompted with correct blame — `REVANCHE: Austria swears to retake Bohemia
and 3 more — Bavaria is not forgiven`, and Spain's against Britain on turn 13.

**Turn 12's enemy phase is a genuine chapter of a war.** Vienna falls — to *Bavaria*, not France —
Archduke John is broken twice in one phase and driven out of his own capital, while Charles scrapes a
fifth of the national manpower pool into a corps that will break on contact: `recruits 10,000 infantry
at Vienna - Cost: 382 gold (capital discount) (ArchdukeCharles's intendance: -15%). Morale: 5% -> 15%`
… `[DANGER] Morale critically low at 15%`. Nobody wrote that; the systems did.

**Consequences persist and compound.** Turn 5: *"Massena's troops plunder Tyrol! Gained 600 gold.
Buildings destroyed. Stability set to 10."* Turn 13 ledger: `{"region": "Tyrol", "income": 63}` — a
150-base city yielding 63. The 600g pays back in ~7 turns and then goes negative forever. And it was
the same Tyrol the army starved in for eight turns. **The simulation joined those two facts. The
narration never did.**

**The economy model reconciles to the digit** and its prices are live: base 200 → capital ×0.75 → war
×3 = **450 at Paris**; in the field 200×3 = **600 for a third of the men**, capped at 3,000. The AI
demonstrated the entire ladder unprompted.

---

## 7. Routing

Per CLAUDE.md **Golden Rule 9**: nothing below is deferred without a named owner.

### → `docs/BUG_FIXES.md` (new §Creative-Audit 2026-08-04)

| id | P | one line |
|---|---|---|
| CA8-1 | P1 | Mirror the two attacker-only mass/ally-casualty lines onto the defender; make terminal casualties the whole-army figure the log already prints |
| CA8-2 | P1 | supply_strain: current-turn recency predicate; live-occupancy names; drop the `"more"` fallback; state the capacity |
| CA8-4 | P1 | Bad-odds interrupt: use the MUSTER format; name the enemy's strength; three options, not two |
| CA8-5 | P1 | Dedupe sub-beats on `(class, identity)` at `dispatch.py:498`; route the ordinary break to `own_broken` |
| CA8-6 | P2 | Per-action render arms from **structured fields** for the six fall-through verbs (**not** by piping `message` — see the two hazards) |
| CA8-7 | P2 | `enemy_voice` render arm in `_format_berthier_report` |
| CA8-8 | P2 | Recurrence register in the jealousy templates; expression variant banks; fix the undocumented rung 3.5 starving the idle rung |
| CA8-10 | P2 | `_execute_economy` net must include admiralty/blockade/trade/tribute; un-guard the War Effort explanation |
| CA8-11 | P2 | Name the reason in the recruit refusal; the levy headline must state the marshal requirement |
| CA8-12 | P2 | Envoy digest: emit once per turn, surface `title` + `deadline_note` |
| CA8-13 | P2 | Own-soil guard on the **player** capture modal (IGR-E scoped it to the AI branch) |
| CA8-14 | P2 | Move P-1 below the `retreated_this_turn` limiter in `enemy_ai.py` |
| CA8-15 | P2 | Prune emptied nations in the `main.py:794-831` collapse (and route them to the fog line) |
| CA8-17 | P2 | Per-name override map for `settlement_multi_court_court_holds_out`; blocker phrased as speech |
| CA8-18 | P2 | `get_threat_tier` needs a **Formed** arm |
| CA8-19 | P2 | Garrison assault: banner/muster parity with field combat |
| CA8-27 | P1 | `_build_base_terms:3381` — split the `or` so a cession requires a losing WAR SCORE, not merely hostile relations (gate CA8-D2) |
| CA8-28 | P3 | Give the strategic movement path the tactical path's unknown-province resolution |
| CA8-21 | P3 | Actor-branch the decree strings — **land with CA8-6, never after it** |
| CA8-22 | P3 | `region_lost` needs an estate-holder branch |
| CA8-23 | P3 | `campaign_log.py:2185` → `PROPOSAL_TYPE_DISPLAY` |
| CA8-24 | P3 | War-room battle counter reads the same source as the "what stirred Europe" block |
| CA8-25 | P3 | Diorama on the interrupt-resolved battle and the garrison assault |

**Append to existing rows, do not re-file:** **XR-3** — add the cause (`enemy_ai.py:1448`
self-targeting) and the frequency asymmetry; note its stated landing trigger already lapsed once at
IGR-X5/X6/X8. **XR-4** — the player-facing 0g estate copy is unchanged and still open.

### → `docs/DESIGN_REFINEMENT.md` (need a gate, do not build in an audit)

| id | owner row | question |
|---|---|---|
| **CA8-D1** the conquest-free gold sink is **13 building slots** for the whole game (`region.py:107-113` × France's 1 capital / 4 major_city / 7 city; `BUILDING_TYPES` tops out at 400g) → lifetime sink 3,250–5,200g, **under two turns of net income** | **row EC-P3** (existing econ backlog owner) | What does gold buy after turn 6? Landing slice must define completion; the plunder prompt quoting a flat 600g for every 150-income city is downstream of this, not a separate row |
| **CA8-D2** settlement leverage should aggregate, not read a pair — `compute_side_pressure_score` *already knew* Austria was 43 while the war-status row and offer producer read the raw France↔Britain 0 | **Pre-EA Victory & Objectives Pass** (existing open gate — war score → terms → ending is exactly its business) | Should the counterparty's leverage key to the war the player is actually fighting? Blessed-number consequences on acceptance and offer generation |
| **CA8-D3** the rival is not a person — `find_jealousy_target` (`jealousy.py:268`) recomputes from the rolling 8-turn window with no bias from `jealousy_history`; one petition per pair per campaign, ever (`jealousy.py:558-563`) | **new row, next marshal-content gate** | Should a marshal's grievance object have permanence, and should a petition re-fire when escalation level rises? |
| **CA8-D6** the dispatch has **no headline class for a French success** — 15 classes / 17 `_add()` sites, every one a wound, an opportunity ranked below every wound by comment, or another power's business; 14 of 14 headlines this campaign were misfortunes; the good news exists but only in a notification bar where 8 of 20 entries are the same "grows bitter" nag (CA8-26) | **new row, next narration gate** — pairs with the Aug-3 enemy-phase-as-theater dissent | Should the briefing be able to lead with a victory, and at what weight against a wound? The decision to revisit is the comment at `dispatch.py:71-73`: *"an opportunity never outranks a wound"* |
| **CA8-D4** `hegemony_pressure` monoculture — thematic variance, not authorship | **DEF-1 Roster Voices** (CLAUDE.md: *"owns the loose voice/copy backlog"*) | Does the enemy phase get its own voice register, or does it stay structured-field rendering? Pairs with CA8-6/CA8-21 |
| **CA8-D5** the threat bar is saturated at 91–97 all campaign, so position 3.5's `military_establishment` term was **unmeasurable in play** | **row EC-P3**, with CA8-18 as its prerequisite | Does anything new need to be measurable on a bar that boots near its ceiling? |

**Not deferred, closed here:** CA8-20's player half is XR-4; its AI half belongs beside IGR-X4/IGR-X9 at
**EC-P3**'s next econ tuning gate and needs no new row.

---

## 8. The single highest-leverage recommendation

### Report the defending army as an army.

Three edits, all in code already written:

1. Mirror `combat_executor.py:5539` (`Massed effective strength: N (lead) + M committed (…) = T`) and
   `:5552` (`His supporting allies lost N combined`) onto the **defender**, in the enemy phase.
2. Make the terminal's `Casualties:` figure the same whole-army figure `campaign_log.py` already prints.
3. Then, and only then, ask whether the ratios need a balance pass.

**Why this and not something else.** It is the only finding in this memo that is simultaneously four
different kinds of defect, and fixing it discharges all four at once:

- **A correctness defect.** Two shipped surfaces report French casualties for the same battle and
  disagree by up to 15× (`Ney 13` vs `197`). A player who notices that stops trusting every number in
  the game, including the true ones.
- **A legibility defect.** Committed mass is the variable that decided *every* battle in this campaign —
  `combat.py:1098` puts the whole stack in the defensive ratio — and it is printed only for the
  attacker. The player was told `+25% mountains` and shown a 567:1 exchange. He cannot learn the
  system from the system.
- **A balance-visibility defect.** France lost **one** engagement in twelve turns. Massing is a dominant
  strategy the player cannot see, so he cannot choose it, cannot choose against it, and cannot be
  proud of it.
- **The missing joint between the campaign's two biggest stories.** The game already models both halves:
  massing wins battles, and massing starves armies. It never puts them in one sentence. Once the
  defence names its massed strength, the dispatch's own line —
  *"Davout, Lannes, Massena, Ney and Soult stand 42,982 men over what Tyrol can feed. 9,410 men lost in
  2 turns"* — stops reading as unrelated nagging and starts reading as **the price of the wall.**

**No balance retune is required to land it, and it is the prerequisite for judging whether one is
needed at all.** Everything else on the P1 list is a sentence; this is the sentence the game has been
refusing to say.

**Runner-up, and I want the ranking argued rather than assumed:** CA8-3 (leverage keyed to a pair that
never fought) is a *bigger* strategic hole — the fight→leverage→terms loop is the game's spine and it
did not connect in seventeen turns. I rank it second only because its fix is a routing change with
blessed-number consequences on acceptance and offer generation, which under GR9 needs the gate named in
§7 (CA8-D2). CA8-1 needs no gate, no new state, and no new copy — it needs the same two sentences the
attacker already gets.

**Cheapest meaningful win, if only one afternoon is available:** dedupe sub-beats on `(class, identity)`
at `dispatch.py:498` and drop the `"more"` fallback at `:749`. Two lines, and the briefing stops
stuttering on the turn the campaign turns.

---

## 9. Method notes

- Live campaign: 12 played turns (world advanced to 13; a diplomacy probe ran to 17),
  `LLM_MODE=anthropic`, real key, `seed=historical`, default `europe_1805.json` boot, backend
  `-m backend.main` on 8005.
- **The digest is built from enemy-action `message` strings by an out-of-client harness.** The shipped
  client does not read that field. Enemy-phase copy claims must be checked against
  `enemy_phase_dialog.gd`'s `_format_action` key list. This invalidated three candidate findings and
  narrowed two more.
- All code references in §4 were opened and read at `e450b02`. Where a refutation pass corrected a
  first-pass claim, the correction is carried in the finding body, not just in §5.
- CA8-26, CA8-27 and CA8-28 were found and code-verified by the play pass itself after the
  review fleet had launched, so they carry no refuter; each states its own evidence and its
  own correction where the first reading was wrong.
- **No repository file was modified and no fix was applied.** Everything above is routed, per §7.

---

## 10. THE CLOSE-OUT GATE RECORD — August 7, 2026 (user-delegated; AUTHORITATIVE)

> Sweeps 1–4 (Aug 4) closed every gate-free row: 20 of 28 fixed, 1 refuted. The user then
> directed *"make design gate decisions and finish CA sweep"* — the four standing gates are
> HELD here under that delegation. This section is the ruling of record; the landing records
> ride `BUG_FIXES.md` §Creative Audit rows as usual.

### 10.1 CA8-D2 — leverage keys to the WAR, and a cession requires LOSING (CA8-3 · CA8-24 · CA8-27)

**Both gate questions answered YES.**

1. **One new single source, `diplomacy.calculate_side_war_score(nation, opponents, world)`** —
   the five pair components (territory / battles / decisive / capital / ticking) summed across
   the war's whole opposing side, each component re-clamped at its own pair cap, total ±100.
   For a single opponent it reduces **byte-identically** to `calculate_war_score` (pinned).
   **The consumer rule (recorded after the first suite run caught the distinction): each
   consumer keeps its pre-gate SOURCE and gains war-level breadth.** The DISPLAY surface
   (war_status, whose own blessed rule is "always live-calculate, not cached war_scores")
   aggregates the live components via `calculate_side_war_score`. The SCORE-CONSUMING seams
   (offer direction, Talleyrand's drafted terms) have always read the STORED
   `world.war_scores`; they now read `sum_stored_side_score` — the oriented stored pair
   scores summed over the opposing side, clamped ±100 — and a BILATERAL war keeps the plain
   stored pair read byte-identically (five `test_settlement_incoming_offers` pins caught
   exactly the drift a source swap would have caused). Encoded in `get_side_war_score_for`
   and the offer producer's arity branch.
2. **Three consumers, and only these three:**
   - the multi-participant HUD collapse row (`war_status._collapse_multi_participant_wars`) —
     `war_score`, `breakdown`, `battles_fought`, `decisive_won`, `recent_battles`, `duration`
     and `trend` now read the war, not the leader pair. The war room stops contradicting
     itself on one screen (CA8-24), with **no `.gd` change** — same keys, honest values.
   - the incoming settlement-offer producer (`ai_diplomacy._emit_settlement_offer_for_war`) —
     offer DIRECTION and the EC-W4 amount read the war the player is actually fighting.
     Twelve turns of victory against Austria now press on Britain's table (CA8-3).
   - `diplomatic_templates._build_base_terms` — Talleyrand prices the war France is in, not
     the leader pair.
3. **CA8-27: the `or` is split.** Territory cession (R147) now requires `war_score < -20`
   STRICTLY — actually losing. The `relation < -50` arm keeps only the ≤200g gold sweetener
   (a hostile court may be sweetened; it is never paid in homeland provinces). The manpower
   (−30) and AP (−50) sweeteners were already score-gated tighter and are unchanged.

**Scope boundary (deliberate):** the settlement acceptance scorer's §6.3 side-pressure
machinery is UNTOUCHED (it is already war-level — the audit's `direct_score: 43` proves it),
and the Stage-D third-party AI peace seams (`effective_peace_threshold`,
`settlement_third_party`) keep pair semantics — those wars are pair instances by
construction and their pins are Stage-D blessed.

### 10.2 CA8-D6 — the briefing MAY lead with a victory (CA8-26)

**Ruled YES.** Four success classes enter `HEADLINE_WEIGHTS`, derived entirely from events
that already exist (no new campaign-log type — the 156 pins hold):

| class | weight | derived from |
|---|---|---|
| `enemy_eliminated` | **93** | the existing `nation_eliminated` event, when the fallen court was at war with France |
| `capital_stormed` | **92** | `region_captured` by France where the region is the previous controller's capital |
| `victory_won` | **73** | a `battle` event France won that was decisive/great or destroyed the enemy corps |
| `region_taken` | **68** | `region_captured` by France (non-capital) |

**The weight principle that replaces the retired comment:** *at equal scale the wound still
leads — a triumph outranks only a wound of smaller scale than itself.* Concretely:
elimination (93) and a stormed capital (92) outrank a broken corps (90) — Vienna is bigger
news than one corps reforming; a decisive field victory (73) outranks the standing hunger
nag (`supply_strain` 72) on the day it is won but NOT a lost province (75); a routine
conquest (68) sits below every direct wound to France's own body and above Europe's
business. The `:71-73` comment ("an opportunity never outranks a wound") is retired to
"…a TRIUMPH may — at larger scale than the wound." `capital_stormed` absorbs the
`region_taken` candidate for the same province; `enemy_eliminated` and `capital_stormed`
may both lead the same turn's dispatch as headline + sub-beat (distinct facts, both true).

### 10.3 CA8-17 — Voice Bible §16.1a AMENDED; the reduced build ships

**The Bible amendment is granted.** §16.1a's leaning/holds-out exemplars stop being
verbatim-committed: the `{top_blocker}` slot is retired from those two templates in favor of
a **spoken-register vocabulary** — the **NINE** negative-capable acceptance components each
get a SPOKEN clause (`SPOKEN_BLOCKER_PHRASES`; the audit row said 8 — §10.6's review proved
`war_objective_alignment` negative-capable too), and the two bands get per-register framings on the
LIVE override idiom (`settlement_multi_court_court_{leaning|holds_out}_{castlereagh|
hardenberg|metternich|einsiedel}` with the `_chancery` fallback re-lookup — exactly the
ally-petition pattern at `settlement_offers.py:430-458`, so DEF-1 can add named voices later
by adding rows, never by restructuring). ~20 authored strings, two files, no `.gd`.
The per-court table LABELS keep the `display_names` vocabulary — labels belong in tables;
the phrases belong in mouths. Talleyrand's own headings reuse the same phrase map (the
"spoken three times on one screen" repeat dies with no new strings). Named-envoy PER-DIPLOMAT
registers beyond the four already-cast suffixes stay **DEF-1's scope** — this build adds
zero per-court banks.

### 10.4 CA8-D4 — what `hegemony_pressure` may sound like besides fear (CA8-16 bounded)

**The gate question is answered: three frames.** (1) **ARITHMETIC/INTEREST** — France's
power as a fact to be priced, not dreaded (the Castlereagh model the row named); (2)
**OPPORTUNITY** — proximity to the hegemon as profit (Montgelas and Marescalchi already
lean here); (3) **HISTORY/LAW** — precedent, the balance, the long view (Rome, the Porte,
Czartoryski's design). **Bounded build under this ruling:** every one of the 24
`hegemony_pressure` banks gains a THIRD variant authored in whichever non-fear frame fits
that speaker's Voice-Bible register — 24 lines, cutting the measured exact-repeat rate for
the register mechanically by a third and breaking the "France is big" monoculture with
every third composition. The single `len == 2` pin (`test_w6_incoming_voice.py:118`) is
consciously flipped to `>= 3`. **Full roster authoring across the OTHER four reasons stays
DEF-1's** — this touches one reason's banks only.

### 10.5 CA8-19 — the parity gate: garrison assault stays its own resolver, BY DESIGN

**Full parity is REJECTED as design, not deferred as work.** An escalade against a static
garrison is not a field battle: there is no opposing commander to out-general, no morale to
break (the 5,000-collapse threshold IS the garrison's morale model), no maneuver to flank.
The things full parity would import — variance, personality, additive terrain — are a
balance-moving combat build that would re-record M1–M7 AND `BASELINE_SERIES` (enemy P4.25
takes this path every campaign), require a defender object that does not exist, and consume
`compose_battle_name` ordinals whose contract excludes garrison assaults (PC-4). The rule
is now stated at the resolver head. If a future combat gate wants garrison texture, it
starts from this record — nothing is left implicitly promised.

**The defeat-side glory divergence is CANONIZED, not wired.** A marshal repulsed from a
garrison reads glory 0, not the spec's −1 — ruled CORRECT: the glory ladder prices
reputation between COMMANDERS, and an escalade has no opposing commander to lose face
against; the repulse's cost is paid in men and materiel (both already charged). One-line
exemption added to `JEALOUSY_SPEC.md` §1's DEFEATS block beside the existing "Garrison
defense" exemption; the existing pin stands. Step 9.5 stays gated — `jealous_of` is not
mutated from a new site for a rung the design rejects.

**The garrison half of CA8-25 (no diorama on a garrison assault) is HOMED at the Battle
Gallery gate** (`BATTLE_DIORAMA_SPEC.md` eval-§6 OUT list): the tableau must first learn a
defender-without-a-marshal (garrison contingent: piece + coat, no locket, no standard-take)
— that is gallery-gate business with a visual sign-off, not a close-out patch. Completion
definition: a stormed garrison renders a tableau whose defending contingent is the garrison
itself; behavior test named at that gate.

### 10.6 THE ASSURANCE ROUND — the 4-lens review fleet and what it took (August 7, 2026)

The user's third clause was *"assure Ca fixes are good"*: after commit `f5acc4e` a
four-agent adversarial fleet (D2-seams · dispatch-arms · voice · mutation-hunter, each
instructed to refute its own findings) reviewed the committed diff. **Sixteen findings
survived their own refutation; ALL are fixed in the follow-up commit, and four of them
were corrections to this record's own claims.** The keepers:

- **[B-F1, HIGH] `enemy_eliminated` was production-unreachable as first built** — the
  arm read `side_by_nation`, but `_eliminate_nation` runs
  `mark_participant_eliminated_in_all_wars` (which POPS the fallen court from that map)
  **before** logging the event. The NA-3 trap, reproduced: the commit's own positive
  test manufactured the pre-pop state by hand. Fixed: the arm reads the durable
  `participant_meta[nation]["side"]` witness with `side_by_nation` as first read, and
  both elimination tests now drive the REAL `_eliminate_nation` path and assert the
  strip happened.
- **[B-F2, MED] the tactical-victory join was dead for the standard assault geometry** —
  battle events name the DEFENDER's region while a routed attacker's retreat event
  stamps his ORIGIN (`from`), so a location join could never compose France's defensive
  victories. Fixed: **the join is by the MAN** — the battle's losing marshal against
  the routed marshal's name — with a new geometry test pinning the repulse shape.
- **[A-F1/A-F2, P2] the suggested-terms pipeline defeated CA8-27 one stage above the
  fixed seam and priced with a split brain** — stage 2a injected a COVETED-province
  cession at pair `war_score < 0`, and stages 2a/2b/2e/3/4 read the pair while stage 1
  read the war (probe-confirmed: one multi-party draft demanded Tyrol and ceded Milan).
  Fixed: ONE war-level score for the whole pipeline; the 2a cession arm obeys `< -20`.
- **[A-F3, P2] two score-derived keys on the collapsed row still told the leader-pair
  story** — `settlement_tier` ("White Peace" beside +50) and `started_turn` (self-
  contradicting beside the oldest-front duration). Fixed and pinned.
- **[A-F4, P3] the request-terms refusal read the leader pair beside the converted
  producer** (two AI mouths disagreeing about one war) — converted with the same
  arity discipline.
- **[A-F5, P3] armistice-suspended members** stayed in `side_by_nation` and inflated
  the live display aggregate by whole belligerents while every stored seam read them 0
  — the collapse now aggregates over the SAME belligerent set as the rows it collapses.
- **[C-F1, MED] the vocabulary's "8 negative-capable components" was FALSE — it is
  NINE**: `war_objective_alignment` clamps to −20/−15, and the close-out test had
  hardcoded the 8-set, enshrining the gap (§10.3's count is corrected in place).
  `SPOKEN_BLOCKER_PHRASES` gains the ninth phrase.
- **[C-F2, MED] the degrade path rendered fragments** ("will not sign while Settlement
  legitimacy") — the `{blocker_clause}` slot demands a clause, so the label fallback is
  now wrapped ("… stands against it") and the cast-court degrade shapes are pinned
  (the first test covered only the one em-dash shape where a noun phrase scans).
- **[D-Probe G, P1] the CA8-17 producer→consumer join was UNPINNED** — stamping
  `top_blocker_component: None` at the one production site killed the whole feature
  with all 47 tests green (synthetic rows + a one-level-below unit test). Now pinned
  through the real `compute_per_court_acceptance` with the scorer patched at the
  stable seam. Five further unpinned claims from the mutation sweep (trend, score
  wiring, both ±100 clamps, the EC-W4 amount, bank pairwise-distinctness) are now
  pins; the 8 prescribed mutations were all killed on the first run.
- **Writing fixes** (voice lens): "settled sea-lanes" → "quiet seas" (the coinage is
  mid-19th-c.), "an asset to the crown" → "among {nation}'s surest holdings",
  Ehrenheim's "waters France now commands" → "ports France now closes" (the shipped
  naval model says the opposite), "treaties current" → "treaties in good repair".

**Rulings recorded, not fixed (each a conscious decision):** [B-F4] a French VASSAL's
conquest fires no success headline while a vassal's loss fires `region_lost` — ruled
CORRECT: the dispatch's triumphs are France's OWN arms; its wounds include the
protectorate's (the asymmetry is the protector's, and it is deliberate). [B-note] an
auto-bombardment annihilation logs no battle event (pre-existing seam), so it yields
`region_taken` rather than `victory_won` — accepted; the conquest is still told.
[A-refuted] the collapse costs ~38µs per multi-war row on the boot world — GR8-clean.

**Two pre-existing pins consciously re-blessed by the [A-F1] pipeline fix** (both sat
on the OLD stage-2a behavior the gate forbids — a cession authored at a mild loss):
`test_bugfix_proposal_flow.py::test_coveted_territory_injected_without_base_territory`
(fixture −10 → −25; its own docstring called −10 "mild loss", the exact state the
rule now refuses to cede in) and `test_nation_agendas.py::TestPreviewPositiveRow`'s
armistice fixture (−10 → −25; the NA-3 rider-(b) CONTRACT — the "+12 Advances their
design" positive row is reachable on the armistice-first route — is unchanged; only
the score at which Talleyrand will cede moved to the gate's honest threshold, and a
France pausing a war it is LOSING is the more Pressburg-faithful shape anyway).