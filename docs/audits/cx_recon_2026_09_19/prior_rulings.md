# CX RECON — what has already been ruled about the typed road

**Read-only census, September 19, 2026, at master `f7008582`.** Every claim below
either names a `file:line` / symbol or is the output of a probe kept under
`scratchpad/cx_recon/probes/`. Anything I could not execute is marked
**UNVERIFIED** or **REASONED-FROM-SOURCE**.

Navigation note honoured throughout: I navigated by symbol, not by the line
numbers the docs carry. Where I quote a doc's own line number I say it is the
doc's, not mine.

---

## 0. The one-paragraph answer

The typed road is the game's stated pillar and is *also* the surface the project
has spent two years fencing off. Four separate user rulings have narrowed what
typing may do (G1 retires 115+ diplomatic phrases to the Cabinet; PARSE-NEG makes
a refusal terminal; CR-5's bias is live-only by construction; IQ-7 pass 3 makes a
petition answer a closed grammar that fails closed). Meanwhile the client's chips
*are* typed commands, so the click road and the typed road are the same road —
except at one seam, `main.gd::_redirect_diplomatic_command`, where the client eats
**111 of the 447 golden-corpus utterances (24.8%) before the backend sees them**,
and the corpus does not know it. A CX row's real scope is that seam and the
escalation economics above it, not "make the parser understand more words."

---

## 1. Standing rulings a CX row must not contradict

