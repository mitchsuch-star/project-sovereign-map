# VERDICT: CX-BEHAV-1 — **CONFIRMED**, sharpened in four places, severity **HELD at P3**

**Refuter pass, read-only, September 19 2026.** Tree at `f52df77f` (one docs commit
above the `727cf88a` the brief names), clean, nothing under `backend/`,
`godot-client/`, `tests/`, `docs/` or `tools/` modified, no git-mutating command run.

Every figure below is the output of a probe **I wrote and ran**, under
`…/scratchpad/cx_review/probes/r*.py`, with `LLM_MODE=mock` pinned *before* the first
backend import and a `socket.connect` guard that raises on any non-loopback address
(`probes/_boot.py`) — standalone scripts do not get `tests/conftest.py`. My first
cut (`r1`) ran without that guard and the banner printed `LLM_MODE: anthropic`; I
re-ran the whole census under `r3` with mock pinned and the results are byte-identical,
so nothing here depends on the parser mode.

---

## 0. SCOREBOARD

| # | the claim says | verdict |
|---|---|---|
| 1 | `repair Lyon` → `Unknown region: Lyon`, success False | ✅ **reproduces exactly** |
| 2 | `Soult, move to Bavaria` → `Bavaria is a nation, not a province…`, success False | ✅ **reproduces exactly** |
| 3 | the census is green while both ship | ✅ **reproduces** — 202 passed, **0 needle hits of 43 non-exempt phrases while 18 fail** |
| 4 | player-reachable, not client-redirected | ✅ **reproduces** — transliterated the real predicate out of `main.gd` |
| 5 | not shipped by row CX | ✅ **holds for the defect** — but the *invisibility* and the *new traffic to the manual* are this row's, and the claim does not say so |
| 6 | "`Lyon` … that is exactly `Ulm`'s story" | ❌ **WRONG, and it under-states the finding** — `Ulm` is in **neither** map; `Lyon` and `Bavaria` are **both** legacy 19-region names |
| 7 | the census misses it because `Unknown region` is "one word off `Unknown target`" | ❌ **understated** — the needle list covers the *strategic/combat* refusal vocabulary and misses the *economy/dotation* one entirely: **8 production sites** |
| 8 | *fix:* `repair Lyon` → a 1805 province | ❌ **does not satisfy its own new assertion** — **zero** 1805 provinces carry war damage at boot |
| 9 | *fix:* assert `success is True` + a gate allowlist | ⚠ **hazard** — the allowlist would be **16 rows, ≥11 of them boot-board *values*** |
| 10 | severity P3 | ✅ **HELD** — measured: **both refusals are FREE** (AP 4→4, admin AP 2→2, gold 800→800) |

---

## 1. THE REPRODUCTION I RAN

`probes/r3_census_mockpinned.py` — extracts the quoted strings from the rendered
`help` myself, drives each through `POST /command` on a **fresh 1805 board**, and
records the full verdict rather than a needle match.

```
help body = 11636 chars ; quoted phrases = 50
non-exempt = 43 ; success is not True = 18
needle hits (the committed pin's failure set) = 0

  'repair Lyon'              needles=[]   Unknown region: Lyon
  'Soult, move to Bavaria'   needles=[]   Bavaria is a nation, not a province. Name a
                                          province, Sire — theirs are Franconia, Munich, Swabia.
```

The pin is green about it (`probes` aside, run at HEAD):

```
.venv/Scripts/python.exe -m pytest tests/test_cx*.py -q -p no:randomly
  202 passed in 21.59s
```

**Both instances reproduce exactly as filed.** The claim is CONFIRMED on its facts.

---

## 2. ⛔ THE CLASS IS NOT `Ulm`'s — IT IS MAP-CUTOVER RESIDUE, AND THAT IS WORSE

The claim's diagnosis: *"`Lyon` is a LEGACY-map region … That is exactly `Ulm`'s story
(CX-3b), eleven lines down the same manual."* Measured (`probes/r5`, `r6`):

