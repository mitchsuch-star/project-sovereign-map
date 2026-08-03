> **Provenance.** Commissioned August 3, 2026 by the user's direction — *"per economy
> send agents to research better solutions historically in other games, etc"* — after the
> quiet-France played campaign (`QUIET_FRANCE_CAMPAIGN_2026_08_03.md`) found that a passive
> France accumulates gold and actions with nothing to buy. Nine agents: four research
> strands (the historical record · how other strategy games solve it · what this codebase
> can carry · an adversarial anti-brief), a critique of each, and a synthesis that
> adjudicates between them. Every ⊕ number was measured against the shipped 1805 board,
> not quoted.
>
> **Status: RESEARCH ONLY — nothing here is built or approved.** §6 carries six open
> questions for the user, each with a recommended default. Owner row: `ROADMAP.md` **EC-P3**
> (economy pass 3) until the user rules on §6; the recommended first slice is bundled with
> the composition slice already owed position 3.
>
> **It corrects the finding that prompted it.** My campaign report said passive France had
> nothing to buy. That is wrong, and the sharper version is worse: the purchase that would
> have saved the campaign existed, cost 2,250 gold, and was invisible — France boots
> **+59,000 over** its own force limit, so the first ten turns teach that recruitment is
> forbidden; by turn 12 it was *under* the limit with a full manpower pool, and nothing
> ever said the gate had re-opened.

# DECISION MEMO — What a Napoleonic Empire Buys When It Isn't Conquering

**To:** project owner · **Date:** August 3, 2026 · **Basis:** four research strands + their critiques, plus an independent 42-turn measurement run this session (`SOVEREIGN_SEED=historical`, mock mode, France fully passive from turn 1). Every number marked ⊕ is mine, measured today, not quoted.

---

## 1. The verdict

**Build a slice, not a programme — and it is not a peacetime economy.** The anti-brief argued we should make passive play legibly punishing rather than comfortable. I tested that claim and it is already true and it did not work: ⊕ over 42 passive turns France's army fell 189,000 → 60,183, it lost nine provinces, war exhaustion ratcheted to its cap of 200 by turn 19, and the War Effort tax burned **2,319 gold a turn** off the treasury from then on. Passive France was punished about as hard as this engine can punish, and *still* ended with ~29,000g and four unused actions. So punishment is not the missing ingredient, and neither is a shop. The actual finding is narrower and more embarrassing: ⊕ **the one purchase that would have saved that campaign was available, cost 2,250 gold, and was invisible.** From turn 12 onward France was *under* its force limit with a full 100,000-man infantry pool; five recruits (2,250g, ~45g per 1,000 men) would have put 47,500 men back in the field. The player never bought them because turns 1–10 had taught the opposite lesson — France boots ⊕ **+59,000 over** its own force limit — and nothing ever said the gate had re-opened. Meanwhile the game confiscated, silently, more gold every single turn than the entire rebuild would have cost. **Recommendation: one session on "the levy is open and the camp decays," bundled with the composition slice already owed position 3. Reject the peacetime-economy programme. Send ES-4 / EC-2 pass 2 back to its own gate, post-position-7.**

---

## 2. The problem, in decisions

For twenty consecutive turns the player had exactly **one** live decision — which marshal gets the next pension — because every other channel was closed by a different mechanism: estates were unreachable (⊕ **0 conquered provinces held in all 42 turns**; `check_estate_eligibility` refuses homeland soil outright), construction was exhausted (⊕ France holds **13 building slots, total, forever**, across 28 provinces; ⊕ 49 of 126 provinces map-wide can never hold a building), the marshal bench was finite (7 men, 30,000g, then dead), shipbuilding was rate-capped at 1–2 keels, and recruitment — the one uncapped, high-impact, correctly-priced channel — had been taught to the player as forbidden during the ten turns it genuinely was. That is not "an empty treasury problem." **It is a game that closed one door in front of the player, opened it again behind their back, and spent their money in the meantime.**

---

## 3. Ranked proposals

Ranked by (impact on the measured campaign) ÷ (build cost). All four together are ~4 sessions; **only #1 is recommended now.**

---

### #1 — THE LEVY AND THE CAMP
*"The army is a standing bill, not a stock — and the levy re-opens out loud."*

Two halves that must ship together because each fixes one of the two idle resources.

