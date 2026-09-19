# Refutation pass — "The Two Roads" (topic: keystrokes)

Adversarial re-derivation of `two_roads.md`. Default verdict REFUTED; every
row below was re-measured from source or by probe. Probes are in `probes/`
with the `rk*` prefix (mine); the recon's are the `p*` files.

**Tree at measurement:** `f7008582`, working tree **DIRTY** (see
REFUTE:CX-R13). All probes `LLM_MODE=mock`, no key, no network. Read-only:
nothing under `backend/`, `godot-client/`, `tests/`, `docs/`, `tools/` was
touched.

**Scoreboard: 3 SURVIVE · 7 NARROWED · 3 REFUTED · 8 MISSED.**

The report's *conclusion* — that the two roads have disjoint dead zones and
the click road's advantage is information rather than clicks — largely
survives. Its two P1 mechanisms do not: **the client does emit movement
verbs**, and **the escalation headline is 2.2× too high**. The most
consequential thing it missed is a live, reproducible **diplomatic backdoor
through the Cabinet door's own wh-word exemption**.

---

## REFUTE:CX-R1 — **REFUTED as stated / NARROWED**
### "The click road has no movement verb anywhere in the client"

**The client emits `march to`, `hold`, `support` and `pursue` as literal
string constants, in `main.gd`.**

`godot-client/project-sovereign/scripts/main.gd:5563-5575`:

```gdscript
func _on_clarification_choice_made(marshal_name, chosen_target, strategic_type):
	var keyword_map = {
		"PURSUE": "pursue",
		"MOVE_TO": "march to",
		"SUPPORT": "support",
		"HOLD": "hold",
	}
	var keyword = keyword_map.get(strategic_type, "pursue")
	var clarified_command = marshal_name + " " + keyword + " " + chosen_target
	api_client.send_command(clarified_command, _on_command_result)
```

The signal is `clarification_popup.gd:113 clarification_choice.emit(...)`,
fired by a **button press**. A second route exists beside it:
`clarification_popup.gd:106 clarification_command.emit(command)` →
`main.gd:5578-5585` sends the backend's own string verbatim, and
`backend/commands/clarification.py:311` builds that string as
`f"{marshal.name}, move to {name}"` — up to **six adjacent provinces**, one
button each (`build_move_destination_clarification`).

**Why the census could not see it.** The census grep was
`grep -o 'order:[a-z_]*\|do:[a-z ]*'` — two *chip prefixes*. Neither
`keyword_map` nor a backend-supplied `option["command"]` carries either
prefix, so the instrument was blind by construction. It is the same blindness
the recon itself worked around for the Admiralty (it chased those into
`naval.py`) and then did not generalise. A census must count the thing, not a
string in two files.

**Also wrong in passing:** "all 44 `.gd` files" — `find godot-client -name
'*.gd'` returns **54** (45 in `scripts/`, 9 in `scenes/`). Off by ten.

**What SURVIVES, and it is the real finding:**

* There is **no proactive movement chip**. The clarification popup is raised
  only by an *ambiguous typed order*, so a player who types nothing never
  sees it. CX-R3's "a click-only turn ends at the first move" stands.
* There is **no marshal-selection gesture**: `grep -rn
  "selected_marshal\|_selected_marshal\|marshal_selected" --include=*.gd`
  returns **zero hits**. `map_renderer_base.gd:2041-2059` maps left-click to
  `region_clicked.emit()` (plus `map_dismiss_requested` on open water), and
  the only drag is middle-button pan. Both cited spans are accurate.

**Correct statement:** *the click road has no movement verb it can offer on
its own; it has four that it can only offer as an answer to a typed order.*

---

## REFUTE:CX-R2 — **NARROWED**
### "The typed road is deliberately CLOSED for the entire diplomatic family"

The redirect is real and the row's eight blocked families reproduce. I did
**not** re-port the matcher — the repo already maintains one, drift-pinned
against `main.gd`'s own const lists:
`tests/test_wo_slice7_cabinet_door.py::_redirect_verdict` (the extractor is
`_extract_gd_list` at `:143`). The recon hand-rolled a second port
(`probes/p2b_client_redirect.py`) and validated it against nine comments;
the maintained one is the better oracle and it agrees on every row the report
publishes (`probes/rk02_redirect.py`).

