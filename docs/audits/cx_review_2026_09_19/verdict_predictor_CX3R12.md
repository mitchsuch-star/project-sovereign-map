# VERDICT: CX3-R12 — CONFIRMED (at INFO), but its rationale would ship a P2

**Finding:** `_add_verb_or_target`'s `prefix` parameter is never read.
**Filed severity:** INFO · player-reachable `false` · shipped by row CX `true`
**My verdict:** **CONFIRMED.** The claim is exactly true, INFO is the right
severity, and both flags are right. But the finding's own rationale — *"the
signature implies the slot logic consults the whole typed line, and it does
not"* — points at a fix I measured to be a **P2 regression**, and its
*"Harmless"* is one measured case short.

Tree: `f52df77f`, clean. Probes in `probes/`. Nothing under `backend/`,
`godot-client/`, `tests/`, `docs/` or `tools/` was written; no git mutation.
`tools/godot_parse_report.json` is a tracked file, so I did **not** run the
committed harness — I built an isolated throwaway project in the scratchpad
instead and ran the shipped source there.

---

## 1. It reproduces, exactly as stated

`probes/r12_a_bodyscan.py` slices each function out of `main.gd` by
indentation and counts identifier occurrences in the **body only**, so a
mention inside a different function cannot satisfy the check:

```
=== _add_verb_or_target  (lines 7040-7079) ===
signature params: ['marshal', 'rest', 'prefix', 'out', 'seen']
  marshal   body occurrences: 3
  rest      body occurrences: 3
  prefix    body occurrences: 0        <====
  out       body occurrences: 4
  seen      body occurrences: 4

=== _add_addressee_or_bare (lines 7023-7039) ===
  prefix    body occurrences: 2
      L7026: if _starts_with_ci(line, prefix) and not seen.has(line.to_lower()):
      L7033: if _starts_with_ci(bare, prefix) and not seen.has(bare.to_lower()):
```

The sibling reads `prefix` for exactly one purpose: **every line it emits must
be a completion of what the player typed.** `_add_verb_or_target` takes the
same parameter and never applies it. That asymmetry is real, and it is what
makes the finding worth having.

## 2. Severity INFO is right — and better supported than the finding knew

The finding calls it harmless without saying whether the engine complains. It
does not. I mirrored the signature in an isolated Godot 4.4.1 project
(`probes/warnproj/probe.gd`, an unused param beside a `_`-prefixed control):

```
EXIT=0
Godot Engine v4.4.1.stable.official.49a5bc7b6
PROBE_RAN out=["Ney, attack "]
----- STDERR -----            (empty)
```

Then the **verbatim shipped function** (sliced out of `main.gd`, not retyped)
in the same project: `EXIT=0`, clean stdout, empty stderr, no
`UNUSED_PARAMETER`. `project.godot` sets no warning keys, and
`tools/godot_parse_check.gd` escalates only `parse_ok`/`load_ok`, so the parse
harness cannot see it either. No log noise, no harness impact, nothing for the
XR-1 `SCRIPT ERROR` grep.

**It reds no pin.** `grep -rn "_add_verb_or_target" tests/ tools/ docs/`
returns nothing — no test, tool or doc anywhere names the function.
`tests/test_cx3_the_predictor.py` passes 17/17 at HEAD and every one of its
source assertions is about other strings (`'var line := str(name) + ", "'`,
the `KEY_TAB` line, `layout.add_child`, and so on).

## 3. Player-reachable `false` — confirmed by experiment, not by argument

I built the delete in the engine (`probes/warnproj/deleted.gd`: parameter gone
from the signature **and** the call site) and diffed it against the shipped
source over 1,617 typed lines on the real 1805 payload:

```
A) DELETE the parameter : 0 of 1617 typed lines change -> BYTE-IDENTICAL
```

A parameter no reader reads has no player-visible behaviour. Confirmed.

## 4. Shipped by row CX `true` — confirmed

```
b4a27a15^ : _add_verb_or_target / _build_completions / COMPLETIONS_ACTIVE — NONE
b4a27a15  : defs=0
5fc3d5c8  : defs=0
2c3535b5  : defs=1   func _add_verb_or_target(marshal: String, rest: String, prefix: String,
```

Born in CX-3 with the signature it has today. Never wired, at any point.

---

## 5. THE CORRECTION THAT MATTERS: the rationale invites a P2

*"the signature implies the slot logic consults the whole typed line, and it
does not"* reads as an invitation to make it consult. I built exactly that
(`probes/warnproj/wired.gd` — `prefix` applied **the way the sibling applies
it**, at both emission points) and ran it in the engine on the shipped payload:

```
B) WIRE the parameter up : 470 unchanged, 0 shrank,
                           1016 of the 1486 lines that HAVE offers go SILENT
```

None shrink. They go dark. And the loss is surgical:

```
canonical-spacing lines in corpus : 396
   changed by wiring              : 0
   silenced by wiring             : 0
=> the loss is EXACTLY the non-canonical spacings; canonical typing is untouched.

by cause:  no space after the comma   496
           a space before the comma   264
           a double space after it    256
```

```
typed 'Ney,attack '      shipped offers 4   wired offers 0
typed 'Ney,march to S'   shipped offers 5   wired offers 0
typed ' Ney, attack '    shipped offers 4   wired offers 0
typed 'Ney , attack '    shipped offers 4   wired offers 0
typed 'Ney, attack '     shipped offers 4   wired offers 4   (control)
```

