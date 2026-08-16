# Row NP — THE PROMISE AUDIT (August 15, 2026)

> **Authoritative record of the row NP exit review.** Landing record for
> the fixes = `docs/NAPOLEON_SPEC.md` §15.9. Commits `4638a85`, `55ec497`
> and the follow-ons named below.

## §0 Why this document exists

Row NP was declared build-complete, given a landing record, and pushed.
The user then asked *"i thought u didn't finish some parts"* and four real
gaps surfaced in ten minutes — the seven golden-corpus rows named by id in
the spec AND promised in the NP-1 commit message; N13's blessed
`morale: 85`; a regex that matched with no verb guard; four verbs in the
rewrite set that do not parse.

The method failure worth naming: **the "still open" list contained only
what had been DECIDED to defer, never what had been FORGOTTEN**, and a
30-agent adversarial review found none of the four, because they were
absences rather than defects. A review looks at what is there.

So this pass inverts the direction. Every commitment in
`docs/NAPOLEON_SPEC.md` (§2's never-do pins, §3–§9's per-slice clauses,
§10 symmetry, §11's blessed numbers N1–N15, §12.2's re-bless list, §13's
slice definitions, both §15 blocks) and every claim and forward promise in
the 13 commit messages `4550ccb..5afb076` was extracted as a row and
verified **against code at current line numbers**. A promise that could
not be pointed at with `file:line` was MISSING until proven otherwise.

Method: 11 parallel extraction agents, one per promise surface, each
returning structured rows; then an independent refuter per non-LANDED row
whose job was to prove the extractor wrong. Alongside that, a
hand-verification pass by the session itself, which is where most of the
confirmed defects below came from — the two passes were deliberately not
told about each other.

## §0.1 The numbers

| | |
|---|---|
| Promises extracted | **450** across 11 surfaces |
| LANDED on first read | **297** |
| Non-LANDED rows put to independent refuters | **60** |
| Refuted (the extractor was wrong) | 23 |
| Downgraded (real but smaller) | 22 |
| Confirmed or upgraded | **15** |
| Fixed this session | **18** |
| Routed with owners (GR9) | **11** |

The refutation pass earned its keep: it killed 23 claims outright and cut
22 more down — including the fleet's own loudest one (that the §6b rivalry
petition could put Napoleon on a card addressing the player), which its
refuter downgraded to LANDED-by-cascade. That claim was still worth a belt,
and got one; it was not worth the P1 it was filed at.

## §1 Verdict

**The row is substantially as advertised.** Every §2 never-do pin holds;
zero new serialized fields; no name-keyed guard anywhere in production
(GR5); the Peril's three roads home work end to end; the Petition for
Independent Command fires end to end; all 19 verbs in the rewrite set
parse to a real action; the assets are git-tracked.

**Eighteen defects were found and fixed** (§2 + §2b), and the largest
cluster has one root, worth stating once because it is the same root five
times over:

> **§15.4's design amendment made `sovereign_aura_strength` "the single
> source" for the aura and the fear — and updated two of its four
> readers.** The garrison assault, the cavalry charge and the muster
> preview kept the old constant — and the muster preview kept the wrong
> ROSTER as well; the glorious charge kept both; and the Shadow's boolean
> was derived from the decayed float, so a broken aura switched a separate
> mechanic off. That is the exact split brain the amendment's own commit
> message said it was retiring, surviving five seams over, in the mechanic
> the user's brief was about.

The second theme is **a returned value that three of four callers
ignored**: `destroy_marshal` returns False when it converts a sovereign to
capture, and only the charge copy read it. A structural pin written for
that found a fourth copy on its first run, and the fleet found a fifth in
the attrition sweep.

The third is **a guard the table names and the code never had** — §6.1's
"autonomy gate", its "restlessness loop belt", §2 pillar 1 at the rivalry
producer. Each held by cascade off some other exemption, which is the
difference between safe and safe on purpose.

## §2 Confirmed defects — FIXED