**Three corrections:**

1. **"the entire diplomatic family" is false, and the report's own §3 row 38
   says so.** `DIPLO_NO_HOME_KEYWORDS` (`main.gd:1635-1654`) is **18
   entries** covering five verb families — `set war purpose`, `repudiate
   bargain`, `make amends`, `repair relations`, `offer reparations` — all
   **exempt, typed-only**. Measured: `make amends with Austria` → SEND →
   `make_amends/Austria`; `repudiate bargain` → SEND → `repudiate_bargain`.
   The report tabled one of the five (row 38) and then generalised past it.
   The client's own docstring calls them "the three verbs with no UI home";
   the *list* is five families wide.
2. **115 keywords, not 114** (`main.gd:1665-1785`, counted by regex over the
   const block).
3. `request terms` is claimed by the **war room**, not the Cabinet — the
   report gets this right in row 32 but the finding text says "the whole
   diplomatic family" is closed *to the Cabinet*.

**Hygiene item found in the list (INFO):** entry 35 of
`DIPLO_FAMILY_KEYWORDS` is the literal `"break the alliance with Austria"` —
a hardcoded court name inside a nation-agnostic keyword table, made redundant
by `"break the alliance"` ten entries later.

---

## REFUTE:CX-R3 — **NARROWED** (arithmetic survives; the headline sentence does not)

I re-derived the census independently (`probes/`, inline script): **31 files,
1,416 commands** — attack 14.34%, status 14.12%, move+march 14.12%,
fortify+unfortify 15.32%, drill 6.57%, recruit 3.18%, build 2.82%, hold
1.91%, propose 1.84%, invest 1.34%, declare 1.20%, improve 2.97%. Every
published figure reproduces to within rounding. The attack-chip gate that
carries the "7 of 8 marshals" attribution also checks out: the chip is built
inside `_format_marshal_row` (`region_panel.gd:525-557`), so it is
**co-located only**, capped at two enemies, and enemy marshals ride
`region_marshals` at FULL visibility only.

**Correction 1 — "the click road wins … about 6% of the volume" invites a
false reading.** Six percent is the share where click *strictly beats* typed.
By the report's **own** per-intent verdicts, the click-**reachable** share of
the same 1,416 commands is **57.0%** (status, fortify, unfortify, drill,
scout, recruit, build, repair, land, the Admiralty verbs and the whole
click-only diplomatic set). A reader who takes "6% of the volume" as coverage
is wrong by an order of magnitude, and §4's own PARITY column is what proves
it.

**Correction 2 — `hold` is an artefact of the probe scripts.** Split by
family:

| script set | n | cmds | move+march | hold | recruit+build |
|---|---|---|---|---|---|
| all | 31 | 1,416 | 14.12% | **1.91%** | 6.00% |
| minus `weird_*` | 21 | 927 | 19.74% | **0.32%** | 5.61% |
| core only (no `weird_*`, no `np_*`) | 17 | 802 | **20.45%** | **0.00%** | 6.48% |

Every `hold` in the corpus comes from the absurdist/Napoleon probe arms. On
the seventeen scripts that represent ordinary play a France issues `hold`
**zero times**, so listing it as a typed-only per-turn cost is unsupported.

**This cuts the report's way too, and it should have said so:** move+march
rises from 14.1% to **20.5%** on the core set. The central claim gets
*stronger* when the absurdist scripts are dropped.

**Correction 3 — the typed-only share.** By verb head alone it is **16.2%**,
not 30%; the report's ~30% only holds once 7/8 of attack volume is attributed
to typed. That attribution is sound (co-located chip), so ~29% is defensible
— but it is a derived estimate resting on a boot-board co-location count the
report's own §6 flags as unmeasured on a played board.

---

## REFUTE:CX-R4 — **SURVIVES** (every citation verified exact)

Unusually for this repo, the line numbers hold. Spot-checked all of them:

* `region_panel.gd:279-300` — levy headroom + **per-region** price with the
  capital rate as fallback (the comment records the 654g-vs-872g defect that
  forced it). ✅