| # | Ruling | Source (authoritative) | Re-open condition |
|---|---|---|---|
| R1 | **Golden Rule 6 — the LLM parses, the executor is deterministic.** CR-5's own distinctness lives at the *router*, not the parser: `route_arm`/`classify_arm` take only `(personality, resolved_bool)` and structurally cannot read an LLM `strategic_score`/`ambiguity`. | `CLAUDE.md` Golden Rule 6; `COMMAND_ROBUSTNESS_SPEC.md` §6.3(a), §6.5 AC-2 | None. Any coupling of `strategic_score` to an outcome "REQUIRES its own design gate per the ROADMAP LLM Mechanical Expansion rules" (CR spec header). |
| R2 | **G1 — the typed diplomatic verbs are RETIRED as a player surface.** User ruling, verbatim: *"the diplo screen should be only path for these actions typing commands should just have it tell them to go to the diplo room or something thematic."* Lands on the **client input path** (`main.gd::_execute_command`, below the redemption block), never as a backend refusal — because the wizard executes by *sending typed commands*. | `DESIGN_REFINEMENT.md` §"AND THE GATE WAS HELD THE SAME DAY" G1 (WO-D2); `WEIRD_OUTCOMES_SPEC.md` §3 slice 7; code `main.gd:1590-1602`, `:1921` | None recorded. **Absorbs WO-4 and most of WO-5.** |
| R3 | **PARSE-NEG: a refusal is terminal and does NOT escalate to the LLM.** A recorded deviation from the filed prescription: under forced tool use every reply must name an action, and the sentence in hand is the one whose verb the player forbade. | `COMMAND_ROBUSTNESS_SPEC.md` §8(4); `BUG_FIXES.md` §PARSE-NEG landing; code `llm_client._should_fallback_to_llm` (`if fast_result.refusal: return False`) | Explicit: *"If CR-6's gate returns yes on free-text classification, this is the boundary that gets re-opened — with the constraint that a model must never be able to re-derive an action the player explicitly forbade."* |
| R4 | **Clauses are blanked with SPACES, never spliced.** Every position-aware rule downstream indexes into the command text; a length-changing edit moves all of them silently. `clause_guards.py` is the single source for the four sentence-shape predicates. | `COMMAND_ROBUSTNESS_SPEC.md` §8(1)(2) | None. |
| R5 | **The guards are subtractive, never decisive.** They change what text the keyword chain reads; they never pick an action. A refusal happens when nothing survives — never because a marker was present. | `COMMAND_ROBUSTNESS_SPEC.md` §8(3) | None. |
| R6 | **Conditional orders are refused, not executed.** `if/unless/when/once/after` with a real (two-word) clause issue nothing; `until` is the sole exception because `StrategicCondition` implements it. `Ney, retreat if outnumbered` is pinned **accepted-not-ideal** (`parseneg-retreat-if-outnumbered-executes`). | `COMMAND_ROBUSTNESS_SPEC.md` §8(5) | "A real conditional-order system is **CR-6/CR-7 scope**." |
| R7 | **A question routes to `help`, after diplomatic routing** — Talleyrand's desk keeps precedence. FA-D25's *fact* half is built (`question_desk.py`); **advice and feasibility stay CR-8's.** | `COMMAND_ROBUSTNESS_SPEC.md` §8(6); `DESIGN_REFINEMENT.md` FA-D25; `BUG_FIXES.md` SLICE 7 (vi) | "A question-answering Berthier is CR-6's to build; when it exists, it **replaces the `help` route, not the guard**." |
| R8 | **A question never ANSWERS a dialogue.** A line containing `?`, or flagged by `is_question`, or carrying a subject-auxiliary inversion anywhere (`shall/will/…` + `we/i`), answers no dialogue on any family. Exact option ids, digits and exact labels are exempt. | `BUG_FIXES.md` IQ7-RV25 / RV32, lever `dialogue_routing.A_QUESTION_NEVER_ANSWERS` | None. |
| R9 | **A client petition's typed answer is a CLOSED literal allowlist keyed to the petition's own subject, and it FAILS CLOSED.** An unaccepted phrasing is a *re-prompt by design*, re-prompted **in place** so nothing mounts over the petition. `they` is deliberately out of the allowlist; auxiliaries answer in STATEMENT order only. | `BUG_FIXES.md` IQ-7 review-round passes 2–4; `IMPROVEMENT_QUEUE_SPEC.md` §1.6 | None. ⛔ The recorded lesson: *"a rule built by stripping what you recognise is only as safe as the list it strips — for an irreversible priced answer, write the allowlist out and fail closed."* |
| R10 | **CR-5's personality bias is LIVE-ONLY by construction.** `parse_resolved_to_action` returns False for `mode=="mock"`; the shipped default is `LLM_MODE=mock`, so a default-config player is guaranteed *correct*, not *biased*. | `COMMAND_ROBUSTNESS_SPEC.md` §6.9, §6.7 "Live-only exposure"; `.env.example` (verified: `"mock" … - DEFAULT`) | None. Framing note, not a defect. |
| R11 | **Delegation is feel-first and mechanically OPTIONAL.** "Neither rider (d) nor CR-5b makes delegation *mechanically* competitive with explicit verbs — both are **feel** carrots." | `COMMAND_ROBUSTNESS_SPEC.md` §6.4 "Named open gap" | A "mechanical delegation incentive" is a **parked row owned by the CR-6/CR-7 gate** (§4). |
| R12 | **Every inferred-resolution surface NAMES the acting marshal's personality** — required, not polish; without it CR-5 ships *invisible*. | `COMMAND_ROBUSTNESS_SPEC.md` §6.3(c), AC-7 | None. |
| R13 | **One modal, objection-first.** An inferred battle-starting action runs `evaluate_situation`; if the marshal objects the objection IS the gate; else bad odds → one lightweight confirm; else execute + soft note. Never two modals. The gate must cover **attack-on-arrival**, fortification-aware. | `COMMAND_ROBUSTNESS_SPEC.md` §6.3(c), §6.8 SPEC FIX | None. |
| R14 | **`personality_type` = CHARACTER, never situation.** "Danger is handled by guardrails (§6.3c), not by falsifying character." Earned by reverting a Massena recast. Soult-literal is canon since MC-4; the rule is now **unconditional**. | `COMMAND_ROBUSTNESS_SPEC.md` §6.8 + MC-4 addendum; `MARSHAL_CONTENT_PASS_SPEC.md` §9 | None. |
| R15 | **Temperature 0 on the PARSE body only.** The Berthier recovery call is narrative and keeps the server default. Verified: `providers.py` parse body `"temperature": 0`; `ProviderConfig(..., temperature=0.3)` is the config default the Berthier body inherits. | `COMMAND_ROBUSTNESS_SPEC.md` §6.3(b); code `backend/ai/providers.py` | None. |
| R16 | **At most ONE blocking LLM call per request** (`ParseResult.llm_error` + `skip_llm` + the `reparse_with_llm` guard). Exception, pinned: a *gibberish* utterance costs **two** (parse tool-mode, then Berthier text-mode). | `SYSTEMS_REFERENCE.md` §5 "CR-3 latency guard"; `COMMAND_ROBUSTNESS_SPEC.md` §9 tiers ("Berthier's second call (2)") | None. |
| R17 | **The suite is keyless by CONSTRUCTION.** `LLM_MODE=mock` is a MODULE-LEVEL assignment in `tests/conftest.py` (an autouse fixture alone leaves `backend.main`'s import-time parser singleton live), plus the autouse pin and a loopback-only network guard. A cassette miss is a `BaseException`. The cassette key is `(kind, utterance, world)`, never the prompt hash. **The suite never records.** | `SYSTEMS_REFERENCE.md` §48; `COMMAND_ROBUSTNESS_SPEC.md` §9; `IMPROVEMENT_QUEUE_SPEC.md` §1.8 | Never-do list is explicit: *"record from the suite; key a cassette on the prompt hash; raise an `Exception` for a miss; ban loopback; put the `LLM_MODE` pin in a fixture alone."* |
| R18 | **Prompt caching assessed and REJECTED, with the reason recorded so it is not re-litigated.** | `docs/STATUS.md:10464` | ⚠ **Two of its three premises do not reproduce — see §4, finding F3.** |
| R19 | **The bare `attack` resolve-and-rewrite happens at the DISPATCH seam**, so the whole named-attack pipeline applies unchanged (objection block untouched, zero lines changed). Ask when >1 commandable marshal in contact; muster gate armed; objections routed. | `COMMAND_ROBUSTNESS_SPEC.md` §7 (the CR-6 mini-gate, blessed by the user July 16, 2026) | None. |
| R20 | **A sentence the game PRINTS must be a sentence the parser knows**, pinned as a drift test between the producer's copy and the parser's keywords. | `SYSTEMS_REFERENCE.md` §49; `BUG_FIXES.md` IQ10-6 | None. ⚠ The pin is backend-only — see §4, finding F1. |
| R21 | **Every chip carries the full typed command** — *"the same string a player would type; the executor owns every gate."* Every chip pipeline **bypasses the G1 fence by construction**. | Code comment `region_panel.gd::_on_meta_clicked`; `main.gd:1595-1598` | None. |
| R22 | **`proposal_result_popup` is RETIRED.** A dialogue that concludes with a CHOICE needs its own popup; do not reach for that field. | `DESIGN_REFINEMENT.md` FA-S17-D9; `CLAUDE.md` troubleshooting row | None. |

---

## 2. Explicitly DEFERRED — who owns what

### 2a. Routed to **CR-6 *proper*** (ROADMAP position **15**, gate first, still unbuilt)

ROADMAP row 15 verbatim: *"**CR-6 proper — Conversational Objection Negotiation.**
Gate first: may the LLM classify a free-text rebuttal into the **existing
deterministic** Insist/Trust/Compromise buckets? That is the GR6 boundary case and
the user's call. Mock fallback = today's three buttons."* — and *"The most
VISION-central unbuilt feature in the repo."* Note on the row: *"the CR-6 gate slot
was consumed once by the S5-D1 bare-attack mini-gate — this is the other CR-6."*

| id | What is owed | Filed | Completion recorded on the row |
|---|---|---|---|
| **IQ9-X1** | The CR-2 forced retry **cannot rescue the word-scan family** — `hunt down mack` binds `down`→Davout at 0.9, the retry fires once, and the marshal-less live parse is re-run through the fuzzy pass whose word-scan re-reads `down`→Davout. One live call, discarded. | `BUG_FIXES.md` §The Keyless Parser Gate | "the retried live parse is ADOPTED when it resolves the marshal the fast pass mis-bound; the pin above flips; new `tests/test_cr6_retry_rescues_the_word_scan.py`" |
| **IQ9-X2** | The fuzzy suggestion can name a **FOGGED enemy** (`_extract_enemy_marshal_names` is omniscient; R5). | same | "the suggestion list reads the player's visible enemies (`get_visible_enemies`) while matching stays omniscient (the WO slice-10 shape)" |
| **IQ9-X3** | A live-road failure stamps `parse_mode: "mock"` (a failure dict carries no `mode`; `main._PARSE_PROVENANCE` reads it). | same | "the failure dict carries `mode` and the stamp reads it; the pin above flips" |
| **IQ7-X7** | **A deferred or conditional typed answer still signs an ORDINARY letter** (every non-petition family). Measured: `accept the offer later`, `accept it next turn`, `is that a yes`, `yes, later`, `if we accept`, `accept the offer, but not now`, `maybe accept` each sign PEACE→OPEN_BORDERS. | `BUG_FIXES.md` §The Satellites Have a Position | "every dialogue family's typed answer is read by a closed, per-family grammar that fails closed, so the seven lines resolve to None and execute nothing through `/command`" |
| **R6 above** | A real conditional-order system (`if/unless/when`). | `COMMAND_ROBUSTNESS_SPEC.md` §8(5) | CR-6/CR-7 scope |

### 2b. Routed to **CR-7 (backlog)** — no gate, no schedule

`COMMAND_ROBUSTNESS_SPEC.md` §2 CR-7 row owns: conditional/compound orders (wire
or replace `parse_multiple`), command-surface shortcuts, map-driven command
context, the fuzzy **autocomplete dropdown UI**, and **R158 parse-confidence
display**. Verified today:

- `parse_multiple` still exists at `backend/commands/parser.py:2204`; its only
  in-`backend/` caller is the `__main__` demo block at `:2356`. **Still dead in
  production.**
- `validation.py:413` still returns the player-facing string
  `"Multi-marshal commands coming in a future update!"`. Reachable **live-mode
  only** (`result.marshals` is an LLM field; the mock branch never sets >1), and
  **zero tests reference it**. A live "coming soon" promise with an owner row and
  no landing slice.
- **R158 is not built:** grep of every `.gd` finds no surface rendering parse
  confidence; `parse_mode` is set on the response (`main.py:568`) and read by
  **no** `.gd`.

### 2c. Held for **CR-8** (the two-way channel), unchanged since the July-5 gate

- *"Ney, what do you see?" / "Berthier, can we take Vienna before winter?"* —
  military-side advisory. **HELD for CR-8** (`COMMAND_ROBUSTNESS_SPEC.md` §4).
- FA-D25's **advice and feasibility halves** stay CR-8's; only the *fact* half
  shipped (`question_desk.py`, slice 7).
- **FA-S7-D1** observation homed here: the live parser reads *"fix bayonets"* and
  *"cover the retreat"* as a cavalry **CHARGE**. Fixed with one prompt line; *"CR-6/CR-8's
  gate owns the model-side vocabulary."*

### 2d. Held elsewhere

- **Commander-intent orders** ("Take Vienna" → Berthier proposes the assignment) —
  HELD as a **CR-2 extension**.
- **Tone parsing** (phrasing → trust modifier) — shares the **CR-6 gate**; mechanical.
- **Pre-battle councils** — its own **mini-gate after CR-6**.
- **Autonomous "Grouchy Moment"** — **RE-HOMED OUT of CR-5**, needs a dedicated
  marshal-autonomy gate. It is an event/AI feature: the parser has no read access
  to a marshal's `StrategicOrder` and `VALID_ACTIONS` has no continue/noop verb.
- **Mechanical delegation incentive** — parked for the **CR-6/CR-7 gate**.
- **`cover / watch / keep an eye on [X]`** — CUT from CR-5; re-add post-playtest
  **only** as a named row with its own table entry + test. *"Do not half-implement."*
- **Anti-memorization / creative-phrasing bundle** — gated behind CR-4/CR-5 per ROADMAP.
- **Groq** — a stub; Pre-EA BYOK. Confirmed: `GroqProvider` exists, `LLM_MODE=groq`
  degrades to fast-parser-only.
- **IQ10-X1 / IQ10-X2** — routed to "the next UI slice" (top bar overflows at
  Interface Scale 2.0; the petition's decisive line sits at the fold).

### 2e. What position 10 (the shippable build) needs from this area

Row 10's remainder, verbatim: *"the fresh export itself + verify JSONs in the
.pck, the v1 LLM touchpoints below, client-side supervision beyond the launcher's,
and the clean-machine run."* The **LLM-access v1 touchpoints are owned by that row**
and are player-facing typed-road copy: rename every surface off "API key" →
**"Smarter Parsing (optional) — Connect your Anthropic account"** with three-fears
copy, a live status line, a once-ever non-modal Berthier hint on first keyless
campaign start, and a quiet once-per-session *"clerks could not reach the wire"*
notice on live-parse failure. **A CX row must not build these — they are row 10's.**

---

## 3. The strongest recorded arguments, both quoted

### FOR the typed road

> "A Napoleonic strategy game where you **talk to your generals** — and they talk
> back." … "Players don't click armies. They type commands" — `docs/VISION.md:9,13`

> "**Every input gets a response.** No silent failures. The game always talks
> back." — `docs/VISION.md:78` (Design Philosophy #4)

> "**Vision anchor:** This IS the game's core pillar — 'you talk to your generals'
> — and design philosophy #4 ('Every input gets a response. No silent failures.')."
> — `COMMAND_ROBUSTNESS_SPEC.md` header

And the sharpest institutional statement, on the ROADMAP row that still owes a gate:

> "The most VISION-central unbuilt feature in the repo." — `ROADMAP.md` position 15

### AGAINST it (the strongest is a user ruling, not an argument)

> *"the diplo screen should be only path for these actions typing commands should
> just have it tell them to go to the diplo room or something thematic."*
> — the user, quoted verbatim in `DESIGN_REFINEMENT.md` G1 (WO-D2)

Backed by the phase's own honest self-assessment:

> "**Audience (stated, not implied).** Delegation verbs are a **feel-first
> affordance for the roleplay/immersion player** … **not** the optimizer. Explicit
> verbs remain mechanically dominant (the §6.4 named gap), so success is *not*
> universal adoption" — `COMMAND_ROBUSTNESS_SPEC.md` §6.7

> "**This phase declares delegation feel-first / mechanically-optional.**"
> — `COMMAND_ROBUSTNESS_SPEC.md` §6.4

> "**Live-only exposure (honest denominator).** CR-5's personality bias is a
> **live-LLM feature.** The shipped default is `LLM_MODE=mock` … where a delegation
> verb degrades to the CR-2 clarification (guardrail e) with **no bias** —
> default-config players are guaranteed *correct*, not *biased*." — §6.7

**The tension in one line:** the pillar says typing is how you play; the rulings say
typing is how you *talk to marshals*, and everything that is a matter of state has
been moved to a screen.

---

## 4. Things in the record that are now FALSE or unreproducible (each measured)

> All token figures below are **ESTIMATED from character counts** (chars ÷ 3.6 and
> ÷ 4.0 shown as a band). I could not call `count_tokens` — the conftest network
> guard refuses non-loopback and I am read-only/keyless. Character counts are exact.

### F1 — ⚠ NEW, live, one day old: IQ10-6 opened a hole in the G1 fence, and the drift pin cannot see it

`llm_client.py:1574` (IQ-10, Sept 19) now accepts **both** `gather intel on` and
`gather intelligence on`. The client's `DIPLO_FAMILY_KEYWORDS` in `main.gd` carries
**only `gather intel on`**; `"intelligence"` appears nowhere in `main.gd` except an
unrelated `data.get("intelligence")`. Substring logic verified in Python:

```
"gather intel on"  in "gather intelligence on austria"  ->  False
"gather intel on"  in "gather intel on austria"         ->  True
```

So in the real client the **short** form is redirected to the Cabinet (sends
nothing) and the **long** form — the sentence the game itself prints
(`MISSION_DESCRIPTIONS["GATHER_INTEL"]`) — falls through and **executes the
mission**. Two spellings of one order take two different roads.

**Why nothing caught it:** IQ-10's own pin
(`test_iq10_client_pass.py::TestTheMissionSentenceIsTypable`) drives
`POST /command` through `TestClient`, which bypasses `main.gd` entirely; and the
fence's drift guard, `tests/test_wo_slice7_cabinet_door.py::TestTheMirrorAgreesWithTheParser`,
iterates a **hand-authored 78-entry `CANDIDATE_SENTENCES` list**, measured to
contain `'gather intel on Austria'` and **not** the long form. The pin is green
about it. This is the project's own recorded lesson — *a census must count the
THING, not a string in two files* — one layer up.

**REASONED-FROM-SOURCE**, not executed: I ported `_redirect_diplomatic_command` /
`_matches_cabinet_family` to Python with the tables parsed out of the real `.gd`
(`probes/client_fence.py`). I did not run Godot.

### F2 — the same fence eats a quarter of the golden corpus, and the corpus does not know

Measured by `probes/client_fence.py`: **111 of 447 corpus utterances (24.8%)** are
claimed by the client and never sent. Named cases:

| typed sentence | client verdict | why |
|---|---|---|
| `cede Tyrol to **the** Kingdom of Italy` | **passes** → backend, works | `" to kingdom of italy"` is not a substring of `" to the kingdom of italy"` |
| `cede Tyrol to Kingdom of Italy` | **EATEN** | `cede/grant-to-court` arm |
| `cede tyrol to bavaria` *(a corpus row)* | **EATEN** | same |
| `grant tyrol to bavaria` *(a corpus row)* | **EATEN** | same |
| `Talleyrand, grant the petition` | **EATEN** | `diplomat-addressed`; `petition`/`grant` are not in `DIPLO_ADDRESS_EXEMPT_WORDS` |
| `grant the petition` | passes | no family keyword |
| `Ney, attack Mack` / `recruit infantry in Paris` / `build ships at Brest` | pass | fence is fail-open on non-diplomatic verbs, as designed |

Two of these matter because a landed fix names them:

- The IQ-7 review round's headline P1 was *"the game's own `cede` verb beside the
  popup's Grant"*. Its tests type `cede Tyrol to the Kingdom of Italy` through
  `TestClient`. **Whether that fix is reachable in the real client depends on
  whether the player types the word "the."**
- IQ7-RV24 fixed *"the game's own diplomatic address stopped answering —
  `Talleyrand, grant the petition`, the address Berthier's own help teaches."*
  The client eats that exact sentence at the diplomat-address arm.

⚠ **UNVERIFIED and material:** I could not establish whether the command input is
*enabled at all* while a petition popup is up. `_execute_command` has **no
pending-dialogue bail** above the fence (verified: `main.gd:1528→1602`, the only
early returns are empty-input, the end-turn phrasing gate and the redemption
tokens), so if input is live the fence fires. If a modal disables input, the typed
petition route is reachable only from the letter-book. **This needs one client run
to settle and it decides how big F2 is.**

Not filed as a defect here — it may be exactly what G1 intends. Filed as: *the
corpus is measuring a road 24.8% of which no player walks, and no test compares the
two vocabularies except through a hand list.*

### F3 — the prompt-caching rejection has the wrong number and an undercounted prompt

`docs/STATUS.md:10464`: *"tools+system is ~700 tokens, below Haiku 4.5's
**2048-token** minimum cacheable prefix, and the volatile game state sits at the TOP
of the **~3.7K-token** user prompt."*

Measured on the shipped 1805 boot, turn 1, no history (`probes/prompt_cost.py`,
`probes/prompt_anatomy.txt`):

| piece | chars | est. tokens (3.6 / 4.0) |
|---|---|---|
| `PARSE_TOOL` JSON | 2,860 | 794 / 715 |
| system prompt | 177 | 49 / 44 |
| **user prompt** | **16,582** | **4,606 / 4,146** |
| **total** | **19,619** | **5,450 / 4,905** |

- **"~700 tokens" for tools+system** — measured ~843/759. Close enough; not the error.
- **"~3.7K-token user prompt"** — measured **4,606/4,146**. Undercounted by 12–25%.
- **"Haiku 4.5's 2048-token minimum cacheable prefix" is WRONG.** Per the Anthropic
  prompt-caching reference, Haiku 4.5's minimum cacheable prefix is **4096 tokens**
  (the minimum is not monotonic: 512 on Opus 5, 1024 on Opus 4.8/Sonnet 5, 2048 on
  Opus 4.7, **4096 on Opus 4.6/4.5 and Haiku 4.5**).
- **The load-bearing claim HOLDS and is confirmed:** the volatile state sits at the
  top. Measured section order — `## Your Marshals` (399 chars) and `## Enemy Forces`
  (202 chars) occupy the first ~640 chars; everything after (`## Valid Actions`
  through `## Examples`, ~15,900 chars ≈ 4,400 tokens) is **static per boot**.

**Net effect on the decision:** the conclusion survives, both premises move, and
they move in *opposite* directions. Against caching: the stable-by-construction
prefix (tools+system, ~843 tok) is **five times** below the real 4096 floor, not
just under a 2048 one. For caching: the static tail is ~4,400 estimated tokens —
i.e. **just over** the floor, which the record's arithmetic never considered because
it treated the whole user prompt as volatile. The restructure the record declines
("a prompt restructure whose regression risk outweighs the saving") is therefore
**marginal-but-arguable**, not clearly-not-worth-it, and its margin depends on an
estimate I could not tighten without `count_tokens`. Re-litigating it needs a real
token count first, not another estimate.

### F4 — the "live-LLM-only" backlog is stale for 8 of its 18 rows

`tests/data/parser_golden_corpus.json` → `live_phrasing_backlog.description`:
*"Marshal-less strategic phrasings the keyword-seam tests cover but the MOCK action
chain cannot parse — live-LLM-only capabilities today. NOT evaluated by the
harness."*

Re-measured through the real `CommandParser.parse` in mock (`probes/backlog_now.txt`):
**8 of 18 now parse on the 1805 board** (7 of 18 on legacy) — `link up with davout`,
`follow and destroy wellington`, `stand fast at belgium`, `hold your ground`,
`rally to ney`, `come to the aid of davout`, `bolster ney's position`,
`combine with davout`. FA slice 7's plain-speech and SUPPORT work landed them.
They remain **unpinned** (the backlog is not evaluated by the harness), so this is
shipped capability with no regression gate.

### F5 — "447 entries" and "686" are both right, for different units, and the docs never say which

Measured: the corpus holds **447 entries**; `worlds_for_entry` expands them to
**692** entry×world cases; the default eval loop skips the 6 cases produced by the
4 `live_only` rows, giving **686**. CLAUDE.md's *"Corpus count corrected 681 → 686"*
is the loop count; the task brief's "447" is the entry count; CR spec §2's "233" and
PARSE-NEG's "514/514" and slice 7's "647/675" are historical. Tier split measured:
**394 both-worlds / 49 `mock_only` / 4 `live_only`.**

### F6 — records that DO reproduce (checked, so the next session need not)

- `build_clarification_prompt` is CUT (`prompt_builder.py:855` carries the tombstone;
  a test asserts `not hasattr`). ✅
- `.env.example` documents `mock` as DEFAULT. ✅
- Temperature 0 pinned on the parse body only; Berthier keeps the server default. ✅
- Model pin `claude-haiku-4-5`, `max_tokens=1000`, forced `tool_choice`. ✅
- `clause_guards.py`, `question_desk.py`, `parser_eval.py`, cassettes and
  `tests/_parser_replay.py` all exist as described. ✅
- `region_panel.gd` emits full typed commands; `main.gd:6399` runs them through the
  typed pipeline; **15+ `api_client.send_command` call sites** in `main.gd`. ✅
- CR spec §1's line numbers are the **July 2, 2026 audit state** and the section says
  so; they are history, not live claims. The P0 they describe (4 hardcoded legacy
  marshals) was closed by CR-0.

---

## 5. What this means for scoping a CX row (offered, not decided)

1. **The parser is not the bottleneck — the fence and the instrument are.**
   Escalation measured at **6.4%** of corpus utterances on the 1805 board
   (25/392: 88.3% confident fast parse, 6.4% escalate, 5.4% terminal refusal —
   `probes/escalation_rate2.py`, production seam with the pre-parse typo repair
   applied as `CommandParser.parse` does it). Of those 25, **21 expect FAILURE** —
   the corpus's own Berthier-shrug rows — and each of those costs **two** live
   calls (parse, then Berthier recovery). ⚠ Honest limit: the corpus was mined from
   parser tests, so it over-represents what the mock already handles; it is **not**
   a sample of what a player types. Any "is routing to the LLM worth it" ruling
   needs a real typed-utterance log, which the record does not contain.
2. **A text predictor / autocomplete already has an owner row** (CR-7, "fuzzy
   autocomplete dropdown UI") and no gate. It is the cheapest thing on this list and
   the only one with no standing ruling against it — but R2 constrains it hard: an
   autocomplete that suggests a diplomatic verb would suggest a sentence the client
   then refuses to send.
3. **The highest-value measured work is the fence's drift guard**: replace
   `CANDIDATE_SENTENCES` with a census derived from the parser's own vocabulary, so
   F1's class cannot recur. That is small, it is testable offline, and it is the
   thing that would have caught yesterday's regression.
4. **Do not re-open** R2 (G1), R3 (refusal is terminal), R9 (closed petition
   grammar) or R14 (personality=character) without the user. R18 (caching) *may* be
   re-opened on evidence, and F3 gives the evidence a starting point and a warning
   that its own numbers are estimates.

---

## Probe index (all under `scratchpad/cx_recon/`)

| file | what it measures |
|---|---|
| `probes/corpus_stats.py` → `corpus_stats.txt` | corpus entries, world expansion, tier split |
| `probes/escalation_rate.py` → `escalation.txt` | escalation at the `llm_client` seam (over-counts: misses the pre-parse typo repair) |
| `probes/escalation_rate2.py` → `escalation2.txt` | escalation at the **production** seam, both worlds, with every escalating utterance listed |
| `probes/prompt_cost.py` → `prompt_cost.txt` | parse-prompt size; what the escalating rows expect |
| `prompt_anatomy.txt` | per-section prompt anatomy; where the volatile state sits |
| `probes/client_fence.py` → `client_fence.txt` | Python port of the G1 fence, tables parsed from the real `.gd`; the 111-row corpus census |
| `probes/backlog_now.txt` | the 18 "live-only" backlog phrasings re-measured in mock |
| `probes/census_rows.py` → `dr_parse_rows.txt` | DESIGN_REFINEMENT rows touching parsing/commands, with their statuses |

No file under `backend/`, `godot-client/`, `tests/`, `docs/` or `tools/` was
modified. No git-mutating command was run. No network call was made.

---

## 6. ⚠ CONCURRENT WRITER — the tree changed under this recon, mid-session

**The session began on a clean tree** (the harness's own git snapshot recorded
`Status: (clean)` at `f7008582`). By the time I finished, `git status` reported:

```
 M backend/ai/clause_guards.py      (+71 / -2)
```

**I did not make that change** — this recon touched no file outside its own
scratchpad and ran no git-mutating command. It is a concurrent writer: either a
parallel agent in this workflow or the user's own in-flight work. **I left it
alone.**

It is not a crashed mutation sweep. It is a coherent, fully commented implementation
of **"CX slice 1 — A QUESTION NEVER ORDERS"**, behind a flip lever
`clause_guards.A_QUESTION_NEVER_ORDERS = True`, adding: four subject-WH leads that
cannot open an imperative (`who/whom/whose/why`), a contracted-auxiliary arm
(`where's Ney`), and three deliberative openers (`what about …`, `how about …`,
`is it time to …`). Its own recorded measurements are that `why not attack Mack`
fought a real battle across six corps, `why not retreat` retreated the whole army,
and `what about attack Mack` / `how about retreat` / `is it time to build a depot`
each committed the deed.

**Does it move anything in this report? No — measured** (`probes/clause_guards_HEAD.py`
exported via `git show HEAD:…` into the scratchpad, then both modules loaded side by
side, `concurrent_delta.txt`):

- **0 of 447** corpus utterances change their `is_question()` verdict between HEAD
  and the working tree. Every number I publish above is therefore unaffected, and
  the escalation/anatomy probes are valid either way.
- Independently confirms the slice's own claim ("the four-word rule moves 0 rows").
- All seven of its named cases flip `False → True` as intended, and the corpus pin
  it names as the refutation of the wider rule — `when ready then retreat` — correctly
  stays `False` on both trees.

**Two consequences for whoever reads this recon:**

1. **Sections 1–4 are complementary to that slice, not in conflict.** It closes a
   hole in `is_question` (R7's territory) on the *backend*. Nothing in it touches the
   G1 client fence (F1, F2), the escalation economics (§5.1), or the prompt-caching
   arithmetic (F3) — so those findings stand and are still unowned.
2. **F1 is now more urgent, not less.** That slice adds new question-shaped
   phrasings to the backend's understanding. The fence's drift guard
   (`TestTheMirrorAgreesWithTheParser`) iterates a hand-authored 78-sentence list, so
   it will be green about any of them too. The census fix recommended in §5.3 is the
   guard that would cover both.
