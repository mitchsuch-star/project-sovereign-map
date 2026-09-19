# VERDICT: CX-CLAIM-11 — **NARROWED**

**Title as filed:** *"The predictor's keystroke table is 2-of-7 reproducible, and its
simulator is not committed — the row breaks the IQ-8 table rule it cites in its own
header."* (P4, not player-reachable, shipped by row CX.)

**Verdict: NARROWED — both headline limbs are REFUTED by measurement; a one-line
citation residue survives.**

* **"2 of 7 reproducible" → measured 4 of 7 EXACT, a 5th within 1.2 points.** I
  reproduced `14.8%` and `17.5%` — two of the five the claim calls unreproducible —
  **to the decimal**, plus `16.3%`, `24.7%`, `29.9%`, `31.7%`, `19.2%`, `24,907`,
  `19,792` and `5.1%` to within 0.1 point.
* **The claimant's instrument was the fault, not the row's table.** Their probe
  concatenates 32 campaign scripts into ONE command history. `command_history` is a
  session `var` (`main.gd:348`) that `main.gd:357`'s own comment calls *"Session-only
  and never written to `user://`"*. I reproduced their exact numbers (**31.3% saved /
  56.3% hit**) with the concatenated model, then reproduced the **published** numbers
  with the per-session one. The gap is their model, not the memo's.
* **"Breaks the IQ-8 table rule" → REFUTED on the rule's own text.** The rule
  (`docs/PLAYTESTING.md:248-253`, enforced by
  `tests/test_iq8_the_harness_tells_the_truth.py::TestTheTableRule`) is scoped to
  **playtest-driver** tables and asks per row for platform, engine commit,
  `PYTHONHASHSEED`, *"the flags beyond the script"* and *"the archived digest names"*,
  verified against `docs/audits/playtest_digests/`. A keystroke simulation has no
  script, no flags, no hash seed and no digest. The memo cites the rule in its
  **Playtest archives** line, about the `cx-*` digests — not about this table.
* **And the row DID commit the archive.** `docs/audits/cx_recon_2026_09_19/predictor.md`
  (436 lines) and `refute_predictor.md` are tracked at HEAD, added by the row's own
  `704df816` — the same commit as the memo. Both carry the figures **with their model
  spelled out**, which is why I re-derived four of them exactly without ever seeing a
  simulator. The rule asks for an archive, not for source code.

**What survives (P4, and narrower than filed):** the memo's header promises *"every
figure below cites one by name"* and **§5's table names no recon document**
(`cx_recon` appears once in the memo, at line 11). `docs/COMMAND_EXPERIENCE_SPEC.md`
names it **nowhere at all** while publishing the census model's table. And the two
**template-generator** arms (`29.6%`, `39.7%`) genuinely are not re-derivable — their
design is described (`predictor.md:262,355`) but the template corpus is not enumerated.

---

## 1. THE REPRODUCTION I RAN

Probes (mine, written for this verdict):
`…/scratchpad/cx_review/probes/refute_CXCLAIM11/{v1_four_models,v2_per_session,v3_policy_grid,v4_fixed_k_variants,v5_both_models}.py`

Corpus: every `tools/playtest_scripts/*.json` except `typed_road.json`
→ **1,416 commands, baseline 28,997 keystrokes** (both exact, as the claim concedes).

Semantics taken from the shipped client, read myself:

| seam | `main.gd` | modelled |
|---|---|---|
| `_add_to_history` | `:1121` | skip empty · skip if `== back()` · append · front-trim to `MAX_HISTORY` |
| `_history_pool` | `:1054` | `strip_edges()` then case-insensitive `begins_with`; blank line ⇒ whole history |
| `_history_previous` | `:1071` | first Up lands on `pool[-1]`, each further Up steps one older |
| `MAX_HISTORY` | `:360` | 50 (was 10) |
| history lifetime | `:348`, `:357` | **a plain `var`, "Session-only"** ⇒ one history per campaign |

### v1 — the claimant's model, reproduced exactly

Concatenating all 1,416 into one history, oracle prefix policy:

```
F oracle, window 50 :  31.3% saved   56.3% hit      <- the claim's own two numbers
```

Byte-identical to the figures in the claim. So the claim's probe is reproducible — and
it is reproducibly measuring the wrong thing.