**(a) The Levy is open.** Surface force-limit headroom as a first-class number and announce the moment it flips. **(b) The Camp of Boulogne.** A new `Marshal.readiness` (0–100) that **decays 3/turn** for any marshal that neither fought, drilled, fortified nor moved this turn, restored **+12** by `drill` and **+6** by `fortify`, floor 40, and read as a small multiplier inside `get_attack_modifier`/`get_defense_modifier` — the single-source rule, Golden Rule 1.

**Historical grounding.** The Camp of Boulogne, 1803–05: 150,000–200,000 men drilled for two years, corps-level combined-arms exercise every Sunday, and Houdecek's assessment for *Napoleonica* is that those two years of drill "truly came into their own during the 1805 campaign and at Austerlitz." The invasion never sailed; **the preparation was the product.** The mirror is the conscription classes — the class of 1814 called a year early in January 1813 — France's actual answer to "what do we buy between campaigns."

**Pattern, and who proved it.** Old World's Orders: the action budget is scarce even in total peace because *maintained things consume attention every turn*. The reason this game's 4 military AP sat idle is not a short menu — `move`, `scout`, `drill`, `fortify`, `defend`, `garrison` were all legal every turn — it is that **drill and fortify buy permanent, non-decaying state, so the tenth turn of drill is worth exactly zero.** Decay is what converts a menu into a budget.

**The dilemma.** Real, and it is the same 2 admin AP the dispatch is already screaming about. ⊕ Rebuilding 47,500 men = 5 recruits = **5 admin AP = 2.5 turns of the entire admin budget** — the identical budget the pension and the estate compete for. So: *rearm the army, or settle with Davout.* And on the military side: 4 AP against 5–7 marshals means **you cannot keep everyone sharp**; readiness is a choice about which corps is the one you intend to fight with. Passes all five of the game-design strand's decision tests, including test 5 (an external claimant — the enemy drills too).

**Mechanic.**
- Force-limit headroom: `calculate_turn_upkeep` **already returns** `force_limit`, `total_strength`, `over_limit`, and `ledger.py:387-388` already carries both. This is a render + a dispatch beat, not a computation.
- A new `over_limit` → `under_limit` transition fires a once-per-flip dispatch line: *"Sire — the establishment now stands 18,000 under the ordinance. The depots are open."* Ride the existing `HEADLINE_WEIGHTS` table at weight ~45.
- Region-panel recruit chip states the live price (⊕ **450g per 10,000 infantry at the capital at war**) and the headroom.
- `Marshal.readiness` decay ticks inside the existing `_process_tactical_states` per-marshal loop — **no region scan, GR8 free.**
- Readiness enters combat **only** via `get_attack_modifier`/`get_defense_modifier` (GR1). Suggested band: `+0%` at 100, `−10%` at the floor of 40 — noticeable, never a death spiral.
- `training_ground` (today a 250g building with a 40g/turn bill and no measurable peacetime effect) halves decay in its province. It finally does something.

**New serialized fields: exactly ONE** (`Marshal.readiness: int`), on a class that already serializes ~40. Zero new actions — no `VALID_ACTIONS` row, no parser keyword, no display name, no campaign-log type, no golden-corpus row, **no 12-step checklist pass, and no new enemy-phase rung.**

**GR5.** Free by construction. Decay is nation-agnostic in the shared tactical tick; the AI's existing `drill`/`fortify` rungs restore it with no new decision code. This is the *only* proposal here that adds zero milliseconds to the enemy phase — which matters, because that pillar just re-scored **6.0 against a 6.5 target**.

**Coalition threat.** Half (a) makes a re-arming France strictly stronger, and ⊕ passive threat is **100% territorial** (`coalition.py:1858-1900`: `region_control_60/70/80` plus `_calculate_hegemony_pressure` on bloc share). A France that gets stronger without getting bigger is invisible to Europe — the dominant-strategy hole the failure-modes strand correctly named and then didn't close. **So half (a) ships with a third clause: a strength-share term beside the territorial one** — `add_threat(world, 1, "military_establishment", target=n)` when a nation's share of Europe's standing strength exceeds ~40%, ⊕ boot-zero-checked (France's 189,000 of Europe's ~540,000 is 35%). `add_threat` already keys by source string and `threat_by_target` already has per-nation slots since AI-4a step 5 — **zero new serialized fields**, and it is symmetric, so a re-arming Austria is seen too. Never ship (a) without this.

