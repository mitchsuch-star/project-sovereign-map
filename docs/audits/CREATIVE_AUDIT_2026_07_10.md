# Creative / Fun-Factor Audit — July 10, 2026

> **What this is.** The §8 creative capstone of `AUDIT_GUIDELINE.md` — the scored assessment pass, run **after** the EC pass-1 build landed (judging the improved economy at `fd97b6f`, suite 11,968/1 green). Method per §8: a live outsider's-seat playtest (**`LLM_MODE=anthropic`, real key, live parser/flavor/clarification calls**; most plain keyword commands resolved via the fast parser as designed) — 5 turns of the shipped 126-province 1805 campaign through the real backend: orders, delegations, an objection cycle, four battles, retreats, scouting, conquest + capture choice, estate endowment attempts, recruitment, incoming/outgoing diplomacy, and a live British settlement offer — plus two code-evidence sweeps (present-but-inert systems; memorable-moment generators).
>
> **Output discipline.** Scores + one highest-impact improvement per pillar; a ranked **Expansions worth building** list (the user explicitly opened the aperture: new items welcome, past items revisable). Design/balance items are **escalations behind design gates — nothing here is implemented**. Four trivial legibility slips were fixed inline per the §8 fix aperture (see §7); confirmed correctness defects are **routed, not fixed**, to `docs/BUG_FIXES.md` §Creative-Audit Findings with owning components named.
>
> Prior art: the March 2026 GPT audit scored diplomacy 6.5/10; the July 8 econ audit graded the pre-EC economy ~4.5/10 "emotionally inert."

---

## 1. The one-paragraph verdict

**The game generates genuinely great stories and then doesn't tell them.** In five turns the 1805 campaign produced: a British descent on Flanders, Archduke Charles hunting Bernadotte's broken corps across four countries until 17,000 men became 316 starving fugitives in Russia, Mack overextending into a three-corps pincer on French home soil, a literal-minded Soult standing motionless while Lannes died a league away — *"Soult awaits explicit orders and did not march to the sound of the guns"* — and Austria consoling a defeated Mack with the title Duke of Franconia. That is a war worth writing home about, and almost none of it was pushed at the player: the dispatch led with a supply line and labeled the Bernadotte catastrophe "recovering — severity: good." The command fantasy (CR-5/5b, objections, the guided proposal desk) is the strongest it has ever been; the **narration layer and battle legibility now lag every other system** and are where the next unit of effort buys the most fun.

**Pillar scores:** Command & response **7.5** · Marshals & personality drama **6** · Combat & battle legibility **4.5** · War narration & information surfaces **3.5** · Economy (post-EC) **6** · Diplomacy **6.5** (outgoing 8 / incoming 4) · World aliveness **7.5**.

---

## 2. Pillar scores and the single highest-impact improvement per area

