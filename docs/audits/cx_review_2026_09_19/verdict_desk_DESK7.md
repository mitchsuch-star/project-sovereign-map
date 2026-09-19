# VERDICT: DESK-7 — CONFIRMED, and under-stated in (a); NARROWED in (b)

Default verdict was REFUTED. Both halves reproduced under my own probes, so
the row survives — but neither half is quite the defect it was filed as.

* **(a) is a P2, not a P3**, and the filed reproduction picked the one case
  where the omission costs nothing.
* **(b) reproduces numerically but its framing is wrong**: the banner carries
  the desk's own three figures. It is a POINTER mismatch, not a contradiction
  "by construction".
* **The filed fix shape is safe but incomplete** — it closes one direction of
  a two-directional mismatch.

Probes: `…/cx_review/probes/` (`dh.py`, `r01`…`r10`, `fixplug.py`). Every
board driven through `POST /command`, mock-pinned, network-guarded. Client
reachability decided by re-implementing `main.gd::_redirect_diplomatic_command`
from the `.gd` source, not assumed.

⚠ **A hygiene note on my own first probe**: `CommandParser`'s first positional
arg is `use_real_llm`, **not** the world — `CommandParser(world)` turns the
live API on (it printed `provider=ANTHROPIC, key_source=inhouse`). Caught
before any escalation; every probe from `dh.py` on asserts
`parser.llm.provider_name == "mock"` and installs the IQ-9 network guard.

---

## PART (a) — CONFIRMED, and worse than filed

### The mechanism is exactly as filed

`question_desk._answer_winning` (line 617) builds its foe list from
`world.marshals.values()`:

```python
foes = sorted({m.nation for m in world.marshals.values()
               if m.nation != player and world.is_at_war(player, m.nation)})
```

A belligerent with no marshal in `world.marshals` is silently absent.

### Their stated control reproduces exactly (my probe `r08`)

Shipped 1805 boot, Britain's marshals removed through the ONE removal seam
(`destroy_marshal`):

```
shipped desk names : ['Austria', 'Russia']
banner shows       : ['Austria', 'Britain', 'Russia']
```

Their `t20` reproduction also reproduces: at-war roster is
`['Austria','Britain','Russia','Switzerland']`, the desk's scan is the first
three, and `build_active_wars` **does** carry a Switzerland row. Switzerland
holds `Bern` and has never had a marshal.

### But the filed case is the harmless one — and the ordinary case inverts the answer

Switzerland's war score on `t20` is **+0**, so the omission costs the player
nothing there. Measured on the **shipped 1805 board** instead:

**Nine of the nineteen non-player courts boot with ZERO marshals** (probe
`r10`) — `Hanover, Hesse, Holland, KingdomOfItaly, PapalStates, Portugal,
Sardinia, Saxony, Switzerland`. Almost half of Europe is invisible to this
answer from turn one, before any attrition. So this is not an edge case
produced by a destroyed army; it is the default for half the map.

The fully organic case, on the shipped board, engine's own
`recalculate_war_scores` doing the score sync:

```
France declares war on Hanover and overruns 5 of her 6 provinces
  war score vs Hanover : +45      Hanover's marshals on the board : 0

> who is winning
    War score, Sire — Austria +0 (evenly matched); Britain +0
    (evenly matched); Russia +0 (evenly matched). The breakdown is on
    the war banner on the left (click the war).

> are we at war with Hanover
    Yes, Sire — we are at war with Hanover. The war score stands at +45.
```

And the same shape for a great power whose army France has broken — the
ordinary pre-Pressburg board (probe `r09`):

```
France holds 6 of Austria's 7 provinces; the Austrian army is destroyed;
Austria fights on from her last province.   stored war score: +50

> who is winning
    War score, Sire — Britain +0 (evenly matched); Russia +0 (evenly matched).

> are we at war with Austria
    Yes, Sire — we are at war with Austria. The war score stands at +50.

THE BANNER THE ANSWER POINTS AT:
   card  Britain + Austria + Russia         +50
      bar Britain          +0
      bar Austria          +50
      bar Russia           +0
```

**Two arms of the same module, one board, one turn, contradicting each
other** — DESK-1's pattern (`why not attack Kutuzov` vs `where is Kutuzov`),
one arm over. The player asks the single most load-bearing strategic question
in the game and is told "evenly matched" while holding a dictated-peace score
against a court the sentence never names, with the banner beside it reading
`+50`.

It also falsifies `_answer_winning`'s own docstring in writing: *"the
canonical helper every other consumer reads, so the desk cannot disagree with
the war banner."*

**Severity: P3 → P2.** Player-reachable, ordinary play, shown ≠ applied, and
the answer is not merely incomplete — it points the opposite way.

---

## PART (b) — NARROWED

### The numbers reproduce

`t20`, my probe `r03`: desk says `Austria -26; Britain -54; Russia +0`;
`build_active_wars`' collapsed row carries `war_score: -78`. Confirmed.

### But "the desk cannot agree with the banner, by construction" is FALSE

`build_active_wars` carries `coalition_member_rows` (FA-N75,
`COALITION_CARD_KEEPS_ITS_MEMBERS = True`), and
`war_detail_popup.show_coalition()` draws **a tug-of-war bar per member at
that member's own pair score**. Measured on `t20` (probe `r07`):

```
--- show_coalition() bars ---
     bar Britain          -54
     bar Austria          -26
     bar Russia           +0
```