**Size.** **1 session**, plus ~½ for the threat term and its band test.

**Falsifiable acceptance test.** *In a 40-turn campaign where France goes passive at turn 5: (i) France's strength at turn 40 is ≥ 60% of its turn-5 strength, or the transcript contains a turn on which the player declined a stated levy offer with the headroom and price on screen; (ii) at least **1.2 admin actions per turn** on average are spent on `recruit`; (iii) mean marshal readiness at turn 40 is < 85 (i.e. the decay is biting and cannot be fully covered); (iv) the treasury at turn 40 is below **20,000** — down from ⊕ the measured 29,000 plateau.* All four are readable off the existing sweep driver.

---

### #2 — ES-7b "CONFER A TITLE" — the land-poor reward valve
*"A flat gift buys a K-turn holiday from a marshal's grievance, without land."*

**This proposal is already written, scored, owned and named-with-a-test in the repo** (`ECONOMY_REVISIT_SPEC.md:123` and `:174`; owner EC-2 pass 2; test `test_es7_confer_title_holiday`). Nothing below is new design — it is a recommendation to *land the row*.

**Historical grounding.** The imperial nobility and the *majorats*: hereditary thresholds at duke 200,000fr / count 30,000 / baron 15,000 / knight 3,000, and ~6,000 donataires drawing ~30M francs a year by 1814 — with roughly **20 men absorbing ~60%** of all dotation revenue. The concentration is the point: the *unrewarded* were always the majority, and the Légion d'honneur (1802) was precisely the instrument for honouring a man you could not endow with a province.

**Pattern.** CK3 Court Grandeur's shape — pay for a maintained condition that decays back to baseline — minus the tier ladder, which is where its field cost lives.

**The dilemma.** Land is permanent and free forever once granted; a title is cash now and the clock restarts. ⊕ Against a 29,000g treasury a single title is trivially affordable, so the real dilemma is **the admin AP against the levy in #1**, plus the ES-7 truth that paying stops the bleed and never buys trust. Honest.