| # | Promise | What was true | Sev |
|---|---|---|---|
| A1 | §15.4: "`authority.sovereign_aura_strength` is now the single source for both" | `_calculate_coordination_context` stamped a flat `1.0`, and it is the LAST word on the two paths that never reach the participant stamp — `_resolve_garrison_combat` and the cavalry charge. **Measured at `sovereign_aura_strength == 0.0`** — the myth wholly broken — the Emperor still stormed a capital at the full +10% (attack modifier `1.2320`; the design intends `1.1200`). | **P2** |
| A2 | §5.1 / the code's own comment: "Percentage derives from the consumed constant… Shown = applied, both directions" | The muster `presence_note` hardcoded `+10%`. With a cracked aura the preview promised +10% and the battle report that followed said +6%. | P3 |
| A3 | §7.1: "a sovereign never dies in v1" | `destroy_marshal` returns False when it captures instead of removing. The **battle** copy composed its sentence before the call; the **auto-bombardment** copy said outright *"The preparatory bombardment destroyed {name}."* §15.8's note that this line "is a debug `print()`, not player-facing" is true of `combat_executor.py:5166` and **misses the player-facing sibling ~70 lines below it**. | **P2** |
| A3b | (found by this slice's own structural pin, on its first run) | A **fourth** copy: the CHARGE path had the return-gating right but composed the sentence itself, so "one home each" was still false — and it had no captured-sovereign line at all. | P3 |
| A4 | §4.1 gate (b): "military/movement verbs only — diplomacy keeps its verbs" | The trailing-`myself` arm shipped with **no verb gate** — the third sibling of the defect §15.8 item 3 fixed for the Emperor-lead arm. *"I will offer an alliance to Prussia myself"* rewrote to *"Napoleon, I will offer an alliance to Prussia"*. Inert at the mock layer (the keyword parser ignores the prefix), which is why nothing complained — but the rewrite runs **upstream of both parsers**, so live mode hands the LLM a marshal-addressed diplomatic sentence. | P3 (P2 live) |
| A5 | NP-V: the phantom province `'Bavaria Myself'` is closed | Closed **inside its own arm only**. The two arms above it return first, so the more natural phrasing still produced it: `"I will march to Swabia myself"` → target `'Swabia Myself'`; so did the Emperor-lead form; so did `"Ney, march to Belgium myself"`. NP-1's claim that the fuzzy skip lists close this family is **false by construction** — the destination extraction reads to end-of-string and never consults them. | **P2** |
| A6 | §4.1 checklist step 12: the seven named golden-corpus rows | The rows landed (§15.8 item 1) but **all eight omit the `marshal` key** that 64 other corpus rows use — the only field distinguishing "the sovereign was addressed" from "somebody was". **Mutation-proven**: with the theft simulated, `addressed-i-want-unchanged` — whose stated purpose is *"the sovereign must not steal an order addressed to a marshal"* — still PASSED. | **P2** |

### §2b The fleet's confirmed findings (the second wave)

| # | Promise | What was true | Sev |
|---|---|---|---|
| B1 | §5.1 in-code: "the predicate MIRRORS the applied `eligible` set… Shown = applied, both directions" | The muster note's PREDICATE scanned the **attacker's origin** while the applied aura keys on `_get_casualty_participants` at the **battle region**. Reproduced: with the Emperor fortified / moved this turn / on HOLD / at −2 with the attacker, the SAME SCREEN printed *"WILL NOT — Napoleon: [fortified]"* two lines above *"The Emperor commands in person — +10% harder"*, and the battle carried no Emperor row. Silent the other way too. | **P1** |
| B2 | §15.3: the NP-V fix "also closed the mirror case" | The **glorious charge** was the one glory path without the roster override: aura stamped at the charger's ORIGIN, Shadow falling back to a scan at the TARGET. A cavalryman charging out of the Emperor's headquarters carried the Presence **and** banked full glory — the strictly-dominant stacking the gate rejected option (c) to avoid. Both directions measured. | **P1** |
| B3 | §15.4 changed the aura's MAGNITUDE | `_atk_sovereign = _atk_presence > 0.0` routed that magnitude into a **boolean identity**, so once grip fell below `AURA_GRIP_BROKEN` the §6.2 Shadow switched off entirely and marshals banked full glory at the Emperor's side. Introduced by §15.4 and **extended by part 1 of this audit** — worth saying plainly. | **P2** |
| B4 | §3.1's mandated sweep: no sovereign silently executes another personality's behaviour | A sovereign on HOLD fell into the arm labelled `else:  # aggressive` and **sallied out unordered**. Reproduced through the real player path: *"Napoleon, hold Paris"* → *"Holding position"* → next turn *"Napoleon sallies forth to attack Mack"*, Guard 10,000 → 9,737. A battle nobody ordered, on the verb that means "stay put", feeding §7's capture machinery. | **P2** |
| B5 | §7.1: a sovereign reaching the attrition sweep is CAPTURED | The mechanic is right; the sweep then emitted a false `marshal_destroyed` event — the **fourth** un-routed destruction sentence, riding `tactical_events` to a client that prints it verbatim. | P2 |
| B6 | NP-3: the beat is carried by "the modal + dispatch line + response message" | `shadow_petition` was never added to `_DISPATCH_EVENT_TYPES`, so `_build_turn_events` dropped it at the whitelist — **the dispatch line did not exist**. Its sibling `fontainebleau_petition` always was whitelisted. | P2 |
| B7 | §15.4: "the battle says it out loud" | Wired into the ordinary attack message only; an emperor-led **auto-kill** or **charge** moved his prestige ±2/−5 in silence. | P2 |
| B8 | §6.1 row 9: "modify_trust no-op + autonomy **gate**" | The gate was never written; the property held by cascade off the trust freeze, and the debug `set_autonomy` arm could break it — while its own sibling `dismiss` DID get the guard. | P3 |
| B9 | §6.1 row 4: "restlessness loop **belt**" | Never written; only the cascade through `find_jealousy_target`'s head guard. | P3 |
| B10 | §2 pillar 1: no popup carries his name as speaker | Held by accident at three producers and **not at all** at the §6b rivalry producer, which has no gate — and §6.4 deliberately keeps him in the Win/Loss formula. Belt added at `_push_petition`, the one place channel policy lives. | P3 |
| B11 | §15.4: "+10%" becomes "+9%" becomes **nothing** | Grip is an int over a span of 55, so the smallest non-zero aura is 1/55: the reachable grip 31–32 band rendered a bonus row reading **"+0%"**. | P3 |

**Canonized rather than changed:** the **reckless auto-charge** fires the
Shadow without granting the aura, because that path clears every combat
transient on both sides. The asymmetry is the coherent reading and is now
written at the seam — the aura is a transient buff and that path forgoes
ALL of them (coordination too); the Shadow is not a buff but a fact about
whose field it was. Suppressing it there would make "charge beside the
Emperor" the one way to bank FULL glory under his eye. The underlying
oddity (the one `resolve_battle` site with no coordination recompute) is
pre-existing and belongs to CA8-19.

### The three "left unfixed with reasons" (§15.8), judged rather than accepted

| Item | §15.8's reason | Verdict |
|---|---|---|
| the auto-bombardment "destroyed" line is a debug `print()` | true of the line it names | **Half true — FIXED.** The named line is indeed a debug print. It has a player-facing sibling saying the same thing. See A3. |
| the DP HUD can read "6/5" (accrual correct, ceiling cosmetic) | cosmetic, routed | **FIXED.** The accrual is correct and the 6th point is genuinely spendable — but it is a shown-vs-applied divergence in the top bar of every screen, which is this project's own through-line defect. New single source `diplomacy.displayed_dp_ceiling`, read by the three `main.py` payload sites and the ledger's duplicate. |
| `sovereign_takes_field` can re-fire once per WAR INSTANCE | latent, needs a played campaign | **Confirmed latent, and FIXED anyway** — it was one line. The loop `break`ed after stamping the first unnoted war, so a court in two live instances got the same beat on consecutive turns while the Emperor simply stayed afield. Every live war is now stamped in the one pass. *(A war declared later while he is already afield still notes itself; that sentence is true news for that war — recorded, not papered over.)* |

### Pins corrected

* `test_napoleon_np1_hand.py` asserted `"take the field in person"` → `"Napoleon, take the field"`. Measured at the endpoint that parses to `success=False / action=None`: a **third** surviving pin asserting a broken rewrite. §15.8 item 4 said it found two of these; it found two of three.
* `test_napoleon_np2_presence.py` asserted the enemy-sovereign stamp `== 1.0`, where §15.4 had **already recorded** that a foreign court's flat-75 grip means ~0.82. The pin was asserting the inconsistency this audit closed.

## §3 Verified LANDED (the load-bearing ones, independently re-measured)

* **All §2 never-do pins.** Never on the ladder · never a jealous subject · never an envy target · `get_expectation == 0` · trust frozen against both `modify` and `set` · never autonomous · never crowned · never benched · not reckless cavalry · `get_attack_modifier_for_personality("sovereign") == 1.0` at every stance · AI alias → `aggressive`.
* **Zero new serialized fields** — `Napoleon.to_dict()` has the same key set as `Ney.to_dict()`.
* **GR5** — the only `"Napoleon"` literal in production is `marshal_overview._WIRED_ABILITY_MARSHALS`, which is name-keyed content by nature. No guard keys on the name.
* **All 19 verbs in `_SOVEREIGN_ORDER_VERBS`** parse to a real action on the 1805 board, both by direct address and through the rewrite.
* **The Petition for Independent Command fires end to end** — probe: Ney at the Emperor's side, others ahead on the ladder, petition on turn 5 with correct copy and its three arms. The B0 contract holds (an occupied channel returns without burning the latch).
* **The Peril is reachable and correctly rare.** A cornered-but-not-encircled sovereign never rolls the coin: he escapes and the extraction burns exactly `GUARD_ESCAPE_TOLL` (measured 3,000 → 2,100) while the same shape stages the ordinary "CORNERED" last stand for Ney. A true encirclement — enemy armies in **every** adjacent province — fires the sovereign's own copy: *"fight to the last, or cut our way out."*
* **The three roads home** (§7.3), end to end: peace with the holder frees him at 5,000 / morale 50 / Paris / **not fortified**; storming the city that holds him frees him.
* **The Seat**, both surfaces: `+1 DP` while at Paris (measured 5 → 6), the DP-breakdown line *"+1 the Emperor holds court in the capital"*, and the departure beat *"The Emperor has taken the field — Talleyrand holds the portfolio"* both render in `build_morning_dispatch`.
* **The apex card** carries the sovereign flag, the refusal note, the ability block (`ability_active: True`), and the derived `rally_tier: fast` / `admin_tier: thrifty`.
* **The assets are git-tracked** — `Napoleon.jpg` + 8 `emperor_*.png` + all 16 `.import` siblings (§15.5's own catch, re-verified with `git ls-files`).
* **The tutorial contains no sovereign**; the legacy fixture is untouched.
* **`BASELINE_SERIES` and M1–M7 byte-identical** before and after every fix in this pass, verified by running rather than asserted.
* The §12.2 re-blesses are honest: MC-2's set-equality survives behind an exemption predicate rather than being weakened to a subset check; MC-3's exact edge counts are re-derived, not relaxed. The three NP-A fixture adjustments genuinely isolate the Emperor from tests about something else.

## §4 Corrections to the record itself

1. **§4.1's verb list is stale.** It still reads *"attack, march, move, **ride**, **advance**, withdraw, fortify, hold, scout…"* — but §15.8 item 4 retired `ride` and `advance` precisely because they do not parse. The prose was never updated. *(§4.1 also carries the already-recorded `take` error in its worked example.)*
2. **The spec has two sections numbered §15** — the GR9 deferral table and the landing record. Cross-references to "§15" are ambiguous.
3. **§15.8's auto-bombardment reason is half true** (see A3).
4. **NP-1's "closed regardless of the sovereign gate"** claim about the phantom-province family is false as written (see A5).

## §5 Routed, not fixed (GR9)

`docs/BUG_FIXES.md` §Row NP — promise audit carries these with owners.

| Row | What | Owner |
|---|---|---|
| NP-X1 | The trailing self-marker still reaches the destination extraction in **sovereign-free** worlds (the rewrite is content-gated by design, so the strip cannot run there). The general fix belongs at the destination-extraction seam, which is corpus-moving. | CR-6 *proper* (the parser gate) |
| NP-X2 | The **general prisoner-rescue rule** — NP-4 scoped the storm-the-city release to sovereigns deliberately and its commit says "routed as a follow-up"; it was routed nowhere. | EC-2 pass 2 / the Victory gate, whichever reaches prisoners first |
| NP-X3 | `sovereign_takes_field` still notes a war **declared while he is already afield**. True news for that war; recorded as accepted. | none — accepted, pinned |
| NP-X4 | The whole suite can reach the **live Anthropic API** for low-confidence phrasings (`.env` sets `LLM_MODE=anthropic` and `conftest` does not pin it). Pre-existing, unrelated to NP, but it makes any parser test non-hermetic. | position 10 (the shippable build) |
| NP-X5 | `mods/examples/battle_of_waterloo.json` — the §10 "modding reference" — **fails the validator**, with two capital-not-in-scenario errors that are **pre-existing and identical before row NP** (verified against `4550ccb`). | DEF-1 / the modding-docs row |

## §6 Open, and NOT this session's to close

* **NP-6 "The Three Emperors"** — post-NP-V, strikeable at the user's word. Not started.
* **The live visual sign-off** on the emperor piece / apex card / diorama locket cipher / Captive Eagle row / Tuileries line. The standing convention is the user's own pass.
* **The played 20-turn campaign** (Q9 ruling) runs after this row.
* **Two questions the user owns**, put to them at the close of this session:
  1. the sovereign gets no attack-confirm even on genuinely bad odds, because the CA9 row-2 gate arms only for a `cautious` marshal (objections are correctly gone by design; whether he should get an "are you sure" is a gate);
  2. **"The Interned Column"** — `DESIGN_REFINEMENT.md` §PC15-D1 homes this rider to *"the row NP exit review"*, i.e. this session. It is surfaced with the finding that **PC15-D1's own ruling substantially narrowed its premise**: the retreat scan now obeys the movement law, so an army can no longer retreat ONTO neutral soil at all — the rider's case survives only for an army already standing there when it is cornered.