### 2.1 Command & response (talk-to-your-generals core) — 7.5/10
**What works (live evidence).** `"Ney, deal with Mack"` produced the full CR-5 aggressive arm: inferred PURSUE, a fortification-aware bad-odds interrupt, and a flavor line that echoed my register ("He will charge on your word. Confirm the assault, or hold him back?") plus Berthier's first-use hint. `"Davout, deal with the British in Flanders"` produced the cautious arm: a scout, an in-character explanation, and the override phrasing. Objection triangle (trust/insist/compromise) fired correctly with alternative + compromise attached; trusting Davout auto-chained stance + fortify with honest AP narration. This pillar is the game's spine and it holds.
**What broke.**
- The objection response payload offers `choices: ["trust","insist","compromise"]`, but *typing* those words does not resolve the objection — "trust" fell through to the LLM parser (bewildered clarification), "insist" hit the diplomatic-response handler ("no pending diplomatic matter"). The typed surface cannot answer the system's own question. (Routed: BUG-CA-1.)
- Verb-synonym asymmetry: `"Soult, march to Swabia"` gracefully stopped at contact; `"Lannes, move to Swabia"` hard-failed with a scolding system-voice error. Same intent, opposite outcomes and registers.
- `"Bernadotte, retreat to Rhineland"` silently discarded the destination and retreated him to Dresden — the *opposite* direction (see 2.4/BUG-CA-2).
- Order AP costs vary invisibly (1 vs 2) with no price shown before or after; "reaches the approach to Swabia" never named the region he actually stood in (he hadn't moved).
- `"Endow Ney with an estate"` (no region named) resolved the missing target to **White Russia** — the first region in the world dict — and refused with "We do not hold White Russia." (Routed: BUG-CA-3.)
**Highest-impact improvement:** make the typed surface able to answer *any* question the game itself poses (objection choices, "choose an option 1–3," capture choices) — one pending-question router in front of the parser. The vision line is "every input gets a response"; today several of the game's own prompts are unanswerable in the medium the game is about.

### 2.2 Marshals & personality drama — 6/10
**What works.** Personality is real and consequential: the CR-5 arms diverge visibly; Davout's Iron Marshal fortify bonus is live and captioned; **reinforcement is personality-gated and historically resonant** — aggressive Ney marched to Soult's guns unbidden; literal Soult stood fast while Lannes broke, and the report said so in the best line of the session. Trust moves (70→75 on trust), defiance/vindication machinery is reachable (evidence sweep: 40–80 objections and 2–28 defiance moments per 20-turn campaign).
**What's hollow.**
- **The 1805 roster ships content-free** (verified live on the marshal card): Ney has `ability_name: ""`, skills all identical 5s, `relationships: []`. Card chrome without content — flat skills *advertise* an inert system. (Marshal Content Pass gate, unchanged priority — this audit re-confirms it as the top content gap.)
- One template voice: Davout's STRONG objection reads like anyone's ("the enemy is too strong"). Aggressive Ney obeys a hold with a flat neutral line — no grumble.
- Enemy marshals never speak (evidence sweep §12): personality drives their tactics, never their mouths. Mack lost an army and a duchy in five turns and said nothing.
- No marshal fates: no capture, death, parole, or last stand (evidence sweep §7) — Bernadotte's corps can be destroyed but *he* cannot be lost; the campaign's most dramatic arc has no possible ending.
- The Grouchy Moment — the game's signature beat per `VISION.md` — is **fully inert** (display plumbing exists in `turn_manager._build_turn_result`; no decision logic anywhere). Literal-personality objection triggers are all still TODO.
- `battles_won/lost` ignores reinforcement fights (Ney: 3 battles fought, card says 0W/1L); "3 turns idle" showed on marshals who fought twice.
**Highest-impact improvement:** land the Marshal Content Pass (MC-1..MC-3) — it is the prerequisite for every other drama system on the books (Jealousy, relationship events) and the single cheapest way to make seven identical statlines into seven people.

### 2.3 Combat & battle legibility — 4.5/10
**What works.** The mechanics compose: coordination bonuses, flanking origins, combined-arms captions, the fortify ladder, supply attrition, forced retreat, the recklessness gate on charges (with a clear unlock explanation), and a real battle report with a modifier breakdown.
**What's broken or opaque (all confirmed live).**
- **The meat-grinder is still the game post-EC.** Battle 1: 64k attackers with +17% modifiers *lost* to 50k on open plains (defender 0% terrain bonus) at 1.6:1 casualties against. Three attacks on Mack = two stalemates + one defender win; Mack lost 15k+ men across them and stayed at **morale 95** while my reinforcing marshals bled to 47. Defender dominance + attacker-only morale decay = attacking feels bad even when strategically correct. (Balance — escalation; see E-CA-1.)
- **Who fights is invisible.** Soult's 40k, explicitly ordered to Swabia and adjacent, sat out battle 1 with no explanation; the personality-gating rule surfaced only three battles later, after it killed Lannes. Casualty *sharing* by co-located marshals was disclosed by a tutorial *after* it mauled Murat.
- The battle prose undercounts: "Casualties: Ney 2,266" while the true attacker bill was 6,041 (reinforcers' losses omitted from the headline line).
- Report defects: `attacker_remaining` always equals `attacker_original` (twice confirmed); Berthier called a stalemate "swung the battle in our favor"; "Strategic orders +15" labels a bonus the player can't map to anything they did. (Routed: BUG-CA-4/5.)
- An explicit `attack` at terrible odds gets **no** warning while a vague delegation gets a lethal-odds interrupt — the direct order is *less* protected than the vague one.
**Highest-impact improvement:** a **pre-battle muster preview** — before resolution, one block naming attacker, expected reinforcements *with the personality/relationship reason per marshal* ("Ney will march to the guns; Soult awaits explicit orders — literal; Davout is fortified"), expected odds band, and the shared-casualty warning. It converts the three worst surprises of this playtest into the game's most characterful tactical screen. (Expansion #3 below extends it into a mechanic.)

### 2.4 War narration & information surfaces — 3.5/10
The pillar where the game most undersells itself. Confirmed live, in one five-turn stretch:
- The **morning dispatch missed every headline**: Mack's invasion of Franche-Comte (discoverable only via a supply-attrition line), the enemy-phase battle that mauled Lannes/Murat, and Bernadotte's entire death-march (two forced retreats, two enemy-phase defeats — dispatch said "recovering," severity **good**, while he sat at morale 3 in enemy Russia).
- The **dispatch intel table was stale** — it placed Mack at Swabia while the events and `status` placed him in Franche-Comte. Two first-class surfaces disagreed about the main enemy army. (Routed: BUG-CA-6.)
- The **auto-retreat pathing is both an agency hole and an absurdity engine**: four consecutive retreats moved a French corps *east* — Dresden → Silesia → Lithuania → White Russia — each hop deeper into hostile territory, mid-war with Russia, with the player's stated destination ignored once and never consulted again. (Routed: BUG-CA-2 for the direction contract; the design half is E-CA-2.)
- "NO INTELLIGENCE:" dumps ~85 region names as a wall; the Berthier note is a static "Your orders, Sire."; `campaign_log` has the real story but only as pull-surface one-liners.
The campaign log itself is good raw material — *"dotation_granted | Mack (Austria) endowed with Franconia — styled Duke of Franconia"* is a perfect one-liner. The failure is prioritization and push, not data.
**Highest-impact improvement:** Expansion #1 (the Dispatch Rewrite) — this is the top-ranked item of the whole memo.

### 2.5 Economy (post-EC) — 6/10 (up from ~4.5 pre-EC)
**What landed well.** The sink architecture is real and *visible*: the end-turn one-liner itemizes income / occupation / dotation skim / upkeep (incl. over-limit surcharge) / net / treasury — best-in-class legibility for a strategy game one-liner. France boots **over force limit** (189k vs 130k), so recruiting has a felt cost dimension; occupation cost appeared the turn I took Swabia (-75g at the secured 0.50 stability tier); the AI plays the same economy (markets, watchtowers, supply depots across five nations; British subsidies to Austria); the AI grants estates (`Duke of Franconia`), and my own endowment attempt hit the conquered-only rule with a *good* refusal line.
**What still doesn't bite.** 10,000 infantry cost **200 gold** against a **+2,887/turn net surplus while losing a three-front war** — treasury hit 11,917 by turn 5 with nothing urgent to spend it on; the real recruiting cost is morale dilution (90→78, interesting!) and manpower, never gold. The E1 anchor miss (36.9% vs 55–70%) is *felt* in play exactly as the band test predicted. The blocked estate path also dead-ends: "Swabia already sustains Marshal Mack's household" is a great line with **no follow-up affordance** (no confiscation, no guidance) — see Expansion #4.
**Highest-impact improvement:** make gold the binding constraint *during war* — the cheapest lever is war-scaled recruitment cost (E-CA-3, an EC-pass-2 escalation: per-soldier gold cost scaling with force-limit ratio and wartime, so rebuilding a mauled army is a treasury event, not a rounding error).

### 2.6 Diplomacy — 6.5/10 (outgoing 8, incoming 4)
**Outgoing is the best surface in the game.** "Talleyrand, propose alliance with Prussia" produced prepared terms, Send/Harsher/Generous/Adjust/Reconsider, an acceptance estimate (15, REJECT), the key obstacle, a ratification-gate warning (relations −10 vs required 40), the DP price, a hegemony warning naming Spain as the decisive bloc slice, and a genuinely strategic in-voice line: *"Hardenberg dreams of Saxony, but it is not yet ours to offer. Conquer it first, Sire, and he will come to the table eagerly."* The British settlement offer's dual voice (Talleyrand + London's own register) is equally strong.
**Incoming is people-free and monotone.** Five nations in five turns sent the *identical* proposal (open borders, reason: "hegemony pressure") rendered as clause bullets — the named diplomat is metadata that never speaks (R155's complaint, confirmed live and now the modal diplomatic experience at 20 nations). The settlement offer never states the fate of occupied territory ("Peace" — does Britain keep Flanders? the player cannot tell from the offer).
**Confirmed defects:** the **dialogue-stack misroute** — answering the just-presented British settlement offer landed my rejection on *Saxony's* never-seen proposal (top-of-stack changed between presentation and response; Saxony ate a relations hit sight-unseen; the log then recorded it confusingly as "Saxony rejected our open borders proposal") — the sharpest correctness finding of the session (BUG-CA-7). Also: the failed-response re-mount degrades "Hardenberg (hawk)" to "Unknown diplomat" (BUG-CA-8); "Please choose an option (1-3), Sire" without enumerating options on the typed surface; advisory has no strategic-overview verb ("assess our situation" → "which nation?").
**Highest-impact improvement:** give incoming proposals the outgoing surface's treatment — the diplomat *speaks* the proposal in register, with a motive line (the `decision_reason` already exists — say "hegemony pressure" *in Hardenberg's voice*, not as a tag) and variety pressure on AI proposal selection (anti-monotony: a nation that just watched four identical offers lapse should try something else). Rides queue items 5–6.

### 2.7 World aliveness (Layer 3) — 7.5/10
The 1805 world convincingly runs without the player: AI-AI treaties and rivalries tick (Sweden–Russia, Naples–Russia, Russia–Prussia friction), Britain subsidizes Austria per the coalition contract, allies genuinely fight (Bavaria retook Franconia; Deroy bled from 22k to 10k covering the flank), enemy nations develop their economies, hunt broken armies, exploit undefended coasts (Moore's Flanders/Amsterdam descent), and endow their own marshals. Boot state (mid-Third-Coalition, threat 85, France coalition leader) is dramatically correct.
**Gaps:** vassal loyalty bleeds visibly (−4/−6/−8 per turn, three vassals) with **no reason attached anywhere** (R132 confirmed as the top vassal complaint); coalition posture is computed and AI-consumed but never surfaced; war contribution shares accumulate invisibly until settlement.
**Highest-impact improvement:** attach *why* to every visible drift — vassal loyalty deltas name their cause line ("garrison absent; war weariness"), threat/coalition sources already itemize (that part is done and good).

---

## 3. Present-but-inert systems (the §8 "highest-value output" list)

Code-verified July 10 (file:function evidence in the sweep; verdicts confirmed against live play):

| System | Verdict | Evidence anchor | Disposition |
|---|---|---|---|
| **Grouchy Moment** (march-to-guns / cannon redirect) | **INERT** — display plumbing only, zero decision logic | `turn_manager.py:_build_turn_result` | Own design gate (re-homed at CR-5); Expansion #3 delivers its foundation |
| **Marshal abilities in 1805** | **INERT** — 6 marshals infra-wired; the shipped scenario defines zero abilities; flat skills | `marshal_overview.py:_WIRED_ABILITY_MARSHALS`; `europe_1805.json` | MC gate (MC-1/MC-2) |
| **Literal personality triggers** | INERT — all three marked TODO; literal marshals never object | `personality.py:PERSONALITY_TRIGGERS` | MC/CR follow-on; R59/R153 revised below |
| **Continental System** | INERT — backend fields + settlement term type; no parser/executor/wizard surface | `vassal.py`; `settlement_reactions.py` | EC-5 (Option B self-cost already resolved); activation surface is the EC-5 rider |
| **War contribution shares** | INERT (invisible) — computed, consumed by settlement ranking, never shown pre-settlement | `war_contribution.py:contribution_share` | Fold into war-detail UI (queue item 6 / DEF-13 family) |
| **Vindication** | Uncontextualized — raw int on the card, no narrative surface | `marshal_overview.py:_build_trust_standing` | Dispatch/log line when it changes (cheap, high-drama) |
| **Coalition posture** | Computed + AI-consumed, never surfaced | `coalition.py:get_coalition_posture`; 6 uses in `enemy_ai.py` | Talleyrand Desk (queue item 6) |
| **Authority** | Displayed in ledger; consumed only by internal trust logic — no acceptance/objection/AI coupling | `authority.py`; `ledger.py` | R152 stands; candidate coupling belongs to the Jealousy/MC arc |
| **Settlement memories** | Write-mostly — one +5 acceptance read; AI never re-consults | `settlement_reactions.py:settlement_gratitude_mod` | Queue item 5 (agendas) |
| **Marshal relationships** | Display-only filter — no coordination-bonus or objection coupling | `relationship.py`; `enemy_ai.py:3063` | MC-3 prerequisite work; Jealousy gate |
| **Naval** | Absent by design (movement graph only) | — | DEF-5 (unchanged) |
| **Morale spiral breaker (R154)** | **ACTIVE** — 25% forced-retreat floor works; the real issue is attacker/defender morale *asymmetry* | `combat.py:FORCED_RETREAT_THRESHOLD` | R154 revised below |
| Enemy AI tactical layer (drill/fortify/square) | ACTIVE (20+ refs) — not player-only | `enemy_ai.py` | none needed |
| Estate endowments (ES-7) | ACTIVE both sides; player consequence surface thin (shortfall number, no gripe beat) | `enemy_ai.py:_find_dotation_grant`; `marshal_overview.py:_build_estates` | Erosion-beat surfacing rides Expansion #1; confiscation is Expansion #4 |

---

## 4. Expansions worth building (ranked by depth-per-complexity)

Per the §8 aperture: concrete, gate-routed, propose-don't-build. Each names the mechanic, how it plays, hooks, cost, and the vision tie-in.

### #1 — The Dispatch Rewrite: *Berthier tells the story* ("EXP-N1")
**Mechanic.** A deterministic narrative-priority layer over the existing event stream. Three parts: (a) **headline selection** — score enemy-phase/turn events by stakes (home-region lost > marshal mauled > ally beaten > construction) and open the dispatch with the top beat in prose; (b) **danger flags** — any player marshal co-located with a stronger enemy, at morale <40, or force-retreated last phase gets a red status line (kills the "Awaiting orders" lie next to a 49k enemy); (c) **arc memory** — a tiny per-marshal event chain (consecutive defeats, pursuits, sieges) so Berthier can say *"Bernadotte, hunted across three frontiers, stands at the Niemen with three hundred men."* No LLM required (Golden Rule 6 unaffected); the existing severity/`campaign_log` data carries it.
**Hooks.** `dispatch.py` (builder), `campaign_log.py` (event taxonomy already complete), `world_state` event log; zero new mechanics, zero serialization beyond an optional small arc-chain cache.
**Cost/depth.** ~1–2 sessions. **The highest fun-per-line item on the books** — it monetizes drama the simulation already produces (this playtest alone would have yielded five headlines).
**Vision tie.** "Every input gets a response" extended to the world's inputs; advisors color, mechanics cause.

### #2 — Marshal Fates: capture, parole, and the last stand ("EXP-M1")
**Mechanic.** When a forced retreat would fire and the army is below a threshold (or retreat is cut off), roll a **fate**: *escape* (today's behavior), *capture* (marshal becomes a prisoner of the victor nation), or — aggressive/loyal marshals only — an offered **last stand** (player choice: fight the doomed defense for delay + glory, personality-gated). Captured marshals become **diplomatic objects**: a ransom/exchange clause type in the existing settlement/proposal machinery ("return Marshal Bernadotte — 800 gold or the release of Mack"). Building Blocks: identical rules for enemy marshals — *Mack at Ulm becomes capturable*, which is the actual history the scenario is built around.
**How it plays.** The Bernadotte arc gets an ending; hunts have prizes; broken armies carry a person-shaped stake; settlement tables get a human clause.
**Hooks.** `combat.py` forced-retreat block (fate roll), `marshal.py` (captive state — serialized), settlement clause registry + `diplomatic_templates` (ransom clause), `enemy_ai` P-rule for pursuing broken armies (already emergent!), campaign log/dispatch beats.
**Cost/depth.** 2–3 sessions + a design gate (thresholds, AI valuation of prisoners). Highest pure-drama expansion; directly fills the evidence sweep's "no capture/death/last stand" hole.
**Vision tie.** Personality-driven drama; territory-and-war problems with faces.

### #3 — March to the Guns, surfaced: the muster preview & the standing order ("EXP-C1")
**Mechanic.** (a) **Muster preview**: any player attack first returns a muster block — every friendly marshal in range with WILL JOIN / WILL NOT and the *reason* (aggressive: marches to the guns; literal: awaits explicit orders; fortified: static; hostile relationship: refuses) plus the odds band and shared-casualty note; confirm/cancel. (b) A new cheap **standing order** `"Soult, support Ney"` that pre-authorizes a literal/cautious marshal to reinforce a named colleague — making Soult's inaction a *player-visible choice* rather than a trap. (c) This muster/consent substrate **is the Grouchy Moment's foundation**: the autonomous march-to-guns beat becomes "the muster rule applied on the AI's turn," finally giving the re-homed signature moment a landing.
**Hooks.** `combat_executor._calculate_reinforcements` (rules exist — expose, don't reinvent), CR interrupt plumbing for the confirm step, strategic-order SUPPORT type (exists) for the standing order.
**Cost/depth.** 1–2 sessions for (a)+(b). Converts this playtest's three worst surprises into its most characterful screen.
**Vision tie.** Disobedience-as-negotiation extended to the battlefield's biggest hidden rule; personality over randomness, made legible.

### #4 — The Spoils of War: estate confiscation & the estate web ("EXP-E1")
**Mechanic.** Conquering a region holding an **enemy marshal's estate** opens a choice (same popup family as plunder/secure): **confiscate** (treasury windfall + the dispossessed marshal gains a personal grudge → his nation's acceptance modifier vs you worsens; your *own* cautious marshals lose a point of trust — property is sacred) or **respect the title** (small acceptance bonus with that court; the estate income stays sterilized while you occupy). Confiscated estates become grantable to your marshals — "Endow Ney with the Duchy of Swabia" *works*, and Ney's expectation rises accordingly (existing ES-7 machinery).
**How it plays.** My exact turn-4 dead end ("Swabia already sustains Marshal Mack's household") becomes one of the game's most Napoleonic decisions.
**Hooks.** `dotation.py` (estate registry exists), `capture_executor` (choice popup pattern exists), `diplomacy.py` acceptance mod (one term), ES-7 grant path unchanged.
**Cost/depth.** ~1 session + numbers at an EC-pass-2 gate. Rides code that landed **yesterday**; near-pure payoff.
**Vision tie.** Territory as command dilemma — "territory problems have faces."

### #5 — Enemy marshals speak ("EXP-M2")
**Mechanic.** A deterministic one-liner bank keyed to (enemy personality × battle outcome × situation), attached to battle reports and the campaign log: cautious Mack after repelling you — *"Mack does not leave his ground; he sees no reason to start today."*; aggressive Archduke Charles on pursuit — a hunter's line. Optionally the existing CR-3 parse-call `flavor` pattern could be reused AI-side later, but the template bank alone lands the effect (Golden Rule 6 safe).
**Hooks.** `battle_report._pick_observation` (side-aware since the July 9 audit fix), enemy personality already on the marshal.
**Cost/depth.** <1 session; content authoring dominates. Cheapest "people, not calculators" win on the board; complements DEF-1 (which owns *diplomat* voices, not enemy *marshals*).

### #6 — "What does Europe intend?" — the strategic assessment verb ("EXP-D1")
**Mechanic.** `"Talleyrand, assess our situation"` (the exact phrase that dead-ended live) returns the war room read: per-war trajectory in prose, **coalition posture** (computed today, shown never), the top-3 threat sources (already itemized in `coalition_status`), vassal-loyalty trend + cause, and one recommendation with an executable follow-up option (R117's ask). Mostly a *composition* of data that already exists behind one new advisory arm.
**Hooks.** `diplomatic_advisory.py`, `coalition.py` (posture/threat sources), `war_status.py`, vassal loyalty causes.
**Cost/depth.** ~1 session. This is the natural first slice of queue item 6 (Talleyrand Desk) and this audit's recommended entry point into it.

### #7 — War-priced recruitment (escalation E-CA-3, EC pass 2 — not an expansion proper)
Recruiting at 200g/10k men keeps gold free in exactly the situation (mid-war rebuilding) where the economy should bite; propose per-soldier gold cost scaled by force-limit ratio and war status. Pure numbers behind the EC gate; listed here because it is the missing half of the force-limit tension EC pass 1 built.

---

## 5. Design escalations (gate-owned; no code)

| ID | Finding | Owner gate |
|---|---|---|
| E-CA-1 | **Attacker morale-grind asymmetry**: defenders' morale barely moves on stalemates (Mack: 15k casualties, morale 95) while attackers and reinforcers bleed morale; combined with defender-favored outcomes this *is* the meat-grinder. Recommend an explicit look at stalemate/defender morale deltas at the next combat-balance gate. | Combat balance (user) |
| E-CA-2 | **Retreat agency + direction doctrine**: honor a stated destination when legal, else *narrate* the substitution; bias auto-retreat toward own/allied/home territory and forbid retreating into an at-war nation's soil unless no alternative (the Lithuania death-march). Mechanical half routed as BUG-CA-2. | Combat/movement design gate |
| E-CA-3 | War-priced recruitment (see Expansion #7). | EC pass 2 (E-numbers) |
| E-CA-4 | Delegation gets a lethal-odds interrupt but an explicit bad-odds `attack` gets none — decide whether direct orders deserve a one-line odds warning (not a block). | CR-6 gate |
| E-CA-5 | Settlement offers should state territorial consequences ("Britain retains Flanders") in the terms summary — "Peace" is not legible while home soil is occupied. | Settlement presentation (post-arc, narrow) |
| E-CA-6 | Incoming-proposal voice + AI proposal variety (see 2.6). | Queue items 5–6 (8.EVAL) |

## 6. Correctness defects routed (fix-as-you-find queue, NOT fixed here)

Filed with full evidence in `docs/BUG_FIXES.md` §Creative-Audit Findings (July 10, 2026): **BUG-CA-1** typed objection choices unanswerable + guard copy contradiction (§6.3/§6.4) · **BUG-CA-2** retreat ignores stated destination; pathing retreats into at-war-nation territory (§6.5 movement) · **BUG-CA-3** `grant_dotation` missing-region default resolves to first world region ("White Russia") (§6.5/§6.3) · **BUG-CA-4** battle-report `casualty_summary.attacker_remaining/defender_remaining` echo originals (§6.1) · **BUG-CA-5** Berthier reinforcement observation claims victory on a stalemate; "Strategic orders +15" label unmapped for the player (§6.1) · **BUG-CA-6** morning-dispatch intel table stale vs status/events (Mack at Swabia vs Franche-Comte) (§7.7 read-models) · **BUG-CA-7** dialogue response lands on a different dialogue than presented (Britain offer → Saxony rejection); also leaves a reversed campaign-log line (§7.4/R12 dialogue manager) — **highest priority** · **BUG-CA-8** failed-response re-mount degrades resolved diplomat to "Unknown diplomat" (§7.6) · **BUG-CA-9** `battles_won/lost` and `idle_turns` ignore reinforcement participation (§6.1/§7.7) · **BUG-CA-10** typed dialogue prompt "choose an option (1-3)" never enumerates options on the typed surface (§7.4).

## 7. Inline fixes applied (the §8 trivial-legibility aperture)

Four raw-key/typo-class fixes, pinned by `tests/test_creative_audit_legibility_fixes_2026_07_10.py` (+1 assertion moved with the copy in `test_disobedience.py`): camelCase marshal keys humanized in the intel report (status) and dispatch sightings ("ArchdukeJohn" → "Archduke John"); Talleyrand's nation-landscape list renders display names ("Kingdom of Italy") with labels humanized and routing keys untouched; indefinite-article grammar for treaty/proposal copy (`display_names.with_indefinite_article`; dispatch templates reworded to "signed the {treaty_type}"); the pending-objection guard names the objecting marshal instead of leaking `/respond_to_objection` into player prose.

## 8. What this feeds

- **Marshal Content Pass gate (next in queue):** this audit's evidence (2.2, §3) is the strongest case yet — approve MC-1 scope with the roster-content gap quantified (0 abilities / flat 5s / 0 relationships live).
- **8.EVAL:** E-CA-6 (incoming voice/variety) joins R155/R156 with fresh live evidence; EXP-D1 is the recommended first Talleyrand-Desk slice.
- **EC pass 2:** E-CA-3 (war-priced recruitment) + EXP-E1 numbers.
- **Jealousy (post-MC):** authority coupling (§3) and the estate web (EXP-E1) are natural substrate.
- Expansion items filed in `docs/DESIGN_REFINEMENT.md` §Wave 6 with IDs EXP-N1/M1/C1/E1/M2/D1; revisions to R154, R59/R153, R129/R131/R132 recorded there.

*Cross-linked from `docs/audits/AUDIT_2026_07_09.md` (the correctness-sweep log) per §9. Playtest artifacts: live backend session July 9–10, 2026, turns 1–5, France, default 1805 boot.*

---

## 9. W6 RE-SCORE ADDENDUM (July 10, 2026, second session — post-W6-10 build, per WAVE6_FUN_FACTOR_SPEC §0)

**Method.** The §2 outsider loop re-run LIVE against the running 1805 boot at the post-W6-10 build (W6-0..W6-10 landed; W6-11 balance duo deliberately NOT yet landed so the legibility gains are measured unconfounded): outgoing assessment → live delegation → two gated battles vs Mack (muster + attack_anyway) → standing order → retreat with a stated destination → endow attempt → one incoming proposal answered (typed) → five end-turns reading every dispatch. Transcript beats quoted below verbatim from the run.

### Re-scored pillars

| Pillar | §2 score | Now | Target | Verdict |
|---|---|---|---|---|
| **War narration** | 3.5 | **7.5** | ≥7 | **MET** |
| **Combat legibility** | 4.5 | **7** | ≥7 | **MET** |
| **Incoming diplomacy** | 4 | **7** | ≥6.5 | **MET** |
| **Marshal drama** | 6 | **7.5** | ≥7.5 | **MET** |

**War narration 3.5 → 7.5.** Every morning now leads with the story the simulation was already generating. Live: turn-2's headline was *"Sire — Flanders has fallen. Enemy colours fly over French homeland soil."* with sub-beats naming both maulings; by turn 4 the arc memory read *"Bernadotte — Hunted by Archduke Charles across 2 frontiers — stands at Nivernais with 3,312 men"* — §2.4's exact un-narrated death-march, now narrated every turn as it happens. Danger flags replaced the "Awaiting orders" lie (*"IN PERIL — an enemy force of ~49,496 shares the field"*, *"Starving — supply has failed at Rhineland two turns running"*, *"Morale failing (25) — the men waver"*). Battles accumulate names; the W6-5 fidelity beat narrates the cost of literal command (*"Soult holds at Rhineland, per your orders — the guns at Swabia did not move him"*). Short of higher: one headline + ≤2 sub-beats per dispatch is the ceiling by design; the intel table is fresh but still terse; no long-form chronicle.

**Combat legibility 4.5 → 7.** The audit's three worst surprises are now the game's most characterful screen, live: the muster named every non-joiner WITH the reason AND the remedy (*"WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Ney' and he will march"*), the odds band gated the unfavorable attack behind one modal, and after `Soult, support Ney` the next muster read *"WILL JOIN — Soult: marches under your written support order"*. Report arithmetic is honest (24,000 − 6,999 = 17,001, verified in-run). The beaten enemy speaks his result (*Mack: "Mack does not leave his ground. He sees no reason to start today."* — second variant on the second battle, deterministic rotation confirmed). Retreat substitutions are named (*"Rhineland cannot be reached, Sire — it is not adjacent; Bernadotte falls back to Munich instead"*). What keeps it at 7: the modifier breakdown is still a dense list; shared reinforcement casualties are noted but not itemized per marshal in the one-liner; and the E-CA-1 morale asymmetry remains visible (our line troops fell 31 → 6 → 0 across three defensive turns while the capstone's Mack sat at 95) — W6-11 lands next and should be re-checked at the wave close.

**Incoming diplomacy 4 → 7.** The envoy has a mouth and a motive, live: *Araujo: "Portugal asks only to be reassured that France's greatness leaves room for small nations. Open the borders."* — `hegemony_pressure` voiced in the dove register, no raw tag. Variety confirmed in the same turn the capstone measured five identical asks: Portugal arrived asking open borders while Denmark asked non-aggression (the P3 relation-band pick), and rejected/lapsed types now stay away for 6 turns. Settlement offers state the territorial status quo (E-CA-5). Held below 8 by the R155/R156 residual (owner: queue items 5–6): the AI still has no multi-turn agenda or persistence personality, and counter-offers keep the older register.

**Marshal drama 6 → 7.5.** One five-turn loop produced: Davout's cautious reconnoiter with Berthier teaching the delegation doctrine; Soult's literal register spoken end-to-end (*"'Soult, support Ney.' No more and no less. (1 AP — Soult executes precise orders with fewer couriers.)"*) plus his fidelity beat; Bernadotte's hunted arc narrated across three dispatches; Mack speaking twice in two distinct lines. Behind the visible run: capture/last-stand/ransom stakes (W6-7) now stand behind every broken army, and conquered estates pose the confiscate-or-respect choice (W6-8). The MC-1 content gap (§3) is still the binding constraint on going higher — abilities/relationships remain flat.

### Definition-of-done check (spec §15)

Narration ≥7 **measured** (7.5) and combat legibility ≥7 **measured** (7) — the wave's two required pillars pass. Incoming (7 ≥ 6.5) and drama (7.5 ≥ 7.5) also meet target. **W6-11 (balance duo) remains to land after this measurement by design**; its E-CA-1 defender-morale symmetry is the one item this addendum flags for a spot-recheck once landed (our-side morale collapse remains steeper than the defender's, consistent with §2.3).

*Playtest artifacts: live backend session July 10, 2026 (second session), turns 1–6, France, default 1805 boot, post-`485ce18` build.*

**Post-addendum note (same day):** the one flagged spot-recheck — the E-CA-1 defender-morale asymmetry — is CLOSED: W6-11 landed the symmetric casualty-scaled morale table (winner delta = bonus − the same curve the loser pays; the battle-2 replay's holding defender moves +5 → −5) plus E-CA-3 war-priced recruitment, deliberately after this measurement so the legibility scores above are unconfounded by balance tuning. `tests/test_w6_balance_duo.py`.
