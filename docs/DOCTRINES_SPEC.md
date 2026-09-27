# National Doctrines — SR-D2 "France feels different from Austria"

> **Status: RULED September 27, 2026 by the user.** This is the doctrine half of SR-D2 (`SCORE_MANDATE_PLAN.md` §4). It was pulled forward from Chunk 7's gate so the reforms' law list (`REFORMS_SPEC.md`, built at Chunk 5) could be written against it. **Nothing is built.** The doctrines are still built at Chunk 7, as slice group SR-7d.
>
> This file holds:
> - **the gate record (§0)**, which is authoritative;
> - **the build contract (§1–§8).**
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
  - The map marks nothing poor where history does. Measured:
    - the map's 27 rural, lowest-income provinces are in France, Hanover, Holland, Sweden and the Ottoman islands;
    - every Russian and Prussian province is a city or town feeding 31,500–50,000;
    - so neither region type nor income can stand in for poor country.
  - A new scenario list, `poor_country`, names it. **DRAFT list:**
    - East Prussia, Posen, Samogitia, Lithuania, White Russia and Volhynia — where the 1807 and 1812 campaigns starved;
    - Leon, Aragon and Galicia — the Spanish war;
    - Alentejo and Beira — Masséna's 1810 invasion of Portugal;
    - Rumelia, Epirus and Albania — the Balkans.
  - The build authors the list; the validator checks the names.
- **D-R2 — The flaw bites only where the army is not fed.**
  - It applies only where the supply rule already feeds the army at the base rate: not home soil, not allied or vassal soil, and no naval lifeline.
  - At home and on allied soil the magazines feed a French army as they do today.
- **D-R3 — The Train des Équipages becomes the cure alone.**
  - The draft law's supply bonus (×1.25, `REFORMS_SPEC.md` §6) is dropped. The reform restores what the flaw takes, which was its historical purpose: the decree of 26 March 1807 followed the Polish winter.
  - A law with no effect cannot ship before the flaw exists. So **the Train is authored at Chunk 7 with the doctrines, not at Chunk 5**, and France's Chunk-5 deck has five laws (still within the ruled 5–8).
- **D-R4 — A cure is a new law effect type, `cures`.** This is `REFORMS_SPEC.md` §4's tenth type.
  - Austria's Corps d'Armée and Russia's Divisional System carry it as their second clause. Those laws are worth more to their courts than France's Staff law is to France — that is the catch-up — at the same price.
  - **No cure clause is authored before its flaw exists (GR9).** The cures land at Chunk 7 (slice DC-2). Until then each of those laws does only what it does at Chunk 5.
- **D-R5 — The opening balance moves.**
  - Doctrines apply from turn 1, so the Chunk-7 build re-records `BASELINE_SERIES` once, with a flip arm.
  - M1–M7 will move too, because the harness pits French corps against Austrian ones. They are re-read and re-blessed consciously, not assumed byte-identical.

---

## §1 What a doctrine is

**Where it lives.** A doctrine is authored per court under a new scenario key, `doctrines`, in `europe_1805.json`, and validated by `modding/validator.py`. Each entry carries:

| Field | Meaning |
|---|---|
| `name` | the doctrine's display name |
| `says` | one line, printed verbatim |
| `strength` | one clause from §3's closed set |
| `flaw` | one clause from §3's closed set |
| `cured_by` | the law id that removes the flaw |

**Rules:**
- **Authored content, not formulas** (`SCORE_MANDATE_PLAN.md` §4, the rule of the house): every number sits in the scenario.
- **A doctrine is a data parameter, not a special case.** Any court whose authored doctrine carries a clause gets it (GR5 in the rules sense). Today only the five great powers author one.
- **In force from turn 1, never bought, never lost.** Only its flaw can be removed, by the cure law.

---

## §2 The five doctrines — DRAFT numbers

| Court | Doctrine | Strength | Flaw | Cured by |
|---|---|---|---|---|
| France | **The Corps System** | A French corps within a march joins a battle as if under a written support order: **+10 on the arrival roll** | **Living off the land:** a French army that is not fed (D-R2), standing in poor country (D-R1), is held to **80%** of the province's supply | The Train des Équipages (D-R3) |
| Britain | **The Line Holds** | A British corps defending: **+15%** | **Irreplaceable:** British recruits cost **×1.25**, on top of the small authored manpower pool | The Militia Transfer |
| Russia | **Stubborn** | A beaten Russian army loses **half** the morale a lopsided defeat costs | **Slow to concentrate:** **−10 on the arrival roll** | The Divisional System |
| Austria | **The Guns** | Austrian artillery recruits cost **×0.85** | **The Hofkriegsrat** (the court war council): **−10 on the arrival roll** | The Corps d'Armée |
| Prussia | **Frederick's Drill** | Drill restores **+5** more morale | **Brittle:** a lopsided defeat costs **×1.5** morale | The Articles of War |

**The law list after the doctrines** (`REFORMS_SPEC.md` §6):
- **Cure only:** the Train des Équipages (D-R3).
- **Cure added as a second clause:**
  - the Corps d'Armée and the Divisional System (after their +1 action);
  - the Militia Transfer (after its manpower regen);
  - the Articles of War (after its recruit morale).

---

## §3 The seams — each effect on ONE existing single source

Every seam below was verified at HEAD `34c939cf`.