**And these are sentences the shipped game reads.** Through the real parser
(`probes/r12_e_named_cases.py`): `Ney,attack Mack` → `[OK] Parsed: attack`;
`Ney,march to Swabia` → `[OK] Parsed: move`; `Ney , attack Mack` and
`ney, attack mack` likewise. So the un-wired branch is not a hole — it is
**normalising**: it repairs the player's spacing into the canonical form, and
that is the one thing a prefix-filter can never do, because the repaired line
is not a completion of the broken one.

Measured over 1,592 typed lines (`probes/r12_c_isitharmless.py`), the shipped
branch emits 2,360 candidates that are not completions of the typed text —
**every one differing only in whitespace or case, and zero losing a
non-whitespace character the player typed.** The control (the branch that
*does* read `prefix`) emits 0 such candidates over 214 lines.

Caveat I owe on my own number: my corpus deliberately over-samples separator
variants, so **1,016 is corpus-dependent**. The *classes* are the finding, not
the proportion.

**So the safe fix is to delete the parameter (or rename it `_prefix`), never
to wire it.** If a future reader takes the rationale at face value, the
sentence they break is `Ney,attack Mack` — typed without the space after the
comma — and the completer goes silent on it.

## 6. "Harmless" is one measured case short

Because `prefix` is unapplied while `seen` keys on the **emitted** string, a
history entry and its canonical twin both render. Reproduced in the engine on
the shipped source (`probes/warnproj/dupe.gd`):

```
TYPED Ney,attack M     -> ["Ney,attack Mack", "Ney, attack Mack"]
TYPED Ney,attack Mack  -> ["Ney,attack Mack", "Ney, attack Mack"]
TYPED Ney, attack M    -> ["Ney, attack Mack"]                     (canonical: one row)
```

Two rows, the same order, one space apart. **Reachable through the shipped
client:** `_execute_command` stores `command_input.text.strip_edges()` —
leading/trailing only, inner spacing preserved (`main.gd:1615`, `:1650`) — and
`_redirect_diplomatic_command` covers only diplomatic verb heads, so `attack`
reaches the backend and enters history verbatim.

Cosmetic, **P4**, and it does **not** raise CX3-R12: its root is the dedupe
key, not the dead parameter. Wiring `prefix` would remove this duplicate and
silence 1,016 lines to do it; a normalised `seen` key removes it for free.
Worth filing separately if the reviewer wants it.

## 7. The safe fix has one cost worth naming

Rename to `_prefix` or delete it — engine-proven byte-identical. But
`tests/test_godot_parse_harness.py::test_godot_parse_report_is_not_stale_relative_to_settlement_godot_sources`
compares the committed report's timestamp against `main.gd`'s **filesystem
mtime**, so even a one-character rename reds that pin until the Godot harness
is re-run and `tools/godot_parse_report.json` re-committed. For an INFO with no
runtime effect, that argues for folding it into the next `main.gd`-touching
slice rather than a commit of its own.

## 8. Context the finding lacks: it is the only removable one

Corrected census over all 54 client `.gd` (`probes/r12_f_census.py`) —
parameters declared without the leading-underscore convention and never read:

```
scripts/diplomacy_wizard.gd:188  _on_http_completed(… result …)      PRE-EXISTING
scripts/diplomacy_wizard.gd:188  _on_http_completed(… headers …)     PRE-EXISTING
scripts/main.gd:6152             _on_mailbox_item_selected(… item_type …)  PRE-EXISTING
scripts/main.gd:7040             _add_verb_or_target(… prefix …)     SHIPPED BY ROW CX
```

The three pre-existing ones are **signal-callback arity** (`request_completed`,
`item_selected`) — GDScript requires them; they cannot be removed. Row CX
shipped one dead parameter, and it is the only one in the client that is both
unused and removable.

---

## A note on my own method

My first census reported **21** hits. It was **wrong**, and I record it as
wrong rather than quietly correcting it: its comment-stripper was a naive
`re.sub(r"#.*$", "", line)`, which ate the `#` inside BBCode colour literals
(`"[color=#" + color + "]" + text + ...`) and so reported `bbcode_color(text)`,
`bb_icon(path, size)` and five more as having unused parameters they plainly
use. Seven of the 21 were that artefact. Replaced with a string-state-aware
stripper: 4.

That is this row's own lesson one level up — *a rule built by stripping what
you recognise is only as safe as the list it strips* — and it is the same shape
as the trap in §5: both are a transformation applied without checking what it
destroys downstream.

**Port fidelity.** Claims 5, 6 and the byte-identity in 3 rest on a Python port
of the completer. I validated it against the engine rather than asserting it:
the verbatim shipped source (`_build_completions`, `_add_addressee_or_bare`,
`_add_verb_or_target`, `_starts_with_ci`, `_own_marshal_names`,
`_visible_enemy_names`, `_region_names`, `Utils.humanize_entity_name`, both
`const` tables) sliced out of `main.gd`/`utils.gd` and run in Godot 4.4.1
against the real 1805 payload:

```
typed lines cross-checked ENGINE vs PORT : 1617
disagreements                            : 0
```
