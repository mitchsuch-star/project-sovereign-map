# Round 4 review ledger — every finding of the November 20 review and its ruling (version 6)

Date: November 20, 2026. This is the ledger the spec names in `docs/INDEPENDENT_COMMAND_SPEC.md` §19.4 and §20.

**What ran.** Four code readers (R1 to R4), three design panels (P1, P2, P3) each run twice (two independent samples, written here as P1a and P1b, P2a and P2b, P3a and P3b), and an adversary panel (P4) run twice (P4a and P4b). All ran on Sonnet and all were read-only. Nothing was built or run by them.

**What it was.** A review of version 5 against the code and the user's new rulings. It was **not a scored round**: no marks out of 10 were asked, and the loop's bar from rounds 1 to 3 stands unmet. The user's own play outranks every panel.

**The user's words that day** (quoted from the spec's status block): *"review the new autonomous generla conmcept assure low authority autonomy isnt in conflict even removing it if needed and make sure buttons exist for simpler things but typing is used for missions and excepts a wide array if things and also if army has differner personalities they arent all doing same thing every turn etc full reveiw and u[pdates"*

**How findings are counted.** A finding is one claim, risk or recommendation in a report that needed a ruling. Each is one row below. Every ruling is one of: ACCEPT (written into version 6), ACCEPT IN PART (the part is said), ALREADY ANSWERED (the shipped game or version 5 already does it, and where), REJECT (with the reason from the spec), FILED (a defect row IC-V1 to IC-V4), or OPEN — NOT ANSWERED (version 6 does not answer it). Section numbers and decision numbers (D1 to D31) are those of the spec.

**Counts, taken from the tables below: 332 findings in all.**

| Report | Findings |
|---|---|
| R1 | 25 |
| R2 | 18 |
| R3 | 21 |
| R4 | 19 |
| P1a | 27 |
| P1b | 29 |
| P2a | 37 |
| P2b | 32 |
| P3a | 25 |
| P3b | 25 |
| P4a | 44 |
| P4b | 30 |
| **Total** | **332** |

| Ruling | Findings |
|---|---|
| ACCEPT | 223 |
| ACCEPT IN PART | 66 |
| ALREADY ANSWERED | 12 |
| REJECT | 21 |
| FILED | 10 |
| OPEN — NOT ANSWERED | 0 (3 when drafted; all three written into the spec before the commit) |
| **Total** | **332** |

Findings marked OPEN — NOT ANSWERED when the ledger was drafted: 3. All three were then written into the spec (see the last section); none is left open.

## R1 — involuntary acts in the shipped game against "on his own" (code reader)

Every way a French marshal acts without your order today, and what ties it to trust or authority. (25 findings.)

| ID | Rank | Finding | Ruling | Where v6 answers it |
|---|---|---|---|---|
| R1-1 | — | Authority never grants autonomy; the only standing "acts on his own" state is the trust crisis's Grant Autonomy, keyed on trust 20 or less alone. | **ACCEPT** — Written as the plain fact the design starts from. | §1.3 first bullet; §0 "Autonomy is only ever given"; §6.11; D31 |
| R1-2 | — | Low authority feeds the other involuntary acts indirectly: jealousy thresholds fall, a pressed order is refused more often, the Staff's order to several is not heard. | **ACCEPT** — Kept and named apart from autonomy. | §1.3 second bullet; §6.11 "Acts you did not order — kept"; D31 |
| R1-3 | — | The trust crisis's autonomy breaks five rules of the design: no dice (D9), "Tonight" is true, order of the turn, the count, and the name. | **ACCEPT** — Same five, same reasons. | §6.11; §1.3; D24 |
| R1-4 | — | Remove or re-found the trust crisis's grant rather than let it collide with the new feature. | **ACCEPT** — Removed by the user's consent and re-founded as a task to prove himself. | §6.11; D24; §17 |
| R1-5 | — | The old autonomy runs on the enemy's decision logic, with its moods and a random stream, so it is not deterministic. | **ACCEPT** — Named as the reason it goes; its code is deleted. | §1.3 (trust crisis bullet); §6.11 "Its code goes" |
| R1-6 | — | The old autonomy acts after the enemy phase and the advance, against the design's rule that his act comes first. | **ACCEPT** — The order of turn now says nothing else acts for a French marshal at turn's end. | §2 step 2 (version 6 note); §6.11 |
| R1-7 | — | Nothing shows what the old autonomous man will do before the turn ends, and no client code reads his report. | **ACCEPT** — Both facts are recorded; the report goes with the old engine. | §1.3 (trust crisis bullet); §1.3 table row "…but the client never shows his report" |
| R1-8 | — | A saved game can hold a man in the middle of the old three turns, with counters and a running score. | **ACCEPT** — An old save settles his score on loading by the same bands and says so in one morning line. | §6.11 "An old save"; §12 "Old saves", "Saves" |
| R1-9 | — | The old autonomy and the new one have opposite signs: forced at trust 20 or less against chosen at trust 30 or more. | **ACCEPT** — Given as one of the reasons for the removal. | §6.11 ("opposite sign") |
| R1-10 | — | The old autonomy silently uses the one place in the count for three turns, and is offered even when the count is full (the "2 of 1" case). | **ACCEPT** — The count now counts only men you set; the "2 of 1" rule is struck. | §6.4; §12 "The count" (struck row) |
| R1-11 | — | Shipped strings already say "on his own" and "AUTONOMY GRANTED", colliding with the new phrase and with plain words. | **ACCEPT** — The words leave the marshals' screens; a census test holds it. | §6.11 words table; §13 "The words census"; D1 |
| R1-12 | — | Below authority 30 every jealousy threshold falls to 1, so a bold, jealous, idle man is warned and strikes sooner. | **ACCEPT** — Kept as the felt cost of a weak grip, and named as indiscipline. | §1.3 second bullet; §6.11 "The jealous strike" |
| R1-13 | — | Nothing stops a man in the old autonomy from also making the jealous strike, so he can act twice in one turn. | **FILED** — Filed with a strict-xfail pin; the new strike guard skips a man on his own. | §1.3 third bullet (IC-V3); §6.5 last bullet; §19.4 "Defects" |
| R1-14 | — | The spec disagrees with itself on the strike: "follows, unchanged" against "never applies to a man on his own". | **ACCEPT** — One order: his pass first, then strikes for men with no order and no act, re-read on the board his acts left. | §2 step 2; §6.5; §12 "A jealous strike and his act aim at one enemy" |
| R1-15 | — | The pressed-order refusal (V2b) cannot touch a man on his own, but a change of his card would need the same objection road or an exemption; the spec was silent. | **ACCEPT** — His objection is read once at Give with no mood variance; no refusal is ever rolled on his own task. | §6.3; §6.11 last table; D30 |
| R1-16 | — | Ordinary objections (V2a) are prompts, deterministic apart from a mood variance call, and do not read authority. | **ACCEPT** — The new objection read leaves the mood variance out. | §6.3 ("without its mood variance") |
| R1-17 | — | The shadow petition asks for "a command of my own", exactly what the feature grants, but names no button today. | **ACCEPT** — "Give him a front" opens the line with his own proposal; an ineligible man is told why. | §6.9 "The petition"; §1.3 table row "A marshal can petition" |
| R1-18 | — | A literal man's restlessness counter may never reset if his exact orders do not count as being engaged. | **ACCEPT** — Any live exact order counts as work for his restlessness. | §7 (second to last bullet); §14 last row |
| R1-19 | — | A bold man's standing order yields to cannon fire within two provinces, which would make "Tonight" false for a bold man on his own. | **ACCEPT** — A man on his own is exempt, and his card says so. | §6.5 "He does not leave his task for distant cannon fire"; D30 |
| R1-20 | — | The arrival roll for a friend joining a neighbour's battle uses dice, so "Tonight" cannot promise it. | **ACCEPT** — Shown as "may", never promised; it is not his choice but the battle's. | §6.5; §2 step 4; §12 "He waited, and was drawn into a neighbour's battle" |
| R1-21 | — | A law paid in authority is refused below grip 60, which is exactly when men are most restless, so a weak-grip player cannot buy the second place. | **ACCEPT** — Authority never moves the count; the law's card says why it is refused before it refuses. | §6.4 "Authority never moves N"; D31 |
| R1-22 | — | The Staff's order to several is not heard below authority 50, and the new army task needs the same rule stated. | **ACCEPT** — An army's task obeys the same rule and says so before Give. | §9.1 last bullet |
| R1-23 | — | A whole army of men under one order will do the same thing each turn unless the spec states per-nature differences. | **ACCEPT** — Men differ in seven ways, none of them dice. | §6.7; D28; §9.1 |
| R1-24 | — | The vassal "autonomy" scale and the AI client "autonomy" are unrelated name clashes. | **ALREADY ANSWERED** — The vassals' word is exempt by name. | §0 words note; §13 "The words census" |
| R1-25 | — | Retiring the old arm needs an owner row, a landing slice, a STATUS line and a behaviour test (golden rule 9). | **ACCEPT** — Owner row IC, slice IC-9, with its done-when, STATUS line and rewritten tests. | §6.11 "The owner of the removal"; §15 Session 2 IC-9 |

## R2 — every order's click road (code reader)

A button inventory: what can be done with a click today and what is typed only. (18 findings.)