* `region_panel.gd:320-347` — substitute price/amount/alarm premium/room, and
  `bb_chip_disabled` with a stated reason. ✅
* `region_panel.gd:452-462` — `do:land <m> in <region>` with the odds. ✅
* `region_panel.gd:574-599` — `_build_terms_text`, delivered yield per
  building, "never a constant kept here". ✅
* `marshal_management.gd:362` — `commission:<name>` chip with the price. ✅
* `diplomacy_wizard.gd:664` — `"↳ %s — income %dg, loyalty +%d, they remit
  %d%%"`. ✅
* `naval.py:2786-2805` — the blockade forecast naming what it cannot close. ✅

The finding's thesis — *every CLICK WINS verdict was won on information* — is
the strongest thing in the report and I could not dent it.

---

## REFUTE:CX-R5 — **NARROWED**
### "both roads converge at the executor and inherit identical refusals"

True of chips. **False of the one click affordance the report itself tables
as a click path** (§3 row 23, the Orders-tab `[Cancel]`).

`strategic_ledger.gd:1090` emits `[url=cancel:<marshal>]`, which
`:1153` routes to `api_client.cancel_strategic_order` (`api_client.gd:218`)
→ `POST /cancel_order` (`backend/main.py:5737`), whose body calls
**`executor._execute_cancel(command, game_state)` directly** — skipping the
parser, skipping `CommandExecutor.execute`, and re-implementing the AP check
and the dialogue gate by hand (`main.py:5755-5781`).

That the copies drift is not my inference; the endpoint's own comment records
it: *"FA slice 6 (FA-N62): the typed `cancel` blocks only on a HARD stop …
this button blocked on ANY pending dialogue — refused on 12 of 12 ambient
turns"*.

Second divergence the report missed: `send_structured_command`
(`api_client.gd:151`; callers `main.gd:6462`, `:6573`, `:6592`) posts extra
fields that **override the parser's answer** at `main.py:2992-2999`
(`action`, `target_nation`, `war_id`, `region`). The text must still parse
(`if parsed.get("success")`), so the convergence is real but not total: the
click road can force an action the parser did not choose.

The finding's slogan — *a chip removes naming risk, never gate risk* — is
correct for every `do:`/`order:` chip and I reproduced its measured case.

---

## REFUTE:CX-R6 — **REFUTED**
### "every measured near-miss costs 0 AP — never a wasted action point"

`probes/rk07_apcost.py`, 1805 boot, fresh world per case:

| AP | result | utterance |
|---|---|---|
| **1** | scout → **Swabia** | `Ney, scout Swabiaa` |
| **1** | scout → **Swabia** | `Ney, scout Swabai` |
| **1** | scout → **Nassau** | `Ney, scout Nassua` |
| **1** | scout → **Lorraine** | `Ney, scout Lorrain` |
| **1** | scout → **Franconia** | `Ney, scout Franconi` |

Five measured near-misses, five action points. The generalisation fails
because the thirteen arms were all arms that **refuse**; an arm that
**auto-corrects and succeeds** never entered the sample.

**And the report contradicts itself.** §3 row 4 records the charge in its own
words — *"silently auto-corrects to Swabia and succeeds, **charging 1 AP**"*
— and §3a then asserts "not one of the 13 measured near-miss arms charged an
action point", which is true of the thirteen and false of the claim built on
them.

The distinction matters for the row's conclusion: a refusal costs a sentence,
but a **silent correction onto a different valid object costs the action
point and the turn**, which is the WO-13 hazard class, not a benign one.

---

## REFUTE:CX-R7 — **SURVIVES, and is wider than filed**

Reproduced exactly: `Ney, cancel` → `Unknown action: unknown`, and the
`suggestion` string enumerates `… restrain, **cancel**, build, repair …`.
0 AP. `Ney, halt` → `cancel/Ney`, *"Ney awaits further orders."*

Widened by probe (`probes/rk01_rows.py`):