### v2/v3/v5 — the shipped model: history resets per campaign

```
                    B unfilt   F oracle   F 1st-word   F type-3
window 10             14.8%      17.5%       10.3%       15.3%
window 25             16.3%      24.6%       13.9%       21.4%
window 50             16.3%      29.8%       16.3%       25.9%
window inf            16.3%      31.6%       17.8%       27.6%
hit rate, B @10       19.3%
chip ceiling (1 keystroke/command)                       95.1%
```

Against the committed refuter table (`refute_predictor.md:36-39`):

| cell | published | measured | delta |
|---|---:|---:|---|
| B @10 | **14.8%** | **14.8%** | **EXACT** |
| B @25 / @50 / @∞ | 16.3% ×3 | 16.3% ×3 | **EXACT** |
| F-oracle @10 | **17.5%** | **17.5%** | **EXACT** |
| F-oracle @25 | 24.7% | 24.6% | −0.1 |
| F-oracle @50 ("oracle 29.9") | 29.9% | 29.8% | −0.1 |
| F-oracle @∞ (the ⚠ note's 31.7) | 31.7% | 31.6% | −0.1 |
| hit rate, ships-today arm | 19.2% | 19.3% | +0.1 |

Two corrections to my own first cut, both of which the claimant also missed and which
together are the whole story:

1. **Per-session, not concatenated** — this alone turns the B column from 15.6/17.9/18.8
   into **14.8/16.3/16.3**, i.e. exact at all four windows.
2. **A true oracle minimises over every `k`, not the first `k` that improves.** The
   claimant's probe `break`s at the first improvement with the comment *"longer k only
   adds typed chars"* — which is false: a longer prefix can collapse a 25-press walk to
   one press. Fixing that moves F-oracle@10 from 16.4% to exactly **17.5%**.

### v5 — the census model reproduces too

The memo names both models in as many words (*"the census charged one keystroke per Up
press with no cap; the refuter capped the walk at the command's own length"*), so I ran
both:

| spec §5 / `predictor.md:20-25` | published | measured | delta |
|---|---:|---:|---|
| up-arrow, window 10 | 24,907 = 14.1% | 24,867 = **14.2%** | 40 keystrokes |
| *"a window of 50 saves 5.1%"* | 5.1% | **5.2%** | +0.1 |
| prefix-filtered, unbounded | 19,792 = 31.7% | 19,822 = **31.6%** | 30 keystrokes |
| chip ceiling | 1,416 = 95.1% | 1,416 = **95.1%** | **EXACT** |

### The one cell I could not pin: `21.4%`

The memo's shipped row (`21.4%`, also in `main.gd:356`, `SYSTEMS_REFERENCE.md:6006`,
`STATUS.md:74` and `tests/test_cx3_the_predictor.py:37`) is the refuter's *"type 3 then
reach up"* column. v4 swept the modelling choices:

```
type-3, charging wasted Up presses on a miss : 12.3 / 16.3 / 20.2 / 21.7
                          published          : 12.6 / 16.8 / 21.4 / 23.3
type-3, no waste charge                      : 15.3 / 21.4 / 25.9 / 27.6
```

So the **`12.6% → 21.4%` pair reproduces within 0.3 and 1.2 points** under a plainly
stated model, with the right shape and the right monotonicity. I did not land it to the
decimal; that is one free parameter I could not read off the record, not an
unreproducible figure.

**Score, honestly: 4 of the memo's 7 rows EXACT (28,997 · 95.1% · 14.8% · 17.5%), a 5th
within 1.2 points, and 2 genuinely not re-derivable** (the template arms). *"2 of 7"* is
wrong by measurement.

---

## 2. THE RULE CHARGE

`docs/PLAYTESTING.md:248-253`, verbatim:

> **The table rule (binding since IQ-8).** A measured table in this page, a memo or a
> spec carries, per row: **platform** (OS + CPython version), **engine commit** (+
> dirty), **`PYTHONHASHSEED`**, **the flags beyond the script**, and **the archived
> digest names**. A figure with no archive is **UNCITABLE**.

Every column is a playtest-driver column, and the enforcement
(`TestTheTableRule::test_every_row_names_an_existing_archive_or_says_uncitable`) walks
`docs/audits/playtest_digests/<name>/{meta.json,digest.md}` and cross-checks each row's
hash seed against the archive's own. A keystroke simulation over a static corpus has no
script, no flags, no seed and no digest — the rule cannot be applied to it as written.

The memo cites the rule **where it applies**, in the Playtest-archives line:

> `cx-before-*`, `cx-after-*` and `cx-typed-road` (the IQ-8 table rule: a figure with no
> archive is uncitable).

And the row shipped an archive for the predictor figures anyway:

```
$ git log --oneline --diff-filter=A -- docs/audits/cx_recon_2026_09_19/predictor.md \
                                        docs/audits/cx_recon_2026_09_19/refute_predictor.md
704df816 docs(cx): row CX — the memo, the records, and the arm that can see the typed road
$ git ls-files docs/audits/cx_recon_2026_09_19/predictor.md   # tracked at HEAD
```

That archive was sufficient: I re-derived four figures exactly from it without the
simulator. **"The simulator is not committed" is TRUE** (`git ls-files` finds no
`p5_sim.py` / `p6_sim2.py` / `r2_sim.py` / `r7_ghost.py`) — but the rule asks for an
archive, and one exists.

*Incidental:* the claim's *"CX-3's diff is main.gd + a test + a screenshot scene"*
under-counts it. `2c3535b5` also touched `backend/ai/llm_client.py`,
`backend/commands/meta_executor.py`, `docs/COMMAND_EXPERIENCE_SPEC.md`,
`tools/_sweep_cx.json` and ten PNGs.

---

## 3. SEVERITY · REACHABILITY · ATTRIBUTION

* **Severity — P4 holds, for the residue only.** The filed defect (unreproducible
  figures, a broken rule) is refuted. What is left is a missing citation line.
* **Player-reachable: NO.** Documentation and a source comment. Nothing renders through
  the client; `main.gd`'s redirect lists are irrelevant here.
* **Shipped by row CX: YES** for the residue — the memo (`704df816`) and the `main.gd`
  comment (`2c3535b5`) are both row-CX commits.

---

## 4. THE FIX — AND THE ONE THE CLAIM WOULD HAVE SHIPPED

⛔ **Do not mark `14.8` / `17.5` / `21.4` UNCITABLE.** They reproduce. And they are not
decoration: `main.gd:354-358` is the recorded justification for `MAX_HISTORY = 50`,
which `tests/test_cx3_the_predictor.py:316` pins in source
(`assert "const MAX_HISTORY = 50" in source`), and whose stated rule is *"Never change
one without the other"* (`SYSTEMS_REFERENCE.md:6006`). Retracting the numbers leaves a
pinned constant with its reason deleted and the CX-3 test's own docstring (`:36-38`,
which quotes `16.3%` / `14.8%` and `12.6% → 21.4%`) dangling on figures the docs now
disown. That is a strictly worse record than the one the claim attacks.

