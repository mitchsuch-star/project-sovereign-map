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
* IQ1-2's own `net_residual` is likewise **jsonl-only**.
  ⚠ **Review-round correction:** `turn_spend` is NOT jsonl-only — it prints a
  `- SPENT …g` line into the markdown as well. The jsonl carries the machine
  figure beside it; the markdown is what a reader sees.
* ⚠ **And the mechanism is unchanged:** `--archive` still copies `digest.md`
  and `meta.json` only. This pair was copied by hand. So the NEXT IQ-1 arm
  loses `net_residual` and the per-nation purses again unless it is archived
  the same way — **IQ1-5 owns teaching `--archive` to carry the jsonl**, and
  that is a named landing, not a wish.

So this pair — the **control** (`commanded_full40`) and the **spender**
(`commanded_spender40`), same seed, same `--diplomacy accept`, differing by the
purchase order and nothing else — carries its jsonl so the numbers in
`docs/IMPROVEMENT_QUEUE_SPEC.md` §0.5 can be re-derived from the archive
instead of from a re-run.

⚠ The **ambient** half of row IQ-1's completion definition still has **no
post-SW-0 archived arm**. IQ1-5 must take one.