| utterance | result |
|---|---|
| `Ney, cancel` | **refused** (`unknown`) |
| `Ney, abort` | **refused** (`unknown`) |
| `Ney, stop` | **refused** (`unknown`) |
| `Ney, halt` / `Ney, belay` | works |
| `Ney, cancel order` / `Ney, cancel your order` / `cancel Ney's order` | works |
| bare `cancel` | works (`"No marshal has an active strategic order"`) |

**The sharper version of the finding:** the backend's *own* pending-interrupt
router already accepts all three — `_INTERRUPT_KEYWORDS` at
`backend/main.py:974` is `(None, ("cancel", "abort", "belay"),
("cancel_order",))`. So `Ney, cancel` is typable while an interrupt is
pending and not typable otherwise. Two vocabularies for one verb in one
process. P2 stands.

---

## REFUTE:CX-R8 — **SURVIVES**, with a magnitude correction that strengthens it

Confirmed on the maintained port: `gather intel on Austria` → `cabinet`;
`gather intelligence on Austria` → `SEND`.

**Correction:** the report implies the two phrasings differ. They do not.
Measured end-to-end (`probes/rk01_rows.py`), **both parse identically** —
`diplomatic_mission / Austria`, confidence 0.95 — and both execute:
*"Sire, I shall begin efforts to gather intelligence on Austria. This will
cost 1 DP per turn."* So this is **purely** client-mirror drift against a
backend that never disagreed, which is a cleaner statement of the defect than
the one filed.

Widened: `gather intel on Austria?` also escapes (the `?` exemption) and
executes the same mission.

---

## REFUTE:CX-R9 — **SURVIVES, and is UNDER-stated (P3 → P2)**

The mechanism is exactly as filed: `_names_a_nation` (`main.gd:2071-2083`)
prefix-matches `form` / `form + " "` / `form + ","`, while its sibling
`_contains_word` (`main.gd:2034-2051`) treats a possessive as a boundary *by
design* and its docstring says so.

**But the report picked the one example that does nothing.** `invest in
Holland's defenses` escapes and then refuses: *"Holland's loyalty is already
full (100/100) — the investment would buy nothing, so nothing is charged."*
On the shipped 1805 boot that hole is inert.

The same hole with a different verb is not (`probes/rk03_escapes.py`,
`rk04_natural.py`):

```
client=SEND  release_vassal/Holland  exec=True
   "release Holland's army"
   → DIPLO STATE: France-Holland: VASSAL -> PEACE (vassal_release)
   → "Holland is released from vassalage … Their tribute of 337 gold …"
```

`release Holland` is `cabinet` (nation-gated). `release Holland's army` is
`SEND`, and it **irreversibly releases a vassal**. `DIPLO_NATION_GATED_PREFIXES`
is exactly two entries — `["invest in ", "release "]` — and the report tested
the harmless one.

---

## REFUTE:CX-R10 — **NARROWED**

The defect half reproduces exactly: `build depot in Rhinland` → `target:
None`, *"Specify a region…"*; `recruit infantry in Rhinland` → `target:
None`, answers about marshals; `build shipps` → the building branch.

**The prescription does not.** "The good behaviour already exists one verb
over" holds only when the typo is a near neighbour. On the same board, same
marshal (`probes/`, inline):

| utterance | move arm's answer |
|---|---|
| `Ney, march to Swabland` | *"Did you mean 'Swabia'?"* ✅ |
| `Ney, march to Alsace` | *"Region 'Alsace' not found. **Nearby: Wales, Balearics, Ulster**"* |
| `Ney, march to Alsce` | *"Did you mean **'Wales'**?"* |
| `Ney, march to Baden` | *"Did you mean **'Bern'**?"* |
| `Ney, march to Wurttemberg` | *"Did you mean **'Bern'**?"* |
| `Ney, march to Bavaria` | *"Bavaria is a nation, not a province… theirs are Franconia, Munich, Swabia"* ✅ |

Ney is standing at Rhineland. The arm the report holds up as the model is two
arms: the **nation** arm is genuinely good, and the **not-found** arm offers
Wales and Bern to a marshal on the Rhine. Copying it into `build`/`recruit`
would propagate that.

(`Alsace` is **not a province** on the 126-region map — see MISSED:6.)