```
legacy (create_regions, 19 regions): Lyon True   Bavaria True   Ulm FALSE
1805   (126 regions):                Lyon False  Bavaria False  Ulm FALSE

legacy  'repair Lyon'            "No war damage to repair in Lyon"   <- the region EXISTS
legacy  'Soult, move to Bavaria' resolves; only the ROSTER differs (legacy has no Soult)
legacy  'Davout, hold Ulm'       "Region 'Ulm' not found."           <- never a region, EITHER map
```

`Ulm` is a **town inside Swabia** — the CX-3 test's own docstring says so — and was
never a region on any board. `Lyon` **and** `Bavaria` are both names off the
**pre-cutover 19-region map** (`Bavaria, Belgium, Berlin, Bohemia, Bordeaux, Brittany,
Dresden, Hanover, Lyon, Marseille, Milan, Netherlands, Normandy, Paris, Rhineland,
Saxony, Tyrol, Vienna, Waterloo`).

So the two survivors are **one class with each other and a different class from the one
CX-3 caught**: the COMMAND REFERENCE is still teaching the board the project left on
**July 2, 2026**. The claim's analogy makes it sound like a stray historical place name.
It is the map cutover, fourteen months late.

### …and the attribution names a commit

`git log -S` + `git show` (`probes` not needed — git):

```
2641c23d  feat(MC-X): MC exit review build … + help modernization      (Jul 11 2026)
  -               "Grouchy, move to Belgium"
  +               "Soult, move to Bavaria"
  -               "Ney, march to Bavaria" / "move to Bavaria"
  -               "build fortification at Lyon"
  -               "build stables at Lyon" (cavalry recruitment)
  -               "repair Lyon" / "repair market at Lyon"
  +  hold       - "Davout, hold Ulm" - hold ground (artillery auto-fires)
  +  repair     - "repair Lyon" (1 AP, 150g)
```

The commit whose recorded purpose in `CLAUDE.md` is *"help command modernized to the
1805 campaign incl. all econ verbs"* **deleted four legacy-map examples and
re-introduced two of them in its own new text**, plus invented a third (`Ulm`). Row CX
(`2c3535b5`) then fixed exactly the one of the three its needle list could see:

```
2c3535b5  -  hold  - "Davout, hold Ulm" …
          +  hold  - "Davout, hold Swabia" …
```

**`shipped_by_this_row: false` is correct for the defect.** But row CX opened this file,
at this block, to fix the sibling instance, and left the two next to it standing.

---

## 3. ⛔ THE BLIND SPOT IS A WHOLE VOCABULARY, NOT A NEAR MISS

The claim: *`"Unknown region: Lyon"` — one word off `"Unknown target"`*. That reads as
bad luck. It is structural. The needle list

```python
refusals = ("not found", "cannot parse", "Unknown target",
            "I cannot interpret", "no such", "eludes me")
```

covers the **strategic / combat** refusal idioms (`Region 'X' not found.`,
`Marshal 'X' not found`, `Unknown target: X`) and covers the **economy / dotation**
one **not at all**:

```
grep -rc "Unknown region:" backend/
  backend/commands/economy_executor.py : 5
  backend/commands/meta_executor.py    : 2
  backend/game_logic/dotation.py       : 1      -> 8 production sites, 0 needles
```

…plus IGR-A's honest-refusal idiom `"<X> is a nation, not a province."`
(`git log -S`: written by `3a1fa63b` / `6814469d`, **not** by row CX — the row did not
re-word its way out of a needle).

That is why `hold Ulm` was caught and `repair Lyon` was not: `hold` is a strategic verb
and `repair` is an economy verb. **Any future help example using `build`, `repair`,
`recruit at`, `garrison` or `endow` with a bad place name is invisible to this census by
construction.**

---

## 4. REACHABILITY — CONFIRMED, WITH A BONUS THE CLAIM MISSED

I transliterated `main.gd`'s `_redirect_diplomatic_command` into Python with **every
keyword list parsed out of the `.gd`** rather than retyped (`probes/r4`), including
`_contains_word`'s word-boundary rule and the nation table off the live board:

