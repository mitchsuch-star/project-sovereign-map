# VERDICT: CX-CLAIM-5 — **CONFIRMED AND WIDENED** (severity HELD at P3)

*Refuter pass, read-only, September 19 2026. Tree at `f52df77f` (clean) — note the
task text says `727cf88a`; HEAD is one docs commit above it (`f52df77f`, "correct the
row's own headline figure"), which touches no `.gd`, so nothing below is affected.
Pre-CX control = `f7008582`. Nothing under `backend/`, `godot-client/`, `tests/`,
`docs/` or `tools/` was modified; no git-mutating command was run. Probes under
`…/scratchpad/cx_review/probes/v5_*`.*

---

## 0. THE VERDICT IN ONE LINE

The claim is **right about all three citations and wrong about the size of its own
finding by a factor of five**. It reports "3 wrong of 14 ≈ 21%". Measured: **every
single `main.gd` citation row CX added to live prose is stale — 6 of 6, 100%** — and
across everything the row committed, **180 of 189**. The three it names are not three
mistakes; they are three samples of one total failure with one mechanical cause.

---

## 1. DOES IT REPRODUCE? — YES, ALL THREE, BY MY OWN READ

I navigated to each cited line at HEAD rather than trusting the claim's transcript.

| cited | prose says it is | what is at that line at HEAD | real site |
|---|---|---|---|
| `main.gd:5563-5575` | the `MOVE_TO → "march to"` keyword map | `if response.has("redemption_event"):` | **5652-5657**, `MOVE_TO` at **5654** |
| `main.gd:6399-6409` | `_on_region_panel_command` → `api_client.send_command` | tail of `_on_vassal_command_result` (opens 6394) + head of `_on_naval_command` (6403) | **6485** func, send at **6495** |
| `main.gd:1778` | the client intercepting `vassalize` | `"abrogate",` — a treaty-break keyword | **1864**, inside `DIPLO_FAMILY_KEYWORDS` (declared 1751) |

The claim's "correct and verified" set also holds under my own read:
`region_panel.gd:136-140` is exactly the `do:` branch (`region_command.emit(command)`
at 140); `clarification.py:311` is `"command": f"{marshal.name}, move to {name}",`;
`proposal_confirm_popup.gd:129` is `"war_purpose_selection":`.

**⚠ But the important half of the reproduction is the one the claim did not run: the
pre-CX control.** All three were **EXACT** against `f7008582`:

```
pre-CX 1778: "vassalize",                                         <- the cited keyword
pre-CX 5563: add_output(... "> " + marshal_name + ", target " ...)  <- opens the reissue
pre-CX 5566-5571: keyword_map { PURSUE, MOVE_TO: "march to", SUPPORT, HOLD }
pre-CX 5575: api_client.send_command(clarified_command, ...)      <- closes the range
pre-CX 6399: func _on_region_panel_command(command: String):      <- opens the func
pre-CX 6409: api_client.send_command(command, _on_region_panel_command_result)
```

So these were never sloppy citations. They were measured correctly and then
**invalidated by the row itself**.

---

## 2. ONE CAUSE, MEASURED

`CX-3` (`2c3535b5`) is the only commit in the row that touches `main.gd`:
**+413 / −12, 6,740 → 7,141 lines**, with eight hunks above line 1,778 summing to
**+86**. Every cited site moved by exactly that:

```
1778 -> 1864   delta 86     (vassalize)
5568 -> 5654   delta 86     (MOVE_TO)
6399 -> 6485   delta 86     (_on_region_panel_command)
6409 -> 6495   delta 86     (its send_command)
```

First line whose content differs between the two trees: **`main.gd:350`**. Everything
cited below that line, in every document the row shipped, was broken at once.

This is also why the claim's "correct" set is correct: `region_panel.gd`,
`clarification.py` and `proposal_confirm_popup.gd` were **not touched by row CX at
all**. The split is not "some citations were checked and some were not" — it is
"CX-3 edited one file and nothing that cited that file was re-checked."

---

## 3. THE WIDENING — THE CLAIM UNDERSTATES ITS OWN FINDING ~5×

`probes/v5_citation_census.py` and `probes/v5_blast_radius.py` count **only citations
row CX itself added** (diffed `f7008582..HEAD`, added lines only), then compare the
pre-CX line against the HEAD line.

```
LIVE PROSE     (spec + memo + BUG_FIXES rows the row wrote)
               6 main.gd citations, 6 stale  =  100.0%

RECON ARCHIVE  (docs/audits/cx_recon_2026_09_19/*, introduced by 704df816)
             183 main.gd citations, 174 stale =  95.1%
             click_road.md   76 cited, 75 stale
             predictor.md    25 cited, 23 stale
             two_roads.md    12 cited, 12 stale
             refute_click.md 11 cited, 10 stale   … (18 files)
```

Three corrections to the claim, each measured:

**(a) The rate is 100%, not 21%.** Of the eleven citations row CX added to live prose
and code, six cite `main.gd` and **all six are stale**; the other five cite untouched
files and are all correct. The claim's framing ("3 of 14") makes this read like a
sampling error. It is total.

**(b) The denominator "14" is inflated with citations that are not row CX's.** The
claim sets aside "two `main.py:NNNN` citations inside `dialogue_routing.py`" as
uncheckable and counts them. `dialogue_routing.py` was last written by **IQ-7
(`954efadc`)** and appears nowhere in `git diff --name-only f7008582 HEAD` — those
citations are **pre-existing and not this row's to answer for**.

**(c) Three distinct citations, but six live occurrences.** Each wrong citation is
duplicated: spec:52 + memo:55, spec:71 + memo:74, and `main.gd:1778` in memo:367 **and
in `docs/BUG_FIXES.md:12897`**.

**(d) "Stale" is the wrong word for two of the three.** `main.gd:5563-5575` and
`main.gd:1778` both first appear at **`704df816`** — *after* CX-3 had already shifted
the file. They were **wrong on the day they were committed**, copied out of a recon
measured against the older tree. Only `main.gd:6399-6409` was ever true in-tree: it
entered at **CX-1 (`b4a27a15`)**, correct, and CX-3 broke it — after which the memo
re-asserted it unchanged. This is not drift. It is a row citing line numbers in a file
it had itself edited, from notes taken before the edit.

---

## 4. WHAT SURVIVES AGAINST THE CLAIM — SEVERITY IS RIGHT, NOT OVER-STATED

I tried to argue this down to P4 and could not, and I tried to argue it up to P2 and
could not.

**Not P4.** The reflex defence is the project's own standing rule — CLAUDE.md:
*"Measured: ~80% of rows carry a stale line number — navigate by the symbol a row
names, never by its line."* That rule is about **audit rows drifting over months**.
It does not cover a row breaking its own citations inside six commits, two of them
false at commit time. And one instance is not inert: `docs/BUG_FIXES.md:12897` is
**CX-X3, an OPEN P2 row routed to a different owner** — *"the vassal/Cabinet owner
(`VASSAL_DEEPENING_SPEC`). Done when the backend gates it independently of the
client."* That owner's first navigation lands on `"abrogate",`, and the gate they are
being asked to reason about is 86 lines further down.

**Not P2 either.** I checked the substance behind each stale pointer and **every prose
claim is TRUE at HEAD**: the keyword map exists and does map `MOVE_TO → "march to"`
(5652-5657); the region-panel chip really is sent through `api_client.send_command`
(6495); `"vassalize"` really is in `DIPLO_FAMILY_KEYWORDS`, so the client really does
intercept it. Nobody is misled about a fact — only about where to look. Nothing here
is reachable by a player, and no behaviour changes.

**P3, held.**

---

## 5. PLAYER-REACHABLE? — NO

Documentation only. Nothing in `main.gd`, the backend or any test reads these strings;
`grep` over `tests/` for `5563|6399|1778|5654|6485|1864` returns nothing. Not a typed
road, not a chip, not a popup.

## 6. SHIPPED BY ROW CX? — YES, UNAMBIGUOUSLY

`main.gd` was untouched between IQ-7 and this row; `CX-3` is the sole editor. The
pre-CX control reproduces all three citations exactly. `git log -S` puts the two
false-at-birth citations at `704df816` and the broken-then-re-asserted one at
`b4a27a15`. Both commits are row CX. Not pre-existing.

---

## 7. WOULD THE FIX SHIP A REGRESSION? — NO PIN, BUT THE FIX IS THE WEAKER OF TWO

**No regression risk.** No test asserts any of these numbers, and the three CX test
files mention docs only in their module docstrings — a docs-only edit cannot red a CX
pin. Naming a pin it would break: there isn't one.

**But re-numbering is a treadmill and will fail the same way.** Writing 5654 / 6485 /
1864 restores the citations until the next edit above `main.gd:350`, which is exactly
how they broke this time — CX-3 inserted at 347, 643, 847, 883, 926, 933, 1002 and
1051, and everything below moved. The row's own six commits demonstrate the half-life.

**The durable fix is the one the repo already ruled on:** cite the **symbol**, not the
line — `_on_clarification_choice_made()`'s `keyword_map`, `_on_region_panel_command`,
`DIPLO_FAMILY_KEYWORDS`. All three are unique in the file (`grep -c` gives 1 each), so
a symbol citation is both precise and edit-proof, and it is what CLAUDE.md's standing
rule tells the *reader* to do anyway — the documents should meet the reader there.
For the 174 archive rows, no re-numbering is warranted at all: an audit archive is a
dated snapshot, and one header line (*"line numbers measured against `f7008582`"*) on
`docs/audits/cx_recon_2026_09_19/` makes 183 citations honest for free.

---

## 8. REPRODUCTION COMMANDS

```
git show f7008582:godot-client/project-sovereign/scripts/main.gd | sed -n '5560,5580p;6395,6415p;1774,1782p'
sed -n '5560,5580p;6395,6415p;1774,1782p'  godot-client/project-sovereign/scripts/main.gd
git show --stat 2c3535b5 -- godot-client/project-sovereign/scripts/main.gd
git log --oneline -S "main.gd:5563-5575" --all      # -> 704df816 only  (after CX-3)
git log --oneline -S "main.gd:6399-6409" --all      # -> 704df816, b4a27a15
.venv/Scripts/python.exe …/probes/v5_citation_census.py   # 11 row-CX citations
.venv/Scripts/python.exe …/probes/v5_blast_radius.py      # 6/6 live, 174/183 archive
```
