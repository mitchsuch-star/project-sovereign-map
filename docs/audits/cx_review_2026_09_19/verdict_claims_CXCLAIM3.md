# VERDICT:CX-CLAIM-3 — **CONFIRMED**, wider than filed, and its magnitude clause is wrong

**Tree:** master `727cf88a`, clean. **Probes:** `probes/claim3/p1..p4`
(committed under the scratchpad, not the repo). **Parser: mock throughout, no
key, no network — every gate decision below is computed by wrapping the REAL
`LLMClient._should_fallback_to_llm` with `provider_name`/`api_key` forced to a
live shape, recording its answer, and returning `False` so no provider is ever
consulted.**

---

## 1. It reproduces — exactly, and at the recon's own corpus revision

I did not use the claim's probe. I drove the real `CommandParser.parse` over the
whole golden corpus on both worlds (`parser_eval.build_world` /
`build_llm_game_state`, the production call shape) and counted the gate's real
answers.

At **HEAD** (`p1_gate_census.py`, corpus 449 entries):

```
GATE EVALUATIONS: 694   escalated 45 = 6.5%
UNIQUE escalating corpus entries: 29
  of which expected.success is False: 25 = 86.2%
  DECOMPOSITION OF THE 25:  mock_only 11   live_only 2   neither 12
```

At the revision the recon actually ran against — `b4a27a15^` = `f7008582`,
corpus 447 entries, production code at HEAD (`p4_prerow_corpus.py`):

```
gate evaluations : 692      (memo publishes 692)   ✓
escalated        : 45 = 6.5% (memo publishes 45 = 6.5%) ✓
unique entries   : 29       (memo publishes 29)    ✓
expected False   : 25/29 = 86.2% (memo publishes 25/29 = 86%) ✓
   mock_only=11  live_only=2
```

The eleven `mock_only` ids match the refuter's list member for member.
`backend/ai/parser_eval.py:245` does skip every `mock_only` row when
`use_real_llm` (`skipped_mock_only`), so the refuter's mechanism is real.

**And the memo does not carry it.** `grep` over the whole `docs/` tree outside
`cx_recon_2026_09_19/` finds no mention of the narrowing:
`CX_THE_HAND_ON_THE_KEYBOARD_2026_09_19.md:253` publishes `25 / 29 = 86%`
unmarked, the prose at `:264` repeats it, `COMMAND_EXPERIENCE_SPEC.md:516`/`:528`
mirrors both, and `STATUS.md:36-38` carries it into the routing authority. Memo
§0's promise ("carried here rather than quietly dropped — they are marked ⚠") is
broken for this cell. **Row CX introduced all three surfaces**: the memo file's
only `--diff-filter=A` commit is `704df816`, and the STATUS block is in the same
commit.

