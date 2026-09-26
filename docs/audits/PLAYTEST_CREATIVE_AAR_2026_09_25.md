# The Creative AAR — September 25, 2026: eighteen turns in the Emperor's tent, two passive arms to the Verdict, and what the reign is worth

> **What this is.** The user asked for one thing in four words: *play the game, review it, be creative.* This memo is the record: an after-action report of a campaign played by hand at the game's own command line, a review written the way a critic who had spent an evening in the tent would write it, and every defect and design question the play surfaced, each traced to its producer. Defects are **`BUG_FIXES.md` §Creative AAR (AAR-1 … AAR-32)**; design items are **`DESIGN_REFINEMENT.md` §Creative AAR (AAR-D1 … AAR-D8)**. Nothing was built.
>
> **How it was played.** France, the 1805 campaign, on a fresh backend on port 8007 (`DEBUG_MODE=false`, the shipped defaults, saves sandboxed) with the **live Anthropic parser configured** (`LLM_MODE=anthropic`, the developer's key). Every order was typed through `POST /command` from a small terminal of my own (`tent.py`, in the session scratchpad) that renders what `main.gd` renders — the message, the muster, Berthier's report, the enemy phase, the morning dispatch — and answers every popup through the client's own endpoints. **Turns 1–18 were played by hand: 142 typed commands, 102 of them distinct, 25 refused, 8 of them questions; nine marshal petitions, eighteen envoys and five captures answered.** The archive is `docs/audits/playtest_digests/aar-hand-played/` — the diary I kept while playing, every command with its outcome, and a trimmed transcript of all 176 requests.
>
> **Two honest limits.** (1) The user was at the machine playing another game while this ran, so **no window was opened on their screen**: the Godot client was not driven, UI/UX is not re-scored, and the prior 7.0 stands. (2) **At turn 18 I lost the campaign by my own hand**: `tools/playtest_driver.py --http` opens with `POST /new_game` (its banner says the world *will be modified*, and it means it), and I ran it against the live server to carry the quiet years to the Verdict. The eighteen turns are fully documented; the years after them were measured on two passive driver arms instead (§5). The lesson is recorded in memory for the next session.
>
> **Verification.** Every defect below was reproduced at the wire during play and then traced to its producer by a read-only pass; the producer and the fix shape are on the rows. Where a claim could not be traced to a line it says so.

---

## §0 The verdict in five lines

1. **The command line is the game, and it works.** 141 of 142 orders — including the flowery ones — were read by the offline parser at 0.80–0.95 and executed as meant; the paid model was consulted once in eighteen turns. Every refusal named a remedy.
2. **The war was Napoleonic and legible**: Ulm on turn 1, Mack captured by the Emperor in person, Vienna stormed on turn 6, the Treaty of Vienna on turn 9 — and then a Russian enemy phase that out-generaled me in one night, breaking two corps with a counter-punch and a concentric strike. The AI earned its score.
3. **The diplomacy is the deepest system and the one with the most contradictions on its surfaces**: a settlement editor that says "Will sign" and "cannot be ratified" on one screen (AAR-2), Britain's own offer priced as unacceptable to Britain when laid back verbatim (AAR-3), a proposal menu whose "Harsh demands" and "Generous peace" carry identical terms (AAR-7).
4. **One design hole is a P1**: a lord's separate peace leaves its vassal at war with no army. Austria, at peace with France, ate the Kingdom of Italy province by province and stormed Milan on turn 18, and nothing at the peace table said the client's war would go on (AAR-1).
5. **The ending is written and the road to it is not** — as GE-V found. Holding Vienna, Bohemia, Hungary and Moravia under a signed status quo left them "held, unsettled" (32 of 45 titled), so the Congress stayed out of reach; the passive arm that took Britain's turn-4 gold reached the Verdict at turn 44 as **"an empire contested — the question of 1805, still open"**, which is exactly the right sentence for that board.

**Directional ≈6.9 → ≈6.9.** Narration and AI aliveness up, diplomacy and combat legibility down, first contact up from 5.5 to 6.5 now that a campaign opens with a briefing.

---

## §1 The campaign diary (the after-action report)

*Entries in the Emperor's hand; the reviewer's marginalia in italics after each.*

**Late September 1805 (turn 1).** Berthier's briefing on the table this morning — twenty-eight provinces, a treasury of 800, three courts at war with us and four orders the board will take today. I asked him who we are fighting and why; he set down his pen and pointed me at the campaign log. Talleyrand was better: three designs, three prices, and a counsel. Ney had the honour of the first blow — I wrote it as I would have said it, Ulm and the Danube and all, and the parser read it at 0.95. The Great Battle of Swabia: five corps on the field, Mack from 52,000 to 37,000. I led the second blow myself. *Mack is taken by France at Swabia.* Threat 70 to 86 by nightfall.
*— The briefing (F1) lands. The desk's first-contact shrug on "who am I fighting and why" is AAR-17. The Emperor's presence pays +10% and the report says so. The morning after, 7,189 men were lost to short supply at Swabia: the muster preview had warned of ~4,500.*

**Early October (turn 2).** Bernadotte petitions — envious of Ney after one battle — and I bought his patience for an action point. Prussia, the Porte and Lisbon write; I accepted all three, the Porte "serene and unhurried". I laid a keel: the Admiralty told me plainly that Britain's blockade rots the fleet five a turn at anchor and that *that* is the number to fix. Talleyrand goes to court Prussia.
*— The letter-book's voices are the best writing in the game. The keel's honest futility line is design legibility at its finest. The petition arriving on turn 2 is the jealousy cadence question, AAR-D3.*

**Late October (turn 3).** Ney walked into an empty Bohemia. I licensed Prussia against Hanover and Talleyrand said the truest thing anyone said all campaign: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold." Massena would rather attack than fortify at Milan; I insisted, and paid thirteen trust and — I learned only in the receipt — two actions instead of one.
*— The licence is the Schönbrunn deal and it works. "What can I build" told me there was nowhere to break ground, then `build market at Paris` broke ground (AAR-18). The objection did not name the stance shift's price (AAR-23).*

**Early November (turn 4).** London offers peace and 1,358 gold beside it — on turn four, having lost nothing. Talleyrand: "A court that pays to stop fighting has already decided." I asked for a revision and the table priced Britain's own offer at Britain −32 of 50. Ney scouted Vienna: "No enemy forces detected." Vienna had twenty-five thousand men in it.
*— AAR-3 and AAR-4. The dispatch also told me Lannes was starving at Munich two turns running, the morning after he left starving Swabia for a fed Munich (AAR-13).*

**Late November (turn 5).** Talleyrand offered me a generous peace or harsh demands; they were the same treaty. Ney assaulted Vienna alone — none of the three corps beside him joined, and nobody told me they would not — and lost 4,746 men for 8,033 of the garrison, which grew back two thousand by morning. I bought him three thousand substitutes at four times the going rate; his morale fell from 80 to 69 and the receipt said why.
*— AAR-7 and AAR-24. The substitutes copy is a model of a priced choice.*

**Early December (turn 6).** Vienna falls. Soult bled the garrison to 9,484 and Murat took it — the Great Horseman marching into the Habsburg capital, as he did in fact, if by a bluff. Europe's alarm is 98. The Helvetian chancery petitions for eight collections of tribute and I grant it; the terms were stated to the gold. Britain has landed Paget at Lisbon.
*— The client petition (IQ-7) is the clearest priced dialogue in the game. The supply headline this morning recommended I march a corps into Vienna to relieve the crowding at Bohemia — Vienna, with 17,000 Austrians in it (AAR-14). Bernadotte's counter-punch, I learned, had expired unused; nobody had told me it existed (AAR-25).*

**Late December (turn 7).** Metternich sues — an armistice, 157 gold a turn, "with perfect politeness". The armistice would strike my +67 from the score and the text says so; I declined, countered, and Talleyrand came back with two thousand more gold and the same armistice. I opened the table instead. With Britain and Russia dropped from coverage the draft wrote itself — Carniola and 300 gold — and Austria stood at 51 of 50, *Will sign*, *Will carry as drafted*. The same screen said the settlement *cannot be ratified now: the terms weigh heavier than their defeat*. The one road, "Make peace with Austria only", was greyed for want of a third diplomatic point.
*— AAR-2, the campaign's clearest defect. Hungary and Tyrol were walk-ins the same day; alarm 100. Marmont was commissioned at Paris with three thousand guns for an expedition I had already decided on.*

**Early January 1806 (turn 8).** Prussia offers a defensive alliance; signed. The Kingdom of Italy petitions for Tyrol and I grant it — and spend the diplomatic point the Austrian peace needed. Massena attacked Charles in the Tyrol mountains and lost, still in the defensive stance my insisted fortify had left him in five turns earlier; the preview called the field "even" and did not name the stance. Then the game told me Massena's concerns had been justified and docked my authority for a defeat suffered in the attack he had asked for.
*— AAR-11: the vindication test fires on the marshal's next battle, not on the insisted order. Lannes, cornered at Tyrol, could retreat only to Bohemia: Milan and Munich, an ally's and a vassal's capitals with French corps in them, were not "friendly" (AAR-… noted in D4).*

**Late January (turn 9).** The Treaty of Vienna: Austria pays 145 a turn, mutual open borders, and the four provinces stay in my hands by status quo. Prussia now *RECOGNIZES* on the Congress table, 66 of 50. Kutuzov appeared at Moravia and beat Murat; I struck him with Soult, the Emperor and Ney from three sides and the preview said favorable. Brutal stalemate. Recruiting was refused because I had no military actions left, though recruiting costs none; laying a keel with my last administrative action ended the turn before I had finished with it.
*— AAR-6 and AAR-12. "Favorable" against a cautious defender in defensive stance with an outnumbered bonus produced two stalemates in two turns; the preview does not price those.*

**Early February (turn 10).** The night of the ninth. Kutuzov's free counter-punch broke Murat; Buxhowden crossed from Podolia and broke Ney at Hungary; Kutuzov then hit Bohemia and Lannes covered Ney's retreat. Two corps broken, two provinces lost, in one enemy phase, by two Russian corps against three of mine standing one province apart. The morning's intelligence table placed Buxhowden at Podolia, where he had been two days before; the map had him in Hungary in full view. I asked Talleyrand for an armistice and he drafted one that paid Russia 774 gold at 60% — Napoleon at Znaim.
*— AAR-5. The Russian AI's phase is the best thing the enemy did all campaign and it exploited exactly the dispersion the supply system forces (AAR-D4).*

**Late February (turn 11).** Russia accepts. The dispatch says "peace with Russia is signed" and "the war ends in a stalemate"; it was an armistice, and the war did not end. Kutuzov "marches from Bohemia into Bohemia unopposed" and takes it. Austria — at peace with me — takes Piedmont from my Kingdom of Italy with a small force. Prussia offers a full alliance; signed. I recalled Talleyrand by typing "recall Talleyrand" and was asked which nation I wished to approach.
*— AAR-15, AAR-22, AAR-20. The eliminated vassal's story begins here and nobody says so (AAR-1).*

**Early March (turn 12).** The Irish expedition: Marmont, fifteen thousand, Normandy to Munster, "the transports slip past unseen 56 times in 100". They did not. 4,500 men and 24 sail lost, Spain twenty and Holland six beside us, the escort "beaten decisively". The Admiralty's TRAFALGAR beat came with the morning. I asked for substitutes for Murat and was told there is no market in cavalry — "a substitute may carry a musket, not ride a trooper's horse."
*— The intercept copy is excellent, but the squadrons that caught us were "the Britain squadrons" (AAR-22). The naval road for a French player in 1805 is one throw of the dice and no second (AAR-D8).*

**Late March (turn 13).** Wellesley walked five thousand men from Piedmont into Provence, and the dispatch, in one sentence, taught me the raiding rule: a detached garrison of 3,000 holds a province against a march, as does any garrison of 5,000. I sent Massena and Marmont south and commissioned Oudinot at Paris. Marmont "has concerns about this order" and would not say which.
*— The raid rule teaching itself in the headline is VP-R1 done right. Marmont's reasonless objection is AAR-31.*

**Early April (turn 14).** Britain, asked to name terms, named a white peace in which Britain keeps Provence. Ney's ten thousand substitutes took his morale from 0 to 16, and Berthier warned me he now stood on his own breaking line and should be drilled before he marched. He was.

**Late April – Early May (turns 15–16).** Massena abandoned his march twice to rush to cannon fire — Bavaria's fights with Austria, in a war France had left. Russia's armistice thawed into peace on schedule; the coalition dissolved, alarm 93 to 44; Britain and Spain made their own peace without me; Britain sued. Soult, the literal man, filed his patrols in triplicate: "There were eleven. There was nothing in any of them."
*— AAR-9 (the cannon-fire rule for wars France is not in). The literal-marshal petition is the best marshal writing in the game.*

**Late May – Early June (turns 17–18).** Oudinot's arrival battle beat Wellesley; Marmont's guns from Lyonnais razed his works; the strategic report asked me how Marmont should proceed and the endpoint replied that Marmont had no question. Russia offered its good offices for Britain's peace. Then the news: Austria stormed Milan's garrison of ten thousand and the Kingdom of Italy *is no longer ours — conquered, the satellite is gone.* Oudinot retook Provence. I ratified Britain's white peace, "their own terms — consents". Peace with everyone, thirty-two titled provinces of the forty-five the Congress wants, and the Emperor two days' march from Paris.
*— AAR-8, AAR-1. The campaign ended here, by my error, not the game's.*

---

## §2 The review — what the Emperor learned in eighteen turns

*Written as the game's own end screen would grade it, register by register.*

**AN EMPIRE CONTESTED.** *The Empire holds what it held, and Europe has not accepted it.* That is the verdict the game wrote for the passive arm at turn 44, and it is a fair grade for the game itself: it holds what it held on September 23 — a 7 — and the sharp edges are where Europe, which is to say the diplomacy, meets the player.

**The command line holds.** I typed like an emperor dictating to a secretary — "Marshal Ney, you have the honour of the first blow. Fall upon Mack at Ulm before the Russians can reach him, and do not let him slip away down the Danube" — and the *offline* parser read it, priced it and fought it. Over 142 orders the paid model was needed once, for a question ("Berthier, remind me what the Russians demanded at the table") that it answered in Berthier's voice with two invented commands. Every refusal I hit named its remedy: recruits join a marshal within reach of a depot, a substitute cannot ride a horse, a drill cannot be run with Kutuzov one province away, a keel under blockade fixes nothing. The one class of typed order that misroutes is Talleyrand's: "recall Talleyrand" asks which nation to approach, "improve relations with Russia" answered with an opinion about Prussia while a Prussian mission ran, and a relations mission with a court at war starts from the keyboard and is hidden in the Cabinet. The desk that answers questions still shrugs at the first question a new player asks.

**The war reads.** The muster preview names who marches and at what odds; the report names every modifier; the Emperor's presence is a line item; the reinforcement lines say who came and who "was conspicuously absent". Two things it does not say cost me men: that a garrison assault is a solo affair however many corps stand beside the assaulting one, and that a scouted capital with twenty-five thousand men in it holds "no enemy forces". And the preview's "favorable" is an army-size verdict: against a cautious Russian in defensive stance with the outnumbered bonus it delivered stalemates twice, and the preview never mentioned the stacking that made them.

**The marshals are people, and they talk too much.** Bernadotte's grievance, Soult's eleven patrols, Massena's "borrowed field", Berthier's warning that a corps bought back to 16% morale stands on its own breaking line: the writing is the reason to play. But nine petitions in eighteen turns, three of them from the same man, a crown that passed to Oudinot for beating a four-thousand-man raid, and a vindication that docked my authority for a defeat in the attack the marshal himself had asked for — the drama needs a longer fuse of its own (F4 gave the *reward* curve one).

**The diplomacy is the deepest system in the game and its surfaces contradict each other.** The letter-book, the client petitions with their prices, the licence, the Prussian courtship that ended in an alliance and a *RECOGNIZES* on the Congress table, Russia's mediation, the armistice that thawed into peace on the mission's schedule — all of it works and much of it is beautifully written. Then the settlement editor tells you a court will sign and that the settlement cannot be ratified in the same breath; the revision table prices the enemy's own offer as unacceptable to the enemy; Talleyrand's menu offers a hard peace and a soft one that are the same peace; and — the P1 — a peace with a great power leaves your client at war with it and says nothing, until the client is gone.

**The economy is honest and the long peace is empty.** Every charge is named and sums; substitutes and rentes and estates are priced choices; a war costs gold in materiel and men in supply, and the ledger shows both. Nobody ever asked me for an estate: F4's fuse held for eighteen turns of victories. And the passive arm that took Britain's gold on turn 4 sat on 119,401 gold at turn 44 with threat at zero and nothing to buy — Update 1's row, reproduced a third time.

**The AI is alive.** Russia's enemy phase on the ninth night — a free counter-punch, a river crossing, three attacks on three isolated corps — was better generalship than mine. Austria dithered (fortify, unfortify, square, fortify) and then spent five turns and two archdukes assaulting a Bavarian garrison of forty-seven, then twenty-four, then three; and then, while at peace with me, dismantled my satellite with a "small force" because the game let it. Wellesley's raid on Provence was exactly the kind of thing Britain did.

**The ending exists and is out of reach.** The Verdict's four sentences for the contested register are the best paragraph in the game. The road to the Congress is not there: after Ulm, Vienna, Bohemia, Hungary and Moravia — the whole Austrian campaign — the count stood at 32 of 45, because a signed status quo does not title what it retains (AAR-D2). GE-V's verdict stands from a second, differently-played campaign.

**Score: 7 of 10, an empire contested.** Buy it for the tent; wait a patch for the table.

| Pillar | Sept 23 | Now | Why |
|---|---|---|---|
| Command & parsing | 7.5 | **7.5** | 141 of 142 offline at 0.80–0.95, prose included; the desk's question coverage and the Talleyrand verbs are the deductions. |
| Combat legibility | 7.5 | **7.0** | The solo garrison assault, the garrison-blind scout, "favorable" stalemates (AAR-4, AAR-24). |
| Marshal drama | 7.0 | **7.0** | The voices are the best in the game; the cadence and the vindication misfire (AAR-11, AAR-D3). |
| Narration | 7.0 | **7.5** | Berthier's breaking-line warning, Metternich, Soult's patrols, the raid rule in the headline; minus an armistice called a peace (AAR-15). |
| Diplomacy | 6.5 | **6.0** | AAR-1, AAR-2, AAR-3, AAR-7 on the surfaces of the deepest system. |
| Economy | 6.5 | **6.5** | Honest to the gold; the long peace (AAR-D7). |
| UI/UX | 7.0 | — | Not re-scored: the client was not opened. |
| AI aliveness | 7.0 | **7.5** | Russia's ninth night; Austria's garrison grind and the client-eating under peace are the costs. |
| First contact | 5.5 | **6.5** | The briefing; the desk still shrugs (AAR-17, AAR-18). |
| The ending | 5.5 | **5.5** | Written, not reachable (AAR-D2). |
| Naval | 7.0 | **6.5** | The beats are good; one throw of the dice is the whole road (AAR-D8). |
| **Directional** | ≈6.9 | **≈6.9** | Held. |

---

## §3 What the play found — defects

Thirty-two rows, filed in `BUG_FIXES.md` §Creative AAR with the producer and the fix shape on each. In order of what costs the player most.

| Row | Sev | The observation (verified at the wire; producer on the row) |
|---|---|---|
| AAR-1 | P1 | A lord's separate peace leaves its vassal at war with no army. The Treaty of Vienna (turn 9) resolved France–Austria only; `Austria|KingdomOfItaly` stayed active; Austria, at peace with France, took Piedmont (turn 10), Tyrol (turns 11–13) and stormed Milan's 10,000-man garrison (turn 17) — "the satellite is gone". The ratification named only Bavaria's displeasure. |
| AAR-2 | P2 | The settlement editor's two verdicts contradict on the coverage-drop route: Austria 51/50 "Will sign — will carry as drafted" beside "cannot be ratified now: the terms weigh heavier than their defeat", `can_ratify: false`, blocker "Term harshness" — the war-leader scorer (Britain, 32) gating an Austria-only settlement; the only road, "Make peace with Austria only", disabled for DP. |
| AAR-3 | P2 | "Request Revision" re-prices the proposer's own offer without its consent (Britain's turn-4 offer, laid back verbatim: Britain −32/50, harshness −33) and consumes the original offer. The accept route honours consent ("Their own terms — consents", turn 18). |
| AAR-4 | P2 | The scout report never mentions a garrison: "Ney scouts Vienna … No enemy forces detected." over 25,000 men. |
| AAR-5 | P2 | The dispatch's INTELLIGENCE row places an enemy at its old province after it advanced into a fully visible one (Buxhowden "Podolia [partial]" while the map had him at Hungary, 29,413, the morning after he took it). |
| AAR-6 | P2 | `recruit` is refused at zero military action points ("Not enough actions remaining. 0 actions left.") although it charges an administrative one; substitutes, keels and depots pass at zero military AP. |
| AAR-7 | P2 | Talleyrand's "Generous peace" and "Harsh demands" carry identical terms once the easing ladder has run (peace + Mack returned, demands []); the "Harsh demands" description promises territory and tribute. |
| AAR-8 | P2 | An unanswerable question: the end-turn report said Marmont was blocked at Provence "[REQUIRES INPUT]" while `/strategic_response` answered "Marmont has no pending interrupt" and the Orders tab held no order for him. |
| AAR-9 | P2 | An aggressive marshal abandons a standing order to rush to cannon fire in a war France is not party to (Massena, twice, for Bavaria's fights with Austria under the French peace). |
| AAR-10 | P3 | A corps that marches to reinforce a battle loses its standing order silently (`arriving.strategic_order = None`): Massena's march to Vienna vanished after reinforcing Soult on turn 10. |
| AAR-11 | P2 | The vindication verdict fires on the marshal's next battle, not on the insisted order: fortify insisted on turn 3, an attack of my own ordering lost on turn 8, "Massena's concerns were justified", trust −5, authority −5. |
| AAR-12 | P3 | Spending the last administrative action auto-ends the turn with no confirmation (turns 9 and 11) — the typed route has the envoy-lapse guard, this route none. |
| AAR-13 | P3 | The Starving/Crowded danger flag follows the marshal, not the province: "Lannes — Munich — Starving … two turns running" the morning after he left starving Swabia for a fed Munich; Ney "Crowded" alone at Bohemia; Murat "five turns running" at Vienna. |
| AAR-14 | P3 | The supply-strain headline names an enemy-held, garrisoned capital as the remedy: "Vienna can feed 50,000 more — a corps marched there ends it." |
| AAR-15 | P3 | An armistice is announced as peace: "Sire — peace with Russia is signed … the war ends in a stalemate" (twice) and a `peace_ratified` rail row, for "At War → Armistice". |
| AAR-16 | P3 | Foreign constructions announced in the player's terminal as if ours: "Construction complete: Market in Vienna!" (Austrian), "Supply Depot in Munich!" (Bavarian). |
| AAR-17 | P3 | The desk shrugs at the first question a player asks — "who am I fighting and why", "who are we at war with", "Is Vienna safe?", "What does Kutuzov have with him?", "How long until the armistice expires?" — while the dispatch beside it lists the wars. |
| AAR-18 | P3 | "what can I build" answers "No corps of ours stands on our own soil — there is nowhere to break ground" while `build market at Paris` then succeeds. |
| AAR-19 | P3 | The desk's "What I CAN do today" offered "Marmont, attack Moore" (Normandy to London across a shut crossing) and "Ney, attack Archduke Charles" (41,000 fortified in mountains). |
| AAR-20 | P3 | The typed Talleyrand verbs misroute while a mission runs: "recall Talleyrand" → "which nation shall I approach?"; "improve relations with Russia" → an advisory about Prussia. The ledger's own recall string works. |
| AAR-21 | P3 | The typed "improve relations with Britain" starts a relations mission with a court at war; the Cabinet hides that row. |
| AAR-22 | P4 | Raw tags and in-place walk-ins in copy: "KingdomOfItaly is already under French protection", "the Britain squadrons catch the transports", "Kutuzov marches from Bohemia into Bohemia unopposed", "Oudinot marches from Provence into Provence". |
| AAR-23 | P3 | The fortify objection does not disclose the auto-stance-shift price; insisting cost 2 AP where the direct order would have been refused honestly at 1. |
| AAR-24 | P3 | A garrison assault is solo and unannounced: three corps stood beside Ney at Vienna and none joined, with no muster line saying they would not. |
| AAR-25 | P3 | The counter-punch is announced only after it expires ("Bernadotte's Counter-Punch opportunity has expired!"); nothing on the previous morning said it existed. |
| AAR-26 | P3 | Ally settlement petitions (Bavaria for Tyrol, Spain for Leon) arrive with an enabled "Grant the Claim" that refuses ("the settlement table for this war is not open") and then stand in ENVOYS AWAITING RESPONSE for the rest of the campaign. |
| AAR-27 | P4 | The war label names courts that have left: "France + Spain + Holland + Bavaria + Kingdom of Italy vs Britain + Austria + Russia" four turns after Austria's peace. |
| AAR-28 | P4 | A conflict labelled HARD_STOP on the Austrian peace offer resolved silently into "−20 relation" aftermath. |
| AAR-29 | P3 | The live model's one answer invented commands ("Berthier, conduct a diplomatic mission to Bennigsen in Hungary") and the response recorded `parse_mode: mock` (IQ9-X3's shape). |
| AAR-30 | P4 | "Capital discount" applied to a levy at Vienna, an occupied enemy capital. |
| AAR-31 | P4 | "Marmont firmly objects: 'I have concerns about this order, Sire.'" — a cautious objection to a march with no reason named. |
| AAR-32 | P3 | Two "favorable" strikes on Kutuzov produced brutal stalemates: the muster verdict prices numbers, not the defender's stacked stance, personality and outnumbered bonuses (+30%); the same morning's preview called a lost mountain assault "even" without naming the attacker's leftover defensive stance. |

