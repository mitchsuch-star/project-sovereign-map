# REFUTING THE CLICK-ROAD CENSUS

Adversarial re-derivation of `click_road.md`, 2026-09-19, at `f7008582`.
Default verdict was REFUTED; every row below was re-read from source and, where
the claim was testable, driven through the real `POST /command` on the shipped
126-province 1805 board. Probes are committed under `probes/rf_*.py` with their
`.out.txt` beside them.

**Method note — the tree is dirty.** `backend/ai/clause_guards.py` carries an
uncommitted change from a concurrent slice (WH-lead + deliberative-opener
question guards). I verified it cannot touch this measurement: **0 of the 80
click strings** I drove begins with `who/whom/whose/why`, carries a contracted
`'s` lead, or contains `what about` / `how about` / `is it time to`
(`probes/rf_16` input set, regex check inline). Every number below is from the
working tree as it stands.

**Headline verdict on the census's own headline.** The shape is right and the
count of structured call sites is right. Two of its load-bearing sentences are
wrong: the free-text string on a structured command is **not** a parse the
backend merely "also" runs — it is a **gate** that silently discards the
structured payload when it fails (`backend/main.py:2991`); and the tag claim's
cited proof (`main.gd:6172`) proves nothing, because `add_output` humanises
*every* line (`main.gd:4275-4277`). The census also asserted its one P4 hazard
(CX-10) without testing it, and it does not reproduce: **630 cases, 0 drift.**

---

## PART 1 — THE TEN FINDINGS

### REFUTE:CX-1 — NARROWED (count right, mechanism understated, pipeline count wrong)

**Confirmed.** `send_structured_command` is defined at `api_client.gd:151` and
has exactly **3** call sites: `main.gd:6462`, `:6573`, `:6592`. A caller-count
census of every `api_client.gd` func gives `send_command` **14** and
`send_structured_command` **3** (`probes/` — the loop is in this report's
command log; reproduce with
`for f in $(sed -n 's/^func \([a-z_0-9]*\).*/\1/p' api_client.gd); do ...`).

**Correction 1 — the census's own method does not reproduce.** It cites
"`grep -c` = 3". `grep -rn "send_structured_command" godot-client/ --include=*.gd`
returns **8** lines (definition, a docstring at `diplomacy_wizard.gd:680`, three
`has_method` guards, three calls). The figure 3 is right; the stated derivation
is not.

**Correction 2 — "the backend parses [the free text] as the primary route"
understates it. It is a GATE.** `backend/main.py:2991-2999`:

```python
if parsed.get("success") and isinstance(parsed.get("command"), dict):
    if request.action:
        parsed["command"]["action"] = request.action
```

The structured fields are applied **only if the free-text parse succeeded**.
Measured on the 1805 boot (`probes/rf_08_structured.py`):

| body | result |
|---|---|
| `{"command":"propose white peace with Austria"}` | ok, an **ordinary** Peace Treaty proposal |
| `+ {"action":"propose_white_peace","war_id":"war_1"}` | ok, the **white-peace scorer** ("cannot be sealed as it stands…") |
| `{"command":"zzzz qqqq","action":"propose_white_peace",…}` | **ok=False, Berthier's shrug — the structured action never ran** |
| `{"command":"economy","action":"propose_white_peace",…}` | ok, **the white peace ran** — the parsed action is irrelevant once the gate passes |

So the wire format already has a structured fast path; one `if` neuters it.

**Correction 3 — "all five send pipelines" undercounts.** There are **14**
`send_command` call sites in **nine** distinct pipelines: `end turn`
(`main.gd:1485`), the typed line (`:1614`), clarification ×3 (`:5575`, `:5585`,
`:5596`), the proposal fallback (`:5687`), the wizard free-text (`:6178`), and
the four chip pipelines (`:6262`, `:6305`, `:6328`, `:6409`), plus three
`has_method` else-arms (`:6464`, `:6579`, `:6598`). The census's claim in §1.1
that double-clicks are "guarded by the shared `_chip_command_in_flight` latch"
is true for **4 of 9** — the wizard and clarification pipelines never touch it.
*I checked whether that is a defect and it is not*: `diplomacy_wizard.gd:689`
calls `_close_wizard()` **before** the emit, so a second click cannot reach a
button. And all four latch clears are the **first** statement of their result
handler (`main.gd:6266`, `:6309`, `:6332`, `:6413`), and
`api_client._on_request_completed` fires the callback on timeout, connection
failure, bad code and JSON error alike (`api_client.gd:257-292`) — so the latch
cannot leak. Recorded because a reader of the census would assume the guard is
universal.

