# The economy audit (October 5, 2026)

**The brief, in the user's words:** *"make these decisions, and do full audit of economy to make sure it works well, is engaging and isn't too easy."* The decisions are the "waiting on you" list the final reading left (`docs/audits/SCORE_FINAL_2026_10_05.md`); they are ruled in `docs/SCORE_FINISH_SPEC.md` §6.7, which this memo's §9 summarises. The rest of this memo is the audit.

**Rules:** `docs/SYSTEMS_REFERENCE.md` §97. **Pins:** `tests/test_economy_audit_2026_10_05.py`. **Series attribution:** `tools/_econ_audit_series_arms.py` (record `tools/_econ_audit_series_arms_final.json`). **The reading:** `docs/audits/score_runs/2026_10_05_econ_audit/` (attribution `attribution.md` there). **Rows:** `docs/BUG_FIXES.md` §The Economy Audit (EA-1 … EA-19, EA-E1 … EA-E9) and `docs/DESIGN_REFINEMENT.md` §The Economy Audit (EAD-1 … EAD-9).

## In one paragraph

**The economy works as a brake, and its books were wrong.** No strategy we tried lets gold run away: the Charges of Empire hold a hoard at a ceiling, the upkeep surcharges cap an army at about 1.5× its force limit, and unpaid laws lapse. But every recurring transfer between courts — the sponsorships, the paymaster's war subsidy, London's Congress subsidy, the Continental System's closure, a vassal's own tribute — moved gold every turn on no ledger line, so the player's Net and every AI court's purse test read the wrong number (Britain's Net was positive on 8 of 9 late turns while its chest fell). Trade depended on whether a pair had ever fought, not on its state; dead courts kept trading; the System charged satellites for trade they never earned; a contingent's men were paid by nobody; and a chest that ended a turn just below zero bought halved upkeep forever without one deserter. **All of that is fixed (§4).** On "engaging": a France with 32,903 gold asking *"what should I spend gold on"* was told to raise 3,000 men for 230 gold — the Staff, the law that adds an order every day, was never named; and a market, the one building that exists to make money, netted +7 a turn. **Both are fixed (§5).** On "too easy": the opening war costs France nothing (Net positive on every opening turn, 11–14k in the chest by turn 10), and the AI's gold was inert (300,000 sitting in AI chests at turn 40, 80 watchtowers built for nothing, 13,000 paid to a court with no army). **The AI now spends its purse on its armies (§7)** — the enemy phase attacks 39 / 29 / 39 times on the three commanded seeds (was 31 / 10 / 16) and France still holds 28 / 29 / 28 provinces at turn 40. **The opening war's price is the user's gate** (§10, EAD-1): it sits inside the blessed E1 band, so moving it is a re-blessing, not a fix.

## 1. How it was audited

Six read-only investigators on `c1467898`, each with its own question, then the builds, then a reading.

| Investigator | Question | Method |
|---|---|---|
| A — the money map | Does every gold flow reach the books? | Wrapped `nation_gold` to record every write with its site; compared each nation's real treasury change with the applied ledger Net on every advance of three arms (a 12-turn sponsorship arm, 40 commanded turns, a spend arm) |
| B — trajectories | Is gold ever binding? What does everything cost? | 27 forty-turn campaigns, three seeds each: the commanded arm, a greedy spender, an adaptive saver, a maximum-army arm, the conquest road with and without spending, controls |
| C — the AI's purse | Why do AI chests sit idle? | A tracer on every AI gold write over the three commanded seeds; four counterfactual rungs measured |
| D — SFR-DR1 | Why does the league declare and rarely strike? | Pass-through hooks on every AI decision step, 81 corps-turns classified; four counterfactuals |
| E — §6 rows 22 and 18 | Is the petition floor's fall real? Is the dither reader right? | The FLAG, OP and LAW arms re-run and instrumented; the crisis tier re-simulated; a v1.1 reader written and run over 13 archives |
| F — the EYES marks | Do the panel's provisional marks stand? | Every frame, the capture runner and the client code read; the live client's own screenshots compared |

## 2. The money map

Every flow, where it lives, and what was wrong (✗ = fixed by this audit):

| Flow | Seam | On the Net? | Notes |
|---|---|---|---|
| Province income, trade dominance, overseas, requisitions | `calculate_turn_income` | ✓ | residual 0 on 40 of 40 advances |
| Diplomatic trade | `calculate_trade_breakdown` (new) | ✓ | ✗ a written PEACE traded 50, an unwritten one 0 (175 of 190 boot pairs); ✗ an eliminated court kept trading (EA-3) |
| Admin bonus | `_calculate_admin_bonus` | ✓ | courts with no marshal never receive it (N9, design row) |
| Vassal tribute | `process_vassal_tribute` | ✓ lord / ✗ vassal | the vassal's own Net never showed what it paid (EA-5) |
| Treaty and settlement gold | the applied-transfer idiom | ✓ | — |
| **Sponsorships, licences, neutrality** | `process_instruments` | ✗ | off the books on both sides (SFR-D39 / IQ1-3a′; EA-1) |
| **The paymaster's war subsidy** | `_process_british_subsidy` | ✗ | EA-1; ✗ paid Sardinia 13,000 with no army (EA-12) |
| **London's Congress subsidy** | `congress._london_pays` | ✗ | EA-1 |
| **The Continental System** | `apply_continental_system` | ✗ | charged satellites for trade they never earned, on no line (EA-4) |
| Upkeep | `calculate_turn_upkeep` | ✓ | ✗ a contingent's men billed to nobody, ~88 a turn (EA-6) |
| Occupation, contributions, Charges of Empire, dotations, rentes, laws, infrastructure, Admiralty | the income phase | ✓ | ✗ a market paid the tier upkeep and netted +7 (EA-9) |
| Bankruptcy mercy and desertion | `_update_bankruptcy` | ✓ | ✗ alternating just-below-zero turns: halved upkeep, no desertion, 224,000 men (EA-8) |
| One-shots (plunder, confiscation, the Butcher's Bill, purchases) | single-source quotes | outside Net by design | quote = charge (CN-4 census) |

## 3. Measured trajectories (the shipped tree, before the builds)

The commanded France, three seeds (treasury / Net a turn / army / provinces):

| turn | historical | austerlitz | marengo |
|---|---|---|---|
| 10 | 11.4k / +886 / 117k / 28 | 11.7k / +862 / 126k / 30 | 14.4k / +1,119 / 114k / 30 |
| 20 | 32.6k / +2,394 / 109k / 28 | 36.5k / +2,413 / 135k / 30 | 37.8k / +2,977 / 77k / 30 |
| 40 | 64.2k / +333 / 74k / 28 | 56.5k / −1,088 / 119k / 30 | 74.6k / −1,178 / 63k / 29 |

- **Gold binds only a France that chooses to spend.** The passive France banks; the Charges of Empire are its sink (37–44k over 40 turns, 66–87k on the conquest road — 43–55% of gross income).
- **Everything worth buying costs 50.7k once, then 1.4–1.6k a turn.** An adaptive saver buys it all by turn 35–40: one campaign pays for everything, just.
- **The opening war never puts France in deficit.** The lowest Net on turns 2–12 is +398 to +1,298 on every arm; the chest reaches 11–14k by turn 10 fighting three courts.
- **The levy's price never mattered.** 10,000 drafted infantry at Paris cost 210–260 gold at peace; upkeep, manpower and where a corps stands decide the army.
- **A spender is capped.** At ~200,000 men the upkeep surcharges hold Net near zero; the army plateaus at 195–213k.
- **AI gold was inert.** About 300,000 sat in AI chests at turn 40; the neutral Ottoman reached 58,000.

## 4. Works well — the correctness fixes

Each behind its own lever (`False` = the shipped behaviour); pins in `tests/test_economy_audit_2026_10_05.py`.

- **EA-1 "The Subsidies line"** (SFR-D39, IQ1-3a′, N1, N8): ONE signed Net component, `subsidies` ("Subsidies"), on both sides — payer −, recipient + — for the sponsorships, the paymaster's subsidy and London's Congress subsidy. The engines record what they moved (clamped by the payer's chest) into a transient store opened at the top of every advance; the ledger's applied mode reads it, the projection reads the live records through each engine's own planner (`coalition.projected_paymaster_subsidy` is now the one function the payment and the ledger both read). A short payment is said: "paid 0 of 200". Every AI purse test reads it (`instruments.THE_SUBSIDIES_ARE_ON_THE_BOOKS`). Surfaces: the ledger line with its stream rows, both end-turn banners, the treasury report, the desk's income sentence.
- **EA-3 "Trade is a treaty"** (N4, N5): a PEACE earns no trade, written or not — the 175 unwritten boot pairs never did, and paying them all would add ~250 a turn to every court the wrong way; trade comes from open borders and better (`diplomacy.A_PEACE_EARNS_NO_TRADE`). A court that no longer stands trades with nobody (`THE_DEAD_DO_NOT_TRADE`). `calculate_trade_breakdown` is the one per-partner source.
- **EA-4 "The System taxes trade that exists"** (N6): the closure takes the trade a member actually earns from Britain (at most 75 a member, 200 in all, both sides) and names it on a "Continental System" Net line (`THE_SYSTEM_CHARGES_ONLY_THE_TRADE_EARNED`).
- **EA-5** (N2): a court that is a vassal pays its tribute on its own Net (`ledger.THE_VASSAL_PAYS_ON_ITS_OWN_BOOKS`).
- **EA-6** (N3): the satellite pays for its contingent's men (`contingent.THE_SATELLITE_PAYS_ON_ITS_OWN_BILL`).
- **SFR-D23:** the crisis beat's buy-off line is priced against the morning's chest (`ledger.chest_forecast`), not the mid-advance one (`war_council.THE_BEAT_READS_THE_MORNINGS_CHEST`).
- **EA-8 "The army remembers its arrears":** two marks for every turn ended in deficit, one wiped by every solvent turn; desertion at five. Three deficits in a row desert at the third, as always; a deficit every other turn deserts at the fourth instead of never; one deficit is forgotten after two solvent turns. The mercy is unchanged. ONE new serialized field, `nation_pay_arrears` (`world_state.ARREARS_ARE_REMEMBERED`).

## 5. Engaging — what there is to buy, and whether the game says so

- **EA-9 "A market pays its own keep":** the one work whose whole purpose is revenue carries no maintenance — +27 a turn on a French city, +56 at Paris, paybacks 6–13 turns (was +7 and a 50-turn payback). The region panel's market chip says "no upkeep" (`world_state.A_MARKET_PAYS_ITS_OWN_KEEP`).
- **EA-13 "The Net says why it moved":** the morning dispatch keeps the morning's accounts (a transient snapshot), and the ledger names every Net line that moved 10% or more since yesterday, with its cause where the accounts carry one ("tribute 802 → 712 (Kingdom of Italy pays less by 90)"). The two bills SR-5a already explains keep their own notes, and the Charges' note now names its line ("last turn's charge"). Economy C2 — "every Net-line move of 10% or more names its cause" — reads ✓ for the first time (`ledger.THE_NET_SAYS_WHY_IT_MOVED`).
- **EA-14 "The counsel names the law":** the purse's counsel leads with the first gold law the verb would enact and the purse would carry (the rival courts' own purse test). While the Staff is unbought and the chest holds half its price, no smaller law is offered in its stead. On the commanded turn-20 save: *"enact the Staff — 9,000g, then 300g a turn (+1 order of the day, from the next refill)"* (`counsel.THE_COUNSEL_NAMES_THE_LAW`).
- **EA-15 "The desk answers the purse":** "what should I spend gold on", "what should we buy", "how are our finances", "how's the treasury?" and "are we going broke?" are answered (they shrugged — SFR-D1's class): the chest, its Net, and what is worth the gold today.
- **EA-18 "The counsel sees through the Charges"** (found pinning EA-14): the law line's purse test read the forecast Net, which the Charges of Empire depress in proportion to the chest — a France holding 30,000 netted +47 and was told to levy 3,000 infantry; at 40,000, −305. The Charges fall as the chest falls, so the counsel now asks whether the Net BEFORE them carries the upkeep (`counsel.THE_COUNSEL_SEES_THROUGH_THE_CHARGES`). The AI rung keeps the plain read; whether it should follow is EAD-9 — the rivals already enact above their band, so the plain read is acting as a brake.

## 6. Too easy? — the verdict

**Not too easy at the opening table, too easy at the opening war, and the late game is the player's to spend.**
- **The choices are real at the opening.** The Staff (9,000) against seven commissions (30,000) against a bigger army against laws: a saver needs the whole campaign to buy everything.
- **The opening war costs nothing.** The blessed E1 band (France's turn-1 absorption 62–70%, SR-5a) leaves France a surplus at war by design; changing it is a re-blessing (§10, EAD-1).
- **The Charges of Empire are a tax with no decision attached.** They work as a brake; a player has no lever on them (§10, EAD-2).
- **Men are nearly free to raise and an army carries no alarm.** The draft price never mattered; the army-size threat term needs 40% of Europe's men and even 213,000 reaches 35% (§10, EAD-3, EAD-4).
- **The AI now fights with its gold (§7)**, which is where most of the "too easy" was.

## 7. The AI's purse (GR5)

- **EA-10 "No tower for a court without fog":** a watchtower lifts the player's fog and the AI plays without fog — 80 AI towers, 250 gold and upkeep each, bought nothing. The AI builds and repairs none (`enemy_ai.THE_AI_BUILDS_NO_WATCHTOWERS`).
- **EA-11 "The court arms with its purse":** the AI's recruit rungs stopped at each corps' 1805 boot strength — a limit the executor does not have and the player never meets — so Sweden at war, with 14,000 gold and 61,000 men in its pool, raised nobody. When nothing else on the admin chain is worth buying, a court at war (or preparing one) now recruits past boot up to the severe band of its force limit, at peace up to 1.25× boot and only at a base, behind the laws rung's purse test (`enemy_ai.THE_COURT_ARMS_WITH_ITS_PURSE`). The peace-time field levy is deliberately closed: investigator C measured it ballooning the neutrals (the Ottoman 24k → 91k) for nothing.
- **EA-12 "A subsidy pays a court that fights":** the paymaster's subsidy and the AI's sponsor branch pay only a court that fields a corps (`coalition.A_SUBSIDY_PAYS_A_COURT_THAT_FIGHTS`).

**What it did to the game** (the commanded arms on this tree against the archive): the enemy phase attacks 39 / 29 / 39 times over the 40 turns (was 31 / 10 / 16); France holds 28 / 29 / 28 provinces at turn 40 (was 28 / 30 / 29); France's turn-40 chest is 42.7k / 49.0k / 57.8k (was 64.5k / 55.5k / 73.0k). The league marches (AI aliveness C6 ✓, §9).

## 8. The series, the metrics, the reading

**The series.** `BASELINE_SERIES` is re-recorded ONCE, fifteen arms attributed (`tools/_econ_audit_series_arms.py`; record `tools/_econ_audit_series_arms_final.json`).
- **Arm 0** (every audit lever down) reproduces the prior series byte for byte.
- **Nine levers are byte-identical alone**, with their reach counted: the league's two, the Subsidies line, the dead court's trade, the System's charge, the vassal's books, the contingent's bill, the morning's chest, the arrears. On the passive board the subsidy term is non-zero on one or two turns a court and Holland's contingent is billed for 40 turns, and none of it reaches a threat-bearing decision.
- **Five move it alone:** the arming rung from index 12, no towers from 27, a subsidy that pays a fighter and the market's keep from 28, a peace that earns no trade from 38.
- **All fourteen together part from the prior at index 18**; no single lever reproduces the shipped series. The passive France ends turn 40 with 12 provinces (5 with every lever down), Austria with 19 (26), Britain with 20 (20).

**The WO slice-10 ungated board** moves 7 → 14 collapses (`Champagne → Ney` 5, `Leon → Napoleon` 9; cooldown writes 14 / 1); with every audit lever down in the child the field read's figures return exactly (`tools/_econ_audit_wo_attribution.py`, record `tools/_econ_audit_wo_attribution.json`). The four pins are re-seated with that attribution; the gated board is the new series; the courting cap's rebellion turns are unchanged (12 / 18).

**M1–M7 byte-identical**, no re-record (the harness, 11 passed).

**Pins re-seated consciously**, each with its lever-down arm pinned beside it: the legacy trade tables (a PEACE earns nothing — `test_session_2_diplomacy.py`, `test_audit_2_3.py`, `test_phase3_balance.py`, `test_session5_diplomacy.py`), the damaged-watchtower pin (the AI builds none), the subsidy attribution pin (a court with no army is not paid), Step 1's league pin, the four series chain pins, and the "every lever down" arms of RS-27 and the front page (the audit's fourteen ride down with the rest).

**The reading** (`docs/audits/score_runs/2026_10_05_econ_audit/`): the final reading's arms re-run on this tree, the suite merged in; the client arm and OP-LIVE did not run (no Godot window, no key). Item flips against the final reading, v1:
- **✗ → ✓** economy C2 (EA-13), AI aliveness C6 (SFR-DR1), AI aliveness C5 (the board — ✓ with either lever group down), marshal drama F1 (4 modals, under v1's ≤ 4).
- **✓ → ✗ living balance C4** — the audit's levers in sum. With all of them down, Austria re-declares at turn 34 on CMD-M (✓). On the shipped tree the CMD-M peace breaks at turn 23 through Austria's own design war on Bavaria, which draws France in through its alliance — a cascade, which the item excludes — and CMD-H's general peace comes only at turns 39–40.
- **Living balance C5 read ✗ on the first check — the reader's own defect (EA-16)**: the dispatch records no league table on a morning the old league still stands, while the page's beat reads the same forecast every morning, so Prussia's news came one page before its row. Fixed and re-checked: ✓ (6 of 6 newly free courts on the page); the pre-correction files are kept beside (`*_before_ea16.json`). Tracing it found EA-19 (the forecast names a court in a truce with us; SF-RR4's).
- **·** on the UI/UX items and command C6 (not run).
- **Not flips, read for the record:** AI aliveness C1 stays ✗ for a new reason — the rivals enact 19–20 laws with 0 lapses, above the 13–18 band (SFR-B14's lapses are not reproduced). NAV1T-H ends at turn 27 with the Emperor deposed (the arm had already fallen from 28 to 7 provinces by turn 30 on the final reading); it persists with the arming rung down and completes with every lever down — the audit's levers in sum.

**Directional** (no score is claimed — §5; the panel did not run): v1 as read, 7.62 over 12 of 14 (the final reading 7.50 over 13). Checklist v1.1 with the delegate's EYES marks: the final reading 7.54 over 14 of 14; the audit's reading 7.69 over 13 of 14; **like for like over the 13 both exercise, 7.54 → 7.69**. Per pillar: economy 7.50 → 8.00 (C2), AI aliveness 7.50 → 8.00 (C6), living balance 8.50 → 8.00 (C4), command 6.00 → 7.50–8.00 (SF-RR1 part (i)'s P1 fix, not this audit's; C6 unread without the key); the rest held.

The attribution of every flip, with the raw reads: `docs/audits/score_runs/2026_10_05_econ_audit/attribution.md` (`tools/_econ_audit_exit_attribution.py`).

**Gates:** sweep `tools/_sweep_econ_audit.json` 30 → 30 killed, 0 INERT, 0 BROKEN at close. The first pass found two pins inert, both real weaknesses, both repaired: the System's cap pin read the constant it pinned, and the arming lever's pin called the rung past the lever (and, once moved into the chain, set the lever it was meant to read). The sweep's apply also gained the retry its restore already had, after a transient lock killed it at row 19. The Godot parse harness EXIT=0 (report regenerated); a headless boot smoke 0 SCRIPT ERROR on an unused port; the full suite on the pre-commit hook.

## 9. The decisions (the gate record is `SCORE_FINISH_SPEC.md` §6.7)

The final reading's open list, ruled under the user's delegation; each was researched first. The user's own word overrides any of them.

- **The EYES marks** (`eyes_delegate.json` in both readings): agendas C6 ✓ (the "Loading…" frame is a capture artefact, EA-E8), combat legibility C6 ✓, vassals C6 ✓; first contact C2 ✗ (SFR-H8), narration C6 ✗ (4 of 10 sampled mornings lead with the lesser news), naval C6 ✗ strict (EA-E1, EA-E3), UI/UX C5 ✗ (8 of 10 frames; the two failures are at 2.0 only), UI/UX C6 ✗ strict (Alt+R eaten by the NVIDIA overlay, EA-E9), marshal drama C6 ✗ (below).
- **Row 18 — AI aliveness C5:** as recommended; v1.1 counts a dither only.
- **Row 22 — economy C1 and marshal drama F1:** keep row 16 and every rule, tune nothing; re-anchor both items to the targets the user set (the petition revisit's ≤ 9 / no run of more than 2 / 0 silent losses; REFORMS T1's turns 10–15). The row's suggested lever (raise the crisis tier to level 3) is wrong by measurement: it hides the level-2 card, the one window in which a Promise can still stop the spiral.
- **Rows 17, 19, 20, 21 — CONFIRMED**, each with its re-open condition; A2 re-anchored to *SHUT OUT for a sitting on at least one benchmark seed, the record naming what breaks it on the others*.
- **SFR-DR1 — RULED (a) re-cast, with the rider, and BUILT** (rules `SYSTEMS_REFERENCE.md` §97.12): the probe found no strength restraint holding the league — the wall was diplomatic. `form_coalition` declared each member's war without suppressing the offensive cascade, so the first declarer swept the others into a war against France alone, at peace with France's allies, whose closed frontiers walled Austria in. Each member now declares in its own right; a court whose declaration fails is not a member.
- **Checklist v1.1** (`docs/SCORE_CHECKLIST_V1_1.json`): v1 word for word but for those three items.

**The five petitions behind marshal drama C6** (investigator E, from the FLAG re-run; the full eleven in its run record):

1. **Murat** (§6 L0, an audience, turn 2) — *"Sire, Murat has expressed... displeasure about Ney's recent recognition. He requests a command worthy of his talents."* Speaker: *"Sire — I have earned better than to watch Ney take the field while I hold a road."* [Let it stand — Free] [Promise Glory — 1 AP] [Rebuke] [Give him a command — 2 AP]
2. **Soult** (§6 L0, an audience, turn 4) — *"Sire, Soult's dispatches have become unusually detailed — obsessively so. Staff report he feels his current assignment is... beneath his abilities."* Speaker: *"My orders have been carried out exactly, Sire. I note that Ney was given orders worth carrying out."* The command option disabled: "There is no enemy within his reach to send him against."
3. **Ney** (§6 L2, a modal, turn 6) — *"Settled once at Bohemia — and reopened by Murat's laurels since. Sire, Ney has taken to reading the despatches aloud in his own tent — Murat's despatches. He asks for work. The breach between them has become entrenched; he presses the point with unusual heat."* Speaker: *"Am I to be a garrison officer, Sire? Give me the enemy and I will give you Murat's laurels twice over."*
4. **Davout** (§6 L2, a modal, turn 7) — *"Settled once at Tyrol — and reopened by Murat's laurels since. Sire, Davout observes — without complaint, he is careful to say — that Murat's name reaches you before his own. The breach between them has become entrenched; he presses the point with unusual heat."* Speaker: *"I have said my piece before. I will not say it a third time unless you wish it."*
5. **Massena** (shadow command, an audience, turn 8) — *"Massena has stood 6 turns at your side, Sire, while other men win their laurels in the field. Under the Emperor's eye every victory is the Emperor's."* Speaker: *"Sire — give me a command of my own."* [Give him a front — Free] [He stays with me] [Promise him the next campaign — 1 AP]

Why ✗: the voice belongs to the personality's bank, not the man. `_PETITION_BODY` and `_PETITION_VOICE` rotate on the pair's fire count, so Ney's level-1 card (turn 5) is Murat's text with the names swapped, Bernadotte's level-3 card and Davout's level-0 card share their wording, and Bernadotte's two other cards (Ney, L1, turn 9; Davout, L2, turn 20) are identical. The body is staff narration in the third person; the marshal's own words are the speaker line alone. (The top-rung copy defect the same reading found is EA-17, fixed.)

## 10. Recommendations, for the user's gate

Each is a design row with an owner (GR9); none is built.

- **EAD-1 — the opening war costs France nothing** (Net positive on every opening turn; 11–14k by turn 10). A war footing — upkeep at war ×1.25, or the Charges' war term priced on income rather than the chest — measured against E1 first; the band is the user's to re-bless. Owner: the economy gate (ROADMAP 13).
- **EAD-2 — the Charges of Empire are a tax with no decision attached.** Give the chest a use the Charges cannot reach (an act of state, a forced loan, the Congress's prices), or a law that halves the crown term at an upkeep. Owner: SF-ECON-1's gate.
- **EAD-3 — the levy's price never matters.** Price men by scarcity, or cap the draft per turn by the court's administration; measure against M1–M7 first. Owner: the economy gate.
- **EAD-4 — an army carries no alarm.** Align the `military_establishment` term to the Armed Peace's own share (a third of Europe's power). Owner: the coalition's gate.
- **EAD-5 — commissions are the worst gold-to-men rate** (59% of the buy-everything bill). A commissioned corps raises 8,000–10,000 men, or the price falls with the bench's rank. Owner: the Marshalate's gate.
- **EAD-6 — the neutral's hoard** (the Ottoman 58,000 at turn 40; EA-7, the marshal-less courts). Author law decks for the secondaries; let the AI's standing roster rise to 4 when the chest holds twice the commission; decide what a court without an army is for. Owner: the user; content is SF-RR4's.
- **EAD-7 — the march step cannot follow a lawful road** (Britain's Baltic corps aimed at Sweden, a fellow member, on 14 of 18 corps-turns). Aim at the coalition's declared enemy and follow `find_path(..., passable_for=)`. Owner: SF-RR4.
- **EAD-8 — the league says nothing of the courts that have not marched.** A court-level beat read off the same predicates. Owner: SF-RR3.
- **EAD-9 — the AI's purse test refuses a rich court a law for being rich** (EA-18's AI side). Keep the plain read and name it as the brake, or read the Net before the Charges and re-band AI C1. Owner: the economy gate.

And one defect left owned rather than built: **EA-19** (the league forecast names a court in a truce with us as free to join; the coalition gate should read the truce the declaration reads — SF-RR4, with its series measured).

## 11. Limits

- **No client arm ran.** The game window was not driven (the user plays on this machine), so UI/UX is not exercised on the audit's reading, and the EYES marks are the delegate's, read from the archived frames and the client code — the user's own marks override them.
- **OP-LIVE did not run** (no key in the session); command C6 is unread.
- **Three seeds per commanded arm.** A seeded outcome is a road, not a law; every figure here is reported per seed.
- **No pillar score is claimed.** The panel did not run; the reading is item flips, with the directional for orientation only.
- **EA-16 corrected a reader after the reading.** The corrected mark is recorded beside the reading's own files, never over them.
- **The AI's purse was not re-tuned.** The counsel and the AI rung now read the purse differently by design (EA-18, EAD-9) until the user rules.
- **Investigator C's peace-time levy counterfactual** (the Ottoman 24k → 91k) was measured on its own probe board, not the benchmark; it is why the peace-time field levy stays closed.
