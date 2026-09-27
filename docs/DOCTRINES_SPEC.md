# National Doctrines — SR-D2 "France feels different from Austria"

> **Status: RULED September 27, 2026 by the user; REVIEWED the same day (§0.2).** This is the doctrine half of SR-D2 (`SCORE_MANDATE_PLAN.md` §4). It was pulled forward from Chunk 7's gate so the reforms' law list (`REFORMS_SPEC.md`, built at Chunk 5) could be written against it. **Nothing is built.** The doctrines are still built at Chunk 7, as slice group SR-7d.
>
> This file holds:
> - **the gate record (§0)**, which is authoritative;
> - **the review of September 27, 2026 (§0.2)** — a reach census of every clause on seven boards, two independent review rounds, and the amendments they made. **Seven amendments change what a doctrine does and are FOR USER CONFIRMATION** (RV-2, RV-3, RV-4, RV-5, RV-15, RV-16, RV-17). Each can be reverted to the drafted clause. The rest correct the build contract;
> - **the build contract (§1–§9)**, written with the amendments in.
>
> Reading map: §0 the rulings and readings · §0.2 the review · §1 what a doctrine is · §2 the five doctrines · §3 the seams · §4 what the player sees · §5 the AI · §6 acceptance · §7 the build slices · §8 not in this ruling · §9 the save format.
>
> What may change at the build:
> - Numbers marked **DRAFT** are in-band tunable; the build measures them against §6.
> - A new effect, a change to who a doctrine applies to, or a new cure is structural and escalates to the user.
>
> Two questions are NOT ruled here and stay where they were:
> - **The seasons (HC-6)** keep their own recorded slot: the first content slice after the first outside playtest ("The General Winter", `SEASONS_WEATHER_SPEC.md` header). The user ruled that Russia's doctrine does not include the winter.
> - **The standing alarm floor** (SR-G7 / PB-D1) stays a question for Chunk 7's gate.

---

## §0 Gate record — RULED September 27, 2026

| # | Question | Ruling | Note |
|---|---|---|---|
| Q1 | What a doctrine is | **A strength and a flaw.** Each great power gets one standing doctrine: how its army fought in 1805, with one strength and one flaw. A reform law cures the flaw, so the rivals' reforms are how they catch up. Every effect is a number on an existing mechanic the AI already reads, so no new AI decision rules are needed. | As recommended. |
| Q2 | Which courts | **All five great powers:** France, Britain, Russia, Austria and Prussia. The secondary and minor courts keep the common rules. | As recommended. The plan's original recommendation was three. |
| Q3 | Russia's winter | **Not in the doctrine.** Russia's doctrine is its stubbornness. The winter comes with the seasons, which keep their post-playtest slot. | As recommended. This reverses the September 26 fold of HC-6 into this gate *for the build*: the seasons are not built at Chunk 7. |
| Q4 | France's doctrine | **The corps system, plus "living off the land".** The flaw: French armies starve sooner in poor country until France buys the Train des Équipages. | **The recommended option (corps system only) was NOT taken.** The user chose the historically fuller version, told that it tightens the supply squeeze that already scatters France's army. |
| — | Laws at the start (asked with SR-D1) | **No court starts with a law in force, France included.** The rivals' law descriptions name what they copy from France. | Recorded in `REFORMS_SPEC.md` §0 (Q7). |

### §0.1 Readings taken where the answers meet — FOR USER CONFIRMATION

- **D-R1 — "Poor country" is authored, not derived.**
  - The map marks nothing poor where history does. Measured (census corrected by the review, RV-12):
    - the map's 27 rural provinces are in France (7), Sweden (4), the Ottoman Empire (4: Rumelia, Epirus, Cyprus, Crete), Holland (3), Hanover (3), Denmark (2), and Hesse, Britain, Portugal and Spain (1 each);
    - every Russian province feeds a stranger's army 31,500–50,000 and every Prussian one 35,000–40,000;
    - so neither region type nor income can stand in for poor country.
  - A new scenario list, `poor_country`, names it. **DRAFT list** — all fourteen names resolve in the registry (Galicia is the Spanish province):
    - East Prussia, Posen, Samogitia, Lithuania, White Russia and Volhynia — where the 1807 and 1812 campaigns starved;
    - Leon, Aragon and Galicia — the Spanish war;
    - Alentejo and Beira — Masséna's 1810 invasion of Portugal;
    - Rumelia, Epirus and Albania — the Balkans.
  - The build authors the list; the validator checks the names.
  - **Amended by RV-5 (FOR USER CONFIRMATION): poor country also includes stripped country** — a province eaten bare by war.
- **D-R2 — Where the flaw bites.**
  - ~~It applies only where the supply rule already feeds the army at the base rate: not home soil, not allied or vassal soil, and no naval lifeline.~~
  - **Amended by RV-5 (FOR USER CONFIRMATION): read against the homeland, not the flag.** The flaw applies outside France's 1805 homeland, on conquered ground as well as an enemy's, and never on an ally's or vassal's soil. There a French army in poor or stripped country draws **80% of the supply it would otherwise draw** — a conquered province 80% of its fed rate, an enemy's 80% of its base.
  - At home and on allied soil the magazines feed a French army as they do today.
  - **A depot is not a cure** (added by the review). A depot raises the province's capacity, and the 80% is taken of that larger number. The Train des Équipages is the cure.
- **D-R3 — The Train des Équipages becomes the cure alone.**
  - The draft law's supply bonus (×1.25, `REFORMS_SPEC.md` §6) is dropped. The reform restores what the flaw takes, which was its historical purpose: the decree of 26 March 1807 followed the Polish winter.
  - A law with no effect cannot ship before the flaw exists. So **the Train is authored at Chunk 7 with the doctrines, not at Chunk 5**, and France's Chunk-5 deck has five laws (still within the ruled 5–8).
- **D-R4 — A cure is a new law effect type, `cures`.** This is `REFORMS_SPEC.md` §4's tenth type.
  - Austria's Corps d'Armée and Russia's Divisional System carry it as their second clause. Those laws are worth more to their courts than France's Staff law is to France — that is the catch-up — at the same price.
  - Austria and Russia share one flaw on purpose (RV-9): both lack France's corps system, and both cure it by copying it.
  - **Amended by RV-15 (FOR USER CONFIRMATION): a cure works only while its court's Staff is in force.**
  - **No cure clause is authored before its flaw exists (GR9).** The cures land at Chunk 7 (slice DC-2). Until then each of those laws does only what it does at Chunk 5.