---

## REFUTE:CX-R11 — **NARROWED: the headline figure is 2.2× too high**

The report histogrammed `_parse_with_mock(...).confidence` and called
everything below 0.7 "would escalate". The production predicate is
`LLMClient._should_fallback_to_llm` (`llm_client.py:901-965`) and it has
**six** arms. Two of them suppress escalation for **low-confidence** rows:
`fast_result.refusal` (the PARSE-NEG terminal) and `action in
NON_ORDER_ACTIONS`.

`probes/rk05_escalation.py` runs the real predicate, applies
`repair_leading_verb_typo` first (the layer the report names as bypassed),
and never calls a provider — `provider_name`/`api_key` are faked so the
"is there an LLM at all" arms do not short-circuit:

```
corpus entries: 447    selected (non-live_only, non-legacy): 388
confidence histogram: {0.5: 38, 0.55: 4, 0.75: 1, 0.8: 52, 0.9: 123, 0.95: 162, 1.0: 8}

  confident                      346   89.2%
  ESCALATES                       21    5.4%
  refusal(PARSE-NEG terminal)     21    5.4%

REAL escalation rate:                        21/388 = 5.4%
confidence-only (the recon's number):        42/388 = 10.8%
suppressed BELOW the gate by the other arms:     21
```

* **The published 11.9% should be 5.4%.** Exactly half the sub-gate rows are
  PARSE-NEG terminals. The report *describes* that mechanism in §7(b) prose
  and then does not apply it to its own table.
* The repair pass is worth **four rows** (0.5 bucket 42→38, 0.95 158→162), so
  the report's unquantified "upper bound" caveat is now quantified: 11.9% →
  10.8% on confidence alone, → 5.4% on the real predicate.
* Reproducible: identical output on two runs eight minutes apart, across a
  sibling agent's in-flight edits to `llm_client.py`.

**The gate-freeness claim SURVIVES and is under-stated.** Real predicate,
gate moved:

| gate | 0.55 | 0.60 | 0.65 | 0.70 | 0.75 | 0.79 | 0.80 | 0.85 |
|---|---|---|---|---|---|---|---|---|
| escalating | 17 | 21 | 21 | **21** | 21 | 22 | 22 | 58 |

Anywhere in 0.60–0.80 moves **one** row, not five. The threshold is not a
lever; the 0.5 bucket is the only decision.

**The escalating set is 21 rows, and the report's characterisation of it
needs one split.** Seventeen sit at 0.5/`unknown` (idiom, delegation and
nonsense — `Soult, deal with the Austrians`, `Ney, fix bayonets`, `xyzzy
foobar`). The **four at 0.55 are all NAME misses**: `Soutl, attack Mack`
(typo), `Wittgenstein, attack Mack` (not on the roster), `Grouchy, charge`
(on the commission bench, not commissioned), `Emperor, attack Mack` (title,
not name). That split is the whole answer to "where would prediction pay" —
see MISSED:4.

---

## REFUTE:CX-R12 — **NARROWED**

The mechanism is right: `region_panel.gd:130-134` composes
`order:<verb>:<Name>` into `"<Name>, <verb>"` with no target, so the Scout
chip can only send `Ney, scout`.

**"Strictly weaker" is wrong.** Measured, both at 1 AP:

* `Ney, scout` → *"Ney scouts from Rhineland: Swabia (Bavaria, Plains, 1
  enemies), Lorraine, Frankfurt, Gelderland, Nassau, Brabant"* — **six
  provinces**, enemy counts.
* `Ney, scout Swabia` → *"Ney scouts Swabia: Controlled by Bavaria. Terrain:
  Plains. Enemy forces: **Mack (Austria): ~52,000 troops**"* — **one
  province**, enemy named and counted.

Breadth versus depth at the same price. The correct finding is that **the
chip cannot buy depth**, not that it is strictly worse.

---

## REFUTE:CX-R13 — **REFUTED as a provenance record**

The section names one modified file. At measurement time `git status` showed
**two**, and both had moved past the figures §8 publishes:

| | report (§8) | at my first read (09:33) | at my last (09:47) |
|---|---|---|---|
| `clause_guards.py` | +71 / −2, mtime 09:28:23 | +141 / −10, 09:33:12 | **+166 / −10, 09:38:47** |
| `llm_client.py` | **not mentioned** | +20 / −2, 09:31:27 | **+29 / −2, 09:38:57** |
| untracked | — | — | **`tests/test_cx1_a_question_never_orders.py`** |

`llm_client.py` is the file §7's whole analysis reads (`:63`, `:902`,
`:911-920`), so omitting it from a provenance section written to let a reader
reproduce §7 is the one omission that matters. The change is substantive: the
sibling threaded a live roster into the question guard —
`is_question(command_text, _question_subjects(game_state))` at
`llm_client.py:1370` and `:1619`.

**In the report's favour: §7 does still reproduce.** I re-ran it on the
09:38 tree and got a byte-identical histogram and rate. The conclusion was
right; the record that justified it was already stale when it was written and
is staler now.

---

# What the census missed

## MISSED:1 — **[P2] The wh-word door: a diplomatic order walks through the Cabinet's own advisory exemption and executes**

`_is_advisory_question` (`main.gd:1912-1919`) exempts any sentence whose
first word is in `DIPLO_ADVISORY_STARTS` = `what, how, where, who, whom, why,
which`. The const's own comment justifies the restriction:

> *"A wh-word cannot begin an order, so only those exempt"*

That is false, and the same file records the identical mistake being
corrected once already — the deleted negation exemption, *"a substring bail
is a wildcard … A door with a wildcard in it is not a door."* The wh-word
bail is the surviving wildcard.

Measured end to end (`probes/rk08_join.py`, `rk04_natural.py`) on the 1805
boot:

| client | `is_question` | action | exec | utterance |
|---|---|---|---|---|
| **SEND** | True | `diplomatic_declare_war` | ✅ | `why not declare war on Prussia` → *"Choose your war purpose against Prussia."* |
| **SEND** | True | `diplomatic_proposal` | ✅ | `why not propose peace with Austria` → *"…I have prepared terms…"* |
| **SEND** | True | `diplomatic_proposal` | ✅ | `why don't we propose peace with Austria` |
| **SEND** | True | `diplomatic_proposal` | ✅ | `how do we make peace with Austria` |
| **SEND** | True | `diplomatic_declare_war` | ✅ | `what say we declare war on Prussia` |
| **SEND** | True | `diplomatic_mission` | ✅ | `which court should we declare war on Prussia` (courts Prussia at 2 DP/turn) |
| cabinet | False | — | — | `propose peace with Austria` (control) |
| SEND | True | `diplomatic_advisory` | ✅ | `propose peace with Austria?` (control — read-only, correct) |

These are natural player sentences, not contrivances.

**Two layers agree it is a question and it executes anyway.** `is_question`
returns **True** for every row above (`A_QUESTION_NEVER_ORDERS = True`,
`clause_guards.py:610`), because the guard gates only the clause-strip block
and the FACT-desk route; a question the desk cannot answer falls through to
the keyword chain, which finds `propose peace with` and proposes peace.

**Why no pin catches it:** `test_wo_slice7_cabinet_door.py`'s census
(`test_every_family_utterance_is_claimed`, `:287`) walks the golden corpus,
and the corpus has **8 wh-initial rows and 0 of them carry a diplomatic
expected action** (measured over all 447 entries). The pin is structurally
blind.

**Not a duplicate of the in-flight sibling slice.** Its new test file lists
only military verbs, and at **09:47:11** on its own tree the military half is
closed and the diplomatic half is open:

```
why not attack Mack         -> help        (closed)
why not retreat             -> help        (closed)
why not make Holland a vassal -> help      (closed)
why not declare war on Prussia -> diplomatic_declare_war, exec=True   (OPEN)
why not propose peace with Austria -> diplomatic_proposal, exec=True  (OPEN)
```