| Effect | The seam | Also quoted by |
|---|---|---|
| Arrival roll ± | `CombatExecutor._arrival_deterministic` (the deterministic sum the roll adds its jitter to) | `_arrival_odds_row`, i.e. the muster preview and the glory gate's odds |
| Defence % | `Marshal.get_defense_modifier` (GR1 — the one place a defence modifier lives) | the battle report's modifier snapshot |
| Recruit price × | `EconomyExecutor._calculate_recruit_cost` | `recruit_quote` and every chip that quotes it |
| Lopsided-defeat morale × | `combat.decisiveness_morale_penalty` (both morale paths already read it) | the battle report's morale line |
| Drill morale + | `WorldState.DRILL_MORALE_GAIN` / `_TRAINED` | the dispatch's drill line (`dispatch.py`). The build extracts ONE nation-aware accessor both read. |
| Supply ×, living off the land | `WorldState._supply_multiplier` (the fed/unfed decision) | `get_effective_supply_cap`, i.e. attrition, the supply-strain headline, the depot chip and P6.5 |

**The poor-country test must read province identity, never capacity.**
- `_supply_multiplier`'s WO slice-8 invariant is that the decision reads only (nation, region identity). That is what lets the depot chip price its counterfactual exactly.
- An authored `poor_country` list is identity, so the invariant holds.
- A capacity threshold would break it, so D-R1 authors a list rather than deriving one.

---

## §4 What the player sees

**Each court's doctrine is shown** — name, strength, flaw, and the law that cures it:
- for France, on the Generals screen;
- for every great power, on its Diplomatic Ledger nation card.

**When a doctrine fires, it is named where it fires:**
- the muster row — "the corps system +10", "slow to concentrate −10";
- the battle report's morale line — "Russian stubbornness", "the Prussian line broke";
- the supply-strain headline — "living off the land: this country feeds 80%";
- the recruit quote — "British recruits come dear".

**The laws say what they cure.** The LAWS tab names the doctrine flaw a law cures.

**The rivals' laws name what they copy from France** — `REFORMS_SPEC.md` §0 Q7. Example: "the corps system France has used since 1800".

---

## §5 The AI

**No new AI decision rules.** Every doctrine is a number on a seam the AI already reads:
- its muster and glory-gate odds read the arrival roll;
- its supply rung (P6.5) reads the effective cap;
- its recruit pre-budget reads the price;
- its combat reads the morale and defence terms.

**Cure laws come early in the rivals' decks.** The deck order is authored (`REFORMS_SPEC.md` §7), so a court buys its cure on its own schedule.

---

## §6 Acceptance — falsifiable targets

| # | Target | Pass condition |
|---|---|---|
| T1 | Each doctrine fires | A pinned, staged case for each strength and each flaw, on both boards where the seam is shared. Each case also shows the doctrine named on the surface where it fires. |
| T2 | The cure | Every flaw has exactly one cure law. Enacting it removes the flaw at the next read; a lapse or repeal of the law brings the flaw back at the next read. |
| T3 | The homogeneity guard | The AI-V sweep's homogeneity guard stays green, and a played arm can NAME each great power's style from its digest (the plan's SR-D2 Q5 measurement). |
| T4 | Balance, re-measured | `BASELINE_SERIES` is re-recorded ONCE: with the lever `DOCTRINES_ACTIVE` down, the prior series reproduces byte for byte. M1–M7 are re-read and consciously re-blessed. |
| T5 | The road to 45 | Q0 (`SCORE_MANDATE_PLAN.md` §4 SR-D3) is re-measured after the doctrines land. The corps system should help France; living off the land should hurt only in poor country. |

**Gates for every slice:** every pin mutation-swept to 0 INERT; any `.gd` change passes the parse harness (EXIT=0) and a boot with 0 SCRIPT ERROR.

---

## §7 The build slices — Chunk 7's head, "SR-7d The Doctrines"

| Slice | Scope | Size (sessions) |
|---|---|---|
| **DC-0** | **The substrate.** The `doctrines` and `poor_country` scenario keys, the validator blocks, and the single accessors each seam reads. No doctrine is active yet. | 0.2 |
| **DC-1** | **Strengths and flaws.** The five doctrines' clauses at their seams, behind the lever. The flip arm; T1 and T4. | 0.4 |
| **DC-2** | **The cures.** The `cures` law effect type (D-R4), the Train des Équipages authored (D-R3), the four cure clauses; T2. | 0.3 |
| **DC-3** | **The client.** The doctrine rows on the Generals screen and nation cards, the named firing lines, the LAWS tab's cure line. Parse harness and boot. | 0.3 |

**Size.** About 1.2 sessions. Chunk 7 grows from about 2.0 sessions to about 3.2.

**Dependency.** DC-2 needs the laws (SR-5r, Chunk 5), and Chunk 7 comes after Chunk 5.

**What not to build first:**
- anything the AI cannot play;
- a cure clause before its flaw exists;
- a second playable nation.

---

## §8 Not in this ruling — each with its home, or struck

| Item | Disposition |
|---|---|
| The winter and the seasons | `SEASONS_WEATHER_SPEC.md`: the first content slice after the first outside playtest ("The General Winter"). |
| The standing alarm floor (SR-G7 / PB-D1) | Still a question for Chunk 7's gate (`SCORE_MANDATE_PLAN.md` §2 Chunk 7). |
| Doctrines for secondary and minor courts | Not in v1, and nothing in the client promises them. If they are ever wanted, they re-open at this gate. |
| Historical Moments (SR-D2 Q4) | Not with the doctrines. The Events System is cut to after Early Access (`ROADMAP.md` §The Road to Early Access). |
| A second playable nation | Out of scope (post-EA). The doctrines are written so a British player could inherit Britain's. |
