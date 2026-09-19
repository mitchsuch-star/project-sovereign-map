# WHAT HAPPENS WHEN THE PLAYER IS SLIGHTLY WRONG

Recon, read-only, September 19 2026. Every line below is either a `file:line`
or the output of a probe that drove the **real** `POST /command` endpoint
against the **real 1805 boot board** in-process (FastAPI `TestClient`,
`LLM_MODE=mock`, `SOVEREIGN_SEED=historical`, a **fresh boot world per
utterance**). Nothing was edited.

Probes: `probes/nm_harness.py` (driver), `nm00_smoke.py`, `nm01_regions.py`,
`nm10_families.py` (A–H), `nm20_mechanisms.py`, `nm30_trace.py`,
`nm40_followups.py`, `nm50_census.py`, `nm60_bareverbs.py`.
Raw output: `nmA..nmH.json` / `.rendered.txt`, `nm20_out.txt`, `nm30_out.txt`,
`nm40_out.txt`, `nm50_out.txt` + `nm50_records.json`, `nm60_out.txt`.

---

## THE ONE-PARAGRAPH ANSWER

**Being wrong is cheap and instructive almost everywhere — and then, in one
narrow and very reachable shape, it is neither.** 83 of 119 driven near-misses
charged no AP and fought nothing; 46 distinct refusal templates, 24 of which
name a concrete next step. (That 83 is the *charge* count, not a safety count —
bare `retreat` is inside it and moves eight corps.) Misspelt provinces are the best-served family in the
game. But the guard that refuses an unbindable addressee **keys on a comma**
(`executor.py:972-974`), and the CR-6 attack resolver **clarifies for the
vaguer sentence and not for the more specific one**
(`combat_executor.py:10064` vs `:10080`). So `Nay, attack Mack` is refused for
free and honestly, while **`Nay attack Mack` sends Soult — a marshal the
player never named — into a real battle: 5,922 French dead, 17,087 Austrian,
296 gold, six corps relocated, one AP, no question asked.** The same sentence
shape fires for `Grouchy attack Mack`, `Berthier attack Mack`,
`Wellington attack Mack`, `Blucher attack Mack`. That is the P1, and it is the
answer to the gate question: a chip cannot be mistyped, and here the typed
road punishes a one-letter slip with an irreversible battle.

---

## BOARD FACTS (measured, `nm00_smoke.py` / `nm01_regions.py`)

| | |
|---|---|
| Player | France, turn 1, 4 AP + 2 admin AP, 800 gold, 126 regions |
| Ney, Davout | Rhineland (adj: **Swabia**, Lorraine, Frankfurt, Gelderland, Nassau, Brabant) |
| Soult, Napoleon | Lorraine (adj: **Swabia**, …) |
| Lannes, Murat | Franche-Comte (adj: **Swabia**, …) |
| Bernadotte | Franconia (adj: **Swabia**, …) |
| Massena | Milan (adj: Piedmont, Tyrol, Munich — **not** Swabia) |
| Visible enemies | **Mack** (Austria) @ Swabia 52,000; **ArchdukeJohn** @ Tyrol |
| Not regions | `Bavaria`, `Austria`, `Prussia`, `Venetia`, `Moscow`, **`Ulm`**, `Lyon` |
| Collision | `Brunswick` is a **region** (Hanover) *and* a Prussian **marshal** |

**7 player marshals are adjacent to Mack.** That number is what makes the
auto-pick a real choice rather than a formality.

---

## FAMILY GRADES

Grades: **(1)** refuses honestly and names the near-miss · **(2)** refuses
generically · **(3)** silently does something ELSE · **(4)** does the right
thing.