⚠ **Fix hazard:** do not close this by dropping wh-words from
`DIPLO_ADVISORY_STARTS`. `test_counsel_stays_spoken` (`:439`) asserts that
every `diplomatic_advisory`/`diplomatic_feasibility` corpus row reaches
Talleyrand, and its own docstring says one of them (*"what would it take to
get peace with Prussia?"*) carries a family keyword and is saved **only** by
this guard. The exemption has to become "wh-lead **and** no family keyword
after it", or move to the `?`/no-imperative test the backend now has.

---

## MISSED:2 — **[P3] The no-home exemption is a second wildcard**

`_redirect_diplomatic_command` bails on a `DIPLO_NO_HOME_KEYWORDS` match
**anywhere** in the sentence (`main.gd` loop: `for keyword in
DIPLO_NO_HOME_KEYWORDS: if keyword in lower: return false`). Measured:

```
SEND | diplomatic_proposal/Austria | exec=True
   "propose peace with Austria, then make amends with Russia"
SEND | set_war_purpose | "declare war on Prussia and set war purpose"
SEND | make_amends     | "break treaty with Prussia to repair relations"
```

The first one **proposes peace**. Appending a no-home verb to any claimed
sentence opens the door. Same class as the deleted negation bail, same file.

---

## MISSED:3 — **[INFO] There is a third road, and it is the one the report tabled as a click path**

`POST /cancel_order` (`main.py:5737`) is the only client affordance that
reaches the game without passing through `/command`, the parser, or
`CommandExecutor.execute`. It re-implements the AP check and the dialogue
gate inline and calls `executor._execute_cancel` directly. The endpoint's own
comment (`:5762-5769`) records the two copies having already drifted in
production (FA-N62). Any statement of the form "both roads converge at the
executor" has to except this one.

---

## MISSED:4 — **[P2 / the answer to the predictor question] The client has no completion of any kind, and a quarter of every typed order is a proper noun from a closed 165-item list**

The typed road's only affordance is up/down history (`main.gd:929-934`). A
census of the client's input handling finds **no autocomplete, no
tab-completion, no suggestion list** — `KEY_TAB` is bound to a screen/game key
(`main.gd:959`, `:1161`), not to completion.

Measured against the 1805 boot (`probes/rk08_join.py`):

```
spellable proper nouns at boot: marshals=22  regions=126  nations=20  = 165
name length: min 3, median 7, max 15
scripted commands: 1416
  containing >=1 proper noun:                      1027  (72.5%)
  proper-noun characters / all typed characters:   27.2%  (7,896 of 28,997)
```

This is the concrete form of the report's own closing intuition ("both would
pay on the same narrow band: idiomatic delegation, and **the names**"). It is
supported by the escalation data independently: **all four 0.55-band
escalations are name misses**, and the near-miss arms in §3 are dominated by
name misses. A closed 165-item vocabulary with a median length of 7 is the
textbook case for prefix completion, and it needs no model.

---

## MISSED:5 — **[INFO] The cost side of "is routing to the LLM worth it" was never measured**

`probes/rk06_played.py`. Production builds `build_system_prompt()` +
`build_parse_prompt()` (`providers.py:615-621`) and passes `PARSE_TOOL`:

```
system prompt :     177 chars  ~   44 tok
user prompt   :  16,593 chars  ~ 4,148 tok
tool schema   :   2,860 chars  ~  715 tok
TOTAL INPUT   :  19,630 chars  ~ 4,907 tok   per escalated command
```

(Consistent with the repo's own note at `providers.py:96`, *"the ~5K-token
1805 prompt"*.)

And the rate on utterances a played France actually issues — not on a
regression corpus built to break the parser:

| script set | commands | escalate | rate |
|---|---|---|---|
| core (17 scripts) | 802 | 7 | **0.87%** |
| `np_*` | 125 | 5 | 4.00% |
| `weird_*` (absurdist probes) | 489 | 36 | 7.36% |
| all | 1,416 | 48 | 3.39% |

⚠ **UPPER BOUND:** every command is parsed against the **boot** world, so a
command naming a marshal commissioned on turn 12 (`Senarmont`, `Oudinot`)
reads as an unknown name and escalates. The true core rate is at or below
0.87%.

**So: a 40-turn commanded campaign (160 commands) escalates ~1.4 times and
spends ~6,900 input tokens.** The LLM road is nearly free *because it is
nearly never taken* — which is also why tuning it buys nearly nothing. The
report's §7 published 88.1% / 95.3%; neither is the number a played campaign
produces.

---

## MISSED:6 — **[P4] `Alsace` is not a province, and five committed playtest scripts march to it**

`Alsace not in world.regions` on the 126-province 1805 boot. Of 204 movement
destinations across `tools/playtest_scripts/*.json`, **11 are not regions** —
`Alsace` ×5 (`commanded_full40`, `commanded_spender40`, `flagship_1805`,
`smoke_battle`, `volte_court_austria`), `Bavaria` ×3 (a nation), 3 regex
artefacts. Two effects: those scripted orders are dead (~4% of scripted
movement), and the single most obvious French destination a player could type
is refused with *"Nearby: Wales, Balearics, Ulster"* (see REFUTE:CX-R10).

---

## MISSED:7 — **[INFO] The escape holes are a family of four, not two anecdotes**

`probes/rk03_escapes.py` — 8 escapes in 26 probes, in four classes:

1. **possessive** — `_names_a_nation` vs `_contains_word` (CX-R9), worst case
   `release Holland's army`.
2. **mirror drift** — `gather intelligence on` (CX-R8).
3. **`?` exemption** — `gather intel on Austria?` SENDs and starts the
   mission.
4. **wh-lead / no-home wildcards** — MISSED:1 and MISSED:2, the only two that
   reach a *war declaration* or a *peace proposal*.

The report filed classes 1 and 2 as separate P3/P2 rows; they are one rule
("what counts as a word boundary / what counts as a bail") with four exits,
and two of the exits are worse than either filed row.

---

## MISSED:8 — **[INFO] The attack chip's fog gate**

`region_panel.gd:551-557` builds attack chips only from `enemy_names` in that
province, **capped at two**, and the panel's own comment records that enemy
marshals ride `region_marshals` at **FULL visibility only**. So the report's
row 3 ("CLICK WINS, narrowly") is narrower still: co-located **and** fully
scouted **and** among the first two enemies present.

---

# Method notes and limits

* **I did not run the Godot client.** Every click path here is verified in
  `.gd`/`.py` source only, exactly as in the report's §6. The two claims that
  most need an on-screen check are MISSED:1 (does the wh sentence visibly
  execute in the terminal?) and REFUTE:CX-R1 (does the clarification popup
  render its buttons?).
* **The tree was dirty throughout** and moved twice during measurement
  (REFUTE:CX-R13). Everything in REFUTE:CX-R1/R2/R4/R5/R12 and MISSED:3/4/6/8
  is read from files the sibling never touched. The escalation figures
  reproduced byte-identically across the sibling's edits. MISSED:1 was
  re-measured at 09:47:11, after the sibling's 09:38:57 write, specifically to
  show it survives their fix.
* **The redirect oracle is the repo's own**
  (`tests/test_wo_slice7_cabinet_door.py::_redirect_verdict`), not a
  hand-rolled port. Its one known infidelity: it builds nation forms by
  CamelCase-splitting `NATION_COLORS` tags, where the client calls
  `Utils.display_nation_name(tag)`. 25 tags → 29 forms. None of the rows
  above turns on a tag whose display name differs from its split form.
* **No LLM was called.** `rk05`/`rk06` fake `provider_name`/`api_key` so the
  predicate's availability arms do not short-circuit, and never touch
  `_parse_with_live_provider`.

## Probes written for this pass

`probes/rk_harness.py` (parse+execute, fresh deep-copied 1805 world per case)
· `rk_http.py` (the real `/command` endpoint via TestClient; unused in the
end — the sub-road proved sufficient) · `rk01_rows.py` (CX-R7/8/9/10/12) ·
`rk02_redirect.py` (the maintained port) · `rk03_escapes.py` (escape census)
· `rk04_natural.py` (natural wh/possessive) · `rk05_escalation.py` (the real
escalation predicate + gate sensitivity) · `rk06_played.py` (played-command
escalation + prompt cost) · `rk07_apcost.py` (the AP counter-examples) ·
`rk08_join.py` (wh door + proper-noun census).
