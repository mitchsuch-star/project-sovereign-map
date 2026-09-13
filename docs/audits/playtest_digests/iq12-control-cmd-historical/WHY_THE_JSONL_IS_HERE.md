# Why these two arms carry their `digest.jsonl`

`tools/playtest_driver.py --archive` copies `digest.md` and `meta.json` only,
never `digest.jsonl`. That is normally right — the markdown is the readable
record. It is **wrong for row IQ-1**, and IQ1-2 records the reason rather than
leaving it to be re-discovered:

* SW-0's per-nation `purses` — the only instrument that makes any **GR5** claim
  about the economy falsifiable from an archive — goes to the **jsonl only**,
  by design, because it is omniscient data and the markdown is written to read
  like a player's eye view. So every GR5 economy claim on an archived arm was
  unfalsifiable.
* IQ1-2's own `net_residual` and the `turn_spend` rows are likewise jsonl-only.

So this pair — the **control** (`commanded_full40`) and the **spender**
(`commanded_spender40`), same seed, same `--diplomacy accept`, differing by the
purchase order and nothing else — carries its jsonl so the numbers in
`docs/IMPROVEMENT_QUEUE_SPEC.md` §0.5 can be re-derived from the archive
instead of from a re-run.

⚠ The **ambient** half of row IQ-1's completion definition still has **no
post-SW-0 archived arm**. IQ1-5 must take one.