- **D-R5 — The opening balance moves.**
  - Doctrines apply from turn 1, so the Chunk-7 build re-records `BASELINE_SERIES` once, with a flip arm.
  - ~~M1–M7 will move too, because the harness pits French corps against Austrian ones.~~ **Corrected by the review (RV-11):**
    - M1–M6 build bare marshals and call the resolver directly.
    - M7 builds a real 1805 world, so the RV-6 refresh runs, but it resolves French marshals against bare Austrian stand-ins through the resolver alone.
    - None of them has an arrival roll, a recruit price, supply, or a Russian, Prussian or British corps.
    - So M1–M7 are expected byte-identical, because France's and Austria's clauses carry no resolver-side term. A doctrine that gave France one would move M7.
    - They are re-read either way, and any movement is attributed by a flip arm, never assumed.

### §0.2 The review — September 27, 2026

**Method.**
- Every seam in §3 was re-read at HEAD `652d23d7` (the ruling's own commit; docs only, so its code is `34c939cf`'s).
- A reach census then counted how often each clause's seam is reached by the court that would carry it. The tool is `tools/_dc_reach_census.py`: read-only instrumentation, with its output committed as `tools/_dc_reach_census.json`. The boards:
  - the `BASELINE_SERIES` board (40 turns, a passive France) on four campaign seeds — historical, ulm, austerlitz and eylau (ulm and austerlitz open alike);
  - three committed arms of a commanded France, 40 turns each: `commanded_full40`, the AAR road (`sr1e_aar_road`, which ends in the Fall around turn 30) and the Pressburg road (`gev_pressburg_road`).
- Two independent read-only review rounds then attacked the review itself:
  - **A fact-check** of every code claim. It also checked the instrument: its board reproduces `BASELINE_SERIES` byte for byte, so the wrappers do not perturb play. It found three counting flaws in the first cut, all fixed before the committed run: solo battles read zero casualties, a pursue order's bar was ignored, and the treasury samples were mislabelled by a turn.
  - **A design attack** on the amended design: two P1s and nine P2s, every one taken below.

**The census** (in order: historical · ulm · austerlitz · eylau | commanded · AAR · Pressburg):

| Clause | What was counted | Ambient | Commanded arms |
|---|---|---|---|
| France — the corps system | French arrival rolls | 8 · 32 · 32 · 26 | 31 · 43 · 15 |
| France — living off the land | unfed French marshal-turns in the listed poor country | 0 · 0 · 0 · 0 | 0 · 0 · 0 |
| — in stripped country, read against the flag (as drafted) | marshal-turns where the 80% cap raised attrition (predicate hits in brackets) | 0 (0) · 0 (8) · 0 (8) · 0 (0) | 0 (0) · 7 (13) · 0 (0) |
| — in stripped country, read against the homeland (RV-5) | the same | 0 (0) · 0 (6) · 0 (6) · 0 (1) | 9 (20) · 7 (14) · 0 (0) |
| Britain — the line holds | British corps defending | 0 · 2 · 2 · 0 | 3 · 6 · 2 |
| Britain — irreplaceable | British recruits | 4 · 7 · 7 · 2 | 0 · 2 · 1 |
| Russia — stubborn | Russian defeats | 0 · 0 · 0 · 0 | 0 · 0 · 0 |
| Russia — slow to concentrate | Russian arrival rolls | 0 · 0 · 0 · 0 | 0 · 1 · 0 |
| Austria — the guns | Austrian artillery recruits | 0 · 0 · 0 · 0 | 1 · 0 · 0 |
| — (every arm, RV-3) | Austrian recruits | 18 · 19 · 19 · 14 | 15 · 17 · 28 |
| Austria — the Hofkriegsrat | Austrian arrival rolls | 4 · 3 · 3 · 11 | 5 · 8 · 3 |
| Prussia — Frederick's drill | Prussian drills | 0 · 0 · 0 · 0 | 0 · 0 · 0 |
| Prussia — brittle | Prussian defeats | 0 · 0 · 0 · 0 | 0 · 0 · 0 |

**What it shows.**
- **Six of the ten clauses as drafted fire at most once on seven boards.** Only France's corps system, Britain's two clauses and Austria's Hofkriegsrat fire in ordinary play.
  - Russia fought four battles on one board, all as the attacker, and lost none.
  - Prussia fought no battle and made no drill on any board.
  - France never stood unfed in the listed poor country.
  - Austria recruited artillery once in 130 recruits.
- **Russia's and Prussia's silence is their war record, not their seam.** The lopsided-defeat penalty was paid in 159 of 173 defeats across the seven boards (France 110 of 114, Austria 38 of 43, Britain 11 of 16). So Stubborn and Brittle will fire on nearly every Russian or Prussian defeat — once those courts fight.
- **Living off the land, as drafted, could never bite conquered ground.**
  - The engine feeds any province France *controls* at the home rate, and a corps captures an undefended province on entry. So Posen and East Prussia would feed France at 1.5× the moment it walked in.
  - The drafted reading bit only sieges, contested fields, and France's own provinces while an enemy held them: 7 marshal-turns and 522 men in 280 board-turns. It never touched a province France holds, which is where the supply squeeze the user was told about falls.
  - Read against the homeland (RV-5), it also bites conquered stripped ground: 16 marshal-turns and about 1,780 men, 9 of them on the commanded arm, all on conquered provinces.
- **A cheap cure is an opening purchase.** The AI rung (`REFORMS_SPEC.md` §7) takes the first law a court can afford. Britain's and Prussia's cures are political acts, with purse bars of about 1,750 and 1,500 gold. Britain boots with 2,000, and Prussia has about 2,000 by turn 10, so both flaws would have vanished in the opening on every seed.
  - Separately, AI authority has no live writer: `diplomacy.modify_nation_authority` has no callers and `_process_nation_authority` is a `pass`. So each AI court gets exactly two political acts in a campaign (`REFORMS_SPEC.md` §3 amended).
- **The ±10 on the arrival roll is not monotone as drafted.**
  - The roll fumbles 5% of the time when the score is above 80. A +10 on the *score* pushes a well-placed marshal into that band: 36 of 187 French arrival rolls would have been *less* likely to arrive with the strength.
    - Ney joining Napoleon's battle: 99.1% → 96.2%.
    - Murat: 97.6% → 95.0%.
  - Symmetrically, a −10 on the score makes a top Austrian more likely to arrive.
- **The arrival bar has three copies.**
  - `CombatExecutor._arrival_threshold` is "the ONE source" by its docstring, and only the preview's readers call it (`_arrival_odds_row`, `_expected_arrival_weight`).
  - The resolver restates `60 if has_explicit_order else 65` inline in `_calculate_reinforcements`.
  - `_arrival_odds_row` hard-codes the written-order bar as `60`.