**Build instead, in one edit:**

1. `CX_THE_HAND_ON_THE_KEYBOARD…` §5 and `COMMAND_EXPERIENCE_SPEC.md` §5 each name
   their archive — `cx_recon_2026_09_19/predictor.md` (the census table, arms A/B/F/D/G/E)
   and `refute_predictor.md:33-40` (the window × policy grid) — which is all the memo's
   own header already promises.
2. Add one line to the memo's §5 recording that the model is **per-campaign history**
   (the shipped `command_history` is session-scoped), and that arms **D and G depend on a
   template generator whose corpus is not archived** — so those two, and only those two,
   are uncitable in the IQ-8 sense.
3. Optional and cheap: the spec's §5 table is the **census** model (`14.1%` / `31.7%`)
   sitting beside a memo that calls `31.7%` refuted. Label it, or replace it with the
   refuter's grid.

---

## 5. THE METHOD NOTE THIS ONE EARNS

The claim's own probe is honest, runnable and reproduces its stated output — and it is
wrong, because it held one thing constant that the shipped code does not: **it gave a
player one history across thirty-two campaigns.** The tell was available before any
argument: the concatenated model reproduced *none* of eight published cells, the
per-session model reproduced *five exactly and three within 0.1*. When a re-derivation
misses a whole table by a constant, suspect the harness's world model before the
table — and try the unit the shipped `var` actually lives in.