**Mechanic.** `confer_title <marshal>`, 1 admin AP + a rising flat fee (`int(1500 × 1.5^titles)`, per ES-8's own ladder), sets `expectation_grace_turn = current_turn + K` (K ≈ 8). **Zero new serialized fields — `Marshal.expectation_grace_turn` already exists and already serializes** (`marshal.py:344`, `:1427`). Full 12-step checklist for one new action.

**GR5.** The AI's `_pick_admin_action` already has a `grant_dotation` / `grant_pension` branch; this is one more arm on the same rung, and an AI that has stopped conquering wants it for the same reason.

**Coalition threat.** None. Purely internal. That is a feature.

**Size.** **1 session.**

**Acceptance test.** *In the same passive campaign, `estate_eroding` leads fewer than 8 of 40 dispatches (⊕ measured baseline: **21 of 41, 51%, longest run 7**), and titles are conferred at least 3 times.* Note the July-19 dispatch fix already landed a standing-class yield rule; this measures whether the *cause* is addressable, not whether the symptom is muted.

---

### #3 — SUPPLY BECOMES A DECISION YOU CAN SEE
*"Berthier tells you the corps is over capacity, names the number, and names both remedies."*

**The historical hook** is the magazine system and the subsistence council of 28 August 1811 — but honestly this is a defect fix wearing a proposal's clothes.

**The evidence.** Three corps starved. ⊕ Attrition is capped at 6%/turn (`world_state.py:5215`) — slow enough that no single turn alarms and thirty turns are fatal. And ⊕ **`supply_attrition` is not in `HEADLINE_WEIGHTS` at all**: it can only ever appear as a marshal status note ("Starving — supply has failed at X two turns running"), never as the dispatch's lead, while `estate_eroding` at weight 55 led half of them.

**Adjudication against the strands.** The failure-modes strand said "the sink existed, it cost 300g, the game never said so." **That is wrong and its critique is right**: `supply_depot`'s `allowed_in` is `["capital","major_city","city"]`, so ⊕ it is **illegal in 16 of France's 28 provinces**, and the stacking penalty (+1%/marshal beyond the first, applied even *under* capacity at ≥3 marshals) means three corps in one province bleed by *being three corps*. **The remedy was dispersal — which costs the military AP that was idle — not a building.** So the honest fix names both remedies and never sends the player to build where the order will be refused.

**The dilemma.** Concentration wins battles (the reinforcement system commits neighbours — see PC-6); dispersal survives peace. That is a genuine, historical, permanently-live trade-off and the game already simulates both sides of it.

**Mechanic.** A `supply_strain` headline class at weight ~72 (above `region_lost`, below `enemy_on_our_soil`), fired when a French stack has taken attrition two turns running; the line names the stack, the capacity, the cumulative loss, and **whichever remedy is legal** — the nearest depot-eligible province, or "disperse." Region panel shows `troops / capacity`. **Zero new serialized fields** (the event log already carries `supply_attrition`; `_collect_supply_attrition_turns` already exists at `dispatch.py:586`). Zero new actions.

**GR5.** N/A — display only, player-side. Justified as player-only: it is a dispatch, and the AI does not read dispatches.

**Size.** **~½ session.**

**Acceptance test.** *In a 40-turn passive campaign, cumulative French supply-attrition losses are below 15,000 men (⊕ against a measured 189,000→60,183 collapse in which attrition was a major contributor), OR the transcript shows the strain headline fired and the player chose to eat it.* The second arm is the honest one: legibility's success condition is an *informed* loss, not a smaller one.

---

### #4 — ES-4 PROVINCE DEVELOPMENT — the real gold sink, and it is not next
*"`develop <region>`, +1 level, 500 → 900 → 1500 → 2400 → 3600, hard-capped."*

**Included because it is the only proposal here big enough to actually move the treasury**, and because it is already specified in `ECONOMY_REVISIT_SPEC.md:386` with a written gate. ⊕ Its ladder is **10,700g to cap one province**; across France's 28 that is ~300,000 gold and ~140 admin AP. That is the correct order of magnitude — and it is exactly why it must not be built now.

**The dilemma.** Chunky, permanent, exclusive: 10,700g and 5 admin AP into Normandy is Normandy instead of Lorraine, and it is not the army. Passes the decision test on rivalry and hysteresis; **weak on the clock** — and the row's own honest answer is that the clock should be the coalition threat, not a new timer.

**Fields: ONE** (`Region.development`). **GR5: this is the row's own written problem** — the spec says *"AI won't use it (name as slice-1 non-goal)"*, which is a standing GR5 conflict that must be ruled on at the gate, not per-proposal (see §6, Q3).

**Why not now.** Three reasons. First, ⊕ **the treasury is a fixed point, not a runaway** — at the WE cap the tax takes 8%/turn, so the plateau is ≈ 12.5 × free cash flow (⊕ my probe: 1,938 net × 12.5 ≈ the 29,000 it sat at). A development sink of 10,700g per province is a *stock* purchase against a *stock* that self-limits; it will absorb money without changing the equilibrium. Second, it is priced entirely in the admin AP that ⊕ was **not** the idle pool. Third, Victoria 3 is the standing warning: "the game resembles an idle game with extra strings attached." A 126-province development ladder is that game.

**Size.** **2–3 sessions + a gate.** Recommended slot: after position 7, at EC-2 pass 2's own gate.

**Acceptance test** (for when it is built): *in a 40-turn passive campaign, treasury never exceeds 15,000 and at least 6 development levels are purchased.*

---

## 4. What NOT to build

| Rejected | Why |
|---|---|
| **A new "rente" as a government-bond confidence index** (history strand #5) | Three fatal problems. The **name is already taken** — ⊕ `rente` appears in 17 backend files (`dotation.py`, `jealousy.py`, `ledger.py`, `marshal_overview.py`) and is the pension the player actually bought. The **history is wrong**: Mollien became Treasury Minister 27 January 1806, *after* the October 1805 episode the row describes, and the row conflates the rente price with the *obligations des receveurs généraux* crisis. And it has **no dilemma at peace** — buying your own bonds to hold up a number is not a choice, it is a chore. |
| **"Spend gold to raise stability / repair war damage"** (codebase-fit's #1 substrate) | ⊕ Measured: **all 28 French provinces sat at exactly 100/100/100 for all 42 turns**, and war damage self-heals at −0.02/turn for free. You would be selling a free good. Worse, `_get_stability_modifier` is a **4-step function** (0/0.25/0.75/1.0 at ≤25/≤50/≤75) with +5–10/turn regrowth: any decay under 5/turn is invisible and any decay over it cascades map-wide. There is no interior to spend against. It also directly violates ES-4's own written instruction — *"**Drop** any per-turn maintenance… A **want**, not a tax."* |
| **"Let a rich France outbid Britain for Europe"** (game-design P7 inverted) | Already shipped, and it cannot absorb the surplus by construction. `instruments.py` has `grant_directed_sponsorship` / `compute_buyoff_price` / `pledge_guarantee`; the paymaster caps at **400g/turn** (`agendas.py:37-39`) and a buy-off is `300 + 12×weight` ≈ 1,000g once. The bottleneck is **5 diplomatic points**, not gold. |
| **"France should subsidise its clients"** (history strand row 7) | Direction error, and the machinery is already built the right way round. `vassal.py:988` `process_vassal_tribute` has France *extracting*; `TRIBUTE_RATES` by autonomy tier **is** the Rheinbund squeeze-vs-loyalty dial; `coalition.py:1152` already generalises the paymaster posture with Britain as the boot case. |
| **Roads, canals, education, the Concordat, police, grain reserves** (history rows 10, 12–15) | Empire-wide recurring per-province effects across 126 provinces — the exact shape GR8 forbids — with paybacks longer than a campaign and no visible intermediate state. Row 15 disqualifies itself in its own text: *"you will not see it inside a campaign."* A player already ending turns with 4 unused AP does not need chores. |
| **Monuments / prestige ladders / decadence scoring** (game-design P6, P9, P12) | P9 pays out after the campaign ends. P6 and P12's scoring half are **Victory & Objectives material** (position 6–7) and proposing them here is scope collision with a pass that has its own gate. |
| **More buildings, or raising `EUROPE_INFRASTRUCTURE_UPKEEP`** | ⊕ A market on a `city` — the modal buildable tier, 41 of 126 provinces — earns +37 gross against 40g/turn upkeep = **−3/turn, permanently.** Four of the six building types produce no income at all and cost 40/turn forever. Any new building inherits a system that already punishes building. If anything here changes, it is scaling the 40 by tier — a constants fix, not content. |
| **Un-reversing EC-U1 (non-regressive / high-water-mark upkeep)** | ⊕ The perverse gradient is real and I measured it — France's free cash flow **rose from 1,070 to 1,938/turn** while it lost 129,000 men and nine provinces. But this was a **user-directed reversal on July 14, 2026** ("you pay for the soldiers you have"). Do not re-litigate it by the back door. #1 addresses the same perversity from the other side: make the army something you *want* to buy back. |
| **Converting unused military AP into admin AP, or pricing new sinks in admin AP** | ⊕ The idle pool was **military** (`meta_executor.py:157` reads `world.actions_remaining`); eight admin verbs already contest 2 AP. Fungibility would starve the contested pool and leave the measured warning firing unchanged, while paying the full GR5 enemy-phase cost against a pillar that just scored 6.0. |
| **Deleting `_calculate_admin_bonus` (+25g/unused admin AP)** | Tempting — the game literally pays you for idleness — but ⊕ it is **50g/turn against a 29,000g treasury**, i.e. nothing, and removing it silently re-prices every admin action by 25g. Leave it; note it at the gate as the project's declared AP↔gold exchange rate (Q4). |

---

## 5. The recommended first slice

**Ship #1(a) + #3 together in one session: "The Levy Is Open" + "The Corps Is Starving."** These are the two halves of the same failure — the game had one thing worth buying and one thing worth watching, and reported neither.

**What it would have changed about the actual 42 turns:**

Around turn 12, with 23,430g in the chest, France's army fell below its force limit for the first time. Under this slice the turn-12 dispatch reads:

> *Sire — the establishment now stands 18,000 men under the ordinance, and the depots hold 100,000. Ten thousand foot cost 450 gold at Paris.*

And by turn 14, alongside it:

> *Sire — Lannes, Murat and Bernadotte stand 20,000 over what Franche-Comté can feed. They have lost 4,100 men in two turns. Franche-Comté is a town — no depot may be laid there. Move one corps, or continue to pay.*

⊕ The rebuild that would have followed — **five recruits, 2,250 gold, 47,500 men** — costs **less than one turn of the War Effort tax that campaign was already paying invisibly** (2,319g/turn from turn 19). The player was not hoarding. They were being taxed at 8% a turn for nothing, while the thing the tax would have bought sat behind a closed sign.

I would then add #1(b) (readiness decay) and the threat term in a half-session follow-on — because #1(a) alone hands a passive France a free army, and (b) plus the strength-share threat is what makes it a bet instead of a gift.

**Where it goes on the road.** ⊕ Position 1 is *done* — `docs/audits/QUIET_FRANCE_CAMPAIGN_2026_08_03.md` re-scored the enemy phase at **6.0**, upheld the dissent, and the composition slice is owed **position 3**. This slice should be **bundled with position 3**, not inserted as a new row, and it must not displace position 4. The anti-brief's opportunity-cost argument was written against a stale roadmap, but its *ordering* instinct is right and I am honouring it: this is one session, it touches no `.gd` file, and it adds nothing to the enemy phase.

---

## 6. Open questions for you

**Q1 — Does readiness touch combat, or only display?**
Recommended default: **it touches combat**, small (0% at 100, −10% at the floor of 40), via `get_attack_modifier`/`get_defense_modifier` only. A display-only readiness bar is a chore with a number attached; the whole point is that an army you stopped drilling loses a battle it should have won. But this is a balance change to a system that has an M1–M7 harness, and the harness will move — say so before I build it.

**Q2 — Does Europe see a re-arming France?**
Recommended default: **yes** — a strength-share threat term beside the territorial one, symmetric across all nations, boot-zero-checked. The alternative is the dominant strategy the failure-modes strand identified: stop conquering, re-arm, let threat decay, strike a Europe that stopped watching. If you'd rather ship #1(a) alone and measure the hole first, say so — but then #1(a) is explicitly a comeback mechanic and should be labelled one.

**Q3 — The standing GR5 ruling for peacetime verbs.**
ES-4's own text says *"AI won't use it."* ⊕ Every peacetime sink has this problem: the AI nations on the 1805 board are essentially never simultaneously at peace, solvent and passive, so GR5 compliance will be *nominal* — the verb exists in the shared executor and the rung ~never fires. **Rule this once, at the gate, not per-proposal.** Recommended default: *"reachable by the AI through the same executor, with a measured firing rate that may be zero on the 1805 board"* satisfies GR5, and the acceptance test records the firing rate rather than requiring it to be non-zero.

**Q4 — Is an admin AP still worth 25 gold?**
⊕ `_calculate_admin_bonus` pays the player 25g per unused admin AP — the game's declared AP↔gold exchange rate. Every price in every proposal above inherits it. Recommended default: **leave 25 alone and price new actions against it deliberately** — a 500g action tells the player AP is free and gold is the only constraint, which is the precise inversion a 29,000g treasury does not need.

**Q5 — Where does #4 (ES-4) actually go?**
Recommended default: **EC-2 pass 2's own USER DESIGN GATE, scheduled after position 7.** It is the only thing here big enough to move the treasury and it is the thing most likely to turn this game into a spreadsheet. It should not ride in on a slice about the army.

**Q6 — One live GR9 debt, unrelated to this decision but surfaced by it.**
`ECONOMY_REVISIT_SPEC.md:175` — **EC-7 / ES-6** (distance-from-capital supply attrition) carries a dated trigger reading *"opens immediately after the EC-2 pair lands and its AI-solvency band test is green."* That happened **July 9, 2026**. The row was never opened. It is nearly a month old, it owns the *manpower* half of the exact failure this campaign produced, and it needs either a landing slice or an explicit cut.

---

**Files consulted for the measurements above:** `backend/models/world_state.py` (127-128, 141-142, 160, 180, 4391-4409, 4606-4616, 4618-4676, 4886-4895, 5140-5225) · `backend/models/region.py` (99-113, 196-212, 255-311) · `backend/commands/economy_executor.py` (268-300, 1209, 1267) · `backend/commands/meta_executor.py` (30-32, 156-159) · `backend/game_logic/coalition.py` (1845-1900, 2005-2028) · `backend/game_logic/dispatch.py` (55-105, 586) · `backend/game_logic/dotation.py` (43-55, 215-237) · `backend/models/marshal.py` (304, 339-352, 1426-1429) · `docs/audits/QUIET_FRANCE_CAMPAIGN_2026_08_03.md` · `docs/ROADMAP.md` §THE ROAD TO EARLY ACCESS · `docs/ECONOMY_REVISIT_SPEC.md` (123, 174-175, 386-396). Probe scripts left at `…/scratchpad/probe_static.py` and `probe_passive.py`.