- **The corps system would erase Bernadotte.**
  - Toward a lead he is neutral with (Soult, Lannes, Masséna), "Eyes on a Crown" holds him to 17.6%; a bar 10 lower makes it 76.5%.
  - Toward Davout — Auerstedt itself — he is hostile, so he marches only under a written order, and even then arrives 0% of the time. A bar 10 lower makes it 47%.
- **A doctrine-decided no-show would read as bad roads, and cost the man trust.** A roll that lands between the old bar and the shifted one is classified `low_score` ("could not reach the battlefield in time"), and the Session-61a loop docks −3 trust on both boards. So Austrian and Russian marshals would bleed trust for their court's council.
- **"Attacking" and "defending" do not mean what the words say in a battle with reinforcements** (§2 gives the rule). A Prussian reinforcer relieving a Prussian defence would push harder; a British reinforcer would never feel the line.
- **Two surfaces §4 named do not exist yet.**
  - Nothing quotes the lopsided-defeat morale penalty; the battle report has no morale line.
  - The battle report's modifier snapshot lists components; it does not read the modifier's total.
- **The resolver holds no world.** `combat.py` and `Marshal.get_*_modifier` cannot look up a court's doctrine. The Presence precedent shows the trap:
  - its battle stamp is cleared on the auto-charge path by design;
  - the NP promise audit found two combat paths — the garrison assault and the charge — that never reached its participant stamp;
  - the charge has since been given its own re-stamp. Each path had to be found and patched one at a time.
- **The spec had no save format, and its slices could not boot.** `from_scenario` raises on any validator error, and §1's `cured_by` rule needed DC-2's cures at DC-0.
- **For Austria and Russia, the cure is the dearest law in the deck.** The Staff costs 9,000 gold, and the AI's purse bar for it is about 11,500 (more once other laws are in force).
  - Austria's treasury reaches that around turn 20 on the ambient seeds (11,836 · 16,577 · 16,577 · 12,011, sampled at the 21st attrition pass). Under French pressure it comes after turn 30: 10,446 at the 31st pass on the commanded arm, and 7,113 on the AAR road before the Fall.
  - Russia reaches it around turn 30 on the ambient seeds. Under pressure it is not reliably there by turn 40 (8,785 on the Pressburg road).
- **A naive Jena road loses.** A scratch arm (not committed) had France declare war on Prussia on turn 1 and march east two corps a turn. France lost all 26 of its defensive battles and never reached Posen, while Prussia attacked 19 times and lost none. The committed evidence arm (T3) must be a real campaign.

**The amendments.**

*Change what a doctrine does — FOR USER CONFIRMATION.* Each keeps the ruled frame (a strength, a flaw, a cure), and each can be reverted to the drafted clause:

