# ES-7 Second Pass — Balance + Integration + Creative Eval (July 11, 2026)

> **Method** (per the July-10 capstone pattern): (1) a deterministic balance harness over the real 1805 boot — estate-vs-rente cost curves, France absorption under a realistic reward load, 20-turn autoplay solvency, forced AI-rung probes through the REAL enemy admin phase; (2) a live playtest through the full HTTP stack (anthropic mode) — 8+ turns of the 1805 campaign exercising the muster gate, battles, the endow/strip arc, the peace-table warning, and the typed rente verbs; (3) findings fixed inline where in-bounds, routed where owned elsewhere. Evaluates `ECONOMY_REVISIT_SPEC.md` §0.6.8 as landed at `5eec1c1`.

## 1. Balance verdicts (measured, not asserted)

**B1 — The estate-vs-rente decision is GENUINE (the user's requirement holds numerically).** Expectation 120, fresh stability-50 conquest (base 150g):

| Steward | Covers the gap from | Cumulative cost @ t8 | Trust bleed before coverage |
|---|---|---|---|
| admin 9 (prosperous) | turn 3 | 1,124g (redirected) | ~0–1 pt |
| admin 5 (baseline) | turn 8 | 1,010g | ~4–5 pts (−1/turn after grace) |
| admin 2 (wasteful) | turn 12 | 896g | ~9 pts |
| **rente** | **turn 1** | **1,440g** (180/turn, flat) | **0** |

The instruments genuinely trade off: the rente buys *immediacy and zero trust bleed* at a ~30–60% gold premium; the estate is cheaper and appreciates, but a fresh conquest undershoots the gap for 2–11 turns depending on the Steward — land for Davout, paper for Masséna is the mechanically correct read, exactly as designed. Neither dominates.

**B2 — France absorption stays in the blessed E1 band.** Boot net +1,652 (49% absorption). A realistic mid-war reward load (1 estate to Davout, 1 rente to Ney, 2 conquests) → net +1,542, **55% of gross absorbed** — the band's lower edge, leaving headroom for upkeep growth and more endowments.

**B3 — No solvency regressions.** 20 end-turns through the real enemy phases: zero bankrupt nations; AI-side trust erosion ticks symmetrically (both accruing Austrians bled trust, GR5). Forced-condition probes through the REAL admin phase: the land arm endowed Charles with (AI-captured!) Swabia and John with Silesia; with no land and a rich treasury the rente arm pensioned Kutuzov at 120/180, and Russia's income phase carried the −180 line. The AI guard (≥ max(400, 10× cost)) correctly refused at 1,799 and granted at 1,800.

**B4 — The erosion arc is precise.** Win → `dotation_expectation` at shortfall-open → 2-turn grace → −2/turn (trust 75→69 over 5 turns) → pension → bleed stops the same tick, to the point.

## 2. Live playtest — what fired, what it felt like

The campaign told the story unprompted: Mack immovable at Swabia through three coordinated assaults ("You see? The position was sound. It is always sound."), Flanders fell to the coalition, **Bernadotte was captured by Austria** (W6-7), and when Silesia — freshly endowed as Masséna's duchy — fell in the enemy phase, **Russia confiscated the estate through the W6-8 AI rule**: *"Russia has seized Silesia, the estate that funded Marshal Massena's honor. He will not forget it, Sire."* Title lapsed, investiture reset to 200g. The new system and its neighbors compose into drama without scripting.

Verified live end-to-end: the endow decree ("styled Duke of Silesia"), the treasury report's Dotations block naming the estate, the card's title + wasteful-Steward note + honestly-zero rente offer, the settlement preview's inline warning (*"Silesia sustains Marshal Massena's title — ceding it strips his estate, and his loyalty will bleed"*), typed grant/revoke refusal copy, and the dispatch staying correctly SILENT with no wins earned (no noise without signal).

## 3. Findings

**F1 (was HIGH, FIXED this session) — muster typed answer misroute.** The W6-4 muster gate offers `attack_anyway`, but main.py's interrupt matcher only mapped attack-words to a choice named `attack` — typing the popup's own label ("attack anyway") fell through the parser as a FRESH ungated attack by a defaulted marshal (live: Masséna charged Archduke John into the mountains while Soult's question stood). Fixed in the matcher + 2 endpoint-tier regressions (`test_w6_muster_preview.py`, now 21).

**F2 (was MED, FIXED this session) — battle-report expectation note under-fired.** `battles_won` increments differ by path (combat.py: decisive only; the coordination caller: tactical wins too; the destruction sweep converts tactical outcomes into kills) — the outcome-string condition missed ~half of real increments (seed-sweep: 4/8). Rewritten as a pre-combat `battles_won` snapshot + delta read; 8/8 seeds now fire; capped marshals stay silent. 2 new pins (`test_estate_second_pass.py`, now 74).

**F3 (ROUTED → BUG_FIXES §Estate-Second-Pass-Eval, owner 8.EVAL) — battles_won seam inconsistency + slow expectation on-ramp.** The solo combat path counts only DECISIVE outcomes toward `battles_won`; the coordination path counts tactical victories too (`combat_executor.py:3629`). Same battle, different bookkeeping depending on whether allies marched — and since expectation derives from `battles_won`, the Cost-of-Success on-ramp is materially slower in solo defender-grind wars (8 live turns vs Mack/John produced ZERO French expectation). Also observed: displayed outcome copy ("Brutal stalemate") can disagree with the casualty-ratio classification in coordination battles. Not force-fixed here — unifying win semantics moves combat-wide pins and belongs to the 8.EVAL triage.

**F4 (ROUTED → same row family, owner 8.EVAL) — region-attack silent redirection.** "Massena, attack Venetia" resolved as a battle against Archduke John at Tyrol with no substitution note — the W6-1 "substitutions are named" principle holds on the retreat path but not the attack-region path.

## 4. Pillar scores (July-10 capstone scale; economy was 6)

- **Economy as a decision space: 6 → 7.** The reward portfolio is the first sink that asks a real either/or question, and the measured crossover proves the answer flips by marshal and situation. Held back from 8 by F3 (the on-ramp can starve in grinding wars) and by gold still accumulating fast in quiet play.
- **Marshal drama: 7.5 (held, texture deepened).** The confiscation beat, the title flavor, and the honest refusal copy all read in character; the Fontainebleau beat (ESP-1) remains the missing capstone scene.
- **Legibility of the new system: 8.** Same-unit numbers everywhere, the card explains the instruments, warnings fire at the table, the dispatch stays quiet without signal. Best-in-game for a new mechanic.
- **Integration: PASS.** W6-7 capture freeze, W6-8 confiscate/respect, the settlement layer, dispatch, notifications, AI admin phase — all composed correctly live, including the unscripted Russia-confiscation scene.

**Verdict:** the second pass does what the design conversation asked — territory is one instrument among two, the choice is genuinely situational, the player is warned before every silent strip, and the game announces demands when they rise. The system's remaining risk is upstream of it (F3: decisive-win scarcity), owned at 8.EVAL.