## §4 Design items

Filed in `DESIGN_REFINEMENT.md` §Creative AAR.

- **AAR-D1** The client's war is the lord's war. Whether a lord's peace should cover its satellites' pairs, whether an AI should prosecute a war against a court whose lord it has just signed with, and what the peace table must say either way — the design half of AAR-1.
- **AAR-D2** Status quo is a cession. The Congress counts "ceded by treaty"; a signed status quo that retains Vienna, Bohemia, Hungary and Moravia left them "held, unsettled". Uti possidetis in a ratified treaty is a title, and the road to 45 is four provinces shorter than the count says.
- **AAR-D3** The jealousy cadence: nine petitions in eighteen turns, a crown that passed to Oudinot for a four-thousand-man raid, "there is no one left to envy" when two corps broke. The ladder needs a floor under what counts as a laurel.
- **AAR-D4** Dispersion is taxed and dispersion is punished: three corps anywhere bleed to the crowding tax, and the Russian AI's concentric night broke exactly the corps the tax had spread. A balance note for the FA-D27 owner; the retreat's "friendly" list that omits an ally's and a vassal's capitals belongs beside it.
- **AAR-D5** Diplomatic points are the bottleneck of the diplomatic game: five a turn, two for a courtship, one for a client's petition, three for a separate peace. One granted petition cost the Austrian peace a turn. Whether the Seat's +1 should be the only lever.
- **AAR-D6** The Arbiter's Offer and the paying peace, from the player's chair: four British offers in seventeen turns (1,358g on turn 4; 2,330g on turn 9; a white peace keeping Provence; a Russian-mediated white peace) — evidence for Update 1's PR-D1b, plus the passive arm's 119,401 gold at the Verdict.
- **AAR-D7** The naval road for France in 1805 is one throw: a keel that fixes nothing under blockade, an expedition at 56% that cost 4,500 men and 24 sail. The honesty is exemplary; whether there should be a second road (pooling with Spain before the throw, a diversion that the expedition can wait for) is the question.
- **AAR-D8** The AI's garrison grind: two Austrian archdukes spent four turns assaulting a Bavarian garrison of 47, 24, 12, 6 and 3 men, losing 12, 6, 3 and 1. A floor under the AI's assault rung, or a garrison that surrenders under 500.