| # | Amendment | Why |
|---|---|---|
| **RV-2** | **The army's doctrine never overrides the man's character.** The corps system does not lower the bar for a marshal whose own ability keeps him away (Bernadotte's Eyes on a Crown), who holds a live grievance against the lead, or who is hostile to him — the three causes the resolver already names. The exemption holds whether or not he is under a written order; an order still gives him its own +15, never more. The literal Grouchy rule is untouched: Soult without an order still does not march. §1 states the rule for every court. | Personality is the real man's character. Without this, Bernadotte under a neutral lead arrives 76.5% of the time, not 17.6%, and under a written order to support Davout at Auerstedt 47%, not 0% — the hostility arm is what keeps Auerstedt. A grievance would lose its teeth. |
| **RV-3** | **Austria's strength is "The Hereditary Lands": Austrian recruits cost ×0.85, every arm** — replacing "The Guns" (artillery recruits ×0.85). Same effect type, same number; only the arm and the name change. | No court fields an artillery marshal at boot. Austria's one gunner, Smola, is fourth of four in its pool, and artillery is recruited only by an artillery marshal (CN-1). The Guns fired once in 130 Austrian recruits, and three rivals' laws buy the same ×0.85 on artillery. Austria's true 1792–1809 trait is the army that always comes back. *Alternative if the guns are preferred:* "The Guns — an Austrian corps defending, +10%" (fires 3–15 times a board, but shares Britain's seam). |
| **RV-4** | **Prussia's strength, Frederick's Drill, becomes +10% on the Prussian attack modifier** — replacing "drill restores +5 more morale". That modifier is read when a Prussian lead attacks, and for every Prussian reinforcer's weight on either side (§2). | The AI's drill rung (P6) fires only for aggressive marshals, or inside a coalition whose posture is aggressive. Both Prussian marshals at boot are cautious, and Prussia drilled on no board. Of 62 drills any court made, only 5 had room for five more morale. Q1 asks for a number on a mechanic the AI already reads; this one is read only when an aggressive marshal drills below 95 morale. The attack is Frederick's own — Leuthen's oblique order, the parade-ground lines before Jena — and it pairs with Brittle: Prussia attacks hard and breaks all at once. The scratch Jena road had Prussia attack 19 times. |
| **RV-5** | **Living off the land is read against the homeland, and poor country includes stripped country.** Outside France's 1805 homeland — conquered ground as well as an enemy's, never an ally's or vassal's — a French army in the listed poor country, or in a province whose war damage stands at **0.25 or more (DRAFT)**, draws **80% of what it would otherwise draw**. | As drafted the flaw could not reach conquered ground, and so it never reached Poland — the case it was ruled for. It bit 7 marshal-turns in 280 board-turns and never touched a province France holds. Read against the homeland it also bites conquered stripped ground, and the Train cures something real. History agrees: conquest did not feed the Grande Armée in Poland in 1807, and the land failed where armies had already eaten it — Moravia before Austerlitz, the Lobau in 1809, the Smolensk road in 1812.<br>War damage moves like this:<br>• a battle adds 0.10, or 0.20 when the two leads number 50,000 or more;<br>• a sack adds 0.35;<br>• the owner's repair order removes 0.15 at once;<br>• it recovers 0.02 a turn and is capped at 0.5. |
| **RV-15** | **A cure works only while its court's Staff is in force.** A reform needs the institution that carries it. The cure clause is read at the doctrine's seam as *cure law in force AND Staff in force*; the law's other clause works from enactment. For Austria and Russia the cure IS the Staff, so nothing changes. | Without it, Britain's Militia Transfer and Prussia's Articles of War — political acts with purse bars of 1,750 and 1,500 — would cure both flaws in the opening on every seed. With it, every rival's catch-up arrives with its Staff (9,000 gold, mid-campaign), as the post-1806 reforms did. A Staff that lapses (the largest upkeep lapses first, `REFORMS_SPEC.md` R5) silences its court's cure: the reforms collapse when the state cannot pay. France's Train des Équipages needs the Grand Quartier Général the same way (GR5). |
| **RV-16** | **The court's flaw never costs the man trust.** A no-show decided by a doctrine gets its own reason, `doctrine_delayed`: a roll between the unshifted bar and the shifted one. Its copy names the flaw ("The Hofkriegsrat's orders reached Archduke John too late"), and it is exempt from the Session-61a trust dock. An arrival the corps system decides is named too ("the corps system brought Davout in"). | Trust arithmetic then matches the lever-down world except where a doctrine really changed who arrived. A6 reclassified grievance no-shows as copy only and kept them in the dock, so as not to change trust arithmetic silently; this ruling changes it openly, for a cause the marshal does not own. |
| **RV-17** | **The recruit clauses price the draft, not the substitute market.** Austria's ×0.85 and Britain's ×1.25 apply to a levy drawn from the court's own manpower. Hired substitutes (`_execute_purchase_levy`) keep the market's price. | A doctrine is how a court raises its own people. The substitute market is Britain's road around its small pool — the road it took historically — and a flaw that also taxed it would close that road. IQ1-3C kept its alarm term out of the substitute price for the same reason. |

*Correct the build contract — no ruling changes:*

| # | Correction |
|---|---|
| **RV-1** | **The arrival clauses move the bar, not the score.** "±10 on the arrival roll" becomes the bar 10 lower (France) or 10 higher (Austria, Russia): the same "+10 on the roll", with the fumble judged on the unmodified roll, so a strength can never lower the odds it names (T7). DC-0 first makes the resolver's inline bar and the odds row's `60` call `_arrival_threshold`, which gains an explicit `assume_order` parameter for the with-support odds and T7's grid. This is byte-identical with the lever down, and pinned. "As if under a written support order" is struck: a written order is worth +15 (+10 on the score, a bar 5 lower), and it is also what lets a literal marshal march and a hostile one join. The corps system is +10 and moves neither. |
| **RV-6** | **The combat clauses ride a standing term, never a battle stamp.**<br>• One writer, `doctrines.refresh_doctrine_terms(world)`, sets each marshal's private, derived `_doctrine_terms`; `get_attack_modifier`, `get_defense_modifier` and the two morale arms read it.<br>• Every change of a marshal's `nation` goes through ONE setter that refreshes (§3), and an AST census forbids bare `.nation =` writes.<br>• The term is declared in a new production tuple (§3), in both serialization censuses.<br>• It is an explicit, pinned exception to `REFORMS_SPEC.md` §2's "no second store can drift" (T9).<br>• It is never in `COORDINATION_TRANSIENT_FIELDS`, which the auto-charge and every clear path zero on purpose. |
| **RV-7** | **The surfaces are built, not quoted.** DC-3 gives the battle report its first morale line (for a lopsided defeat) and adds doctrine rows to the modifier snapshot. Each row prints the share that actually applied after the caps: the 1.75 defence cap can absorb The Line Holds. Every DC-3 surface gets a pin (T1). |
| **RV-8** | **One save field**, `world.doctrines` (§9). A pre-doctrine save is backfilled only when it is the 1805 campaign, so a tutorial or modded save never receives 1805's doctrines. |
| **RV-9** | **Russia and Austria share their flaw on purpose** — the absence of the corps system France has as its strength — and both cure it by copying it (Russia's divisions, 1806; Austria's corps, 1809). It is the only shared clause; the validator warns on any other. |
| **RV-10** | **The cure's timing is measured per court, not promised** (T8). With RV-15, every rival's cure arrives with its Staff. Only the treasury half of the rung's purse test was measured here; the second half (the forecast Net stays ≥ 0 after the new upkeep) may hold a court under French pressure back even with the gold in the chest. A miss belongs to RF-3 (`REFORMS_SPEC.md` §7). |
| **RV-11** | D-R5's M1–M7 claim corrected (above). |
| **RV-12** | D-R1's census corrected (above). |
| **RV-13** | **The player sees the flaw before the march** (§4):<br>• the map names poor and stripped country, the stripped mark obeying fog (a fogged province's war damage is sent as −1, the PC15-16 sentinel);<br>• the supply headline names the Train as the remedy;<br>• the LAWS tab says what the Train would lift this turn;<br>• every forecast reads stripped country forward, as the next attrition pass will read it (§3). |
| **RV-14** | **Evidence.**<br>• T3's arm, the Jena road, is authored as a real campaign and carries its own `"policy": {"declare_war": "proceed"}`, because the census passes no `--declare-war` and would otherwise cancel the war.<br>• T6 counts supply *bites*, not predicate hits.<br>• T7's grid spans the whole reachable deterministic range.<br>• T9 stages one case per nation-change seam. |
| **RV-18** | **The slices boot and the series moves once.**<br>• `cured_by` and its validator rule land at DC-2, with the cures.<br>• DC-1 lands the clauses behind `DOCTRINES_ACTIVE = False` (its pins run the lever up in-test).<br>• DC-2 flips the lever and re-records `BASELINE_SERIES` ONCE, with per-court and cure arms. RV-15 makes a deck reorder unnecessary, so no scenario data moves outside the lever. |

---

## §1 What a doctrine is

**Where it lives.** A doctrine is authored per court under a new scenario key, `doctrines`, in `europe_1805.json`, and validated by `modding/validator.py`. Each entry carries:

| Field | Meaning |
|---|---|
| `name` | the doctrine's display name |
| `says` | one line, printed verbatim |
| `strength` | one clause from §3's closed set |
| `flaw` | one clause from §3's closed set |
| `cured_by` | the law id that removes the flaw (lands at DC-2 — RV-18) |
| `shared_on_purpose` | optional: the reason a clause is shared with another court (RV-9) |

The scenario also carries the `poor_country` list (D-R1) as its own key — it is geography, not France's. France's supply clause carries its own stripped-country line (RV-5, DRAFT war damage 0.25).

**Rules:**
- **Authored content, not formulas** (`SCORE_MANDATE_PLAN.md` §4, the rule of the house): every number sits in the scenario.
- **A doctrine is a data parameter, not a special case.** Any court whose authored doctrine carries a clause gets it (GR5 in the rules sense). Today only the five great powers author one.
- **In force from turn 1, never bought, never lost.** Only its flaw can be removed — by the cure law, while the court's Staff is in force (RV-15).
- **Who carries it:** every marshal of the court — the flag he fights under, `marshal.nation`. An assimilated vassal contingent fights under its lord's doctrine; a commissioned marshal takes his court's at once; a prisoner keeps his court's.
- **A doctrine is the army's, never the man's (RV-2).** No doctrine clause overrides a marshal's own character — whether or not he is under a written order:
  - the literal Grouchy rule;
  - an ability that keeps him away;
  - a live grievance against the lead;
  - a hostile pair.
- **The court's flaw never costs the man trust (RV-16).**

**The validator** (errors unless marked):
- every court is a scenario nation;
- at most one doctrine per court;
- every clause is from the closed set, with its number inside a clamp band:
  - arrival bar ±20;
  - attack or defence 0–25%;
  - recruit price ×0.5–1.5;
  - lopsided-defeat morale ×0.25–2.0;
  - supply ×0.5–1.0, with its stripped-country line at war damage 0.1–0.5;
- from DC-2: `cured_by` names a law in the same court's `reforms` deck whose effects carry `cures` for this flaw, and the court's deck carries a Staff;
- every `poor_country` name exists;
- *warning:* two courts share an identical clause (the same seam, sign and number) without `shared_on_purpose`.

---

## §2 The five doctrines — DRAFT numbers (with the review's amendments)

| Court | Doctrine | Strength | Flaw | Cured by |
|---|---|---|---|---|
| France | **The Corps System** | A French corps within a march comes to the guns more surely: **its arrival bar is 10 lower** (RV-1), except for a man his own character keeps away (RV-2) | **Living off the land:** outside the homeland, in poor or stripped country, a French army draws **80%** of the supply it would otherwise draw (RV-5) | The Train des Équipages (D-R3), with the Grand Quartier Général in force (RV-15) |
| Britain | **The Line Holds** | A British lead defending: **+15%** on his defence modifier | **Irreplaceable:** British recruits drawn from the draft cost **×1.25** (RV-17), on top of the small authored manpower pool | The Militia Transfer, with the Horse Guards Reforms in force |
| Russia | **Stubborn** | A beaten Russian army loses **half** the morale a lopsided defeat costs | **Slow to concentrate:** the arrival bar is **10 higher** | The Divisional System (itself the Staff) |
| Austria | **The Hereditary Lands** (RV-3; was "The Guns") | Austrian recruits drawn from the draft cost **×0.85**, every arm (RV-17) | **The Hofkriegsrat** (the court war council): the arrival bar is **10 higher** | The Corps d'Armée (itself the Staff) |
| Prussia | **Frederick's Drill** | **+10% on the Prussian attack modifier** (RV-4; was "drill restores +5 more morale") | **Brittle:** a lopsided defeat costs **×1.5** morale — applied after the penalty's own cap of 55, so a Prussian rout's extra loss can reach 82 | The Articles of War, with the General Staff in force |

**The design shape.** The five doctrines answer three questions of 1805 war, each asked from opposite ends:
- **Who reaches the field?** France's corps system lowers the bar; the old armies without corps, Austria and Russia, raise it. Buying the corps (Austria's Corps d'Armée, Russia's Divisional System) closes the gap.
- **Who replaces the dead?** Austria's hereditary lands make recruits cheap; Britain's small army makes them dear.
- **Who stays on the field?** Russia's stubbornness halves a rout; Prussia's brittleness deepens it.

Two clauses stand alone: Britain's line in defence, and Prussia's attack in the old manner. France pays for its speed with the land it eats.

**For France, the two halves are one idea — march divided, fight united.** Beyond its own frontier, in poor or stripped country, a French army must spread its corps across provinces to eat — conquest does not make a poor land richer. The corps system is what brings them back together for the battle. The flaw teaches the dispersal and the strength rewards it.

**What "attacking" and "defending" mean in a battle with reinforcements** (`combat.py`, measured by the review):
- The resolver reads a lead's attack modifier only when he attacks: it scales the damage his side deals.
- It reads a lead's defence modifier only when he defends: it scales the damage his side takes.
- Each reinforcer's committed weight is read through *his own* attack modifier, on either side (`_committed_share`).

So:
- **The Line Holds:** a British side whose lead defends takes less. A British lead who attacks gains nothing from it, and a British reinforcer adds his weight like every court's.
- **Frederick's Drill:** a Prussian lead who attacks deals more. A Prussian lead who defends gains nothing from it. But every Prussian reinforcer pushes harder, relieving a defence as well as joining an attack — the old manner was the whole army's drill, not only its assaults. The report names it on the reinforcer's line wherever it applies.

**The measured bite (DRAFT numbers, for the build to tune):**
- **The corps system.** On the commanded arms, French arrival odds rise from 0.56–0.71 to 0.68–0.88 with RV-2's exemptions (0.74–0.89 without them). RV-2 exempts 15 of the 187 French rolls.
- **The Hofkriegsrat.** Austrian arrival odds fall from 0.32–0.60 to 0.04–0.35. That is steep; T4 decides whether −5 is the better number.
- **Living off the land at 80%.** It bites the army that crowds a province:
  - A lone French corps standing between 80% and 300% of the province's fed-or-unfed capacity pays up to about 0.9 more points of attrition a turn.
  - A two-corps stack pays up to about 1.4, because the flaw also switches on the stacking charge (+1 point) that two corps under their cap do not pay.
  - Above three times the capacity, the attrition formula's 3% ceiling binds with or without the flaw.
  - Measured: about 1,780 men over the seven boards, nearly all on the commanded arms. T5 decides whether 80% is felt.

**The words (DRAFT `says`, printed verbatim):**

| Court | `says` |
|---|---|
| France | "The corps march apart and fight together — and eat what the country gives them." |
| Britain | "A small army that cannot be replaced, and a line that does not give way." |
| Russia | "Easier to kill than to beat — and slow to gather from the ends of an empire." |
| Austria | "Beaten, and back with another army — once Vienna has written the orders." |
| Prussia | "Frederick's army still attacks as it did at Leuthen, and it breaks all at once." |

**The law list after the doctrines** (`REFORMS_SPEC.md` §6):
- **Cure only:** the Train des Équipages (D-R3).
- **Cure added as a second clause:**
  - the Corps d'Armée and the Divisional System (after their +1 action);
  - the Militia Transfer (after its manpower regen);
  - the Articles of War (after its recruit morale).
- **A cure works only while its court's Staff is in force** (RV-15). The law's other clause works from enactment, so the reforms' Chunk-5 behaviour is unchanged.
- **Stacking, stated:** Austria's Generalissimus (`recruit_price` ×0.9, every arm) stacks with the Hereditary Lands (×0.85 × 0.9 = ×0.765 on the draft). After RV-4, no law duplicates Prussia's strength.

---

## §3 The seams — each effect on ONE existing single source

Every seam below was re-read by the review at HEAD `652d23d7` (code identical to `34c939cf`).

| Effect | The seam | Read by | Build notes |
|---|---|---|---|
| Arrival bar ± | `CombatExecutor._arrival_threshold`, with a new explicit `assume_order` parameter (RV-1) | the resolver (`_calculate_reinforcements`); the muster preview's odds and with-support odds (`_arrival_odds_row`); the committed-strength band (`_expected_arrival_weight`), so the glory gate and the AI's `_muster_price` too | DC-0 makes the resolver's inline bar and the odds row's hard-coded `60` call it — byte-identical with the lever down, pinned — before any doctrine reads it. The shift moves the bar; the score, and so the fumble, is never touched. RV-2's exemption lives here, so every reader inherits it. A roll between the unshifted and the shifted bar is `doctrine_delayed` (RV-16). |
| Defence % | `Marshal.get_defense_modifier` (GR1), reading the marshal's standing doctrine term (RV-6) | the resolver (a defending lead's term scales his side's losses — §2); the muster band's posture note (`consume=False`); the battle report's snapshot (a new row, RV-7) | Inside the 1.75 defence cap; the snapshot prints the share that survived the cap. |
| Attack % (RV-4) | `Marshal.get_attack_modifier` (GR1), reading the doctrine term | the resolver (an attacking lead's damage dealt); every reinforcer's committed weight via `_committed_share`, on either side (§2); the snapshot (a new row, on the reinforcer's line too) | |
| Recruit price × | `EconomyExecutor._recruit_cost_terms` → `_calculate_recruit_cost` (price and named terms from one source) | the recruit, `recruit_quote` and every chip that quotes it, the levy status and the ledger's price, and the AI's three pre-budget sites | The doctrine is one named term ("the Hereditary Lands ×0.85"), inside the Europe block, before the Intendance's rounding. **It prices the draft only (RV-17)**: the substitute market (`_execute_purchase_levy`, its quote, the region panel's price and the AI's purchase-levy rung) is priced without it, behind the same kind of flag IQ1-3C uses for its alarm term. The enemy-phase recruit line carries only the doctrine's term: the full list's "× over the ordinance" would reveal the enemy's army against its force limit. The arm parameter arrives with RF-2. |
| Lopsided-defeat morale × | the two morale arms in `CombatResolver` — the immediate path and `_build_deferred_result` — scaling `decisiveness_morale_penalty`'s result by the losing side's doctrine term | a new battle-report morale line (RV-7) | A side is one court by construction: reinforcement Rule 1 and `_get_casualty_participants` both filter on nation, and every other `resolve_battle` caller is one marshal against one marshal. So the coordinated path's uniform side delta is safe. If that ever changes, the factor must move per participant. |
| Supply ×, living off the land | `WorldState._supply_multiplier` (the fed/unfed decision) | `get_effective_supply_cap`: attrition, the supply-strain headline, the depot chip, the muster's supply note, P6.5 | The decision reads the nation, the province's identity (the list, and France's 1805 homeland from `nation_starting_regions`) and its war damage (RV-5) — never its capacity. That keeps the WO slice-8 invariant: the depot chip still prices its counterfactual exactly. **Stripped is read forward:** `advance_turn` runs the war-damage recovery tick (−0.02) *before* the attrition pass. So every forecast reads the damage the next pass will read: today's, less one recovery tick, plus the muster's own battle when a muster previews one there (0.10, or 0.20 when the two leads number 50,000 or more). The bill reads the post-recovery value. Otherwise a quote at 0.20 says 100% and its own battle bills 80% — the error pointing toward committing — or a province at 0.25–0.26 is quoted stripped and billed as fed (IQ1-5-1's "one tick stale" class). |
| *(struck by RV-4 unless restored)* Drill morale + | `WorldState._apply_drill_morale` | the dispatch's drill line (`dispatch.py`) | Kept here only so a restoration has a home. If restored, T6 records it as dormant for the AI. |

**How the resolver learns a court's doctrine (RV-6).** `combat.py` and `Marshal.get_*_modifier` hold no world, so each marshal carries a standing, derived, **unserialized** term, `_doctrine_terms`: the court's combat clauses, with the cure (and its Staff) already applied.
- **One writer:** `doctrines.refresh_doctrine_terms(world)`.
- **One setter for a marshal's court.** Every change of a marshal's `nation` goes through `doctrines.set_marshal_nation(world, marshal, nation)`, which refreshes, and an AST census forbids a bare `.nation =` write anywhere else. The writers today:
  - `assimilate_vassal_marshals`, `transfer_vassal` and `release_vassal`;
  - `complete_vassal_break` (all three rebellion exits), and the lever-down branch of `check_vassal_rebellion`;
  - `_defect_vassal_free_and_hostile`;
  - `WorldState._eliminate_nation` (satellites freed when their lord falls).
  - A new marshal (`commission_marshal`) is refreshed where he is created. `create_client_nation` writes no marshal's nation.
- **Also refreshed:**
  - at every law enactment, repeal and lapse;
  - as the last statement of `from_scenario`, and of `from_dict` — after the `reforms` store loads, or a loaded cure would be missed;
  - once a turn, as a belt.
- **Never** in `COORDINATION_TRANSIENT_FIELDS`, which `clear_coordination_transients` zeroes on the auto-charge and every other clear path. Every combat path — the garrison assault, the charge and the auto-charge — reads the standing term (the Presence lesson).
- **Its own declared set.** The term is listed in a new production tuple, `Marshal.DERIVED_STANDING_FIELDS`. Both serialization censuses take the union of the declared sets:
  - the fresh-marshal enforcement test;
  - the played-world census's `_exempt_for`.
  - This is a conscious change, recorded (FA-91: an exemption is a declared set, never a copy). The glory crown takes the other road: it is serialized, and re-derived by `recompute_crowns`. This term is derived whole at every load, so storing it would only add a second copy that can drift. It is the one pinned exception to `REFORMS_SPEC.md` §2's "no second store".
- **T9 is the drift pin**, with one staged case per nation-change seam.
- A bare marshal with no term (M1–M6's `_mk` marshals, M7's Austrian stand-ins) reads neutral.

**The poor-country test reads province identity and war damage, never capacity.**
- `_supply_multiplier`'s WO slice-8 invariant is that the decision reads only (nation, region). That is what lets the depot chip price its counterfactual exactly.
- The authored `poor_country` list and the 1805 homeland are identity, and war damage is not capacity, so the invariant holds.
- A capacity threshold would break it, so D-R1 authors a list rather than deriving one.

---

## §4 What the player sees

**Each court's doctrine is shown** — name, `says`, strength, flaw, and the law that cures it:
- for France, on the Generals screen;
- for every great power, on its Diplomatic Ledger nation card, with the flaw's status: "uncured — the Articles of War would end it once the General Staff stands", or "cured since turn 23".

**Before France marches (RV-13).**
- **The map.** The region panel and the map tooltip mark a province outside the homeland that is not an ally's or vassal's:
  - "Poor country — a French army here draws 80%";
  - or "Stripped by war (30%) — poor country for a French army until it recovers below 25%".
  - The stripped mark obeys fog: it reads `region_econ_visible`, and a fogged province's war damage is sent as −1 (the PC15-16 sentinel), never 0 or its true value. The poor-country mark is geography and always shows.
- **The muster.** The supply note names the doctrine when it is the cause, and reads stripped country forward (§3).
- **The laws.** The LAWS tab's Train des Équipages row says what it would lift *this turn*: "cures living off the land — 2 corps drawing 80% now". This is live, read from the same multiplier with the flaw off. The row also names its Staff condition: "needs the Grand Quartier Général in force".

**When a doctrine fires, it is named where it fires:**
- **The muster row:** "the corps system lowers the bar"; on an enemy reinforcement line, "slow to concentrate" or "the Hofkriegsrat".
- **The battle report (RV-7, RV-16):**
  - doctrine rows in the modifier snapshot, each printing the share that applied after the caps — "The Line Holds +15%", "Frederick's Drill +10%" (on a reinforcer's line too);
  - a new morale line for a lopsided defeat, with its numbers — "the Russians would not break: stubbornness halved the rout (−21 morale, not −42)"; "the Prussian line broke: −63 morale";
  - a doctrine-decided arrival or no-show, named — "the corps system brought Davout in"; "the Hofkriegsrat's orders reached Archduke John too late".
- **The supply-strain headline:** "living off the land: this stripped country feeds a French army 80%". Its remedy clause names the Train des Équipages when France has not enacted it and `law_refusal` allows it.
- **The enemy-phase recruit line**, from a structured field (the CA8-6 idiom), carrying only the doctrine's own term: "Austria raises another army (the Hereditary Lands, ×0.85)"; "Britain recruits dear (×1.25)".
  - The recruit quote names the same term by construction, since it is one of the price's named terms. It appears only when the player's own court carries a recruit clause, which today none does. No owner is needed.
- **A Berthier observation:** when a French battle is joined by corps arriving from two or more provinces, "The corps marched apart and arrived together." It reads the existing reinforcement results and is display only.

**The laws say what they cure.** The LAWS tab names the doctrine flaw a law cures, and the Staff it needs.

**The catch-up is announced.** When a rival's cure takes effect — its cure law and its Staff both in force — the reforms' dispatch beat (`REFORMS_SPEC.md` §8) names the flaw it ends: "Vienna adopts the corps d'armée — the Hofkriegsrat's delays are over." Diplomacy has no fog.

**An uncured flaw is a window, and the player can see it.** The nation card says whether each rival's flaw still stands, so "strike Austria before Vienna adopts the corps" is a plan the player can read off the ledger. In 1805 Napoleon met an Austria without corps; by 1809 it had them, and Aspern was the price. A cure goes silent when its law or its Staff lapses because its court cannot pay, which reopens the window, and the dispatch says so: "Vienna can no longer pay for its corps".

**The rivals' laws name what they copy from France** — `REFORMS_SPEC.md` §0 Q7. Example: "the corps system France has used since 1800".

---

## §5 The AI

**No new AI decision rules.** Every doctrine is a number on a seam the AI already reads:
- its muster and glory-gate odds read the arrival bar;
- its supply rung (P6.5) reads the effective cap;
- its recruit pre-budget reads the price;
- its combat reads the morale, attack and defence terms.

**The cures come with the Staff, when a court can pay for it** (RV-10, RV-15).
- A rival's cure takes effect only with its Staff in force. For Austria and Russia the cure IS the Staff: 9,000 gold, with an AI purse bar of about 11,500, and a forecast Net that must stay ≥ 0 after its 300 a turn.
- The RF-3 rung takes the first law a court can afford, so cheaper laws may come first and raise that bar. `REFORMS_SPEC.md` §7 names the recommended fix if T8 misses: the rung saves for the Staff.
- AI authority has no live writer, so each AI court makes exactly two political acts in a campaign (`REFORMS_SPEC.md` §3). Britain's and Prussia's cures are political acts, and the rung must spend one of those two on them.
- T8 records, per court: the turn the cure takes effect, which half of the purse test held it back, and every lapse. A miss belongs to RF-3's rung. Moving a cure to a different law is structural and goes to the user.

---

## §6 Acceptance — falsifiable targets

| # | Target | Pass condition |
|---|---|---|
| T1 | Each doctrine fires, and is named | A pinned, staged case for each strength and each flaw, on both boards where the seam is shared, and on both sides where §2 says a clause reaches both: a Prussian lead attacking; a Prussian reinforcer in a Prussian defence; a British lead defending; a British lead attacking, which gains nothing. Each case shows the doctrine named on the surface where it fires. So does every other DC-3 surface: the nation card's status line, the Generals block, both map marks (the stripped one fogged too), the LAWS tab's live line, the cure beat, the doctrine-decided copy and the Berthier line. |
| T2 | The cure | Every flaw has exactly one cure law. Enacting it with its Staff in force removes the flaw at the next read; a lapse or repeal of either brings the flaw back at the next read. |
| T3 | The homogeneity guard, and each style named | The AI-V sweep's homogeneity guard stays green. A played arm names each great power's style: a grep-able census of the named firing lines in its digest shows at least one line per court. The committed arms cannot show it, because Russia and Prussia never fought on any of them (§0.2). So DC-1 authors `tools/playtest_scripts/dc_jena_road.json`: a real campaign — concentrated corps, the corps system — that goes to war with Prussia and reaches Posen and East Prussia (1806–07). The script carries `"policy": {"declare_war": "proceed"}` itself. |
| T4 | Balance, re-measured | `BASELINE_SERIES` is re-recorded ONCE, at DC-2. With the lever `DOCTRINES_ACTIVE` down, the prior series reproduces byte for byte. Per-court and cure arms attribute the move. M1–M7 are expected byte-identical (RV-11); they are read, not assumed, and any movement is attributed. |
| T5 | The road to 45 | Q0 (`SCORE_MANDATE_PLAN.md` §4 SR-D3) is re-measured after the doctrines land. **Pass:** the best road's titled count falls by no more than two provinces. A larger fall re-opens France's numbers (the corps system's bar, the 80%) before the doctrines ship. |
| T6 | Reach | `tools/_dc_reach_census.py` is re-run on the lever-up tree, with the Jena road added. Every clause fires at least once on the arm built to reach it; for supply that means *bites* (the reduced cap raised attrition), never predicate hits. A clause that fires 0 times on every ambient seed is recorded in the landing record with its condition, e.g. "Russia's clauses fire only when France fights Russia". The pre-build census (§0.2) is the comparison. |
| T7 | Monotone | Over the whole reachable deterministic arrival range — sums −10 to 150, with `assume_order` both ways — the corps system never lowers the probability of arrival, and the two flaws never raise it. The supply, recruit, attack, defence and morale clauses are monotone the same way. Pinned as a grid, not a sample. |
| T8 | The cure's timing | Per rival, on the four ambient seeds: the turn its cure takes effect, which half of the purse test held it back until then, and every lapse. **Pass:** no rival's flaw is cured before turn 10 (the flaw lives), and at least two of the four have a cure in effect by turn 30 on the historical seed. A miss belongs to RF-3 (§5). |
| T9 | No drift | After every mutating route of a driven arm, and in one staged case per nation-change seam (§3), every marshal's `_doctrine_terms` equals a fresh derivation. A load restores the terms only after the `reforms` store (RV-6). |

**Gates for every slice:** every pin mutation-swept to 0 INERT; any `.gd` change passes the parse harness (EXIT=0) and a boot with 0 SCRIPT ERROR.

---

## §7 The build slices — Chunk 7's head, "SR-7d The Doctrines"

| Slice | Scope | Size (sessions) |
|---|---|---|
| **DC-0** | **The substrate.**<br>• The `doctrines` and `poor_country` scenario keys and their validator blocks (§1, without `cured_by`).<br>• The save field and its 1805-only backfill (§9).<br>• `backend/game_logic/doctrines.py`: the accessors, the forward-reading poor-or-stripped predicate, `refresh_doctrine_terms`, and `set_marshal_nation` with its AST census.<br>• The ONE arrival bar with `assume_order` (RV-1: the resolver and the odds row call `_arrival_threshold`, byte-identical, pinned).<br>No doctrine is active yet. | 0.4 |
| **DC-1** | **Strengths and flaws.**<br>• The ten clauses at their seams, behind `DOCTRINES_ACTIVE = False` with per-court sub-levers; pins run the lever up.<br>• The character rule (RV-2); `doctrine_delayed` and the trust-dock exemption (RV-16); the draft-only recruit term (RV-17).<br>• The census re-run counting bites, and the Jena road authored as a real campaign.<br>• T1 (backend), T3, T6, T7 and T9. | 0.6 |
| **DC-2** | **The cures.**<br>• The `cures` law effect type (D-R4) with its Staff condition (RV-15); the Train des Équipages authored (D-R3); the four cure clauses; `cured_by` and its validator rule.<br>• The lever flipped and `BASELINE_SERIES` re-recorded ONCE (T4).<br>• T2 and T8.<br>• `REFORMS_SPEC.md` §11 T2 (the sink) re-run with the Train in France's slate. | 0.4 |
| **DC-3** | **The client and the words.**<br>• The doctrine rows on the Generals screen and the nation cards.<br>• The named firing lines, including the new morale line, the snapshot rows with their applied shares, and the doctrine-decided copy (RV-7, RV-16).<br>• Poor and stripped country on the region panel and tooltip, with fog.<br>• The supply headline's Train remedy; the LAWS tab's live cure line; the enemy-phase recruit note; the cure beat; the Berthier line.<br>• T1's client pins. Parse harness and boot. | 0.4 |

**Size.** About 1.8 sessions. Chunk 7 grows from about 2.0 sessions to about 3.8.

**Dependency.** DC-2 needs the laws (SR-5r, Chunk 5), and Chunk 7 comes after Chunk 5.

**What not to build first:**
- anything the AI cannot play;
- a cure clause before its flaw exists;
- a clause whose reach was not counted (T6);
- a second playable nation.

---

## §8 Not in this ruling — each with its home, or struck

| Item | Disposition |
|---|---|
| The winter and the seasons | `SEASONS_WEATHER_SPEC.md`: the first content slice after the first outside playtest ("The General Winter"). |
| The standing alarm floor (SR-G7 / PB-D1) | Still a question for Chunk 7's gate (`SCORE_MANDATE_PLAN.md` §2 Chunk 7). |
| "The Guns" — Austrian artillery recruits ×0.85 | **Struck by RV-3** unless the user restores it; RV-3 names the defensive alternative. If restored, T6 records it as dormant on every measured board. |
| "Frederick's Drill" as drill morale +5 | **Struck by RV-4** unless the user restores it. If restored, T6 records it as dormant for the AI (§3's struck row). |
| Stripped country for every army, not only France's | Not planned and not promised: it would be a new rule of supply for every army, not a doctrine. |
| Doctrines for secondary and minor courts, created clients and formed nations | Not in v1, and nothing in the client promises them. They boot with none (§9). If they are ever wanted, they re-open at this gate. |
| Historical Moments (SR-D2 Q4) | Not with the doctrines. The Events System is cut to after Early Access (`ROADMAP.md` §The Road to Early Access). |
| A second playable nation | Out of scope (post-EA). The doctrines are written so a British player could inherit Britain's; the recruit quote would name his term by construction (§4). |

---

## §9 The save format (RV-8)

**ONE new serialized world field, `doctrines`.** It holds the scenario's per-court table (the stripped-country line rides France's clause) and its `poor_country` list, copied at `from_scenario` (the agendas-deck idiom).

**Old saves.** A pre-doctrine save is backfilled from the 1805 scenario at load (the EB-2 idiom, drift-pinned) — **only when the save's `scenario_name` is the 1805 campaign**. A tutorial or modded-scenario save receives none. `REFORMS_SPEC.md` §10's backfill takes the same discriminator.

**Derived, never stored:**
- whether a flaw is cured — read from the laws in force and the court's Staff (`REFORMS_SPEC.md` §10, RV-15);
- stripped country — read from `region.war_damage`, already serialized;
- the homeland — `nation_starting_regions`, already part of the world;
- each marshal's `_doctrine_terms` — re-derived at load after the `reforms` store (RV-6), and declared in `Marshal.DERIVED_STANDING_FIELDS`.

**Docs and tests.** Update `SAVE_FORMAT_REFERENCE.md` and the serialization censuses: the new world field serialized, and the Marshal exemption widened to the union of the declared sets in both the fresh-marshal test and the played-world census.

**Who has none.** The legacy 19-region world (N1), the tutorial scenario (so the School's lesson, pinned as arithmetic, stays byte-identical) and every created client or formed nation author no doctrine.