Those are the desk's three figures, to the digit. The desk does not disagree
with the banner about any number it prints.

### What is actually wrong is the POINTER

`surface_pointer("war")` renders *"the war banner on the left (click the
war)"*. Clicking a war **card** emits `card_clicked → _on_war_card_clicked →
show_war()`, which renders the collapsed row — **−78**, a number the desk's
sentence does not contain. The per-court bars live behind the coalition
**header** (`coalition_header_clicked → show_coalition()`), which the pointer
never names. The desk quotes the coalition-card view and sends the player to
the war-card view.

### Two more corrections to the row's own body

* **The war-level figure is not the sum of the pairs.** −26 + −54 + 0 = −80;
  `calculate_side_war_score` re-clamps per component and yields **−78**. So
  "reconcile the arithmetic" is not available; naming the figures as
  per-court is.
* **CA8-D2 §10.1 does not condemn this.** That ruling keys *leverage* — the
  score-CONSUMING seams — to the war. The coalition card deliberately keeps
  the pair view for display, which is what FA-N75 landed. A display quoting
  per-court scores is in-contract; the pointer naming the wrong surface is not.

**Severity for (b) alone: P4.** It is a legibility/pointer defect on a
surface that already shows both numbers.

---

## PLAYER-REACHABLE — YES, confirmed (probe `r04`)

Re-implemented `_redirect_diplomatic_command` from `main.gd` (115 family
keywords, 7 advisory leads):

```
who is winning          sent (advisory)       who's winning      sent (not claimed)
are we winning          sent (not claimed)    am i winning       sent (not claimed)
who is winning?         sent (advisory)       how goes the war   sent (advisory)
what is the war score   sent (advisory)
are we at war with Austria                    sent (no family keyword hit)
```

All eight winning phrasings and the contradicting sibling reach the backend.
Nothing here is API-only.

---

## SHIPPED BY ROW CX — YES (CX-2, `5fc3d5c8`)

`git show b4a27a15^:backend/ai/question_desk.py` is 353 lines and contains no
`_answer_winning` and no `winning` question kind; `git log -S"_answer_winning"`
attributes it to `5fc3d5c8` "CX-2 Berthier answers the board". `git grep
winning b4a27a15^ -- backend/` finds only armistice-variant strings. The
question was unanswerable before the row, so both halves are the row's.

---

## WOULD THE SUGGESTED FIX REGRESS? — No pin reds; but the shape is incomplete

I applied the filed fix verbatim (*"iterate `get_nations_at_war_with(player)`"*)
as a **read-only pytest plugin** (`probes/fixplug.py`; the repo was never
edited) and ran it over the row's own files and every test that touches the
desk or the war banner:

```
baseline, unpatched  tests/test_cx2_…                           51 passed
patched              test_cx1 + test_cx2 + test_cx3            202 passed
patched              test_ca8_gate_closeout_2026_08_07,
                     test_war_status, test_hc1_blockade_war_score,
                     test_iq2_collapse_war_room, test_pt_j_rulings,
                     test_fa_slice7_the_mock_speaks_plainly    305 passed
```

The two pins that touch the sentence —
`test_cx2…::test_the_war_score_is_the_canonical_helper_s` and the
`("who is winning", ("War score", "Austria"))` row — both name Austria, which
is at war on the boot board either way, so neither binds the roster source.
**No regression, and also no pin that would have caught this.**

**The fix shape is nonetheless incomplete, and the row should say so.**
`get_nations_at_war_with` does not mirror `build_active_wars`' own elimination
skip (`opp_regions == 0 and opp_marshals == 0`). On a board with Austria at 0
regions and only strength-0 marshals (probe `r08`):

```
                      desk names                     banner shows
shipped   ['Austria','Britain','Russia']   ['Britain','Russia']   extra=['Austria']
FILED FIX ['Austria','Britain','Russia']   ['Britain','Russia']   extra=['Austria']
```

The mismatch's *other* direction survives the fix untouched. I could not show
that state arising organically — `_eliminate_nation` deletes the WAR rows from
`diplomatic_states`, so the window is transient at most — which is precisely
why `build_active_wars` carries a defensive skip of its own. **So the honest
shape is not "iterate the at-war roster" but "read the rows the banner already
built"**: `build_active_wars(world)["wars"]` (plus `coalition_member_rows`)
already applies the elimination rule, already carries a per-court `war_score`,
and makes the two structurally unable to disagree — which is the sentence the
docstring already claims.

⚠ **Do not take the row's other option, "quote the war-level aggregate".** On
`t20` that answers *"−78"* and stops naming which court France is losing to,
which is what the player asked. Keep the per-court figures — they are on the
coalition card — and fix the POINTER to name the coalition header.

---

## ONE THING I MEASURED AND WILL NOT INFLATE

`_answer_winning` reads the **stored** `world.war_scores` (via
`get_war_score_for`), while `build_active_wars` explicitly **live-calculates**
(*"always live-calculate, not cached war_scores"*). That is a real seam
difference, and it is the kind of thing this review is for — but on all three
boards I measured (`boot`, `t20`, the staged sharp board) stored and live were
identical, because `recalculate_war_scores` re-derives every WAR pair from
`calculate_war_score` on the turn tick. **I found no board where they
diverge, so I am not filing it.** It is worth a line in the fix's comment,
not a finding.
