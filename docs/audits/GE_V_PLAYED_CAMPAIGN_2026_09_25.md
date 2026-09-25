# GE-V — "The Played Campaign": the road from the 1805 boot to the Congress, measured

> **September 25, 2026 · row EP slice GE-V (`ENDGAME_PLAN.md` §6 + §2.8) · memo of record.** Run under the user's grant: *"do this and make these decisions … review the game, don't be afraid to find errors, make the changes after finding how it is now."* Evidence = the archived digests under `docs/audits/playtest_digests/gev-*` (every order through the real `POST /command`, every popup answered by a stated policy, deterministic on the `historical` seed). Everything measured here was measured on master at `7f6e6735` + this slice's tree.

## 0. The verdict in four lines

1. **The Congress machinery is sound and legible** — the recognition table, the prices, the sitting and the gold card all read as designed on the driven arms and the committed frames (§4).
2. **The road to it is not reachable on typed orders in forty turns.** Two differently-shaped openings, played by hand in chunks of one to three turns, both stalled at **35 titled provinces by turn 12** with the army at roughly half its boot strength; the best any arm reached was **41**. §2.8's rule fired: **`hold_titled` 50 → 45.** That rule does not rescue the road — the blocker is the campaign layer beneath it (§2).
3. **The play found a P1 hole** — `vassalize Austria`, typed on turn 1 with no battle fought, subjugated a great power and assimilated three archdukes — plus a parse shrug and two harness gaps. All fixed (§5).
4. **Both open rulings were taken under the grant and built** — GE-D2 "The Guard is Spent" (the Emperor is asked before the fatal battle) and GE-D1 "The Fortunes of War" (a bounded wound-or-death roll for a losing lead, both boards) (§6). **The ending pillar re-scores 3.0 → 5.5; the ≥ 7 target is NOT met**, and the memo names why and what would meet it (§7).

## 1. What was played

| Arm | Archive | Shape | Turns | Titled (boot 35) | France's provinces | Army (boot 189k) | Verdict |
|---|---|---|---|---|---|---|---|
| probe | `gev-probe1` | the vassal verbs typed cold on turn 1 | 2 | 38 → 35 | 28 | 333k → 210k (!) | `vassalize Austria` SUCCEEDED (§5.1) |
| road v1 | `gev-road-v1` | scripted Ulm → Bohemia → Vienna, Hanover by Soult, `--diplomacy decline` | 6 | 36 | 31 | 135k | Vienna 25k → 17k; Milan lost to Charles |
| road v2 | `gev-road-v2` | v1 extended to 16 | 16 | **34** | 30 | **92k** | Lannes captive, Ney 3,654 men, Provence + Corsica landed |
| road v3 | `gev-road-v3` | the same road under `--diplomacy accept` | 20 | **21** | **20** | 85k | the accepting dial signed Hanover's armistice mid-conquest and a white peace with Austria at zero conquests; Wellesley's 3,782 men walked through nine undefended interior provinces |
| **played A** | `gev-played-a-c1..c7` | chunked by hand: Ulm, main body Munich → Tyrol, Hanover from the north, Hesse + Saxony off their own pacts | 13 | 38 → **35** | 30 | 81k | Deroy and Ney captive; Charles raiding Provence and Lyonnais; Hesse 60 → 29 |
| **played B** | `gev-played-b-c1..c6` | chunked by hand: Ulm, the whole body to Munich, one supported strike a turn, Milan retaken | 12 | 40 → **35** | 28 | 88k | Charles refortified at Bohemia at 23k after four "favorable" strikes; Corsica landed |