| Family | Grade | One line |
|---|---|---|
| **A. Misspelled marshal** | **(4) mostly, with a (3) that is the P1** | ≥4-char typos are corrected and executed; 3-char typos get no did-you-mean; **without a comma an unbindable name fights with the wrong marshal** |
| **B. Misspelled / unknown province** | **(4)/(1) — the best family** | corrects, *discloses the substitution*, names the reason and often the next command; one (3) (`scout <garbage>`), one gap (`Ulm`) |
| **C. Wrong order / missing address** | **(3) — P1 family** | bare `attack`/`move`/`scout`/`hold` correctly ASK; `attack Mack` and bare `retreat` do not |
| **D. Verb the game does not have** | **(1)/(2)** | free, honest, names valid orders — but the excuse is `random.choice` and two cited examples are untypable |
| **E. Legal order, currently illegal** | **(1) — strongest copy in the game** | every refusal states WHY; two of eight cost AP for nothing |
| **F. Compound / sequential** | **(4)** | first clause executes, the tail is explicitly handed back by name |
| **G. Politeness and register** | **(4) with one (3)** | `would you` marches, `could you` prints the 12,717-char manual |
| **H. Negation / condition** | **(1) with one (3)** | 9 of 12 conditionals refuse for free; **3 fail open into a real battle** |

---

## ⛔ CATEGORY (3): EVERY INSTANCE MEASURED

### P1-1 — a typo'd name **without a comma** sends a marshal nobody named into battle

`probes/nm40_out.txt` §1. Fresh board each row.

| utterance | outcome |
|---|---|
| `Nay, attack Mack` | refused, **0 AP** — *"There is no 'Nay' in the order of battle, Sire. Whom did you intend?"* |
| **`Nay attack Mack`** | **Soult attacks. Battle fought. 1 AP.** |
| `Grouchy, attack Mack` | refused with did-you-mean, 0 AP |
| **`Grouchy attack Mack`** | **Soult attacks. Battle fought.** |
| `Berthier, attack Mack` | refused, 0 AP |
| **`Berthier attack Mack`** | **Soult attacks. Battle fought.** |
| `Wellington, attack Mack` | refused with did-you-mean, 0 AP |
| **`Wellington attack Mack`** | **Soult attacks. Battle fought.** |
| **`Blucher attack Mack`** | **Soult attacks. Battle fought.** |
| `Kutuzov attack Mack` | refused honestly (enemy-roster arm fires) |
| `the Guard attack Mack` | refused — but see P3-3 |

Cost of the executed arm, measured on `attack Mack` (`nmC.json`):
**Soult −5,922 · Mack −17,087 · France −296 gold · Ney, Davout, Soult, Lannes,
Murat and Napoleon all relocated Rhineland/Lorraine/Franche-Comte → Swabia ·
1 AP.** Irreversible.

**Mechanism, traced (`nm30_out.txt` §1, §1b):**

1. The parser cannot bind `Nay`, so it returns `marshal=None`,
   `type='auto_assign_attack'` (measured: `nm30_out.txt` §1b).
2. `CommandExecutor._unbound_addressee` (`backend/commands/executor.py:958`)
   is the FA-22 guard that refuses an addressed-but-unbindable phrase. Its
   third statement is:

   ```python
   head, sep, _tail = raw.partition(",")
   if not sep:
       return None
   ```
   `executor.py:972-974`. **The discriminator is a comma.** Its own docstring
   says it returns None "for a BARE order (no comma)" — deliberate, to
   preserve CR-6's blessed instant pick. But a misspelt name followed by a
   verb is not a bare order; it is an addressed order the roster failed to
   bind, and punctuation cannot tell the two apart.
3. With the guard out of the way the command reaches
   `CombatExecutor.resolve_auto_attack` (`combat_executor.py:10033`) →
   `_resolve_auto_assign_attacker` → `world.find_nearest_marshal_to_region`
   → **Soult**, deterministically (5 fresh worlds, 5× Soult —
   `nm20_out.txt` §1).

The FA-22 comment at `executor.py:1505-1516` names this exact case —
*"`Berthier, attack Mack` … ALL sent SOULT, with a battle report"* — and the
fix it shipped covers the comma'd form only. **One comma over, the defect is
live.**

### P1-2 — `attack <enemy>` never asks, while bare `attack` does

`nm20_out.txt` §1:

```
'attack'        success=True AP=0  fought=False  'Which marshal shall lead the attack, Sire?'
'attack Mack'   success=True AP=1  fought=True   MUSTER — Soult (30,000) vs Mack …
```

`resolve_auto_attack` has two branches and only one of them can clarify:

* `general_attack` (bare `attack`) — `combat_executor.py:10064`:
  `if len(pool) > 1: … build_contact_attack_clarification` → asks.