```
quoted phrases: 50
=== CLIENT-REDIRECTED (backend never sees them) ===
  'buy off Prussia'                           -> ANYWHERE:buy off
  'guarantee Saxony'                          -> ANYWHERE:guarantee
  'license Prussia against Austria'           -> ANYWHERE:license
  'sponsor Prussia against Austria, 200 gold' -> ANYWHERE:sponsor
  ---> 4 of 50

  'help'                    redirected=None
  'repair Lyon'             redirected=None
  'Soult, move to Bavaria'  redirected=None
```

**Player-reachable: yes**, all three. And the traffic to the manual is heavier than the
claim says — **row CX itself built the road**:

```
git log -S"Type 'help' for the full command reference." -- backend/
  5fc3d5c8  feat(cx2): CX-2 "Berthier answers the board" …
```

That is the **only** line in the backend that tells a player to type `help`, and CX-2
appends it to Berthier's answer for *every question the desk cannot take*. The CX-3
completer also offers `help` in `_BARE_COMMANDS` — while offering **no `repair` verb at
all** (`_MARSHAL_VERBS` = attack/march to/move to/scout/fortify/unfortify/drill/defend/
hold/retreat/support/garrison). So for `repair`, the manual is the sole teacher, and the
row pointed more players at it.

**Bonus finding for the record:** three of those four client-redirected phrasings
(`buy off`, `license`, `sponsor`) sit in the census's own failure set — the pin is
driving sentences a player *cannot send*, and a "gate allowlist" would file them under
the wrong reason.

---

## 5. ⛔ THE SUGGESTED FIX CANNOT SATISFY ITS OWN ASSERTION

The claim proposes: *assert `success is True` for every non-exempt phrase, keep an
allowlist of gates, then fix the two — `repair Lyon` → a 1805 province.* Measured
(`probes/r7`):

```
1805 provinces with war_damage > 0 at boot : 0    (of 126; 28 French-held)

repair Lyonnais   success=False   "No war damage to repair in Lyonnais"
repair Paris      success=False   "No war damage to repair in Paris"
repair Normandy   success=False   "No war damage to repair in Normandy"
repair Berry      success=False   "No war damage to repair in Berry"
```

**`repair <anything>` can never return success on a fresh board.** Under the proposed
assertion the repair row is a *permanent* allowlist entry; the name fix buys only the
quality of the refusal (dead end → teachable). Follow the prescription literally and you
fix the name, watch the pin stay red, and may revert a good change.

The move half does fix cleanly, and I measured which replacement actually works:

```
Soult, move to Rhineland      success=True    <- adjacent, clean
Soult, move to Orleanais      success=True    <- adjacent, clean
Soult, move to Brabant        success=True    but "900 lost to march" — poor thing to teach
Soult, move to Swabia         success=False   Mack is there
Soult, move to Franconia      success=True    but distance 2 — contradicts the line's own
Soult, move to Munich         success=True    "Move to adjacent region" description
```

**`Soult, move to Rhineland`** is the fix: it succeeds *and* honours the caption.

### the allowlist is a balance-coupled pin

Of my 18 non-exempt failures, 16 survive the two string fixes and **≥11 fail on
boot-board *values***: `buy off Prussia` (price 1008 vs treasury 800), the three
substitute phrasings (4,012g vs 800), `recruit` / `recruit at Paris` (marshal out of
range), `Grant Ney a rente` (expectation already met), `guard home waters` (fleet
already at guard), `Soult, drill` (Mack adjacent), `bombard Swabia` (no artillery
marshal), `Endow Ney with the Duchy of Swabia` (Swabia not held), `Murat, pursue
Kutuzov` (no intel), `land Soult in Munster` (30,000 > 15,000 lift). An allowlist over
those couples the CX census to the boot economy, the naval posture and the jealousy
state — the shape this project keeps finding inert or spuriously red.