So: **CONFIRMED.** P3 is right, and `player_reachable: false` is right — the
figures are docs-only (the sole `86%` hit in product code, `main.gd:6991`, is the
predictor's unrelated history-hit comment), and **no test pins either number**,
so correcting them reds nothing.

---

## 2. ⚠ But the claim named the WEAKER of three members — the row dropped two more

The claim calls this *"the one narrowing that bears directly on the ruling it
supports."* That is false. I checked the memo's §4 ruling table cell by cell
against `refute_llmvalue.md`'s scoreboard. **Three published cells carry an
uncarried refuter narrowing, and the claim's is the softest of them:**

| memo cell | refuter | carried? |
|---|---|---|
| `25 / 29 = 86%` | CX-LLM-2 NARROWED — 11 are `mock_only` | **no** ← the claim |
| `> 0.90 → 50.7% of commands escalate` | CX-LLM-5 — *"0.91 → **46.2%** (not 50.7%)"* | **no** |
| *"Its dollar figure is ~4× high"* | CX-LLM-4 — the census scaled from `$0.003` while `backend/ai/providers.py:471` carries a measured **`$0.0065`**, so ~4× is itself ~2× flattering | **no** |

The 50.7% cell is the hard one, because it is not a contested *reading* — it is a
**false number**, and I measured it myself (`p3_gate_curve.py`, sweeping only the
threshold constant through the same real predicate):

```
gate   escalated / evaluations   rate      (HEAD corpus)
0.70      45 / 694        6.5%
0.85     109 / 694       15.7%
0.91     320 / 694       46.1%
```

and at the recon's own corpus revision (`p4`): **0.85 → 15.8%, 0.91 → 46.2%** —
the refuter's corrected figures to the digit. The memo, the spec and STATUS.md
all publish **50.7%**, which is the census's pre-refutation number.

**The 86% sentence is true-but-incomplete; the 50.7% sentence is simply false.**
The claim filed the incomplete one and missed the false one, in the same table,
four rows down.

---

## 3. ⚠ And the narrowing it quotes is itself over-stated — do not ship it verbatim

The claim endorses the refuter's *"supportable for at most 14 of the 29, not
25 … 44% of the evidence for the 86% is mis-read."* That arithmetic drops the
eleven `mock_only` rows from the **numerator** while keeping them in the
**denominator**. But the refuter's own mechanism is that the live evaluator
**SKIPS the whole row** — so it leaves the denominator too. Measured
(`p2_decompose.py`; all eleven `mock_only` escalating rows are inside the refusal
set, so the live-evaluated escalating population is 29 − 11 = 18):

```
(A) memo, as published           : 25/29 = 86.2%   = 8.2x the corpus base rate
(B) refuter's implied arithmetic : 14/29 = 48.3%   = 4.6x
(C) live-evaluator semantics     : 14/18 = 77.8%   = 7.4x   <-- the honest one
corpus base rate of refusal rows : 47/449 = 10.5%
```

Reading the eleven rows' own notes sharpens it further: **two of them
(`ney-cover-the-retreat`, `ney-fix-bayonets`) have `live_only` twins that are
already inside the 14**, so excluding them loses no refusal contract at all;
three (`break-through-enemy-lines`, `money-for-the-troops`,
`cr5-deleg-literal-live-retired-note`) say in their own notes that the live model
legitimately resolves them — those are the rows the refuter is right about.

**So the correction is 86.2% → 77.8%, an 8.4-point move, and the ruling is
untouched at every framing** (7.4× base rate; even the refuter's own 48.3% is
4.6×). The refuter's second point — *"on these rows the model is the danger"* —
**strengthens** the memo's "re-aim it" decision rather than threatening it, and
the memo never made the *"escalation's job is to NOT help"* claim the refuter was
attacking (it says the opposite: *"Not (v) drop it: two rescue classes are
real"*).

### The regression the obvious fix would ship

A builder who "carries the narrowing" by pasting the refuter's sentence publishes
**48%**, a new wrong number produced by the exact error the claim is complaining
about. No pin reds — nothing in `tests/` asserts either figure — so the suite
would stay green while the memo acquired a fresh false statistic. The fix must be
**77.8% (14/18)**, stated as the live-evaluator framing, with the corpus-file
framing kept beside it.

---

## 4. One thing the claim gets right that is worth keeping

Memo §0 promises *"eight"* refuter overturns carried. Counting per-finding
verdict headers across all twelve refuters gives **58 NARROWED + 19 REFUTED =
77**. Most are about findings the memo never cites, so dropping them is not a
defect — but "eight" is a count of what the memo chose to carry, not of what the
refuters found, and §0 reads as though it were the latter.

---

## 5. Disposition

**CONFIRMED · P3 · not player-reachable · shipped by row CX (`704df816`).**

Corrected fix shape, docs-only, one pass over three files:

1. `CX_THE_HAND_ON_THE_KEYBOARD_2026_09_19.md:253` + `:264`,
   `COMMAND_EXPERIENCE_SPEC.md:516` + `:528` — mark ⚠ and state both framings:
   *"25/29 = 86% of the corpus rows; **14/18 = 78%** of the rows a live run
   actually evaluates, the other eleven being `mock_only` and skipped
   (`parser_eval.py:245`). 7.4× the corpus base rate of 10.5% either way."*
   **Do not publish 14/29 = 48%.**
2. Same files + `STATUS.md:38` — `50.7%` → **`46.2%`** (measured; `p3`/`p4`).
3. `memo:296` — the *"~4× high"* cost clause, against the measured `$0.0065` at
   `backend/ai/providers.py:471`.
4. §0's *"eight"* — say "eight of the ones this memo relies on", or count them.