**Verdict: NARROWED.** Shape and counts survive; the "primary route" framing is
replaced by the gate, and the pipeline count is 9, not 5.

---

### REFUTE:CX-2 — NARROWED (mechanism confirmed, cited proof invalid, harm inverted)

**The mechanism is real and I re-derived it from the backend, not the client.**
`backend/main.py:5593` builds the step-1 entry as `"name": n` while iterating
`world.enemy_nations`. Measured on the 1805 boot
(`probes/rf_01_tags.py`): 19 tags, of which **two are camelCase** —
`PapalStates`, `KingdomOfItaly`. So `propose peace with KingdomOfItaly` and
`guarantee PapalStates` are real wire strings. ✔

**The cited proof is invalid.** The census argues that `main.gd:6172`'s
`humanize_nation_keys_in_text()` "confirms the string on the wire carries tags."
It confirms nothing: `add_output` (`main.gd:4275-4277`) humanises **every line
of terminal output**, so the explicit call at 6172 is a redundant second pass.
The inference is unsound even though the conclusion happens to be true.

**The harm is the opposite of what the census implies.** It frames this as the
parser being fed machine spelling ("Any fuzzy/typo layer tuned on human spelling
is being fed machine spelling"). Measured, the parser does not care
(`probes/rf_02_tagparse.py`, `rf_05_drive2.out.txt`):

```
propose peace with KingdomOfItaly     ok  conf 0.95  diplomatic_proposal
propose peace with Kingdom of Italy   ok  conf 0.95  diplomatic_proposal
invest in KingdomOfItaly  -> "The Kingdom of Italy's loyalty is already full (100/100)"
court PapalStates         -> "court and charm Papal States"
```

The real defect is the **return** direction — 7 of 80 driven messages echo the
raw tag back ("France guarantees PapalStates", "regarding the Peace Treaty
proposal to KingdomOfItaly", "KingdomOfItaly is our vassal, Sire") — and there
is a guard one layer down that neutralises it:
`Utils.PROSE_NATION_KEY_SUBSTITUTIONS` (`utils.gd:271-273`) maps exactly those
two tags, applied at `add_output`. So in the terminal the player never sees it.

**Verdict: NARROWED, P3 → INFO for the parser.** One real leak survives the
guard, on a surface that never reaches `add_output` — see **MISSED-1**.

---

### REFUTE:CX-3 — NARROWED (the list is bigger than its own headline, and two rows are wrong about the shipped board)

The fenced `EMITTED_STRINGS` block is **88 lines, 87 distinct** (`Ney, attack
Mack` appears twice), not "~70". I filled the templates from the measured boot
and drove **80** of them through the real `POST /command`
(`probes/rf_05_drive2.py`). **All 80 parsed**, at confidence 0.8–0.95, mode
`mock`. That is a genuine strengthening of the census's §4 claim.

Two rows are wrong about what the string *does*:

- **`recruit cavalry in <R>` / `recruit artillery in <R>` are cosmetic** on the
  shipped board — see **MISSED-4**.
- **`land <M> in <R>`** — the census recorded it as UNVERIFIED. Driven:
  `land Soult in Munster` → *"The transports lift 15,000 men; Soult commands
  30,000 — 15,000 too many."* Refused, and the chip states no such gate.

**Verdict: NARROWED.**

---

### REFUTE:CX-4 — NARROWED (the 16 is right; "no typed equivalent" is wrong for save/load, and the finding contradicts itself three ways)

`api_client.gd` POSTs **17** distinct endpoints; `/command` is the parser road,
so **16 bypass the parser** — the count is correct.

**The finding's own arithmetic does not agree with itself:** the title says
"5 of them have no typed equivalent", the evidence sentence names **6**, and the
§2.1 table marks **7** rows "no".

**Two of those are wrong, and the census checked the wrong table.** It concludes
from `VALID_ACTIONS` (`backend/ai/validation.py`) that no save verb exists. The
save/load road is a `meta_command` that bypasses `VALID_ACTIONS` entirely:
`backend/ai/llm_client.py:1794-1796` returns `action="meta_command"` at
confidence 1.0 for any input starting `save` or equal to `load`, and
`backend/commands/executor.py:1224-1240` handles it before marshal resolution,
AP checks and objection checks. Driven (`probes/rf_14_saveload.py`):

```
save            -> ok  'Game saved: Save - Turn 1'
save quicksave  -> ok  'Game saved: quicksave'       <- the EXACT name pause-menu /save sends
load            -> ok  'Available saves: …  Use the load menu to load a save.'
new game        -> shrug          dismiss notification -> shrug
```

So `/save` has a **full** typed equivalent, `/load` a **partial** one (list, no
load). `/new_game`, `/notifications/dismiss`, `/mailbox/activate`,
`/mailbox/respond`, `/config/llm` survive as click-only.

**Verdict: NARROWED.**

---

### REFUTE:CX-5 — SURVIVES, and under-counts by one

`api_client.gd:85` defines `get_marshal_trust`; a repo-wide `.gd` grep returns
only the definition. `GET /marshal_trust/{marshal_name}` (`backend/main.py:4552`)
is unreachable from the UI. ✔ Exactly as filed.

**But the census called §2 "the complete inventory" and missed a second dead
method.** A caller-count census over every `api_client.gd` func returns **two**
at zero: `get_marshal_trust` **and `get_llm_config` (`api_client.gd:99`)**. The
endpoint itself is live — `settings_panel.gd:260` GETs `/config/llm` through its
own `HTTPRequest` — so this is dead client code, not a dead endpoint. Note also
the census's §2.2 GET list names `/config/llm` but omits `/marshal_trust`, the
one endpoint its own §2.3 calls dead.

**Verdict: SURVIVES (P4), with the inventory corrected to two dead methods.**

---

### REFUTE:CX-6 — NARROWED; its predicate claim is FALSE

Line ranges are fair (chips at `marshal_management.gd:650/652/654` under the
gate at `:644-645`; `region_panel.gd:545/547/549/550/557`). The asymmetry is
real: the Generals card offers fortify/unfortify/drill only; the region panel
adds Scout and up to two `Attack <Enemy>` chips.

**"Both gate on the same broken/retreating predicate" is wrong, in both
directions:**

- `marshal_management.gd:644-645` gates on `captured` **or** `is_broken` **or**
  `is_retreating`.
- `region_panel.gd:543` gates on `retreating` **or** `broken` only — **no
  `captured` arm** — and additionally requires a non-empty `tactical_state`
  (`:540`).

A captured player marshal is therefore chip-free on the card and, if he ever
rides `region_marshals` with a populated `tactical_state`, chip-bearing on the
map. I did **not** establish that he does, so this is a divergence in the guard,
not a demonstrated defect; and `backend/main.py`'s PC15-4 lost-marshal guard
refuses an order addressed to a prisoner by name before any parse, so the wire
is safe either way.

**Verdict: NARROWED.** The asymmetry survives at P4; the "same predicate"
sentence is struck.

---

### REFUTE:CX-7 — SURVIVES, but its failure model is wrong

The three display-copy strings are confirmed in code
(`diplomacy_wizard.gd:697-736` `_structured_payload_for_action`, branches for
`open_settlement`, `propose_white_peace`, `grant_region_to_vassal`) **and
measured**: the same sentence produces two different outcomes depending on
whether the structured payload rides (see the CX-1 table). The code comment is
telling the truth.

**"A parse failure on them would be silent" is wrong.** Per `backend/main.py:2991`
a parse failure means the structured payload is **never applied**, and the
player gets Berthier's shrug — the loudest failure the game has. Measured
directly. The danger is not silence; it is that the *entire* structured road is
conditioned on a sentence nobody treats as load-bearing.

**Reachability, which the census did not ask:** every one of these parses at
0.95 with an ordinary court, so the gate is always cleared — **except** on a
board where the court has fallen off the parser's nation map. See **MISSED-2**.

**Verdict: SURVIVES at P3, failure model corrected.**

---

### REFUTE:CX-8 — SURVIVES with a count correction; reachability still UNVERIFIED (and my probe could not settle it either)

`main.gd:5660` does call it "old keyword path"; the map runs `:5662-5681`; the
send is `:5687`. ✔

**Two corrections.** `_ACTION_KEYWORD_MAP` has **19** entries, not 18 (14
distinct keywords is right). And because the lookup is
`_ACTION_KEYWORD_MAP.get(action, action)`, an action **absent from the map**
goes into the sentence raw — so the emitted sentence space is not "14 variants",
it is unbounded by the set of actions a settlement affordance can emit.

**Reachability.** The popup has three emitters
(`proposal_confirm_popup.gd:1230`, `:1765`, `:1774`). `_on_option_selected`
binds actions taken from `options[]`, which the index path resolves, so the
fallback cannot fire there. The two settlement-affordance emitters can, if an
action is in neither `data["options"]` nor `SETTLEMENT_DIALOGUE_ACTIONS`
(`main.gd:53-137`, 36 entries). I could not close this: the affordance actions
are composed from row dicts via `_fire_line_action`, not from literals, so a
source census cannot enumerate them.

⚠ **I deliberately do not offer my drive of `Talleyrand, send the Austria
proposal` ("Sire, I await your instructions regarding Austria") as evidence.**
I measured it with no pending dialogue, and the fallback only fires with a
proposal popup mounted. It says nothing about the fallback's behaviour.

**Verdict: SURVIVES as filed (live code, no guard, UNVERIFIED), counts
corrected.**

---

### REFUTE:CX-9 — SURVIVES

`tutorial_overlay.gd` has 22 `"suggest"` keys, **11 distinct non-empty** strings
— matching the census. The handler `main.gd:6721-6730` writes to
`command_input.text` and grabs focus; nothing is sent. The one deliberate
non-bypass. ✔ Note its 11 strings are *tutorial-scenario* names (Senarmont,
Jellacic, Kienmayer), which the census does flag `[F]`.

**Verdict: SURVIVES.**

---

### REFUTE:CX-10 — REFUTED as a hazard; SURVIVES as a description

The interpolation is real, but **two of the six cited lines are stale by one**:
the `str(def[2]) % _region` sites are `region_panel.gd:371` and `:374`, not
372/375. The others (272, 412, 424, 462) are exact.

**The census asserted a hazard and never tested it. I tested it**
(`probes/rf_06_region_names.py`): every one of the **126** provinces on the
shipped map × **5** chip templates (`recruit … in`, `build depot in`, `repair`,
`repair buildings in`, `build watchtower in`) = **630 parses, 0 anomalies** —
no parse failure, no target drift onto a different province, no binding to a
marshal. A collision scan finds nine names that contain or are contained by a
marshal or nation name (`Bern`⊂`Bernadotte`, `Leon`⊂`Napoleon`,
`Brunswick`==a marshal, `Hanover`/`Naples`==nations, `Ile-de-France`,
`East Prussia`, `New Russia`, `White Russia`) and **all nine still resolve to
the province** — WO slice 10's `_correction_survives` gate and the
addressee→province rule are exactly the guard one layer down that the census was
asked to look for.

**Verdict: REFUTED at P4.** The description stands; the hazard does not
reproduce on the shipped map.

---

## PART 2 — WHAT THE CENSUS MISSED

### MISSED-1 (P3) — The region panel is the one click surface that never humanises a marshal name: it renders `Attack ArchdukeCharles`

The census's own §1.1 walked `region_panel.gd` line by line and its CX-2 was
about raw keys reaching the player. It looked only at **nation** keys and only
at the wire, and missed that this panel prints **marshal** keys raw.

`region_panel.gd` calls `Utils.display_nation_name` twice (`:158`, `:444`) and
`humanize_nation_keys_in_text` once (`:477`), and calls
`Utils.humanize_entity_name` **zero** times. Its content goes to its own
`content_area.text` at `:484` — it never passes through `main.gd add_output`,
the humanising chokepoint. `_format_marshal_row` prints `m_name` verbatim
(`:531`) and builds the Attack chip's label as `"Attack " + enemy` (`:557`).

Measured (`probes/rf_07_camel_marshal.py`) on the shipped 1805 boot: two
camelCase enemy keys exist — **`ArchdukeCharles`** (Austria, Carniola, 54,000)
and **`ArchdukeJohn`** (Austria, Tyrol). At FULL visibility they ride
`map_data[<region>]["marshals"]` with the raw key
(`backend/models/world_state.py:9536-9542`), which is precisely the condition
the Attack chip requires. The rendered label is:

```
FORCES PRESENT
  ArchdukeCharles (54,000)   [Fortify] [Drill] [Scout] [Attack ArchdukeCharles]
```

The backend is innocent — driven, `Ney, attack ArchdukeCharles` answers
*"No intelligence on **Archduke Charles**'s position, Sire."* This is the client
surface alone, on a panel the IQ-10 client pass shipped three days ago.

**Fix shape:** `Utils.humanize_entity_name` on `m_name` and on the chip label
only; the meta string must keep the raw key, since that is what the backend
resolves.

---

### MISSED-2 (P2) — The wizard renders an ENABLED button whose command the parser cannot read, once a court loses its last province

This is the seam the census's own thesis points straight at and never checked:
**the wizard's court set and the parser's court set are derived from different
places.**

- Wizard step 1 (`backend/main.py:5575-5580`) lists a court when it
  `has_forces` **or** `has_regions`.
- The parser's nation map, `backend/ai/llm_client.py:562-585
  _extract_known_nations`, is built from **region controllers** plus
  **fog-filtered visible enemy marshals** only.

A remnant — army alive, every province taken — satisfies the first and fails the
second. Measured by conquering the shipped board (`probes/rf_11_remnant2.py`;
all Ottoman provinces to Russia, Abdurrahman alive, fogged):

```
wizard still offers Ottoman?  True
parser still knows  Ottoman?  False

guarantee Ottoman          -> ok=False  Berthier: "this order eludes me"
invest in Ottoman          -> ok=False  Berthier: "this order eludes me"
release Ottoman            -> ok=False  Berthier: "this order eludes me"
sponsor Ottoman, 200 gold  -> ok=False  "Name the court to sponsor, Sire"
buy off Ottoman            -> ok=False  "Name the court to buy off, Sire"
court Ottoman              -> ok=True   (survives — does not read the nation map)
```

Reproduced identically for **Sweden**. Five of the wizard's 28 commands die.

**The reachability is confirmed, not hypothesised.** `GET /diplomatic_preview?nation=Ottoman`
on that same remnant board ships `{"action": "guarantee_nation", "available": true}`
(`probes/rf_13_actkeys.out.txt`) — the wizard draws an enabled **"Guarantee
Their Borders"** button that emits a sentence Berthier refuses.

The code reason is narrow and citable: `guarantee_nation` is selected only when
`any(n in command_lower for n in known_nations_lower)`
(`backend/ai/llm_client.py:2236-2238`); `invest_vassal` (`:2177`) and
`release_vassal` (`:2197`) are selected off nation-keyed keyword lists; and the
whole D5+vassal family binds its target from `known_nations` at `:2294-2298`.

⚠ **Honest limit:** I stripped the provinces by hand rather than playing the
conquest. Both arms are the shipped ones and the engine models remnants (FA
slice 2 has a rung for it), but the *frequency* in real play is unmeasured.

**Fix shape:** feed `_extract_known_nations` from the same roster the wizard
lists — `world.enemy_nations` plus the player — rather than from region control.
It is the same single-source argument this repo applies everywhere else.

---

### MISSED-3 (P2) — 14 of 46 chip templates have ZERO golden-corpus coverage, including the region panel's busiest chip

If the click road *is* a typed road — the census's own headline — then
`tests/data/parser_golden_corpus.json` is its only regression net. The census
never asked how much of the click road that net covers. Measured
(`probes/rf_15_corpus.py`, 447 entries, 46 chip templates):

**Zero coverage (14):** `recruit <arm> in <Region>` · `repair buildings in <R>` ·
`<M>, unfortify` · `<M>, drill` · `Talleyrand, cancel mission with <N>` ·
`increase autonomy <N>` · `decrease autonomy <N>` · `cede territory to <N>` ·
`propose common peace with <N>` · `propose white peace with <N>` ·
`propose vassalization to <N>` · `downgrade relations with <N>` · `never mind` ·
`Talleyrand, <keyword> the <N> proposal`.

A loose word search shows the corpus pins **near neighbours, not the chip's own
shape**, which is the more dangerous state — it reads as covered:

| the chip sends | the corpus pins |
|---|---|
| `recruit infantry **in** Rhineland` | `recruit infantry **at** Paris` |
| `increase autonomy **Holland**` | `increase autonomy` (bare) |
| `cede **territory** to Holland` | `cede **tyrol** to bavaria` |
| `Talleyrand, cancel mission **with Austria**` | `Talleyrand, cancel mission` (bare) |
| `Ney, drill` | `Ney, drill **the troops**` |
| `unfortify` / `white peace` / `common peace` / `downgrade` / `never mind` | **nothing at all** |

Two of these are not ordinary chips: `Talleyrand, cancel mission with <N>` is
one of only **two** backend-authored `action_command` strings in the whole game
(`backend/game_logic/diplomatic_dialogue.py:611`; the other is
`dotation.py:1104`) and is the notice rail's one-click reward/recall road; and
`never mind` is how the clarification popup cancels.

All fourteen **work today** — I drove them. The finding is that nothing stops
them breaking. This is the strongest argument in the whole census's material
for either a structured chip road or a corpus row per chip template, and it was
not made.

---

### MISSED-4 (P3) — The region panel's Cavalry and Artillery chips are cosmetic on the shipped board, and the comment says the executor gates them

`region_panel.gd:270-272` builds all three arm chips unconditionally, under the
comment *"Recruit — all three arms (the executor gates gold/pools/AP)."* The
executor gates gold, pools and AP — it does **not** gate the arm. `requested_type`
only drives a soft-correction message (`backend/ai/recruit_arm.py:1-18`,
docstring: *"drives the soft-correction message"*). Driven on the boot board
(Davout, an infantry corps, at Rhineland):

```
recruit infantry  in Rhineland -> "Davout recruits 3,000 infantry … Cost: 741 gold"
recruit cavalry   in Rhineland -> "Berthier notes: 'Marshal Davout commands infantry, Sire.'
                                   Davout recruits 3,000 infantry … Cost: 741 gold"
recruit artillery in Rhineland -> identical
```

Three chips, one outcome, 741 gold charged either way, and nothing on the chip
says so. The census listed all three in §3 as distinct strings without noticing
two are no-ops wherever a single-arm corps holds the province.

---

### MISSED-5 (INFO) — the measurement the census explicitly punted: **0 of 80 click strings escalate to the LLM** — and the two that most need rescuing are the two the gate blocks

The census's §4.2 wrote: *"a chip escalating to the LLM would be pure waste.
Whether any do is the other agent's measurement."* Measured here, keyless.

The gate is `backend/ai/llm_client.py:63`
(`LLM_FALLBACK_CONFIDENCE_THRESHOLD = 0.7`) consumed by
`_should_fallback_to_llm` (`:895-959`), which is a pure predicate. I ran the
real fast parse for all 80 click strings and asked the real gate with
`provider_name`/`api_key` set to simulate live — nothing downstream is invoked,
no request is made (`probes/rf_16_escalate.py`):

> **WOULD ESCALATE TO THE LLM IN LIVE MODE: 0 of 80.** Every click string sits
> at confidence 0.8–0.95.

Cost of the parse they do pay (`probes/rf_15_corpus.py`, 200 reps each,
in-process mock): **0.73–2.30 ms**. So "every chip pays the parse cost" is true
and the cost is not latency — it is the correctness coupling of MISSED-3.

**The sharp part.** Run the same gate on the MISSED-2 remnant board
(`probes/rf_17_remnant_escalates.py`):

```
guarantee Ottoman          escalates=True   conf=0.5  action=unknown
invest in Ottoman          escalates=True   conf=0.5  action=unknown
release Ottoman            escalates=True   conf=0.5  action=unknown
sponsor Ottoman, 200 gold  escalates=False  conf=0.8  action=sponsor_design
buy off Ottoman            escalates=False  conf=0.8  action=buy_off_design
```

So on the one click-road case that is actually broken, the LLM is doing real
work in live mode and **mock mode — the shipped launcher default — has no
rescue at all**; and the two strings that parse *confidently wrong* (verb
matched, target unbound) are held **below** the escalation gate by their own
0.8 confidence, so the model never sees them in either mode. That is the
concrete, measured answer to whether routing to the LLM earns its keep on this
road: **nothing on the happy path, everything on the failure path, and the gate
is pointed the wrong way for the confident-but-wrong case.**

---

## PART 3 — SCOREBOARD

| id | verdict | note |
|---|---|---|
| CX-1 | **NARROWED** | counts right; free text is a GATE (`backend/main.py:2991`), not a parallel route; 9 pipelines, not 5 |
| CX-2 | **NARROWED** | mechanism confirmed at `backend/main.py:5593`; cited proof invalid; harm is the return direction and is guarded at `add_output` |
| CX-3 | **NARROWED** | 87 distinct, not ~70; all 80 driven parse; two rows wrong about the shipped board |
| CX-4 | **NARROWED** | 16 bypassing endpoints correct; `/save` has a full typed road, `/load` partial; the finding's own count is 5/6/7 in three places |
| CX-5 | **SURVIVES** | and under-counts: `get_llm_config` is dead too |
| CX-6 | **NARROWED** | asymmetry real; "same predicate" is FALSE both ways |
| CX-7 | **SURVIVES** | confirmed by measurement; "silent" is wrong — it is Berthier's shrug |
| CX-8 | **SURVIVES** | 19 map entries not 18; unbounded sentence space; reachability still UNVERIFIED, and my own probe could not settle it |
| CX-9 | **SURVIVES** | 11 distinct suggests, fill-only |
| CX-10 | **REFUTED** | 630 cases, 0 drift; 2 of 6 line numbers stale by one |
| MISSED-1 | P3 | `Attack ArchdukeCharles` — the region panel humanises no marshal name |
| MISSED-2 | P2 | an enabled wizard button the parser cannot read, once a court loses its last province |
| MISSED-3 | P2 | 14 of 46 chip templates unpinned by the golden corpus; the rest pinned by near neighbours |
| MISSED-4 | P3 | the Cavalry/Artillery recruit chips are cosmetic and the comment misattributes the gate |
| MISSED-5 | INFO | 0 of 80 escalate; the broken cases are where the LLM earns its keep, and the gate blocks the worst two |

**Things I checked and found NOT to be defects** (recorded so nobody re-walks
them): the `_chip_command_in_flight` latch cannot leak and the unguarded wizard
cannot double-send; the `negotiate:` chip is guarded on
`controller != "Neutral"` and `visibility != "unknown"` (`region_panel.gd:443`);
`action_command` really does have exactly two backend producers; the naval chip
set really is exactly four (`backend/game_logic/naval.py:2761, 2801/2814,
2825/2845, 2862`); the terminal's own meta handler carries only `diorama:last`
and `cabinet:open` (`main.gd:2395-2408`).

**One claim of mine that was wrong, recorded rather than deleted.** My first
parse probe reported that `invest in <N>`, `release <N>` and `guarantee <N>`
fail to parse on the ordinary board. They do not — I had built `game_state`
by hand without `map_data`, and `_extract_known_nations` reads exactly that.
The endpoint drive corrected it. The failure is real only in the remnant state
of MISSED-2, and that is how it is filed.

---

## PROBES

All under `probes/`, runnable with `.venv/Scripts/python.exe <path>`, all
`LLM_MODE=mock`, no key, no network.

| probe | what it measures |
|---|---|
| `rf_01_tags.py` | the 19 tags the wizard binds; 2 camelCase |
| `rf_02_tagparse.py` / `rf_03_full.py` | tag vs display parse (and the game_state artefact above) |
| `rf_05_drive2.py` → `.out.txt` | **all 80 click strings driven through real `POST /command`** |
| `rf_06_region_names.py` → `.out.txt` | CX-10: 126 provinces × 5 templates = 630 cases |
| `rf_07_camel_marshal.py` → `.out.txt` | MISSED-1: `Attack ArchdukeCharles` |
| `rf_08_structured.py` → `.out.txt` | CX-1/CX-7: the structured gate, four arms |
| `rf_09_court_sets.py` / `rf_10_remnant.py` / `rf_11_remnant2.py` / `rf_12_offered.py` / `rf_13_actkeys.py` | MISSED-2, end to end incl. `available: true` |
| `rf_14_saveload.py` → `.out.txt` | CX-4: the typed save/load road |
| `rf_15_corpus.py` → `.out.txt` | MISSED-3 coverage + parse cost |
| `rf_16_escalate.py` / `rf_17_remnant_escalates.py` → `.out.txt` | MISSED-5: the escalation gate, keyless |