| ID | Rank | Finding | Ruling | Where v6 answers it |
|---|---|---|---|---|
| R2-1 | — | The records claim "every order has a button", which is false for about ten verbs. | **FILED** — Filed as IC-V4; STATUS and Help made true when the buttons land. | §1.3 fourth bullet (IC-V4); §8.1; §19.4 "Defects" |
| R2-2 | — | The Orders page of the Help and the boot help say the map's clicks give every order, which is untrue. | **FILED** — Part of IC-V4; the Help and boot help are made true in IC-7. | §8.1 last paragraph; §15 IC-7 |
| R2-3 | — | The game says typing is a convenience for most orders and never says typing is for standing tasks, the reverse of the user's request. | **ACCEPT** — Typing becomes the road for tasks and for asking; every simple order keeps a button. | §8 head; §8.2; §8.8; D25 |
| R2-4 | — | Chase (pursue) has no click road: the map offers only Attack on an enemy. | **ACCEPT** — A "Chase him" button beside Attack. | §8.1 table; §15 IC-7; IC-V4 |
| R2-5 | — | Hold on the card is the two-action strategic hold, and the one-action stand is typed only. | **ACCEPT** — "Stand here · 1 action" beside "Hold the ground · 2 actions". | §8.1 table |
| R2-6 | — | No click road composes a condition (hold until, hold unless) on an order. | **ACCEPT IN PART** — Conditions are typed, but word-chips under the filled line write them into the sentence. | §8.2 "Word-chips"; §8.3 |
| R2-7 | — | A march can carry a "then" tail that the card reads, but no control composes it. | **ACCEPT** — A small pick on the order card: then hold, fortify, dig in. | §8.1 table row "A march's then…" |
| R2-8 | — | Posture (stance) change has no button. | **ACCEPT** — A "Posture" menu on the general's card. | §8.1 table |
| R2-9 | — | Form square and break square have no button. | **ACCEPT** — In the Posture menu where the game allows them. | §8.1 table |
| R2-10 | — | A charge you start has no button; the charge and restrain choice appears only as a popup as a reckless horseman is about to charge. | **ACCEPT** — "Charge" / "Restrain" on a reckless horseman's card. | §8.1 table |
| R2-11 | — | Bombard has no button. | **ACCEPT** — "Bombard" beside Attack on a gun corps with a seen enemy in range. | §8.1 table |
| R2-12 | — | Scouting a named province is typed only; the button scouts where he stands. | **ACCEPT** — "Look at Swabia" on a click on a province he can look into. | §8.1 table |
| R2-13 | — | There is no per-marshal "wait" button. | **ACCEPT** — "Stay put", free, with its limits stated (not work for a literal man's restlessness, clears no warning). | §8.1 table |
| R2-14 | — | The group face offers only Hold, Fortify, Drill and a march; group attack, support, fall back and garrison are typed only. | **ACCEPT** — Those four are added beside Hold… Fortify… Drill…, each showing the list first. | §8.1 table last row; §15 IC-7 |
| R2-15 | — | The right-click or drag gesture for support is findable only from the boot help. | **ACCEPT IN PART** — The boot help is made true; no new support button is added because the gesture is a built road. | §8.1 "Built today" and last paragraph |
| R2-16 | — | The new "ask, change, give, recall" verbs need a click twin, and none exists for ask or recall. | **ACCEPT** — "Ask him", "Change" and "Stand him down" on a man's card in Session 3. | §8.1 last sentence; §8.6 |
| R2-17 | — | Nothing on screen yet maps to "on his own", "Tonight", the count or exact orders, and no stub exists. | **ALREADY ANSWERED** — Stated plainly: nothing version 6 adds is built; Session 3 builds the surfaces. | Status block; §15 Session 3 IC-10 |
| R2-18 | — | There is no "on his own" equivalent of the Cancel slot. | **ACCEPT** — Recall ("Stand him down") is free and has a button. | §6.3 "Recalling"; §8.1 last sentence |

## R3 — how far the typed line reaches for standing orders and conditions (code reader)

What the typed line takes today, what it refuses or drops, what its read-back shows, and what a task needs. (21 findings.)

| ID | Rank | Finding | Ruling | Where v6 answers it |
|---|---|---|---|---|
| R3-1 | — | Today's typed road is a closed grammar: four standing verbs, five kinds of "until", one if-then, one "then" tail. | **ACCEPT** — The word table widens it, with every word generated into the parser. | §8.3; §8.2; D26 |
| R3-2 | — | The read-back shows neither a condition it took nor a clause it dropped; both appear only after the order is sent. | **FILED** — Filed as IC-V2; the read-back's four rows close it. | §1.3 fifth bullet (IC-V2); §8.4; §15 IC-8 |
| R3-3 | — | "Ney, retreat if outnumbered" retreats now and drops the "if" without a word, because a one-word condition slips under the two-word floor. | **FILED** — Filed as IC-V1; its example row reads "Taken: fall back now; Not taken: if outnumbered". | §1.3 (IC-V1); §8.3 examples; §15 IC-8 |
| R3-4 | — | "Unless attacked, hold position" also runs as a plain hold with the clause lost. | **FILED** — Same class as IC-V1; refused or read back, never dropped in silence. | §1.3 (IC-V1); §8.4 row 2; §8.3 "unless" |
| R3-5 | — | Risk words such as "carefully" are stripped as filler and no order carries a risk field. | **ACCEPT** — "How bold" becomes a word-table part that moves one step of his own odds. | §8.3 "How bold"; §6.1 "Risk"; §14 (the order's `risk`) |
| R3-6 | — | A target is one place or one man, so a two-province hold is not read today. | **ACCEPT IN PART** — A two-province hold is read as one area; nothing wider. | §6.1 (last paragraph); §8.3 "Where" |
| R3-7 | — | Durations are only "for N turns" and "until turn N", with nothing like weeks or winter. | **ACCEPT** — Kept; seasons, weeks and "as long as it takes" are refused free with the nearest real sentence. | §8.3 "What the line refuses" |
| R3-8 | — | A second task in one sentence is only a relay that waits behind the first, not a stored plan, and the note says "waits" for something the relay may refuse. | **ACCEPT** — Refused free: "One task at a time", the first already written in. | §8.3 "What the line refuses" first item |
| R3-9 | — | Only one if-then trigger exists today (a foe within reach), so a task with several if-thens needs new deterministic, fog-honest triggers. | **ACCEPT** — Six new ifs and three new answers, read only from what his own nation sees. | §7 (last bullet); §15 IC-9 |
| R3-10 | — | An if-then needs a stored record with serialization and a save-format entry, not a hold with a hack. | **ACCEPT** — The order gets `if_thens`; every new field gets `to_dict`/`from_dict` and the save reference. | §14 "The order"; §12 "Saves" |
| R3-11 | — | The model path only fills the verb, and the grammar re-reads the condition from the text, but if the detector finds nothing the model's condition may survive. | **ACCEPT** — The parser re-reads conditions from the text every time; the model never writes a condition. | §8.5 |
| R3-12 | — | WS-12: a live-model parse feeds the model's own score into morale, trust and attack, breaking golden rule 6. | **ALREADY ANSWERED** — Ruled November 17, moved unchanged to IC-8: the model's number moves nothing. | §8.5; §8.7; §19.4 "WS-12" |
| R3-13 | — | GRD-33, the Grouchy ambiguity buff with no expiry, belongs with WS-12. | **ACCEPT** — Moved with WS-12 to IC-8. | §8.7 |
| R3-14 | — | Four open defects (UI6-X70, X73, X74, X75) make long typed orders silently drop a part. | **ACCEPT** — Moved from Session H's head to the head of IC-8. | §8.7; §15 IC-8; §20 |
| R3-15 | — | WS-14: the read-back calls a line "an answer" while a question stands, and Enter disagrees. | **ACCEPT** — Moved to IC-8 with the others. | §8.7 |
| R3-16 | — | The task road must read through one reader so the read-back, the line and the executor cannot drift. | **ACCEPT** — `parse_preview.read_one` serves all three. | §8.4 "One reader"; §14 "The line and the read-back" |
| R3-17 | — | Nothing may be spent before the player confirms; authoring should be free and pricing happen only on acting. | **ACCEPT** — Nothing is spent before Give; every quote is a pure read. | §8.4; §6.3; §19.4 adversaries' list |
| R3-18 | — | "When" and "in case" are refused today where "if" is read. | **ACCEPT** — "When", "should" and "in case" read as "if". | §8.3 "If … then" row |
| R3-19 | — | "Unless" is refused today. | **ACCEPT** — Offered back as the if-then it means. | §8.3 "What the line refuses" |
| R3-20 | — | A risk word must change a number the executor reads, never the model, and must not collide with "personality is character". | **ACCEPT** — It moves one step of his own authored odds and is shown as numbers. | §8.3 "How bold"; §6.1; §8.5 |
| R3-21 | — | Simple tasks fit buttons and the typed line is for combinations of a task with a limit and if-thens. | **ACCEPT** — The split into simple orders and typed tasks. | §8.1; §8.2 |

## R4 — do different personalities act differently? (code reader)

The enemy's decisions by nature today, the French roster, and what version 5 would have made of them. (19 findings.)

| ID | Rank | Finding | Ruling | Where v6 answers it |
|---|---|---|---|---|
| R4-1 | — | Today's enemy differs by three types only (aggressive, cautious, literal), not by man, and skills and abilities play no part in its decisions. | **ACCEPT** — Recorded as a finding of the review and the reason for §10.6. | §1.3 ("Today's enemy differs by type"); §10.6 |
| R4-2 | — | Two aggressive corps on one board differ only by strength, position, tiebreaks and an order-dependent mood draw. | **ACCEPT** — Same reading; the mood is noise, not character. | §1.3; §10.6 |
| R4-3 | — | Version 5 as written would make the bold men near-identical and the careful men dig in every night. | **ACCEPT** — The reason version 6 rewrote how the men differ. | §6.7 (version 6 paragraph); §1.3 ("Version 5 as written") |
| R4-4 | — | A pure per-man, per-turn draw is buildable and reload-stable but collides with "no dice" (D9). | **ACCEPT IN PART** — Kept only as R-VARIETY's written fallback, the day's nerve; D9 stands. | §6.7 "The fallback"; §13 R-VARIETY; D9 |
| R4-5 | — | The seeded helpers have pitfalls: the saved-state temper stream folds actions in, the AI and battle streams are order-dependent, and every helper collapses on the historical seed. | **ACCEPT** — The fallback uses the stateless hash, shown, zero on the historical seed. | §6.7 "The fallback"; §14 "His choice" |
| R4-6 | — | The enemy's daily mood is one stream per nation drawn in call order, so it shifts with how many corps were weighed before him. | **ACCEPT** — Re-keying it per man is an arm of Session 4's measure behind its own switch. | §10.6; §15 IC-14 |
| R4-7 | — | Directives are uniform by design, so variety belongs to what a man does on his own. | **ACCEPT** — Directives stay uniform; the men's differences live in §6.7. | §1.3 ("Directives are uniform by design"); §9.1 |
| R4-8 | — | Soult is literal and cannot be on his own, so his only variety is the exact-order if-thens the player writes. | **ALREADY ANSWERED** — Already the design's rule for every literal man. | §6.2; §7; D2 |
| R4-9 | — | Careful men repeat "dig in, wait" every night, and the spec's only limit was "the usual limit". | **ACCEPT** — Ways of waiting by nature, and the third-night rule. | §6.6 item 6; §6.7 points 3 and 4 |
| R4-10 | — | A bold Masséna told to hold would dig in and wait, against his own biography. | **ACCEPT** — A bold man strikes an enemy beside his area, in the field, once per order, shown under Tonight. | §6.7 point 1 table; point 2 (Masséna) |
| R4-11 | — | Murat's Hold would dig in, which cavalry already may not do. | **ACCEPT** — A horseman never digs in; his Hold is a screen. | §6.2 last bullet; §6.7 point 3 |
| R4-12 | — | Three bold men in reach of one enemy would all attack the same target every turn. | **ACCEPT** — One man per target, a second joins only when he needs the first; the line says so. | §6.7 point 5 |
| R4-13 | — | Only Davout's shipped ability bears on a solo task, so the other personal lines are only candidates. | **ACCEPT** — Davout keeps his; the rest are authored lines that never contradict the shipped ability. | §6.7 point 7; D15; §14 last warnings |
| R4-14 | — | Recommendation: odds should be the authored figure plus a skill term. | **REJECT** — It counts skills twice (the forecast has them) and hides a calculation. | §17 ("A skill term added to his odds") |
| R4-15 | — | Recommendation: let a shown, hash-drawn nerve of one step answer D9. | **ACCEPT IN PART** — Only as the fallback if R-VARIETY's bar is missed. | §6.7 "The fallback"; D9; §19.4 split table |
| R4-16 | — | Careful men need a non-waiting act (besiege, counter-attack a beaten enemy, fall back to better ground). | **ACCEPT** — Those are the careful man's list. | §6.7 point 3 |
| R4-17 | — | Bernadotte, with odds of 14, would wait on almost every board. | **ACCEPT IN PART** — Ways of waiting and a late start give him things to do; his odds figure stays authored with the user. | §6.7 points 3 and 7; §13 "Each marshal's own odds" |
| R4-18 | — | The odds differ only in a narrow band of forecasts, so men would agree outside it. | **ACCEPT** — Odds are spaced further apart than the risk step, and seven further ways of differing are added. | §6.1; §6.7; §13 R-VARIETY |
| R4-19 | — | Recommendation: key the enemy's mood per man and per turn by hash. | **ACCEPT IN PART** — Adopted only as an arm of IC-14 on its own gate, with the user's word, since it changes the old game. | §10.6; §15 IC-14 |

## P1 (first sample) — does autonomy as a punishment contradict autonomy as a reward?

A systems designer, a historian of the marshalate and a UX lead, working from R1 and spec §6.2–6.10. (27 findings.)

| ID | Rank | Finding | Ruling | Where v6 answers it |
|---|---|---|---|---|
| P1a-1 | — | The one true clash is the trust crisis's Grant Autonomy; remove it. | **ACCEPT** — Removed by the user's consent. | §6.11; D24 |
| P1a-2 | — | Replace it with a plain stand-down now and "a task to the letter" when exact orders land. | **ACCEPT IN PART** — Replaced by a task to prove himself under exact orders, built in the same commit as the removal; a plain stand-down is not adopted. | §6.11 "What takes its place"; §17; §19.4 split table |
| P1a-3 | — | Old saves should convert the remaining turns to a stand-down with no refund and no penalty. | **ACCEPT IN PART** — An old save settles his score on loading by the same bands instead. | §6.11 "An old save"; §12 "Old saves" |
| P1a-4 | — | Keep the jealous strike but rename it "rushes to battle without waiting for orders", never "on his own", and exclude a man on his own. | **ACCEPT IN PART** — Kept; its words become "attacks without waiting for orders"; a guard skips a man on his own. | §0 words table; §6.11; §6.5 last bullet |
| P1a-5 | — | The strike's warning row should carry buttons to put him on his own, give him an order, or let him. | **ACCEPT IN PART** — Two buttons: [Give him an order] and [Set him on his own]; leaving it is simply not pressing either. | §4 "TO DECIDE" (row 2); §6.11 |
| P1a-6 | — | Low authority speeding up jealousy is kept; the desk says "Restless: your authority is low". | **ACCEPT IN PART** — Kept as the felt cost of a weak grip; no new desk wording is written. | §6.11 "The jealous strike"; D31 |
| P1a-7 | — | V2b refusal is kept, in the words "refused your order". | **ACCEPT** — Same words. | §0 words table; §6.11 |
| P1a-8 | — | Changing the card of a man on his own is never insisted and never defied; he accepts or states an objection before Give. | **ACCEPT** — His objection is read once at Give, with no refusal rolled. | §6.3; D30 |
| P1a-9 | — | The shadow petition folds into the reward: "Give him a front" opens the card. | **ACCEPT** — It opens the line with his own proposal. | §6.9 "The petition" |
| P1a-10 | — | The cannon-fire redirect is kept for ordinary orders and exempted for a man on his own, Lannes's line excepted. | **ACCEPT** — A man on his own is exempt; his march to the guns is Lannes's line or the arrival roll. | §6.5; §6.7 point 7 |
| P1a-11 | — | Reinforcement arrival by dice is kept and shown as "may". | **ACCEPT** — Same. | §6.5; §2 step 4 |
| P1a-12 | — | The authority floors are kept, and the Staff's cost must be said before it is refused. | **ACCEPT** — The law's card says so before it refuses. | §6.4 |
| P1a-13 | — | V2a objections are kept; they are prompts and change nothing in the count. | **ACCEPT** — Unchanged. | §6.3 |
| P1a-14 | — | The literal restlessness counter is kept, and an exact order counts as engaged while live. | **ACCEPT** — Same. | §7 (second to last bullet) |
| P1a-15 | — | The audience's other arms (administrative role, dismiss, settle account) are kept. | **ACCEPT** — Pay what he is owed, a quiet post, dismissal all stay. | §6.11 "What takes its place" |
| P1a-16 | — | The last marshal must never be left with only a priced option. | **ACCEPT** — The task to prove himself is always offered. | §6.11 ("Always offered") |
| P1a-17 | — | A man below trust 30 may never be set on his own; the old redemption gets back only by a deed. | **ACCEPT** — Trust 30 stands; the trial's deed earns trust back. | §6.2; §6.11 |
| P1a-18 | — | Payoff bands should stay as today and be settled by a thirty-seed read before being written down. | **ACCEPT** — Bands kept from today; measured with the France band re-read. | §6.11; §13 ("A task to prove himself"); R-INERT |
| P1a-19 | — | A census test must grep player strings for "autonom", "independent" and "on his own" and expect them only where they belong. | **ACCEPT** — The words census. | §13 "The words census" |
| P1a-20 | — | The count's "2 of 1" sentence and its table line should be deleted. | **ACCEPT** — Struck. | §6.4; §12 "The count" |
| P1a-21 | — | Order of the turn: the on-his-own pass, then strikes for men with no order and no act, then the enemy; the strike needs an explicit guard. | **ACCEPT** — Same order; the guard is part of IC-10. | §2 step 2; §6.5; §15 IC-10 |
| P1a-22 | — | Retire "independent command" as the name of the three redemption turns. | **ACCEPT** — Retired. | D1; §6.11 |
| P1a-23 | — | The removal needs a deferral contract: owner row, slice, STATUS line, test (golden rule 9). | **ACCEPT** — Owner IC-9 with all four. | §6.11 "The owner of the removal" |
| P1a-24 | — | A player with a weak grip can still delegate, since the card has no authority gate; the feel is untested. | **ACCEPT** — Intended: authority never grants or bars the card; the user's own play outranks any measure. | §0; §6.4; §19.4 "Honest state" |
| P1a-25 | — | Players who liked the old redemption lose a free, easy way back. | **ACCEPT IN PART** — The way back stays, but it is a deed under exact orders, not a free grant. | §6.11 |
| P1a-26 | — | The historian says a man at trust 20 given a free hand is anti-historical. | **ACCEPT** — Used as a reason for the removal: Napoleon gave wide commands to men he trusted. | §6.11 ("opposite sign") |
| P1a-27 | — | On one card, men of different natures must give different results; the spec needs per-nature rows. | **ACCEPT** — Seven ways of differing, with R-VARIETY's bar. | §6.7; §13 R-VARIETY; D28 |

## P1 (second sample, P1_b) — does autonomy as a punishment contradict autonomy as a reward?

The same panel, a second independent sample. (29 findings.)

| ID | Rank | Finding | Ruling | Where v6 answers it |
|---|---|---|---|---|
| P1b-1 | — | One word, "autonomy", cannot mean both a prize and a penalty. | **ACCEPT** — Each phrase is given one meaning. | §0 words table; §6.11 |
| P1b-2 | — | History has both, but they were different things: Soult, Bernadotte and Masséna acted without leave; wide commands were granted. | **ACCEPT** — Indiscipline and grant are named apart. | §6.11 table "On screen / Who chose" |
| P1b-3 | — | Remove Grant Autonomy and replace it with "Stand him down". | **ACCEPT IN PART** — Removal adopted; the stand-down is not (a free trust farm). | §6.11; §17 ("Stand him down"); D24 |
| P1b-4 | — | Keep the jealous strike, rename it "goes in without leave", exclude a man on his own. | **ACCEPT IN PART** — Kept; worded "attacks without waiting for orders"; excluded. | §0 words table; §6.5; §6.11 |
| P1b-5 | — | The strike's desk row should read "[Give him a task] [Hold him]". | **ACCEPT IN PART** — Two buttons: [Give him an order] and [Set him on his own]. | §4 TO DECIDE row 2; §6.11 |
| P1b-6 | — | Low authority speeding jealousy is kept; Berthier says the marshals are restless because your word carries little. | **ACCEPT IN PART** — Kept; the exact line is not written. | §6.11; D31 |
| P1b-7 | — | V2b is kept for typed orders and never rolled on a card. | **ACCEPT** — No refusal is ever rolled on his own task. | §6.3; D30 |
| P1b-8 | — | V2a objections are kept. | **ACCEPT** — Unchanged. | §6.3 |
| P1b-9 | — | The shadow petition is kept and wired so "Give him a front" opens the card. | **ACCEPT** — It opens the line with his proposal. | §6.9 "The petition" |
| P1b-10 | — | A standing exact order counts as engaged for literal restlessness. | **ACCEPT** — Same. | §7 |
| P1b-11 | — | The cannon-fire redirect is exempted for a man on his own. | **ACCEPT** — Same. | §6.5; D30 |
| P1b-12 | — | Reinforcement arrival by dice is kept, and Tonight says "may be joined". | **ACCEPT** — Shown as "may". | §6.5 |
| P1b-13 | — | The Staff's order is unheard below authority 50 and the purchase floor is 60; the second place may then be unreachable when men are restless. | **ACCEPT** — Authority never moves N; the law's card says why before it refuses. | §6.4; §9.1 |
| P1b-14 | — | The vassal autonomy scale and the AI client autonomy are name clashes only. | **ALREADY ANSWERED** — Exempt by name. | §0 words note; §13 words census |
| P1b-15 | — | "Stand him down" would give +8 trust for three idle turns at the cost of an idle corps. | **REJECT** — A free trust farm with nothing to do. | §17 ("Stand him down"); §19.4 split table |
| P1b-16 | — | The last marshal should still be offered a free option, labelled "your army has no one else". | **ACCEPT IN PART** — The task to prove himself is always offered; no stand-down. | §6.11 ("Always offered") |
| P1b-17 | — | Old code (`_process_autonomous_marshals`, `_end_autonomy`, the debug arm) is deleted, and an old autonomous save loads as a stand-down. | **ACCEPT IN PART** — The code is deleted; an old save settles its score on loading rather than becoming a stand-down. | §6.11; §14 "The audience" |
| P1b-18 | — | Four phrases (on his own, without leave, refused, stood down) must never be swapped. | **ACCEPT IN PART** — A table of four phrases is kept, with "a task to prove himself" in place of "stood down". | §0 words table; §6.11 table |
| P1b-19 | — | The words "autonomy" and "independent command" leave every player string, including while_you_waited and the redemption dialog. | **ACCEPT** — The census holds it. | §6.11; §13 words census; §14 "The audience" |
| P1b-20 | — | The count should show stood-down men on their own line and delete the "2 of 1" sentence. | **ACCEPT IN PART** — "2 of 1" is struck; stood-down is moot because that state is not adopted. | §6.4; §17 |
| P1b-21 | — | Order of the turn: his pass, then strikes for men with no order and no act, then the enemy, then the advance and stand-down tick. | **ACCEPT IN PART** — Same order without a stand-down tick. | §2 step 2 |
| P1b-22 | — | On one identical card, six men must give at least three different Tonight lines, tuned over thirty seeds with the bar written first. | **ACCEPT** — R-VARIETY's bar. | §13 R-VARIETY; §13 "Each marshal's own odds" |
| P1b-23 | — | A typed order to several men must never override a man's card without a visible change. | **ACCEPT** — His row says "on his own — not included". | §9.1 (Directives bullet); §12 |
| P1b-24 | — | Every simple act needs a button, and the new ask, change, give and recall verbs each need a button twin. | **ACCEPT** — Same. | §8.1; §8.6 |
| P1b-25 | — | A strike has no exclusion for a man on his own today. | **FILED** — Filed as IC-V3 with its pin. | §1.3 (IC-V3); §6.5 |
| P1b-26 | — | The cannon-fire exemption makes a bold man on his own slow to help a neighbour; a playtest might show players hate it. | **ACCEPT** — Deliberate and on his card; the user's own play outranks any measure. | §6.5; §19.4 "Honest state" |
| P1b-27 | — | A grep census for the removed words must run before landing. | **ACCEPT** — The words census. | §13 "The words census" |
| P1b-28 | — | The old-save conversion needs a pin in the serialization test and the save reference. | **ACCEPT** — Required for every new or changed field. | §12 "Saves"; §6.11 tests |
| P1b-29 | — | The historian wanted a low-trust "goes his own way" state to survive. | **ALREADY ANSWERED** — It survives as the strike and the refusal, named apart. | §6.11 "Acts you did not order — kept" |

## P2 (first sample) — buttons for simple things, typing for tasks, a wide array

A strategy-UX designer, a parser engineer and a newcomer's advocate. (37 findings.)

| ID | Rank | Finding | Ruling | Where v6 answers it |
|---|---|---|---|---|
| P2a-1 | — | A simple order is one marshal, one verb, at most one place, no condition, limit or risk word, and has a button; a mission is the rest and is typed. | **ACCEPT** — Same line; the screen says "task", not "mission". | §8.1; §8.2; §0 words table |
| P2a-2 | — | Typing is also the road for asking and for any simple order the player prefers to type, and is never the only road to a simple order. | **ACCEPT** — Same. | §8.6; §8.8 |
| P2a-3 | — | Chase, the one-action stand and a named-province scout need buttons. | **ACCEPT** — "Chase him", "Stand here · 1 action", "Look at Swabia". | §8.1 table |
| P2a-4 | — | Posture, form and break square, bombard, and a player-started charge or restrain need buttons. | **ACCEPT** — Same menus and chips. | §8.1 table |
| P2a-5 | — | A per-marshal "stay put this turn" button, free, is needed. | **ACCEPT** — "Stay put" with its limits. | §8.1 table |
| P2a-6 | — | The group face needs attack, support, retreat and garrison beside Hold, Fortify and Drill. | **ACCEPT** — Same. | §8.1 table last row |
| P2a-7 | — | A march's "then" tail should be a small dropdown on the order card. | **ACCEPT** — A small pick on the order card. | §8.1 table |
| P2a-8 | — | Ask, recall and give need a click twin: "Ask him" and "Stand down" on the card. | **ACCEPT** — Same, in Session 3. | §8.1 last sentence; §8.6 |
| P2a-9 | — | The three untrue lines (STATUS "every order has a button", the Orders tab footer, the boot help) must be corrected. | **FILED** — Filed as IC-V4. | §8.1 last paragraph; §1.3 (IC-V4) |
| P2a-10 | — | Every button gap needs an owner row, landing slice, STATUS line and behaviour test, or the promise is removed. | **ACCEPT** — One table `SIMPLE_ORDER_BUTTONS`, owner IC-7, with its pin. | §8.1; §15 IC-7 |
| P2a-11 | — | The mission grammar is a closed set of fixed parts and the model only maps wording onto them. | **ACCEPT** — The word table, generated into the parser. | §8.3; §8.5; D26 |
| P2a-12 | — | Risk words should map to fixed odds floors (careful 12 to 10, normal 8 to 10, bold 6 to 10) and "at any cost" to no floor. | **REJECT** — A word must not override a man's own odds; a word moves one step. | §17 ("Fixed risk floors"); §6.1; §8.3 "How bold" |
| P2a-13 | — | "The line of the Inn" and "between X and Y" should be authored areas. | **REJECT** — A river line or a stretch is refused free; name one or two provinces. | §8.3 refusals; §17; §18 |
| P2a-14 | — | "Their main army" should be a target meaning the largest seen enemy force. | **REJECT** — Refused: "Name its commander"; a fog hazard. | §8.3 refusals; §17 |
| P2a-15 | — | A hold may name two provinces joined by "and". | **ACCEPT IN PART** — Taken as one area, he does one thing a turn inside it. | §6.1; §8.3 "Where" |
| P2a-16 | — | The if-then list needs new triggers (attacked, outnumbered, surrounded, a friend attacked, a place falls, a friend arrives, a named foe). | **ACCEPT** — The eight ifs and five thens of §7. | §7; §8.3 "If … then" |
| P2a-17 | — | "First X, then Y" should be a two-step chain. | **REJECT** — A second task in one sentence is refused free; the first is written in. | §8.3 refusals; §17 ("Two-step tasks"); §6.1 note |
| P2a-18 | — | Duration words other than turns (a week, winter, spring) should be refused with a helpful answer. | **ACCEPT** — "Say 'for N turns' or 'until turn N'". | §8.3 refusals |
| P2a-19 | — | The panel's 34 example lines each name what they map onto and whether the code reads them today. | **ACCEPT IN PART** — The spec keeps the examples with a landing slice each; lines built on refused ideas are not kept. | §8.3 "Examples" |
| P2a-20 | — | "Ney, retreat if outnumbered" must read back "Taken: fall back now. Not taken: if outnumbered" with a one-click fix. | **ACCEPT** — Its example row. | §8.3 examples; §8.4; IC-V1 |
| P2a-21 | — | The read-back has four fixed rows (taken, not taken, his answer, price); a half-understood line cannot be sent as it is. | **ACCEPT** — Give reads "Send what I understood" and sends the restated line. | §8.4; D27 |
| P2a-22 | — | The preview, the confirm card and the executor must use one reader, and the model never fills the condition. | **ACCEPT** — `parse_preview.read_one` serves all; the parser re-reads conditions. | §8.4 "One reader"; §8.5; §8.7 |
| P2a-23 | — | An ambiguous name should draw one question with buttons ("Which Ney: the marshal or the road?"), spending nothing. | **ACCEPT** — added after the fresh readers' check: a name that could mean two things draws one question with a button for each reading, nothing spent (row PW's "did you mean Ney?" road). | §8.3 (what the line refuses) |
| P2a-24 | — | A named foe the marshal cannot see should read back "not in our sight". | **ACCEPT IN PART** — An unseen enemy and a name that does not exist get the same answer, so the read-back must not say "not in our sight". | §8.3 "Whom"; §12 (typed task naming an unseen enemy) |
| P2a-25 | — | A careful man given "at any cost" should read back a plain warning with a Change button, not be refused by mood. | **ACCEPT IN PART** — "At any cost" is one step bolder and a careful man states his objection. | §8.3 "How bold"; §12 |
| P2a-26 | — | A man under trust 30 cannot go on his own, and the line should say so in plain words. | **ACCEPT** — Trust 30 is the gate; the petition says why in plain words. | §6.2; §6.9 "The petition" |
| P2a-27 | — | A literal man given "on your own" should read "Soult follows orders to the letter". | **ALREADY ANSWERED** — His answer is already written for him. | §6.2 ("Give me my orders to the letter, Sire"); D2 |
| P2a-28 | — | Words that need a new mechanic (avoid, protect the baggage, race a friend, seasons) are refused with the nearest real task pre-filled. | **ACCEPT** — Refused free with the nearest real sentence. | §8.3 "What the line refuses" |
| P2a-29 | — | The card should stay as a fallback form with the same fields as the line. | **REJECT** — No separate form; the chips under the filled line are the form. | §17 ("The card with [Give] and [Change]"); §18; §19.4 split table |
| P2a-30 | — | A mission must not be counted as a fifth task; it is a task plus optional parts. | **ACCEPT** — Stated in the spec. | §6.1 note; §8.3; D11 |
| P2a-31 | — | A "Give a mission" button should open the line pre-filled with three examples built from the board. | **ACCEPT IN PART** — "Give him a task…" opens the line already written with his own proposal; the screen says "task". | §8.2; §6.9; §0 words table |
| P2a-32 | — | Tab completion, a hint under the box, the first-open line and a Help page should teach the grammar. | **ACCEPT** — Same four. | §8.2 |
| P2a-33 | — | Without a key the fixed parser reads everything; with a key the model maps freer wording onto the same parts only. | **ACCEPT** — Same. | §8.5 |
| P2a-34 | — | WS-12 must be closed before the mission road ships; the panel recommends retiring the bonus. | **ALREADY ANSWERED** — Ruled November 17: the model's number moves nothing; moved to IC-8's head. | §8.5; §8.7; §19.4 |
| P2a-35 | — | Sequencing: close the dropped-part defects first, then the read-back and the buttons, then the new fields, last on his own. | **ACCEPT** — Session 2 before Session 3, with IC-8's head defects first. | §8.7; §15 Sessions 2 and 3 |
| P2a-36 | — | The risk thresholds are placeholders to be settled over thirty seeds. | **ACCEPT IN PART** — Moot for named floors; the risk step is one man in ten and is settled by R-READ. | §13 "The risk step" |
| P2a-37 | — | Risk words as typed words only or as a three-step pick on the card: both, one source. | **ACCEPT** — Typed words and chips write the same field. | §8.2 chips; §6.1 "Risk" |

## P2 (second sample, P2_b) — buttons for simple things, typing for tasks, a wide array

The same panel, a second independent sample. (32 findings.)

| ID | Rank | Finding | Ruling | Where v6 answers it |
|---|---|---|---|---|
| P2b-1 | — | A simple order is one verb, one target or none, standing without a condition, and has a button; a mission is typed or built on the card. | **ACCEPT IN PART** — Same line for simple orders; a task is typed, with chips and no card. | §8.1; §8.2 |
| P2b-2 | — | Pursue (on the selection card), the second hold chip for the one-action stand, and a targeted scout need buttons. | **ACCEPT** — "Chase him", "Stand here · 1 action", "Look at Swabia". | §8.1 table |
| P2b-3 | — | Stance change, form and break square, bombard and a player-started charge or restrain need chips. | **ACCEPT** — Same. | §8.1 table |
| P2b-4 | — | "Wait" should be End Turn, and the typed "wait until next turn" should be dropped as a promised button. | **REJECT** — A free "Stay put" button is built and the typed verb stays. | §8.1 table ("Stay put") |
| P2b-5 | — | Group attack, support, retreat and garrison need to join Hold…, Fortify… and Drill…. | **ACCEPT** — Same. | §8.1 table last row |
| P2b-6 | — | "Ask him" and "Stand him down" are the click twins of the new verbs. | **ACCEPT** — Same. | §8.1 last sentence; §8.6 |
| P2b-7 | — | Conditions, a "then", a duration and a two-province area are deliberately not buttons; they are missions. | **ACCEPT IN PART** — They are typed tasks, but chips write them into the sentence; a march's "then" also gets a small pick. | §8.2 chips; §8.1 table |
| P2b-8 | — | The task list should include march, fortify, scout and fall back as tasks. | **ACCEPT IN PART** — Only take, chase, hold and support are tasks; the others stay single orders or a "then". | §8.3 "Task" and "Then"; D11 |
| P2b-9 | — | The area may be one province, two joined by "and", "between X and Y" or "the line of <river>". | **ACCEPT IN PART** — Two provinces for a hold only; the river line and "between" are refused. | §8.3 "Where" and refusals; §17 |
| P2b-10 | — | Risk words should map to an odds floor (careful 8 to 10, bold 6 to 10, at any cost no floor). | **REJECT** — One step of his own odds only. | §17 ("Fixed risk floors"); §6.1 |
| P2b-11 | — | The condition list includes the eight ifs and five thens of §7. | **ACCEPT** — Same. | §7; §8.3 |
| P2b-12 | — | "The main army" should be a target (the strongest seen corps of that nation). | **REJECT** — Refused: "Name its commander". | §8.3 refusals; §17 |
| P2b-13 | — | "First X, then Y" should be a stored two-step list reusing the plan-step record. | **REJECT** — A second task in one sentence is refused free. | §8.3 refusals; §17 |
| P2b-14 | — | The panel's 35 examples say which the parser reads now and which are new. | **ACCEPT IN PART** — §8.3 keeps examples with a landing slice; refused ones are not kept. | §8.3 "Examples" |
| P2b-15 | — | New mechanics are needed for outnumbered, attacked and surrounded triggers, a stored risk word, a two-province area, river lines, "the main army" and a stored two-step list. | **ACCEPT IN PART** — Triggers, risk step and two-province hold are built; river lines, main army and two-step lists are refused. | §7; §14 "The order"; §8.3 refusals; §17 |
| P2b-16 | — | "Unless", weeks and seasons, "for as long as it takes", recruit or build or spend or treaty words, and anything about a diplomat are refused with an answer. | **ACCEPT** — Same list. | §8.3 "What the line refuses" |
| P2b-17 | — | The read-back is four lines, and any clause that cannot be read blocks Give until "go without it"; the two-word floor goes. | **ACCEPT IN PART** — Blocks only a part that changes what he does; filler is a quiet note; the floor is IC-V1. | §8.4 row 2; D27; §1.3 (IC-V1) |
| P2b-18 | — | The three false "every order has a button" lines must be corrected. | **FILED** — Part of IC-V4. | §8.1; §1.3 (IC-V4) |
| P2b-19 | — | An ambiguous name such as "Davout and Ney" should draw a "Which?" card with both as buttons. | **ACCEPT IN PART** — a name that could mean two things draws the "which?" question with buttons; but "Davout and Ney" is a list of names, which the user's ruling "One list for all" reads as an order to both (a directive), not as an ambiguity. | §8.3; §9.1; §230 |
| P2b-20 | — | A mission naming an unseen corps should be refused "we do not see him". | **ACCEPT IN PART** — Refused with the same answer as a name that does not exist. | §8.3 "Whom"; §12 |
| P2b-21 | — | A mission against his nature or trust is refused in the man's own line with an "order him for today instead" button. | **ACCEPT IN PART** — A task against his nature draws his objection with today's answers; trust is the gate; no such button is written. | §12 "A task against his nature"; §6.2; §6.9 |
| P2b-22 | — | A mission that duplicates or contradicts a standing one should say "already holding Milan; replace it?". | **ACCEPT** — The price row says what it replaces. | §8.4 row 4 |
| P2b-23 | — | When the count is full the card should say whom to recall first, as buttons. | **ACCEPT** — The read-back says so and offers to recall another man. | §12 "The count is full" |
| P2b-24 | — | The model only names parts and the parser re-reads the text, unconditionally on the task road. | **ACCEPT** — Same. | §8.5 |
| P2b-25 | — | The dropped-part defects (X70, X73, X74, X75, WS-14) land before or inside the task slice, and WS-12 is ruled first. | **ACCEPT** — They head IC-8. | §8.7; §15 IC-8 |
| P2b-26 | — | The task card should stay as a real second road for newcomers, not just a fallback. | **REJECT** — No separate form; chips write the sentence. | §17; §18; §19.4 split table |
| P2b-27 | — | The model should show its mapping ("I read 'keep an eye on' as: hold"), and with no key a closed refusal with two example buttons should answer. | **ACCEPT IN PART** — The model maps onto the same parts and a refusal carries the nearest real sentence; showing the mapping is not written. | §8.5; §8.3 refusals |
| P2b-28 | — | Typing is also the only road for a condition, a duration, a two-province area and a long line, and §8 should say so. | **ACCEPT** — §8 says typing is the road for tasks and asking. | §8.2; §8.8; D11 |
| P2b-29 | — | The remaining open items (risk floors, "main army" meaning, river-line list) need owners. | **REJECT** — All three are refused, not promised. | §8.3 refusals; §17; §18 ("none is a promise for later") |
| P2b-30 | — | Group buttons are not worth the cost since "everyone, attack Mack" works typed (parser engineer's dissent, overruled). | **ACCEPT** — Overruled; group buttons are built. | §8.1 table last row |
| P2b-31 | — | A table of what you want, what you say and what you pay (ask, change, give, exact orders, recall) should sit in §8. | **ACCEPT** — §8.6's table. | §8.6 |
| P2b-32 | — | The card should open on a sentence with "Tonight" and [Give] and [Change]. | **ACCEPT IN PART** — The line opens already filled with his proposal; it is a line, not a card. | §6.9 (version 6); §8.2 |

## P3 (first sample) — different men, different nights

A designer of character-driven AI, a historian of 1805–1809 command and a hardcore player. (25 findings.)

| ID | Rank | Finding | Ruling | Where v6 answers it |
|---|---|---|---|---|
| P3a-1 | — | Version 5 makes the bold men near-copies and the careful men repeat "dig in", which is the user's worry. | **ACCEPT** — The reason for §6.7's rewrite. | §1.3; §6.7 (version 6 paragraph) |
| P3a-2 | — | Variety must come from authored lines, nature-specific acts and a shown seeded temper, not from mid-turn dice. | **ACCEPT IN PART** — Authored lines and nature-specific acts are adopted; the seeded temper is only a fallback. | §6.7; D28; §13 R-VARIETY |
| P3a-3 | — | The authored odds should not include a skill term, which would count skills twice. | **ACCEPT** — Same reason. | §17 ("A skill term added to his odds") |
| P3a-4 | — | The temper should be shown whenever it is not zero. | **ACCEPT IN PART** — If the fallback is built, it is shown on his line. | §6.7 "The fallback" |
| P3a-5 | — | Bernadotte's slowness should be a delay, shown, capped at one turn per order. | **ACCEPT** — He starts a new task one night late, once per order, and the line says so. | §6.7 point 7 |
| P3a-6 | — | D9 should be amended from "no moods, no dice" to "no hidden dice". | **REJECT** — D9 stands; a written fallback exists if the bar is missed. | D9; §19.4 split table ("A daily seeded temper") |
| P3a-7 | — | Temper should be a pure hash of seed, turn and man, not the saved-state stream and not the AI or battle streams. | **ACCEPT IN PART** — The fallback uses the same stateless hash with the same constraints. | §6.7 "The fallback"; §14 "His choice" |
| P3a-8 | — | Temper cannot break "Tonight is true" and is zero on the historical seed. | **ACCEPT IN PART** — True of the fallback, which is not built unless needed. | §6.7 "The fallback" |
| P3a-9 | — | Placeholder weights: bold 30% more risk and 20% less; careful 15% more and 35% less. | **REJECT** — The fallback leans with his nature only: a bold man steady or bolder, a careful man steady or more careful, three days in ten. | §6.7 "The fallback"; §13 ("The day's nerve") |
| P3a-10 | — | The bar: fewer than 40% same act, no man with temper on over 55% of turns, temper changing the act under 25%. | **ACCEPT IN PART** — R-VARIETY keeps the 40% clause, adds the third-night rule and two kinds of act; the 55% and 25% clauses are not adopted. | §13 R-VARIETY |
| P3a-11 | — | Each man's proposal comes from his nature and line (Ney, Murat, Lannes, Masséna, Davout, Bernadotte). | **ACCEPT** — The proposals table. | §6.7 point 2 |
| P3a-12 | — | Soult and the Emperor are offered no proposal; Soult gets exact orders. | **ACCEPT** — Neither can be set on his own. | §6.2; §7 |
| P3a-13 | — | Nobody drills on his own because a drilling corps is locked out of the fight. | **ACCEPT** — Same reason. | §6.6 item 6; §6.7 point 3 |
| P3a-14 | — | A bold man's idle acts are probe, scout, and dig in only if walled or outnumbered by more than 1.4 to 1. | **ACCEPT IN PART** — Probe, look and strike; the spec gives a bold man no dig-in. | §6.7 point 3; §14 "Not verified" |
| P3a-15 | — | A bold Hold should get a counter-strike once per order, in the field only. | **ACCEPT** — Strikes an enemy beside his area at his odds, shown under Tonight. | §6.7 point 1 table |
| P3a-16 | — | A careful man's idle acts: dig in, siege a walled place, fall back to better ground, counter-attack a force he beat off. | **ACCEPT** — Same list. | §6.7 point 3 |
| P3a-17 | — | Murat's Hold is a screen because cavalry never digs in. | **ACCEPT** — Same. | §6.2; §6.7 point 3 |
| P3a-18 | — | A man must not take the same idle act three nights running, tracked in a saved `idle_log`. | **ACCEPT** — A saved record of his last waiting acts. | §6.7 point 4; §12 "Saves" |
| P3a-19 | — | Davout's dig-in stops making sense once his stacks are full, so on the fourth night he moves to another act. | **ACCEPT** — A dig-in stops being sensible at the usual limit; Davout's at three stacks. | §6.7 point 4 |
| P3a-20 | — | Several men on their own must not pile on: rank order, targets taken removed, a second man joins only if his odds need the first. | **ACCEPT** — One man per target. | §6.7 point 5 |
| P3a-21 | — | Authored personal lines: Lannes to the guns, Bernadotte late, Davout does not fall back, Murat follows two provinces, Ney at once, Masséna keeps a walled place. | **ACCEPT** — The same six lines. | §6.7 point 7 |
| P3a-22 | — | A mixed named army under one mission should be one list with roles by nature and derived exact lines for men over the count. | **REJECT** — The commander is set on his own and the rest support him by today's rules; directives stay uniform. | §9.1; D29; §19.4 split table |
| P3a-23 | — | Three worked 1805 turns show five different men doing five different things. | **ACCEPT IN PART** — Illustrative only; the rules are §6.7 and the spec's own mornings are in §3. | §6.7; §3 |
| P3a-24 | — | The enemy's mood should be keyed per man by the same hash; file it as a sibling row. | **ACCEPT** — An arm of IC-14. | §10.6; §15 IC-14 |
| P3a-25 | — | Unverified: exact probe and scout costs, the real adjacencies of the worked turns, and the 1.4 to 1 threshold. | **ACCEPT IN PART** — The builder reads them; the 1.4 to 1 threshold is not adopted. | §14 "Not verified" |

## P3 (second sample, P3_b) — men of different natures, and different men of one nature

The same panel, a second independent sample. (25 findings.)

| ID | Rank | Finding | Ruling | Where v6 answers it |
|---|---|---|---|---|
| P3b-1 | — | Temper should lean with character, range one step, and be displayed as a number before the order. | **ACCEPT IN PART** — Held only as the written fallback. | §6.7 "The fallback" |
| P3b-2 | — | D9 should be amended to "no hidden dice", the one draw being the man's temper for the day, from the stateless hash. | **REJECT** — D9 stands. | D9; §19.4 split table |
| P3b-3 | — | Temper must not use the saved-state stream or the AI and battle streams, so asking, undoing and reloading cannot move it. | **ACCEPT IN PART** — The fallback uses the stateless hash and is never saved. | §6.7 "The fallback"; §12 "Saves" |
| P3b-4 | — | On the historical seed temper is zero for everyone. | **ACCEPT IN PART** — True of the fallback. | §6.7 "The fallback" |
| P3b-5 | — | A purity test should pin that his reading calls only the seeded hash and never the AI stream or mood threshold. | **ACCEPT** — The purity test; the reading must not call `_get_mood_adjusted_threshold` or `ai_rng`. | §13 R-INERT; §14 "His choice" |
| P3b-6 | — | Temper and the player's risk setting stack but are capped at two steps from his authored figure. | **ACCEPT** — The cap is two steps, and the read-back shows all three numbers. | §6.1 "Risk"; §13 |
| P3b-7 | — | Reject the skill term added to authored odds. | **ACCEPT** — Same. | §17 |
| P3b-8 | — | Odds are authored once per man and spaced so no two bold men sit within one. | **ACCEPT IN PART** — Spaced further apart than the risk step. | §6.1; §13 |
| P3b-9 | — | Each man's proposal is picked by a pure function, with Bernadotte's card warning "slow to join a fight". | **ACCEPT** — The proposals table and its line. | §6.7 point 2; point 7 |
| P3b-10 | — | Careful men propose Take only where the place is empty or weak; bold men propose Hold only when nothing is worth taking. | **ACCEPT IN PART** — "A bold man takes; a careful man holds"; the finer conditions are not written. | §6.7 point 2 ("Any other") |
| P3b-11 | — | Waiting is a short menu of real acts (dig in, look, shift within the area, wait). | **ACCEPT** — The same acts, by nature. | §6.7 point 3 |
| P3b-12 | — | Drilling stays banned on his own, and Soult's exact order is his road to drill. | **ACCEPT IN PART** — The ban is written; Soult's drill under exact orders is not stated. | §6.7 point 3 |
| P3b-13 | — | A man never takes the same idle act a third night running, and says why, or says "nothing has changed". | **ACCEPT** — Same. | §6.7 point 4 |
| P3b-14 | — | Cavalry's menu never contains dig in. | **ACCEPT** — Same. | §6.2; §6.7 point 3 |
| P3b-15 | — | A bold Hold gets teeth: a strike on an enemy inside or on the road into the area, once per order. | **ACCEPT** — Same. | §6.7 point 1 table |
| P3b-16 | — | One man per target; a second bold man may join; a careful man covers the road; a Pursue is one man per army. | **ACCEPT** — Same. | §6.7 point 5 |
| P3b-17 | — | A mixed-nature army under one mission is shown as one list, roles by nature, extra men given derived exact lines. | **REJECT** — The commander on his own, the rest supporting. | §9.1; D29 |
| P3b-18 | — | The enemy's mood needs a sibling row, keyed per man. | **ACCEPT** — An arm of IC-14. | §10.6 |
| P3b-19 | — | Lannes's shipped ability does bear on Support, so R4's claim that it adds nothing is wrong for that task. | **ACCEPT** — Lannes proposes Support; his "to the guns" bears on it. | §6.7 point 2 |
| P3b-20 | — | The panel ruled the historian's lean, a one-step range and the player's display rule. | **ACCEPT IN PART** — Only for the fallback. | §6.7 "The fallback" |
| P3b-21 | — | A draft §6.1 sentence should add temper to the card ("give or take a day's temper"). | **REJECT** — §6.1 carries the risk step and recent record as numbers instead; temper is a fallback. | §6.1; D9 |
| P3b-22 | — | Tests to pin: purity, temper identical across ask, undo, give and reload, Tonight equals the act, historical zero, no third-night repeat, two bold men never attack one target alone unless the combined forecast meets both bars. | **ACCEPT IN PART** — R-TRUE, R-VARIETY and the purity test pin most; the join rule is §6.7 point 5. | §13 R-TRUE, R-VARIETY, R-INERT; §6.7 point 5 |
| P3b-23 | — | The share of restless days is open, three in ten as a placeholder. | **ACCEPT** — The fallback's row uses the same placeholder, settled by R-VARIETY. | §13 ("The day's nerve") |
| P3b-24 | — | Three worked 1805 turns show different acts every night. | **ACCEPT IN PART** — Illustrative; rules are in §6.7. | §6.7; §3 |
| P3b-25 | — | When a man's Pursue target leaves his ring he stops and asks, shown as one row in TO DECIDE. | **ACCEPT** — Same. | §6.1 "Pursue"; §6.8; §4 |

## P4 (first sample) — the adversary panel

An engineer who knows this code's traps, a QA lead and an enemy-side designer, told to break P1, P2 and P3. Rank is the panel's severity (1 = must fix first). (44 findings.)

| ID | Rank | Finding | Ruling | Where v6 answers it |
|---|---|---|---|---|
| P4a-1 | 1 | Removing the old grant strips the trust-recovery road and its +10 authority payoff, turning a risk-and-reward into a free wait. | **ACCEPT** — The trial keeps the deed and the bands, authority +10 included. | §6.11 "What takes its place"; D24 |
| P4a-2 | 1 | A free stand-down would let a player farm trust back to the gate. | **ACCEPT** — Stand-down is not adopted; the trial needs a deed and keeps the audience's cooldown. | §17; §6.11 ("Given only through the audience") |
| P4a-3 | 1 | An old save in the middle of the old autonomy must not convert silently or drop its pending payoff. | **ACCEPT** — It settles by the same bands on loading, with one morning line. | §6.11 "An old save" |
| P4a-4 | 2 | Stand-down for the last marshal is a free three turns off; say it plainly on the button. | **ACCEPT** — Moot: the trial is always offered and stand-down is not adopted. | §6.11 ("Always offered"); §17 |
| P4a-5 | 2 | A card change must read the pure concern with no mood variance and never be insisted, or V2b's dice come back through the side door. | **ACCEPT** — Read once at Give without mood variance; no refusal rolled. | §6.3; D30 |
| P4a-6 | 2 | The petition button must handle an ineligible man and never be a dead button. | **ACCEPT** — The petition says why and offers "He stays with me". | §6.9 "The petition"; §12 |
| P4a-7 | 2 | The cannon-fire exemption leaves two different "march to the guns" behaviours, so the card must say so. | **ACCEPT** — His card says he will not leave his task for a distant battle; only Lannes's line or the arrival roll applies. | §6.5 |
| P4a-8 | 1 | Recalling and re-setting the slot each turn lets a player cycle men for free and probe each one's reading. | **ACCEPT** — A man does nothing the night he is given; moving the place costs 2 actions and a lost night. | §6.3 last bullet; §12 |
| P4a-9 | 3 | The words test should also cover the Help strings and exempt or remove the debug arm. | **ACCEPT IN PART** — The census reads the marshals' screens; the debug arm is deleted with the engine. | §13 "The words census"; §6.11 |
| P4a-10 | 3 | Telling the player the Staff costs authority before refusing it is just show-before. | **ALREADY ANSWERED** — Already the rule. | §6.4 |
| P4a-11 | 1 | A mission written as two places and a "then" can smuggle a second act, and P2's two-step example promises what the game cannot keep. | **ACCEPT** — A two-province hold is one area; a second task is refused; a "then" is an arrival verb only. | §6.1 note; §8.3 refusals |
| P4a-12 | 1 | Risk words with floors and "at any cost" let a typed word override a man's authored odds and dodge the objection road. | **ACCEPT** — One step only; the careful man states his objection; no fixed floors. | §6.1 "Risk"; §8.3; §17 |
| P4a-13 | 2 | "His answer" plus a free "ask" is an unlimited free what-if, and must use the same forecast and show no hidden enemy figure. | **ACCEPT** — Asking changes nothing and is the same reading as Tonight; it reads only what France can see. | §8.6; §6.1; D10; §8.3 "Whom" |
| P4a-14 | 2 | "Send what I understood" would reproduce silent dropping unless it sends the restated clean line. | **ACCEPT** — It sends the line restated without the unread part, shown. | §8.4 row 2; D27 |
| P4a-15 | 2 | Eleven new buttons collide with golden rule 9 unless filed as one row with owners and tests, and the three untrue lines should be fixed first. | **ACCEPT** — One table, owner IC-7, IC-V4 closed when they land. | §8.1; §15 IC-7 |
| P4a-16 | 2 | A free "wait" must not count as engaged for the literal counter and must not clear a jealousy warning. | **ACCEPT** — Both stated on the button's row. | §8.1 table ("Stay put") |
| P4a-17 | 2 | Authored areas touch the scenario format and validator and need a cached, at-most-two list under scale rule 8. | **ACCEPT IN PART** — Areas are refused; a two-province hold is one area. Caching the lookup is not written. | §8.3 refusals; §6.1 |
| P4a-18 | 2 | WS-12's retirement is not the user's word and must not be written as a fresh ruling. | **ALREADY ANSWERED** — It is not a fresh ruling: ruled November 17, moved unchanged to IC-8. | §19.4 ("WS-12 — not a fresh ruling"); §8.5 |
| P4a-19 | 3 | P2 reconciles with D11 by calling a mission a task plus parts; accept. | **ACCEPT** — Stated. | D11; §6.1 note |
| P4a-20 | 3 | Eight if-thens plus five conditions should be one table generating the grammar (CX-R1). | **ACCEPT** — One word table generated into the parser with a census. | §8.3; §7 last bullet; §14 |
| P4a-21 | 2 | seeded_int is a pure hash, so "zero on the historical seed" must be checked by the temper function. | **ACCEPT** — The fallback is zero on the historical seed. | §6.7 "The fallback" |
| P4a-22 | 1 | A temper must be computed lazily for men on their own only, or the unused game stops reproducing byte for byte. | **ACCEPT** — Computed only for men on their own. | §6.7 "The fallback"; §13 R-INERT |
| P4a-23 | 1 | A temper computed from a visible seed can be read ahead and gamed. | **ACCEPT** — Only today's is shown; seed-knowers can compute ahead as with other seeded draws. | §6.7 "The fallback" |
| P4a-24 | 1 | A free recall plus a visible temper lets the player cycle the slot to the best man each night. | **ACCEPT** — The lost night prevents it. | §6.3; §6.7 "The fallback" |
| P4a-25 | 2 | Changing D9 is a design decision the user should make; prefer authored lines and the idle log first, temper only if a bar is missed. | **ACCEPT** — D9 stands; the fallback is built only if R-VARIETY is missed. | D9; §6.7; §13 R-VARIETY |
| P4a-26 | 2 | Temper and the risk word both move the bar, so the order and display must be stated. | **ACCEPT** — Your step, his record, never more than two steps from his figure, all three numbers shown. | §6.1 "Risk"; §13 |
| P4a-27 | 2 | A bold man's probe is a move that could enter a seen enemy's reach, so it must stay in his area and be shown. | **ACCEPT** — Probe inside his area, never into a province with a seen enemy; coming back is part of the same act. | §6.7 point 3 |
| P4a-28 | 2 | A bold Hold's counter-strike is a second act that runs the whole combat pipeline and must use only seen enemies. | **ACCEPT** — Once per order, shown under Tonight, runs the post-battle road, reckoned from what France knows. | §6.7 point 1; §12 ("A bold man strikes an enemy beside his area"); §6.1 |
| P4a-29 | 3 | Bernadotte starting a new order one night late is a certain penalty with no counter-lever. | **ACCEPT IN PART** — Kept, shown on his card and line; no counter-lever added. | §6.7 point 7; §12 (Bernadotte row) |
| P4a-30 | 2 | Murat's screen scout could become a free scouting engine. | **ACCEPT** — It reveals what a scout order would and no more. | §6.7 point 3 |
| P4a-31 | 2 | The one-man-per-target rule must reuse the combat forecast and never add a modifier path. | **ACCEPT** — The forecast with the first man's force added; golden rule 1. | §6.1 ("How the odds are reckoned"); §6.7 point 5 |
| P4a-32 | 2 | A mixed army's roles by nature create a second decision system beside directives; keep directives uniform and call the result a plan card. | **ACCEPT IN PART** — Directives stay uniform and the army's commander is on his own with the rest supporting; no plan card. | §9.1; D29 |
| P4a-33 | 3 | Moving the enemy's mood to a per-man hash changes every pinned enemy run and needs its own row and sweep. | **ACCEPT** — An arm of IC-14 behind its own switch, adopted only on its gate. | §10.6; §15 IC-14 |
| P4a-34 | 1 | Opening Tonight for all six eligible men is a free probe of the roster; say it is a ruled property. | **ACCEPT** — Asking is free by design and changes nothing; the fog stays honest. | §6.3 "Asking is free"; §8.6; D10 |
| P4a-35 | 1 | Setting, recalling and swapping the slot need one rule shared by all panels. | **ACCEPT** — One rule: 2 actions to give, recall free, a lost night. | §6.3; §12 |
| P4a-36 | 1 | The take-back's ORDER_KEYS must list every new field deliberately and never restore a night already spent. | **ACCEPT** — Decided field by field. | §12 "Saves"; §14 "Other warnings" |
| P4a-37 | 1 | Every new field needs to_dict, from_dict, the save reference and the enforcement test, and the temper must not be saved. | **ACCEPT** — Listed; the nerve is never saved. | §12 "Saves" |
| P4a-38 | 1 | R-INERT must be reworded for the redemption removal, and the old tests rewritten, not deleted. | **ACCEPT** — The audience is the one stated exception, and the tests are rewritten. | §13 R-INERT; §6.11 |
| P4a-39 | 2 | "Temper" reads as a mood, which the design forbids. | **ACCEPT** — Renamed "the day's nerve". | §6.7 "The fallback" |
| P4a-40 | 2 | Each new line (Tonight, restless, ask answers) must say which desk section carries it. | **ACCEPT IN PART** — Tonight is in the turn-end list and the morning; strike and ask rows are in TO DECIDE; "under THE WAR" is not written. | §4; §5; §6.9 |
| P4a-41 | 2 | A directive to an army that holds a man on his own must not override him silently. | **ACCEPT** — His row says "on his own — not included". | §9.1; §12 |
| P4a-42 | 2 | A one-turn dip in authority must not make the Staff lapse and cost the player a man. | **ACCEPT** — N falls only when the law lapses, never with a dip. | §6.4; §12 ("Your authority dips") |
| P4a-43 | 2 | A man on his own who wins takes glory and raises jealousy; the card should say who would be jealous. | **ACCEPT** — The read-back names who would take the choice ill; glory runs as today. | §6.9 "Glory", "The slight"; §12 |
| P4a-44 | 3 | Only the old grant's removal and WS-12's retirement remove shipped content; WS-12 is awaiting the user's word. | **ACCEPT IN PART** — The removal is read as within consent; WS-12 was ruled November 17. | §19.4 split table; §8.5 |

## P4 (second sample, P4_b) — the adversary panel

The same panel, a second independent sample. Rank is the panel's severity (1 = fix before anything is written into the spec). (30 findings.)

| ID | Rank | Finding | Ruling | Where v6 answers it |
|---|---|---|---|---|
| P4b-1 | 1 | P3's daily temper breaks R-INERT, can be read ahead, and lets the player shop for days by setting and recalling men; do not add it. | **ACCEPT** — No dice by default; the nerve is only a written fallback. | §6.7; D28; §17 ("A daily seeded temper"); §6.3 |
| P4b-2 | 1 | Re-keying the enemy's mood changes the old game and must be its own row, not tucked into row IC. | **ACCEPT** — An arm of IC-14 on its own gate with the user's word. | §10.6; §15 IC-14 |
| P4b-3 | 1 | Deleting the old grant goes beyond the user's consent, which covered low-authority autonomy, so the default should be to keep it. | **REJECT** — The game ties no autonomy to authority and the only one granted at low standing is this one; D24 is one line to strike. | §19.4 split table ("Is the removal inside the user's consent?"); §1.1; D24 |
| P4b-4 | 1 | If stand-down replaces it, it is a new mechanic and a trust farm unless it costs something real. | **ACCEPT** — Stand-down is not adopted. | §17; D24 |
| P4b-5 | 1 | An old save's autonomous fields and a new stood-down field would need migration, serialization and tests. | **ACCEPT IN PART** — No stood-down field; the old fields stay only to settle an old save on loading. | §6.11; §14 "The audience"; §12 "Saves" |
| P4b-6 | 1 | Blocking Give on every unread clause turns each stray "and report" into a modal; block only a part that changes what the order does. | **ACCEPT** — Filler is a quiet note and blocks nothing. | §8.4 row 2; D27 |
| P4b-7 | 1 | The one-word-condition hole ("retreat if outnumbered") is a shipped defect and should be filed now. | **FILED** — IC-V1. | §1.3; §19.4 "Defects" |
| P4b-8 | 1 | P2's grammar smuggles a second act (two-step list, areas, river lines, main army) and breaks "four tasks" and golden rule 9; ship only what the spec owns. | **ACCEPT** — Refused free, none promised. | §8.3 refusals; §17; §18 |
| P4b-9 | 1 | Directives and a mixed army collide with the count: derived exact lines let a player bypass N, and a new store must be in the take-back keys. | **ACCEPT IN PART** — The list says who is over the count and offers a recall, giving nothing; the keys are decided field by field. | §9.1; §12 ("An army's task when the count is full", "Saves") |
| P4b-10 | 2 | A refusal that differs for an unseen enemy and a name that does not exist is a fog oracle. | **ACCEPT** — They get the same answer. | §8.3 "Whom"; §12 |
| P4b-11 | 2 | "Ask" must read the same fog-honest forecast, from seen strength or a range, never the true strength. | **ACCEPT** — He reckons from what France knows, from the middle of the range where partly seen. | §6.1; D10; §8.6 |
| P4b-12 | 2 | A free look from the waiting scout is a systematic fog-lifter; it must reveal no more than a scout order and be announced. | **ACCEPT** — Same. | §6.7 point 3 |
| P4b-13 | 2 | A risk word with "at any cost" dodges the objection road; run the objection at Give and refuse it for careful men. | **ACCEPT IN PART** — The objection is read once at Give; "at any cost" is one step bolder and a careful man states his objection. | §6.3; §8.3 "How bold"; §12 |
| P4b-14 | 2 | Two panels define risk differently; pick the step form. | **ACCEPT** — One step form, shown as numbers. | §6.1; §17 |
| P4b-15 | 2 | If the old grant is kept, the count line must stay. | **ALREADY ANSWERED** — Moot: the grant is removed and the "2 of 1" rule struck. | §6.4; §6.11 |
| P4b-16 | 2 | A bold Hold's sortie is an improvisation unless Tonight shows it, and it is a second step outside the area. | **ACCEPT** — Once per order in all, shown under Tonight. | §6.7 point 1; §12 |
| P4b-17 | 2 | About twelve new buttons in one slice are too many; land a small set and rule the rest typed-only. | **REJECT** — IC-7 builds every one of them and IC-V4 closes only when all are; "nothing is dropped". | §8.1; §15 (Session 2 IC-7; re-cut preface) |
| P4b-18 | 2 | A typed "Murat, wait" must still be understood and golden-corpus entries kept. | **ACCEPT** — A "Stay put" button is added and the typed verb stays; the corpus gains rows. | §8.1 table; §14 "The word table" |
| P4b-19 | 2 | A bold man's sortie and a jealous strike aimed at one target must be settled in rank order across both passes. | **ACCEPT** — Rank settles a shared target across both passes. | §2 step 2; §12 |
| P4b-20 | 2 | A man on his own who wins must pass through the same post-battle road, glory and jealousy included. | **ACCEPT** — Same road as any attack. | §12 ("A bold man strikes an enemy beside his area"); §6.9 |
| P4b-21 | 2 | A free "ask" and a free change loop let a player farm trust; a card change must be priced and re-evaluate the objection. | **ACCEPT** — Any change costs 1 action and the objection is read at Give; asking changes nothing. | §6.3; §8.6 |
| P4b-22 | 2 | A card quote must be a pure read so give-then-undo is not a free probe. | **ACCEPT** — Give is the only change of state; every quote is pure. | §8.4; §19.4 adversaries' list |
| P4b-23 | 2 | Every new field needs serialization and the save reference, old saves must load with no men on their own, and the count must scan only the player's laws. | **ACCEPT** — Stated for saves and old saves; the count stands on the laws. | §12 "Saves", "Old saves"; §14 "The count" |
| P4b-24 | 2 | "Tonight" for each man must not scan regions per man per turn (golden rule 8). | **ACCEPT** — added after the fresh readers' check: "Tonight", the proposals, the ways of waiting and the one-man-per-target pass read cached helpers, worked out once per state and kept, never a scan of every region per man per turn. | §14 (other warnings, golden rule 8) |
| P4b-25 | 3 | Renaming the strike's words moves pinned tests; budget the re-pins. | **ACCEPT** — Budgeted with the census, never bypassed. | §14 "Other warnings" |
| P4b-26 | 3 | The authored odds are placeholders to be tuned by the playtest driver over thirty seeds with the bar written first. | **ACCEPT** — Authored with the user and settled by R-READ and R-VARIETY. | §13 "Each marshal's own odds" |
| P4b-27 | 3 | A law paid in authority could close the second place when the grip is low; verify before pricing. | **ACCEPT** — The card says why before it refuses; authority never moves N. | §6.4 |
| P4b-28 | 3 | Lannes's arrival is a dice roll, so his Tonight line can only show an odds row. | **ACCEPT** — Shown as "may", never promised. | §6.5 |
| P4b-29 | 3 | The model section is consistent with parsing only, provided the preview is built from the deterministic read and WS-12 heads the slice. | **ACCEPT** — Same. | §8.5; §8.7 |
| P4b-30 | 3 | Sibling sweep: does the enemy have an "on his own" state, and can the pure reading be called with an enemy marshal? | **ALREADY ANSWERED** — Courts set no man on his own; the per-man mood sibling is filed. | D4; §10; §10.6; §17 |

## Where the two samples split, and how it was settled

The spec's §19.4 table, in plain words, with the findings on each side. Where both samples of a panel agreed with each other, that was taken as settled (see §19.4 "Where both samples agreed"); the splits below are between panels, or between a panel and the adversaries.

| Split | One side | The other side | Settled | Why |
|---|---|---|---|---|
| What replaces Grant Autonomy | Both P1 samples: a "stand him down", three idle turns, a small trust gain (P1a-2, P1b-3) | Both adversaries: a stand-down is a free trust farm and drops the deed-and-reward (P4a-2, P4b-4) | A task to prove himself under exact orders, with today's rewards | The adversaries' point stands, and P1's first sample had itself named "a task to the letter" as the later answer; version 6 lands it with the removal (D24, §17). |
| Is the removal inside the user's consent? | One adversary: "low authority" is not trust, so default to keep (P4b-3) | Both P1 samples: remove it, the user said "even removing it if needed" (P1a-1, P1b-3) | Yes, read plainly | The game ties no autonomy to authority; the only autonomy granted at low standing is this one; version 5 itself counted it as "a man acting without orders"; D24 is one line to strike. |
| A daily seeded temper, or none | Both P3 samples: a temper drawn from a hash (P3a-6, P3b-2) | Both adversaries: do not add it (P4a-25, P4b-1) | No dice; seven earned ways; the temper only as R-VARIETY's written fallback | Count-shopping and "personality is character, not situation"; the bar, written now, decides (D9, §6.7). |
| A card as a second road, or typing for tasks | Both P2 samples: keep the card as a real road (P2a-29, P2b-26) | The user's own ruling in the status block: typing is used for missions | The line, filled with his proposal, with chips that write into it | Typing stays the road, and every player can still give any task (D25, §8.2). |
| Fixed risk floors and "at any cost" as no floor, or one step | P2 samples: three named floors (P2a-12, P2b-10) | P3 samples and both adversaries: one step (P3b-6, P4a-12, P4b-14) | One step | A word must not override a man's own odds (§6.1, §17). |
| Two-step tasks, river lines, "their main army" | P2 samples (P2a-17, P2a-13, P2a-14, P2b-13, P2b-12) | Adversaries: only what the design owns (P4a-11, P4b-8) | Refused free, the nearest sentence written in | A second act, new scenario data, or a fog hazard (§8.3, §17). |
| A mixed army's roles by nature, with derived exact lines | P3 samples (P3a-22, P3b-17) | Adversaries: a second decision system and a way round the count (P4b-9, P4a-32) | The commander on his own, the rest supporting by today's rules | No new system; the men's natures already decide how they join a fight (§9.1, D29). |
| Re-key the enemy's mood per man | R4 and both P3 samples (R4-6, P3a-24, P3b-18) | Adversaries: it changes the old game, so its own row (P4b-2, P4a-33) | An arm of Session 4, adopted only with the user's word | It changes the old game (§10.6, IC-14). |

The adversaries' other first-rank points were taken into version 6 as listed in §19.4, last paragraph: a smuggled second act refused; risk words moved one step; one rule for setting, recalling and swapping (a lost night); R-INERT stated precisely; D9 decided in the open; every new field listed; WS-12 not a fresh ruling; an unseen enemy read the same as a name that does not exist; Give the only change of state.

## Defects filed

Four defects the review found in the shipped game, filed with strict-xfail pins in `tests/test_ic_review_pins.py` and listed in `BUG_FIXES.md` §IC review (spec §1.3 and §19.4).

| Row | What it is | Found by | Closed by |
|---|---|---|---|
| IC-V1 | A one-word condition slips under the two-word floor, so "Ney, retreat if outnumbered" retreats now and the "if" is dropped without a word. | R3-3, R3-4, P4b-7 (and the example row P2a-20) | IC-8 (the line for tasks) |
| IC-V2 | The read-back shows neither a condition it took nor a clause it dropped; both appear only after the order is sent. | R3-2 | IC-8 |
| IC-V3 | A man acting independently can strike and act again in one turn, because the strike's warning pass and `process_autonomous_attacks` never read `autonomous`. | R1-13, P1b-25 | IC-9 (with the old engine) and IC-10's guard |
| IC-V4 | Eight simple orders and four group orders have no button; the Help's Orders page says the clicks "give the same orders" and row PW part 3's record says every order has a button. | R2-1, R2-2, R2-4, P2a-9, P2b-18 | IC-7 (the buttons) |

## Findings v6 does not answer

None. The draft found three (P2a-23, P2b-19, P4b-24); each was written into the spec before the commit and its row above now says where.

## After the draft: the fresh readers' check

Two fresh Sonnet readers checked version 6 before the commit — one for plain words and contradictions, one for every claim about the code. Their corrections were made in the spec: two province names that are not provinces ("Venetia", "Ulm" as a place) replaced; the two-word floor located in the clause guard (`clause_guards.py`), not in `unread_condition_clauses`; risk words "not read at all", not "stripped as filler"; the purchase floor stated as a purchase that would leave authority under 60; a devoted man immune below authority 30; "then dig in" marked new and today's four arrival verbs listed; three task words marked new and "defend" kept the one-action stand; six condition clauses, not five; the Help's words quoted exactly; Napoleon's ability in full. And the contradictions: the risk cap (one step from you, one from him, never more than two), Murat's two provinces inside the once-per-order step, a man never objecting to his own proposal, today's order to a man on his own as an ordinary order, the rule that decides between "on his own" and an exact order, which ways of waiting are still waiting, the costs of a Support task, of another man's exact order and of the trial, what happens when the trial ends, an army whose commander cannot be set on his own, and when if-thens are checked.