* `auto_assign_attack` (`attack Mack`) — `combat_executor.py:10080-10085`:
  calls `_resolve_auto_assign_attacker` and returns `{"kind": "named", …,
  "explanation": ""}`. **There is no `len(...) > 1` branch anywhere in that
  function** (grep over its body: the only marshal selection is
  `world.find_nearest_marshal_to_region`, two call sites, both returning
  `named`).

So the **more specific** order gets **less** protection, and the empty
`explanation` means the response never says a choice was made — the MUSTER
header naming Soult is the only clue. CR-6's docstring
(`combat_executor.py:10036-10040`) states the row's own purpose as fixing
"the most ambiguous lethal order had the fewest safeguards"; the auto-assign
half of that row is unbuilt.

`charge Mack` and `bombard Mack` both **refuse** without a marshal
(`"Charge requires a marshal. Try: 'Ney, charge Wellington'"`). Three lethal
verbs, three different policies.

### P1-3 — bare `retreat` retreats the entire army for **zero AP**

`nm60_out.txt`:

```
'retreat'  success=True AP=0  asks=False  marshals_changed=9
  'General retreat ordered! Ney falling back! Davout falling back! Soult falling back!
   Lannes falling back! Murat falling back! Bernadotte falling back! Massena falling
   back! Napoleon falling back!'
```