Dials that mattered (all new this slice, §5.4): `--settlement decline` (refuse the league's turn-4 table), `--decline-from Hanover` (refuse the armistice of the court being conquered), `--objection insist` (a "trust" answer let Ney attack on his own and break), `--last-stand breakout` (the default fought Ney to the last at Bohemia).

## 2. Why the road stalls — six mechanics, measured

These are findings about the campaign layer the Congress sits on. None is a Congress defect; every one is what a real player meets on the way to 45 titled provinces.

1. **The muster is a lottery the preview overstates.** Every strike's preview promised "X if all march, up to Y if every corps arrives" and delivered roughly a third: Soult's turn-8 strike at Franconia read *"21,691; 38,878 if all march, up to 61,779"* and fought with Lannes, Murat and Napoleon while *"Ney, Davout and Deroy failed to reach the field"*; the turn-11 strike (*51,719 if all march*) arrived with two of five. A cautious Davout and a Bavarian Deroy never once reached a field led by Ney or Soult in twelve turns. Charles, one AI corps, took four "favorable" strikes for 5,791 + 2,836 + 2,010 + 1,295 dead and refortified each time. (CO-1b's relationship-scaled arrival is working as designed; the preview's two figures are not the number a player can plan on.)
2. **Four action points for eight corps.** Half the army idles every turn; the AI's corps all move. The static scripts spent 1–3 of 4 actions on refusals most turns; the hand-played arms used all four and still could not both strike and cover.
3. **Concentration is taxed.** 117,752 men at Munich against a 37,500 supply cap cost *"13,408 men lost in 3 turns"* before a shot was fired (played B, turn 4) — the design that forces dispersion is exactly what the muster then punishes.
4. **The marshals fight their own war.** Murat's autonomous glory charge on Archduke John cost 9,891 men (played B, turn 3 — *"Murat stood alone"*); a "trust" answer to Ney's fortify objection had him attack Charles instead and break (played A, turn 6); Davout auto-fortified at Munich and refused every march for five turns (road v3). Each system is landed and pinned; together they cost each arm a third of its army by turn 8.
5. **A 3,000–5,000-man British landing takes undefended homeland.** Wellesley's 3,782 men captured Ile-de-France, Orleanais, Champagne, Artois, Burgundy, Savoy, Rhineland, Brabant and Gelderland (road v3); Shrapnel's 3,000 took Corsica on every arm. Each landing costs the titled count directly (homeland lost) and a scripted France cannot answer it.
6. **A losing lord's satellites bleed.** Hesse went 60 → 29 in eight turns of a hard campaign (`the lord's defeats` −2 per lost battle, cap −6, on top of satellite drift); below 40 its two homeland provinces stop counting as titled. Working as designed, and it makes the treaty-vassal road to titled provinces self-cancelling while the army is losing.

**Consequence for §2.8:** the Pressburg shape (three cessions + three satellites + Hanover twelve quiet turns) needs Austria beaten to a signature by roughly turn 12 and Hanover taken by turn 10 with the army intact for twelve quiet turns after. On this AI, with these mechanics, neither hand-played arm had an intact army at turn 12. The 45 line is the plan's own rule and is applied; it is not the fix.

## 3. The rule applied: `hold_titled` 50 → 45

`congress.HOLD_TITLED` and `europe_1805.json`'s `campaign_end.hold_titled` both read 45; the boot gate line reads *"35 of 45 titled"*; the two Congress fixtures were regenerated (`tools/gen_ge3_congress_fixtures.py` — the Premature fixture summons on exactly 45, the Pressburg fixture stands at 55). Pinned in `tests/test_gev_played_campaign.py::TestHoldTitledIsFortyFive`; the GE-3 pins re-staged on the new line. `BASELINE_SERIES` and M1–M7 are byte-identical (the ambient board never approaches either line).

**Recommendation, not built (the user's gate — a balance ruling, ROADMAP's Victory & Objectives pass):** the levers that would make 45 reachable by a competent player are the six above, and the two cheapest are (a) the muster preview quoting the EXPECTED arrival — the personality/relationship-weighted figure the engine already computes — instead of "if all march", and (b) a garrison-detachment default on homeland coast provinces against the 3k raids. Neither changes a Congress number.

## 4. The Congress surfaces reviewed (the user's open item)

Read on the committed IQ-10 frames (`IQ10_DIPLO_CONGRESS_{GATE,SITTING,SITTING_TABLE}_2026_09_25.png`, `IQ10_CAMPAIGN_END_IMPERIAL_CONGRESS_2026_09_25.png`) and the driven arms' digests (`ge3-pressburg-*`, `ge3-premature-*`).

- **The table reads.** Each court's card carries the stance in colour, one reason sentence and one price sentence, and a typed order the player can copy (*"Type 'offer Prussia 2000 gold for recognition'"*). The Prussia card's arithmetic checks: *"Its reckoning: −17 — it signs at 50. Price: needs +67: a 2,000g sweetener at the table (+20) + open borders with Prussia (+5) + 42 more relations (court them)"* — −17 + 20 + 5 + 42 = 50. The refusal's warning is crimson and dated: *"Refusing 2 turns — it takes up arms against us at this end turn unless it signs."*
- **The prices are true.** On the Pressburg arm the table named *"needs +12: a 1,200g sweetener at the table (+12)"* for Berlin; `offer Prussia 1200 gold for recognition` answered *"1,200g is laid before Berlin (+12). Prussia now RECOGNIZES the order."* on the same turn — shown = applied.
- **The sitting is a crisis — across the two arms, not inside one.** The Premature arm produced the declaration (*"Berlin — at war after its warning"*, turns 4–6, three seeds) and the loss; the Pressburg arm produced the flip (Prussia bought) and the bills (six client petitions presented on day one at ×2 stakes, the rentes ×1.5 on the ledger) and the win. A single played sitting that holds all three is what a reachable road would give.
- **Feel, honest:** the gate/sitting/table pages are dense lists in a small serif — legible at 1×, and the ×2 frames show they scale. Two nits, routed not fixed: Russia's seat reads *"(St Petersburg)"* while its capital lever reads *"or take Vilna"* (the seat is display, the capital is the map's; say "its capital, Vilna"); and Britain's price on the gate page reads *"or take London"* before the ports lever — a Descent the player cannot mount in most campaigns should not lead the sentence.
- **The gold card** (THE IMPERIAL PEACE) is the best surface of the four: the four flags SIGNED / SHUT OUT / GONE, the eight-day strip with Hold ✓ and Signed 4/4, the record, two buttons. On a staged board it prints *"No battle was fought"* — true of the fixture, not of any played road.

## 5. Defects found by play — fixed

1. **P1 — a great power subjugated by a word** (`gev-probe1`, turn 1): *"Austria has been subjugated as a Puppet vassal of France (loyalty: 20). Marshals assimilated: Mack, ArchdukeCharles, ArchdukeJohn."* — 126,000 men under French orders, Austria out of the coalition, the treasury −534 from their upkeep, and a rebellion the next turn. The typed road's only gates were WAR and the power cap (Austria is 31% of France's power on the 1805 board, under the cap). **Fixed at the single source `vassal.subjugation_refusal`:** a court is subjugated by fiat only once BEATEN — its capital held by the lord's bloc, or its war score against the lord at `SUBJUGATION_WAR_SCORE` (−40, the Congress's own sue line), or no corps left standing; the refusal names all three roads; the peace table's signed clause arrives with `by_treaty=True` at the ratify seam. GR5 (any lord). Eight legacy pins that staged a bare WAR re-staged with the beaten proof; `TestACourtIsSubjugatedOnlyWhenBeaten` (13, driven at `/command`).
2. **P3 — `invest in Bavaria` after Bavaria's elimination** answered *"which marshal should act? Try: 'Ney, attack Bavaria'"* (road v3, turn 17): an eliminated court holds no province and fields no marshal, so it vanished from the parser's nation set. Fixed: every court the scenario authored stays a name the nation-keyed verbs recognise (`_extract_known_nations` reads `nation_starting_regions`), and the executor answers *"… no longer exists as a court — it was eliminated."*
3. **The Guard's question wore the wrong words.** With the new floor (§6.2) the spent-Guard ask fires, and its report line and rail row said *ENCIRCLED* / *surrounded* — they now say *the Guard is SPENT* / *cannot buy another road*.
4. **Two harness gaps** (`tools/playtest_driver.py`): `--settlement accept|decline` (the league's common-peace table on its own dial) and `--decline-from <courts>` (refuse the named courts' envoys whatever `--diplomacy` says). Absent, both mirror the old behaviour byte-for-byte; documented in `PLAYTESTING.md`.

5. **Caught by the suite before landing:** the first cut of VP-M1's Moniteur caption ("a marshal of France wounded") had no row in the gazette's special-weights table, so the first wound to fire in a played turn raised a `KeyError` inside the collector — found by the driven GE-1 arm (`test_the_fall_clears_the_choices_nobody_can_answer`), which produced a wound organically. Priced at 40 (below "a marshal of France lost" at 50) and pinned by driving the collector on a real wound event.

Filed, not fixed (the campaign-layer findings of §2 are design, not defects): none new beyond §2 and the two §4 nits.

## 6. The two rulings, taken and built

### 6.1 GE-D1 "The Generals' Mortality" → **(a) YES, bounded — VP-M1 "The Fortunes of War", built**
`backend/game_logic/fortunes_of_war.py`. Only the LEADING marshal of the LOSING side of a real battle (`battle_scale.is_a_battle`) whose corps lost ≥ 25% of what it brought rolls, once, through the campaign-seed helper (`seeded_int` — no module RNG, so M1–M7 and every RNG-order pin are untouched): killed 1%, wounded 8%. A wound is ONE serialized field, `Marshal.wounded_until_turn` (3 turns): the corps stands, defends and marches; he cannot attack, charge, bombard, pursue, or carry a PURSUE/HOLD order; the AI's P0 rung stands its wounded man down; the card shows the wound; a wounded literal is not counted as sidelined. A death keeps the corps — its men pass to the nearest friendly corps within three regions or disperse — and goes through `WorldState.destroy_marshal` with cause `killed_in_action` (the reward rows, the ask, the totals and the chronicle all follow). The sovereign never rolls here (GE-1 owns him). Beats: `marshal_wounded` (dispatch 84, Moniteur *"a marshal of France wounded"*, log type 167 → 168 flipped consciously in twelve files) and the killed arm of `marshal_destroyed`. `BASELINE_SERIES`: `tools/_vpm1_series_arms.py` — arm 0 (lever down) and arm 1 (shipped) both reproduce the recorded series byte-for-byte; the roll's seam was reached 39 times on the ambient board and no qualifying draw produced an outcome in forty turns, so **no re-record**. `tests/test_ge_d1_generals_mortality.py` (22 — the row's nine named pins and the surfaces).

### 6.2 GE-D2 "The Guard is Spent" → **YES, the floor is built**
`CombatExecutor.GUARD_SPENT_FLOOR = 1000` (the rubble line stays 50): when paying the 30% toll would leave the Guard under a thousand men, the toll is refused and the player is ASKED — fight to the last, or cut our way out — so GE-1's death roll only ever meets a corps the player chose to keep in the field. The strategic breakout copy reads the same floor. The FA-S17-7 pin that staged a 1,000-man Guard "that can pay" was flipped consciously to 3,000 (it now asks at 1,000, by design). The row's named pin `test_the_guard_asks_before_the_last_battle` is green in `tests/test_gev_played_campaign.py::TestTheGuardIsSpent`.

## 7. The re-score: the ending, 3.0 → 5.5 (target ≥ 7 NOT MET)

| What the pillar asks | Read |
|---|---|
| Can the campaign end, and does the ending say why | **Yes** — GE-1/2/3 driven: the Fall on three roads, the Verdict, the Humbled Peace, the Imperial Peace (7.5) |
| Does the winning condition read as a challenge to hold | **Yes** on the table — the sitting's hold, the refusers' teeth, the bills (7) |
| Can a player reach it from the boot | **Not in forty turns on typed orders**, on two hand-played openings (3) |
| Does the road teach what it costs | Partly — the table teaches the Congress; the muster preview and the objection arms mislead on the way (4.5) |

Weighted: **≈5.5**. The 3.0 read was "there is no ending"; the 5.5 read is "there is an ending, and it is not on the road." What would meet 7: a road a competent player can walk to 45 in forty turns — the two cheap levers in §3, then a re-measure on the same chunked method (the archives are the baseline).

## 8. Not measured — said plainly

- **The D1 band** (AI-3's council wars on a played board): no AI-vs-AI war opened on any arm (as on every prior board — AI-3r §8.2); the Congress's refusal term was never a live input because no played arm summoned. Stays with AI-V arm (a).
- **The naval pillar's SHUT OUT arm** (16 of 26 ports, a landing answered): no played arm reached a Continental System above the boot's 38%; Britain's landings were measured (§2.5) but never answered. Stays open.
- **GE-D2's completion on the Eagle-Falls road:** the floor is built and pinned at the seam; the archived `ge2-eagle-falls` arm predates it and was not re-driven this session (the driver's sovereign at Burgundy would now be asked at ≤ 1,428 men rather than paid down to 255).

## 9. Gates

- `tests/test_gev_played_campaign.py` (31) + `tests/test_ge_d1_generals_mortality.py` (22); the re-staged legacy pins; ruff clean; M1–M7 byte-identical; `BASELINE_SERIES` byte-identical (arms in `tools/_vpm1_series_arms.json`); the two Congress fixtures regenerated; the full suite in the hook.
- Archived digests: `gev-probe1`, `gev-road-v1..v3`, `gev-played-a-c1..c7`, `gev-played-b-c1..c6` (`docs/audits/playtest_digests/`).