**A better shape, on the evidence above:** keep the executor-level census, but replace
the hand-written needle tuple with the *executor's own* place-not-found vocabulary
derived by AST/grep census over `backend/` (`Unknown region:`, `Region 'X' not found`,
`is a nation, not a province`), with a sensitivity arm — so a *new* refusal idiom fails
the census until somebody adds it, instead of silently widening the blind spot.

**No pin reds from the two string fixes.** `grep -rn "repair Lyon\|move to Bavaria"
tests/` finds one hit, a docstring (`test_wo_slice8_panel_states_its_terms.py:1033`);
the `12,717-character COMMAND REFERENCE` in `test_fa_slice7…py:649` is prose, not an
assertion; `test_square_formation.py` and `test_ca9_row3_a11…` pin other strings.

---

## 6. SEVERITY — P3 HELD, AND HERE IS WHY IT IS NOT HIGHER

`probes/r8`, one persistent board, four commands in sequence:

```
'repair Lyon'              success=False  AP 4->4  adminAP 2->2  gold 800->800
'Soult, move to Bavaria'   success=False  AP 4->4  adminAP 2->2  gold 800->800
'help'                     success=True   AP 4->4  adminAP 2->2  gold 800->800
'Soult, move to Rhineland' success=True   AP 4->3  adminAP 2->2  gold 800->800
```

**Both refusals are free.** The harm is a wasted keystroke and a moment of doubt, not a
spent action point. And the two are not equal:

* `Soult, move to Bavaria` **self-corrects** — it names Franconia, Munich and Swabia,
  and two of the three succeed. That is CX-2's honest-refusal design working. Nearly P4.
* `repair Lyon` → *"Unknown region: Lyon"* names nothing and suggests nothing. It is the
  real one. It is held at P3 rather than raised because `repair` has a correct
  alternative road the manual does not own: the region panel's
  `do:repair <region>` chip (`region_panel.gd:424`), built with the live region name and
  shown only when the province needs it.

**P3 is right.** Not P2 — nothing is spent, nothing is mis-executed, and no order goes
to a marshal the player did not name. Not P4 — `help` is the canonical discovery surface,
this row added the only line that sends players to it, and the manual is the sole
teacher of the verb it names with a dead region.

---

## 7. WHAT I WOULD CHANGE ON THE ROW

1. `repair Lyon` → `repair Lyonnais`, and `"Soult, move to Bavaria"` →
   `"Soult, move to Rhineland"`. Both free, both pinned by nothing.
2. Re-key the census off the executor's **own** refusal vocabulary with a sensitivity
   arm, not a hand-written tuple. State in the docstring that the economy half was the
   blind spot and name the 8 sites.
3. Say on the record that the census caught 1 of the 3 instances present when it landed,
   and that CX-2 increased traffic to the manual it guards.

**Do not** adopt `assert success is True` + a gate allowlist as written: it cannot be
satisfied by the repair fix it prescribes, and it would enshrine eleven boot-board
numbers in a parsing pin.

---

## PROBES

| file | what it measures |
|---|---|
| `probes/_boot.py` | pins `LLM_MODE=mock` before import + non-loopback `socket.connect` guard |
| `probes/r1_help_census.py` | first cut (un-pinned) — kept so the re-run can be compared |
| `probes/r3_census_mockpinned.py` | the census, mock-pinned: 50 quoted / 43 non-exempt / 18 fail / 0 needle hits |
| `probes/r2_lyon_and_bavaria.py` | `Lyon`/`Bavaria`/`Ulm` membership, Soult's adjacency, the executor's own suggestions |
| `probes/r5_legacy_map.py` | the 19-region legacy list vs the 126-province board |
| `probes/r6_legacy_executes.py` | both survivors driven on the **legacy** world — the cutover proof |
| `probes/r4_client_redirect.py` | `_redirect_diplomatic_command` transliterated, lists parsed from `main.gd` |
| `probes/r7_would_the_fix_work.py` | 0 war-damaged provinces at boot; which adjacent move succeeds |
| `probes/r8_cost_of_the_refusal.py` | AP / admin AP / gold across both refusals |