Eight French corps displaced, no confirmation, no cost. Every other bare verb
in the game asks: `attack`, `move`, `scout`, `hold`, `fortify`, `drill`,
`wait`, `unfortify`, `pursue` all answer *"Which marshal …?"* at 0 AP. Only
`retreat` (army-wide, free) and `defend` (army-wide, 1 AP — *"All forces take
defensive positions: Ney, Davout, Soult, Lannes, Murat, Bernadotte, Massena,
Napoleon"*) act for everyone unasked. Also named in the FA-22 comment
(`executor.py:1514-1516`) and also unfixed.

### P1-4 — three conditional forms fail **open** into a real battle

`nm60_out.txt` §2 — twelve conditionals, same sentence otherwise:

| fails OPEN (fought, 1 AP) | fails CLOSED (refused, 0 AP) |
|---|---|
| `…attack Mack if outnumbered` | `…unless he is fortified` |
| `…attack Mack when ready` | `…if you can` |
| `…attack Mack should the odds favour us` | `…when Davout arrives` |
| | `…once the roads dry` · `…provided he is alone` · `…only if he is weak` · `…in case he retreats` · `…next turn` · `…tomorrow` |

The open arm prints *"Your words named no foe our maps know, Sire — Ney
marches on Mack at Swabia, the nearest in sight"* — i.e. the guard blanked the
clause, the blank took the target with it, and the nearest-enemy substitution
then supplied one and fought. This is PARSE-NEG's own class, surviving in the
`if <adjective>` / `when <adjective>` / `should <clause>` shapes.

### P3-1 — `could you` prints the manual; `would you` marches

`nm20_out.txt` §3, measured both at `is_question()` and end-to-end:

| utterance | `is_question` | outcome |
|---|---|---|
| `Could you have Ney attack Mack please?` | True | **12,717-char COMMAND REFERENCE**, 0 AP |
| `Would you have Ney attack Mack please?` | False | **attacks**, 1 AP |
| `Can you have Ney attack Mack?` | True | manual |
| `Ney, could you attack Mack?` | True | manual |
| `Ney, would you attack Mack?` | False | attacks |

`clause_guards.py:561` — `_MODAL_LEADS = frozenset({"will", "would",
"shall"})`. The polite-imperative exemption at `clause_guards.py:597-605`
("the polite imperative to the person addressed … *'would you have Ney attack
Mack'*") applies **only** to that set, while `can|could|may|might` sit in the
general lead list at `clause_guards.py:558-559` and take the `?`-or-
first-person rule instead. Identical politeness, opposite outcomes.

### P3-2 — a misspelt scout target vanishes without comment

`nmB.json`: `Ney, scout Bavarai` → **1 AP charged**, a generic
scout-from-here of all six adjacent provinces, and the word `Bavarai` is never
mentioned. Compare the move arm, which for the same class says *"(Our maps
read Swabia as the province nearest your order, Sire.)"*.

### P3-3 — a nonsense refusal reads three provinces off the far edge of the map

`the Guard attack Mack` → *"Region 'Attack Mack' not found. Nearby: La Mancha,
Karaman, Stockholm"* (`nm40_out.txt` §1). Spain, Anatolia and Sweden, offered
to a player whose army is on the Rhine.

---

## WHAT THE GOOD FAMILIES LOOK LIKE (the bar the rest should meet)

**Family B** is the model and should be the template for a fix:

```
'Ney, move to Swabya'
  Cannot move into Swabia - enemy forces present! Use ATTACK to engage Mack.
  (Our maps read Swabia as the province nearest your order, Sire.)
  Try: 'Ney, attack Mack'                                     0 AP
'Ney, move to Austria'
  Austria is a nation, not a province. Name a province, Sire — theirs are
  Bohemia, Carniola, Croatia, Hungary, Moravia, Tyrol, Vienna.              0 AP
'Ney, move to Venetia'   Region 'Venetia' not found. Did you mean 'Vienna'?  0 AP
```

It corrects, **discloses that it corrected**, states the reason, and hands back
a typable command. **Family E** is nearly as good — every one of eight
illegal-but-legal orders states its cause:

```
FORTIFIED     'Ney is fortified at Rhineland and cannot move. Order 'unfortify' first…'
              Try: 'Ney, unfortify' to abandon fortified position          0 AP
CAPTIVE       'Marshal Ney is a prisoner of Austria, Sire — no order can reach him…'  0 AP
FALLEN        'Marshal Ney is lost to us, Sire — his corps was destroyed at Rhineland.
               His name cannot lead the army again.'                        0 AP
UNSEEN TARGET 'No intelligence on Archduke Charles's position, Sire. Scout for him
               before Ney can give chase.'                                  0 AP
```

*(Correction to my own first pass: the FALLEN line above is the real
`destroy_marshal` path, `nm20_out.txt` §5. My earlier probe popped the marshal
out of `world.marshals` by hand and got the generic unknown-name copy — that
was my setup's artifact, not the game's.)*

**Family F** hands the tail clause back by name:
`Ney attack Mack then fortify` → the attack executes, then
*"Berthier: 'One order at a time, Sire — I have relayed the first. "fortify"
must follow as its own command.'"*

---

## WHERE BEING WRONG COSTS SOMETHING

| near-miss | cost | reversible? | says why? |
|---|---|---|---|
| `Massena, attack Mack` (out of range) | **2 AP + 2,520 men** to march Milan→Munich | a standing PURSUE; cancel costs 1 AP | yes — *"Massena pursues Mack (at Swabia). Moves to Munich."* |
| `Ney, attack Hohenlohe` (nation at PEACE) | **1 AP, and the attack does not happen** | n/a | *"Choose your war purpose against Prussia. Issue the attack again after the declaration is settled."* |
| `Nay attack Mack` | **1 AP + a battle** | **no** | **no** |
| `attack Mack` | **1 AP + a battle** | **no** | **no** |
| bare `retreat` | 0 AP, 8 corps displaced | no | no |
| `attack …if outnumbered` | 1 AP + a battle | no | partially |

**The war-purpose detour is a trap on the typed road** (`nm40_out.txt` §2).
Measured, seven typed commands:

```
[1] 'Ney, attack Hohenlohe'  AP 4->3  'Choose your war purpose…issue the attack again'
[2] 'conquest'               AP 3->3  Talleyrand advisory (threat 70) — does NOT settle
[3] 'proceed'                AP 3->3  'There is no pending diplomatic matter to respond to'
[4] 'Ney, attack Hohenlohe'  AP 3->2  same message again
[7] 'Ney, attack Hohenlohe'  AP 2->1  same message again
AP spent: 3.  Prussia still not at war.
```

⚠ **Stated limit:** the client answers this through a `war_purpose_popup`, and
`tools/playtest_driver.py:2863` answers it by dialogue policy, not by typing.
I did not drive the popup endpoint, so *"there is no way through"* is
**UNVERIFIED**. What **is** measured is that **each typed re-issue costs
another AP and the attack never happens** — a player who mistakes a neutral
for an enemy can burn a whole turn.

---

## THE REFUSAL-COPY CENSUS

**Empirical** (`nm50_out.txt`) — 119 near-miss utterances driven end to end:

| | |
|---|---|
| refusals / no-ops | **83** |
| acted | 36 |
| distinct refusal first lines (raw) | **52** |
| distinct refusal **templates** (names/numbers elided) | **46** |
| templates naming a concrete next step | **24** (52%) |
| templates naming none | **22** (48%) |

The 22 that name no next step are mostly *statements of fact* rather than
shrugs — `'Ney is not currently fortified.'`, `'Not enough actions! Need 1,
have 0.'`, `'Region 'Ulm' not found.'`, `'Unknown region: Lyon'`,
`'Cannot enter Frankfurt — it is controlled by Hesse (diplomatic state:
PEACE). Open borders or higher required.'` Each is true; none says what to do
instead (propose open borders, end the turn, name the province you meant).
Full list in `nm50_out.txt`.

**The generic shrug** is `LLMClient._berthier_mock_response`,
`backend/ai/llm_client.py:1164`.

* **Code paths that reach it: 2** — `backend/main.py:3543` and
  `backend/main.py:3691`, both at the parse-failure fallthrough, via
  `generate_berthier_recovery` (`llm_client.py:1120`). (`providers.py:779` is
  the live-LLM arm of the same call; `delegation.py:614` reuses the *shape*,
  not the function.)
* **Utterances that landed on it: 16 of 119** — `besiege`, `raid`, `forage`,
  `promote`, `burn the bridges`, `requisition food`, `flank`, `encircle`,
  `surrender`, `disband`, `desert`, `execute`, `sing`, `asdfgh`, `Ney,`, and
  **`Ney, cancel`** (a real verb, with nothing to cancel — the shrug instead
  of *"Ney holds no order to cancel"*).
* **It is `random.choice`** (`llm_client.py:1240`) over 8 templates in 3
  buckets. Measured, same utterance 8×:

  ```
  'Ney, forage'  x4 "Berthier adjusts his spectacles. …"
                 x3 "Berthier frowns at the dispatch. …"
                 x1 "…Marshal Ney awaits your command, but I cannot parse…"
  ```
  A player repeating a bad command to learn the rule gets a different excuse
  each time. Two of the three buckets *do* name valid orders, so the copy is
  decent — the randomness is what defeats learning.

**The COMMAND REFERENCE is the second shrug.** 12,717 characters / 236 lines,
returned in full to **6 of 119** utterances: `?`, `how do I attack`,
`what can Ney do`, `should Ney attack Mack?`, `will Ney beat Mack`,
**`Could you have Ney attack Mack please?`**. The first three are correct by
design (`question_desk.py:14-19` scopes the desk to FACT questions and leaves
feasibility/advice to the manual, owned by CR-8). The last three are the
defect: two are questions a desk should answer, one is an order.

---

## THE MANUAL DOES NOT TYPE

`nm30_out.txt` §2 — I harvested all **50** distinct quoted examples from the
game's own `help` output and typed each one back on the boot board. 26 were
refused. Most are refused for honest board reasons (no artillery yet,
treasury short, Ney's expectation already met) — correct behaviour. **Four are
true copy defects: the sentence can never work on this map.**

| the manual prints | the game answers |
|---|---|
| `"Soult, move to Bavaria"` | *"Bavaria is a nation, not a province."* — Bavaria is **not a region** |
| `"Davout, hold Ulm"` | *"Region 'Ulm' not found."* — and **Ulm is what the campaign is about** |
| `"repair Lyon"` / `build … at Lyon` | *"Unknown region: Lyon"* — the map has **Lyonnais** |
| `"halt Ney"` (listed as a cancel alias) | works **only** if an order exists; otherwise the generic shrug |

*(Six further "refusals" — `Bravest of the Brave`, `Iron Resolve`, `Roland of
the Army`, `First Horseman of Europe`, `Eyes on a Crown`, `Child of Victory` —
are ability names quoted in the manual, not commands. Harvest artifact, not
defects. Noted because one of them, `Drillmaster of Boulogne`, **does** reach
a clarification prompt.)*

This is IQ-10's H-row class ("the game's own printed sentence is not typable")
one file over, and it is cheap to pin: the examples can be asserted against
the live region list.

---

## TWO THRESHOLDS WORTH KNOWING

**`_MIN_FUZZY_TARGET_LEN = 4`** (`backend/commands/parser.py:584`, consumed by
`_plausible_name_typo` at `parser.py:649-650`). A near-miss shorter than 4
characters is **never** offered a correction. Measured (`nm20_out.txt` §2):

```
'Nay'  len=3  plausible-typo-of -> []        # 1 substitution from Ney
'Nye'  len=3  plausible-typo-of -> []
'Neyy' len=4  plausible-typo-of -> ['Ney']
'Sult' len=4  plausible-typo-of -> ['Soult']
```

Same floor produces the `Ulm` gap: `Lyon`→*"Did you mean 'Lyonnais'?"*,
`Wien`→`Vienna`, `Munchen`→`Munich`, `Venetia`→`Vienna`, `Moscow`→`Oslo` —
but `Ulm` (3 chars) gets a bare *"Region 'Ulm' not found."*

**Two fuzzy scans disagree.** `_plausible_name_typo('Muart','Murat')` is
**False** (transposition = 2 Levenshtein edits, limit 1 at len<6), yet the
live parser bound `Muart` → `Murat` and fought
(`nm30_out.txt` §1b: `parsed marshal='Murat' … type='specific'`). The gate
exists; the path that executes does not consult it. The *outcome* there was
right — but it means the strictness a reader infers from `parser.py:635` is
not the strictness the player meets.

**And the same unbound name gets two different answers by verb**
(`nm30_out.txt` §1): `Nay, fortify` → *"Which marshal shall carry out this
order, Sire?"* (a picker); `Nay, attack Mack` → a dead-end refusal with no
candidates.

---

## SMALLEST FIXES, IN ORDER OF LEVERAGE

1. **Make `_unbound_addressee` not depend on a comma.** A leading token that
   is neither a roster name nor an order verb, followed by an order verb, is
   an addressee. Closes P1-1 and P1-3 together. `executor.py:972-974`.
2. **Give `auto_assign_attack` the clarify branch `general_attack` already
   has** — `build_contact_attack_clarification` is written and working.
   `combat_executor.py:10080`. Closes P1-2. Failing that, make the auto-pick
   *say* it picked (the `explanation` field is already there and is `""`).
3. **Add `can|could|may|might` to the second-person politeness exemption**, or
   move the exemption off `_MODAL_LEADS` onto "modal + `you`".
   `clause_guards.py:561`. One line; closes P3-1.
4. **`if <adjective>` / `when <adjective>` / `should <clause>`** — three
   shapes to add to the condition guard, which already refuses nine siblings
   correctly. Closes P1-4.
5. **Drop the 4-character floor to 3** for the did-you-mean *suggestion* only
   (not for silent auto-correction), so `Nay`→Ney and `Ulm`→? are at least
   offered.
6. **Pin the manual's examples against the live region and roster lists** —
   4 known-bad sentences today, and the class recurs.
7. **Make the shrug deterministic** (hash the utterance instead of
   `random.choice`, `llm_client.py:1240`) so a repeated mistake gets a
   repeated answer.

---

## LIMITS OF THIS RECON

* `LLM_MODE=mock` throughout. Everything above is the **fast-parser** road.
  Under `LLM_MODE=anthropic` a sub-0.7-confidence parse escalates, and several
  of these near-misses would be resolved differently. **None of the findings
  were checked against the live parser** — but note that P1-1 through P1-3 all
  arise *below* the parser, in `executor.py` / `combat_executor.py`, so the
  escalation cannot reach them.
* The war-purpose popup endpoint was not driven (see the ⚠ above).
* The client road was not driven. `region_panel.gd` chips emit typed strings,
  so they converge here — but the chips emit *well-formed* strings, which is
  exactly why this report matters: **the near-miss cost is a property of the
  typed road alone.**
* Fresh-boot board only (turn 1). A mid-campaign board with a fogged enemy, a
  standing order or a pending dialogue may route differently.