## §5 The two passive arms and the Verdict

**`aar-fastforward`** (over the wire, 30 turns, the driver's policy, `--diplomacy accept`): Austria took Swabia on turn 1 and Mack crossed into Franche-Comte on turn 2 against a France that gave no orders; Britain's turn-4 settlement was accepted (seven pairs resolved, 1,358 gold to France); threat 68 → 32 on turn 4 → 0 by turn 28; provinces 28 throughout; treasury 2,501 → 81,144; the army 183,415 → 139,136, every one of the missing 44,000 lost to the boot stack starving at Rhineland because nobody moved it. **The archived digest is the PR-D1b board a third time.**

**`aar-verdict-peace`** (in-process, seed `historical`, `--diplomacy accept`, `--stop-on-ending`): the same acceptance on turn 4, then forty quiet turns to **THE VERDICT OF HISTORY at Early July 1807 (turn 44), register `verdict`, marked, the campaign continues: AN EMPIRE CONTESTED — "The Empire holds what it held, and Europe has not accepted it. The field has gone against it more often than not, and the table is no kinder. History will call it unfinished — the question of 1805, still open."** THE RECORD: battles 7 (0 won, 2 lost), men lost 34,440, inflicted 24,959, provinces taken 0, lost 0, coalitions faced 1, peaces signed 1; treasury 119,401, threat 0. The register is the right one for a France that bought its peace and never fought again.

The Fall's three registers were read off the archived GE-2 arms (`ge2-eagle-falls`: "In late December 1806, at Burgundy, the Emperor was killed in the fighting … the city that had cheered his coronation walked past the bier in silence"; `ge2-chains`: Olmütz, "where Austria once kept Lafayette"; `ge2-soil-or-sword`: Elba). They were not re-driven this session.

## §6 Method, limits, routing

- **Instrument.** `tent.py` (session scratchpad) renders a `/command` response the way `main.gd` does — including the enemy-phase line builder from `enemy_phase_dialog.gd` — and lists every pending question with its answer syntax; answers go through the client's endpoints (`/respond_to_objection`, `/strategic_response`, `/marshal_petition_response`, `/capture_choice`, `/respond_to_diplomatic_dialogue`, `/mailbox/respond`). The settlement editor was driven with the wizard's own `action_params` (`settlement_cover_drop`, `settlement_demand_add`, `submit_settlement_for_review`). Every exchange is in the archived transcript.
- **The parser.** With `LLM_MODE=anthropic` and a key present, 141 of 142 commands were answered by the offline parser at 0.80–0.95 (mean 0.905); one question reached the model. The keyless build would have played this campaign identically but for that one line.
- **What was not done.** No client pass (the user was at the machine). The naval arc ended at the intercept. The Congress was never summoned (32 titled; alarm 97 at its highest, 36 at the end). The Fall was not reached. The hand-played campaign ended at turn 18 by the driver's `POST /new_game`; the standing memory now says: **save first, and never point `--http` at a campaign you want to keep.**
- **Also running on this machine:** a backend from the September 23 review still listens on port 8006 (started 9/23, a turn-7 world). I left it alone; it is the user's to kill.
- **Routing.** Defects → `BUG_FIXES.md` §Creative AAR; design → `DESIGN_REFINEMENT.md` §Creative AAR; STATUS ▶ NEXT UP carries the entry. **NEXT stays Update 1** (PR-D1b + PB-7), which this play reinforces from two more arms; **AAR-1 is a player report by the plan's own rule and should jump the queue beside it.**
