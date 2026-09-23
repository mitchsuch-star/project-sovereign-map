# Local LLM for the Parser — feasibility (amends HC-L §7b)

> **Status: INVESTIGATION + RECOMMENDATION. Nothing here is built, gated or
> approved.** Produced September 20, 2026 by a 53-agent read-only fleet
> (18 recon -> 18 adversarial refuters -> 7 competing plans -> 6 judges ->
> 4 syntheses), driving the real `POST /command` and the real
> `CommandParser.parse` against an unmodified `europe_1805.json` boot world at
> HEAD `15c498cb`, `LLM_MODE=mock`, seed `historical`. No repo file was modified
> during the investigation.
>
> **User ask: "examine feasibility for local llm for parser making the game just work and how hard it would be."**
>
> Every claim below carries a confidence marker. **measured** = the agent ran it
> and is reporting output. **read** = the code path was read end to end.
> **inferred** = judgement. Claims that could not be reproduced are recorded as
> such rather than deleted. Line numbers were current at measurement time; this
> repo's own records say ~80% of filed line numbers go stale, so **navigate by
> symbol**.

---

## Verdict in one paragraph

Technically feasible but strategically narrow: a local model closes exactly one command family (CR-5 delegation), because 9 of 9 measured "the game acts on an order you didn't give" cells parse at 0.90–1.0 and never reach any model tier. Fund a 1.5-session decision package (instrument + prompt reorder + ceiling probe), not the 8.5-session build — with a hard kill at p50 > 3.0s.


## Key numbers (all measured unless noted)

- 9 of 9 measured defect cells never reach a model — compound, conditional-inversion, multi-marshal and the invade misroute all parse at 0.90–1.0, above the 0.7 gate (measured on the 1805 board through the real gate)
- 40 of 56 compound cells swallow the first clause silently; the 4 that warn are exactly FA-7's stand-still carve-out (hold/wait/stand fast/stay put)
- KV prefix between two calls with the SAME utterance one battle apart = 95 characters (0.6%) — a local model re-prefills ~4,500 tokens cold on essentially every parse
- Parse payload = 19,616 chars ≈ 5,449 tokens; '## Command to Parse' sits at 75.7% with 4,024 static chars (1,118 tokens) AFTER it
- Latency bar is 3s, not 30s: providers.py:99 REQUEST_TIMEOUT_SECONDS = 5.0, MAX_RETRIES = 1, cloud documented at 1-3s. The Godot 30.0s is not the bar
- Golden corpus = 688/688 passed under mock, 0 failed — zero headroom; §7b's ship/no-ship number cannot move upward
- 19 cassettes / 34 provenance entries, ALL 'authored', 0 'recorded' — no cloud baseline exists in the repo either
- Held-out set that does exist: 9 archives with llm='anthropic', 334 CMD lines
- classify_arm(personality, parse_resolved_to_action: bool) — the model's verb never reaches the arm decision; the job is a boolean
- parse_resolved_to_action denylists exactly 'mock': measured mode='local' -> True, so a local provider inherits the CR-5 arms on day one
- llm_client.py:1062 'if not self.api_key: return False' — a keyless local provider is loaded, packaged, shipped and never consulted
- LLM_MODE=local resolves to 'mock' with a warning; get_provider('local') raises ValueError
- len(VALID_ACTIONS) == 56, 'unknown' in VALID_ACTIONS == False, PARSE_TOOL enums == 0
- Working OpenAI-compatible provider = ~93 non-comment lines, 7 files / 11 production call sites, 15 test files


## Open questions that need your ruling

- The latency bar: §7b says 'parse latency <= the cloud round-trip', which providers.py documents at 1-3s. Do you hold that bar (which likely admits only the 0.5B class), or re-gate to a measured abort budget on the grounds that the local road only runs where the game currently shrugs? This is a gate question, not a builder's call.
- CR-5 delegation is 100% dead for keyless players today — Ney/Davout/Soult 'deal with Mack' all return unknown/0.5 and route to ASK. Is shipping that marquee three-way personality split to non-paying players worth ~5.5 sessions if the probe passes?
- L-1 (the prompt reorder) is worth doing regardless of the local decision — it makes the existing BYOK road cheaper on every escalated call. Land it now, or hold it with the rest?
- If the probe passes, the model ships as opt-in DLC per §7b — which preserves the drafted Steam disclosure ('no AI required', 'off by default'). Confirm you do not want it in the base build, because that rewrite re-gates the AI disclosure.


---

# Local LLM for the parser — feasibility

## 1. The verdict

**Feasible, narrowly — and it is not what makes the game "just work."**

| | digits |
|---|---|
| Cost to a **permanent** yes/no | **1.0 session** (instrument + ceiling probe) |
| Plus the one edit worth making regardless | **0.5 session** (prompt reorder — pays for itself on the existing BYOK road) |
| Cost to **ship** on a pass | **+4.0 sessions** |
| Worst case | **5.5 sessions** |
| The version to refuse | **8.5 sessions** behind three gates, latency verdict not arriving until session ~4 |

The framing correction that decides this: I drove nineteen phrasings through the real `_should_fallback_to_llm` on the shipped 1805 board with a keyed live provider simulated, so the gate's real arms were the ones evaluated. **Nine of them are cells where the game acts on an order the player did not give. All nine parse at 0.90–1.0 and return `ESCALATES=False`.** No model — cloud, local, 0.5B or Opus — is ever consulted for any of them.

```
class       utterance                                    action   conf  refusal      ESC
COMPOUND    Ney, scout Swabia then attack Mack           attack   0.95  None         False
COMPOUND    Ney, recruit infantry in Rhineland then att  attack   0.95  None         False   <- target=Rhineland (ours)
COND  +     Ney, attack Mack if he is fortified          unknown  0.5   conditional  False   <- correct
COND  -     Ney, attack Mack if he is not fortified      attack   0.95  None         False   <- fails OPEN
COND trail  Ney attack Mack should the enemy advance     attack   0.95  None         False
MULTI       Soult and Lannes, attack Mack                attack   0.95  None         False   <- Lannes dropped, no warning
VERB        Ney, invade Swabia                           error    1.0   None         False   <- diplomatic misroute
DELEG       Ney, deal with Mack                          unknown  0.5   None         True
VOICE       Murat, ride at the enemy                     unknown  0.5   None         True
```

Generalised: the compound matrix is **40 of 56 cells swallowed** (first clause discarded, `action=attack`, no `dropped_sequel`, no warning). The 16 that warn are exactly `hold` / `wait` / `stand fast` / `stay put` — FA-7's stand-still carve-out, which is precisely why the rest are still broken.

So "will a local LLM make the game just work" is **measured no**. The question that survives is narrower and has a better answer.

## 2. What "just work" already means, and the actual gap

Mock is the shipped default and it is strong: the fast parser answers ~82–90% of commands confidently in **median 0.85 ms**, and the golden corpus scores **688/688 under mock**. The deterministic layer is not the weak half.

The gap is one family, and it is real content, not convenience. `backend/commands/delegation.py:398`:

```python
if (parsed.get("mode") or "").lower() == "mock":
    return False
```

Measured on the 1805 board: `Ney, deal with Mack`, `Davout, deal with Mack` and `Soult, deal with Mack` all return `unknown` / 0.5 / `route_arm -> ask`. The `1b-livevoice2-historical-r1` archive shows those same three sentences on the same board producing the complete §6.2 three-way split — Ney charges, Davout scouts, Soult declines to presume. **A shipped, specced, tested feature that no keyless player has ever seen**, and the `delegation_inferred` machinery in `strategic_executor.py`, `combat.py` and `jealousy.py` is unreachable for them.

Be honest about the size: that is roughly **one command family plus a free-voice tail**, against a fast parser that already handles the other nine tenths.

## 3. Feasibility on four axes

### 3.1 Model capability vs the parse task — two jobs, opposite difficulty

The job the corpus measures is **refusal under forced tool use**, and it is the worst-case task for a small model. `providers.py` sends `tool_choice: {type: tool, name: submit_parsed_command}` — forced — so every reply must name an action. Of the ~50 corpus cells reaching the LLM road, **41 expect a refusal**. The only legal escape is the free string `"unknown"`, and measured: `len(VALID_ACTIONS) == 56`, `'unknown' in VALID_ACTIONS` is **False**, `PARSE_TOOL` enums == **0**. §7b's instruction to derive a grammar "from the existing PARSE_TOOL schema" is therefore a trap — deriving the action terminal from the obvious source makes refusal *ungrammatical* and guarantees `dig a hole` → `fortify`. **Grammar constraint helps output shape and actively hurts refusal.**

The job that actually earns is a **boolean**, and this is the finding that keeps the row alive:

```python
def classify_arm(personality: str, parse_resolved_to_action: bool) -> str:
def route_arm(personality: str, parse_resolved: bool) -> str:
```

The model's chosen verb never reaches the arm decision. The aggressive/cautious/ask split is the deterministic router's. So on the delegation family the local model's entire job is *"emit any valid non-`unknown` action for the named marshal."* This is why the corpus note that Haiku 4.5 resolved Ney/Davout/Soult **all to `scout`** is not damaging — the router was made deterministic precisely because the cloud model is unreliable at the table. A grammar-constrained 1.5B model plausibly hits a boolean.

**Verdict:** plausible for the narrow job, near-hopeless for the wide one — which is why the re-aim matters more than the model choice.

### 3.2 The code seam — small class, four hard gates

A working OpenAI-compatible provider is **~93 non-comment lines** and drives the real `CommandParser` with no change to validation, prompt-building or the executor. But registering it is not the switch:

1. `PROVIDERS` = `['mock','anthropic','groq']`; `get_provider('local')` raises `ValueError` (measured).
2. `LLMClient.create`'s hardcoded allowlist: `LLM_MODE=local` prints a warning and **resolves to mock** (measured).
3. **The headline** — `llm_client.py:1062`: `if not self.api_key: return False`. A keyless local provider is loaded, packaged, shipped and **never consulted**. No error, no log line.
4. `parse_resolved_to_action` denylists exactly `"mock"`. Measured: `mode='local'` → **True**. A local provider inherits the CR-5 personality arms on day one — the opposite of §7b's stated default.

Plus: `_make_api_request` (the Berthier recovery path) is AnthropicProvider-only and `AttributeError`s on anything else; `bind_sdk_client` is Anthropic-*shaped*, so IQ-9's keyless replay needs a new adapter for a `chat/completions` + `tool_calls` transport; `key_source` reports `byok` for a keyless provider, telling the player their stored key is in use when there is no key.

### 3.3 Packaging and latency — where the real cost sits

**The bar is 3 seconds, not 30.** §7b's acceptance is "parse latency ≤ the cloud round-trip"; `providers.py:99` is `REQUEST_TIMEOUT_SECONDS = 5.0` with `MAX_RETRIES = 1` and the cloud documented at 1–3s. These are module constants a local provider inherits. The Godot client's `http_request.timeout = 30.0` is not the bar.

Against that bar, the decisive measurement:

| | chars | share |
|---|---|---|
| Parse payload (system + user + tool schema) | 19,616 | ≈ **5,449 tokens** |
| Shared prefix, **different** commands, same board | 12,576 | 75.9% |
| Shared prefix, **same** command, board moved one battle | **95** | **0.6%** |
| `## Command to Parse` offset | 12,555 | 75.7% |
| Static tail *after* the command | 4,024 | 1,118 tokens |

The board moves every turn, so **KV reuse is structurally zero** and a local model re-prefills ~4,500 tokens cold on essentially every parse. This is also almost certainly the real reason `CLAUDE.md` records Anthropic prompt caching as "deliberately NOT used" — with the command at 75.7% there is no cacheable prefix above Haiku's 4,096-token minimum.

Reordering to `[static rules + Output + Examples][board state][command]` makes ~14,700 chars a stable prefix. It is contained, it is the only realistic route to the latency bar, **and it cheapens the existing BYOK road whether or not any local model ever ships.**

Other packaging facts: llama.cpp DLLs are invisible to PyInstaller's import analysis and are built to one CPU feature level with no fallback (`rapidfuzz` in the existing bundle is the precedent for runtime CPU dispatch); `parser = CommandParser()` runs at **import** (`main.py:55`), inside `launch.bat`'s 30s `/test` budget, so a model loaded in the constructor presents as "the server did not come up"; no abort path exists — llama.cpp has no timeout, only an abort callback, and `/command` is a sync handler holding an asyncio lock; `upx=True` is armed on both EXE and COLLECT and inert only because UPX is absent.

### 3.4 Licensing — one hard stop

| candidate | licence | shippable |
|---|---|---|
| Qwen2.5-0.5B / 1.5B | Apache-2.0 | yes |
| Llama-3.2-1B / 3B | Llama 3.2 Community | yes — **"Built with Llama"** attribution mandatory |
| Gemma-2-2B | Gemma Terms | yes — pass-through terms obligation |
| **Qwen2.5-3B** | **Qwen Research License** | **NO — §7b names it as a candidate and §7b is wrong** |

The repo already has the licence-copy machinery (`deploy/build.bat`, the FA-43/FA-N84 block). Scope its census to the **commands**, not the file — three of that slice's mutations came back inert because the pin matched the comment explaining the copy.

### 3.5 The acceptance gate cannot be run as written

§7b says "corpus green under `LLM_MODE=local` … ship/no-ship is that number." Measured: **688/688 passed, 0 failed** under mock. The golden corpus *is* the mock parser's own regression suite, so there is not one row a better parser could fix. And there is no baseline on the other side either: **19 cassettes, 34 provenance entries, all `"authored"`, zero `"recorded"`.** The gate has neither headroom nor a baseline and can only ever be a regression check.

The held-out set does exist and nobody has used it: **9 archives carrying `"llm": "anthropic"`, 334 `- CMD` lines.**

## 4. The plan

Three slices to a permanent answer. Do not open the build half until the gate returns.

### L-0 — The instrument (0.5 session)
Harvest the 9 live-anthropic arms (334 CMD lines) into a held-out capability set; partition by re-driving each utterance through mock **at HEAD**, not by reading the archived outcome — the archives are dated 2026-08-16/21 and predate WO slices 11–12, the FA slices and row CX, so some already pass. Keep the golden corpus as the **regression floor** it demonstrably is and pin that it is never the capability gate.

- Adjudicate gold **against the spec, never against the recorded cloud answer** — the cloud is self-inconsistent (`send somebody, anybody, to take Munich` produced four materially different outcomes across five runs; the harness's own `meta.json` stamps NONDETERMINISTIC). For a delegation row gold is `{success, marshal, action ∈ VALID_ACTIONS}`, never a specific verb.
- Grade on **parse fields**, never end-to-end messages — several archived "live failures" are world-state artefacts (`Ney, take Vienna` failed 5/5 on *"Not enough actions! Need 1, have 0"*, which is AP exhaustion, not parsing). Exclude `action == "error"`/`diplomatic_error` from the success predicate explicitly.
- Gotcha for whoever builds it: `action` is nested inside `result["command"]` while `dropped_sequel` is top-level. My first pass read `action` at the top level and silently scored 0 swallowed out of 56.

**done_when:** the scorer reproduces the partition deterministically, scores mock at 0 on the headroom arm, and a mutated board (one marshal −5,000 men) changes zero scores.

### L-1 — The prompt turns around (0.5 session) — **unconditional**
Reorder `prompt_builder.build_parse_prompt` to `[static rules + Output + Examples][board state][command]`. Wire the dead `marshal_name`/`personality` params (declared at :364-365, documented at :380-381, never referenced) so an addressed order injects one marshal's line.

**done_when:** two prompts for the same utterance on boards one battle apart share ≥14,000 chars of prefix (today: **95**); the invariant prefix exceeds 4,096 tokens; corpus 688/688 unchanged; the 19 cassettes replay byte-identically (their key is `(kind, utterance, world)`, never the prompt).

### L-2 — The ceiling probe (0.5 session)
One model far larger than any ship candidate (qwen3:8b or Qwen2.5-7B-Instruct Q4_K_M) via Ollama's OpenAI-compatible endpoint — Ollama 0.32.9 is already installed, and the venv has no `llama_cpp`/`torch`/`transformers`, so this defers the whole PyInstaller problem to the build half. **Latency before accuracy.** Grammar terminal is `VALID_ACTIONS ∪ {"unknown"}`; `target` stays a free string for `move`/`scout`/`naval_expedition` or `validation.py`'s deliberate passthrough dies and *"Region 'Venetia' not found. Nearby: …"* becomes unreachable. `flavor` and `suggestion` unemittable (pin 1; and `suggestion` is concatenated onto the player's message at `main.py:754`, so it is model prose the player reads).

If a 7–8B model cannot do this job, no 0.5–3B candidate will, and the row dies for half a session.

### Kill criteria — in digits

Close the row on **any** of:

1. **Ceiling fails** — headroom < **8/11**, OR refusal < **39/41**, OR **one** refusal failure emitting a state-mutating verb (`attack`/`move`/`recruit`/`build`/`charge`/`bombard`). The severity gate overrides the count gate: one such failure is a corps marched and an AP spent on a sentence the player never gave.
2. **The clock** — no licence-clean candidate reaches **p50 ≤ 3.0s and p95 ≤ 5.0s** on the L-1 reordered prompt, on a named mid CPU.
3. **No clean sweep** — nobody clears rescue ≥ 8/11 **and** control unchanged **and** refusal ≥ 39/41 **and** corpus 688/688 + the 4 `live_only` rows (§7b's own carried pin, kept).
4. **Licence** — the only survivor is Qwen2.5-3B.
5. **Toolchain** — no runtime serving a ceiling model within half a session on a quiet machine. Record the VRAM figure and close; this does not become a toolchain project.

### On a pass — the build half (4.0 sessions)

| slice | scope | effort |
|---|---|---|
| L-3 | `LocalProvider` + the four hardcoded gates; `key_source` provider-aware; `_make_api_request` on the base class; the non-SDK replay adapter; IQ-9's network guard taught the local port (it currently **allows loopback**) | 1.0 |
| L-4 | Close the two unenforced pins (`flavor` mode-gated; `parse_resolved_to_action` converted to an **allowlist** with `local` admitted only on the recorded `live_only` pass) + the wall-clock abort with fall-back-to-fast-parser as **production** code | 1.0 |
| L-5 | Settings rung (ladder: key > local > mock), `/config/llm` mode vocabulary, PyInstaller native layer + CPU dispatch, DLC delivery per §7b, Steam disclosure | 1.5 |
| L-6 | Three-arm assurance (keyless+modelless byte-identical / keyless+model / BYOK never replaced) via `tools/playtest_driver.py --llm local`, which already passes the flag through | 0.5 |

### On a fail — L-7 (0.25 session)
Amend §7b in place with the measurement, strike the ROADMAP row, and record the two dormant-but-unfixed pins (`providers.py:366` lifts `flavor` for any non-mock provider; `delegation.py:398`'s denylist) so whoever registers the next provider inherits the finding rather than rediscovering it.

### Where the "just work" money actually goes
Not here. The nine cells above — compound, conditional inversion, multi-marshal, the `invade` misroute — are deterministic work, and they are the answer to your multi-step/conditional question. Fund that row **regardless of this verdict**; the two are complements and neither covers the other.

## 5. The recorded dissent

**The strongest argument against declining is real and I am not minimising it.** CR-5 delegation is complete, specced, tested and 100% dead in the shipped default. Measured: all three `deal with Mack` phrasings return `unknown`/0.5 and route to ASK. Choosing not to build leaves the marquee moment of the command system behind a credit card. The mitigation is that L-0+L-2 costs one session and settles it permanently — but "decline" and "leave CR-5 dead" are separable, and a threshold with no session attached is the open-ended deferral GR9 exists to forbid. **Date the probe or the decline is a deferral by inertia.**

**Every percentage in this track is of a pin-set, not of players.** The corpus is a 449-entry regression set weighted toward edge cases; the archives are 334 commands from at most two authors in two sittings (the two `weird-live-voice` runs started two minutes apart). No telemetry of real human typing exists anywhere in the repo. If players type more free-form than the scripts do, the model's share is larger than measured and this verdict weakens proportionally.

**The determinism argument cuts against the status quo too.** A local model at greedy sampling with a fixed seed would be *more* reproducible than the current cloud path, which sets temperature 0 but carries no bitwise guarantee. "The model tier is a nondeterministic front door" indicts the existing BYOK arm as much as a hypothetical local one. The anti-build case rests on the unreachability measurement, not on determinism rhetoric — quote the former when this is revisited.

**Latency remains unmeasured by everyone, including me.** No llama.cpp toolchain exists in the venv and standing one up was outside this read-only pass. It is the acceptance criterion all three analyses agree is most likely to fail, which is why L-2 measures the clock before accuracy. Do not read this verdict as evidence the clock can be met.

---

## 6. ⚠ AMENDED RECOMMENDATION — September 20, 2026, same day

> **This section supersedes §4's build order and is the recommendation of record.**
> It was written after the memo above, when the user asked for a plain-English
> explanation and the act of writing one surfaced a question nobody in the fleet
> had asked: *if the personality split is decided by a **boolean**, does anything
> other than the model have to supply it?*
>
> **The answer is no, and it was measured.** Everything below marked **measured**
> was run in-process at HEAD `5b5dd038`, `LLM_MODE=mock`, on an unmodified
> `europe_1805.json` boot. Probes are in the session scratchpad; no repo file was
> modified.

### 6.1 The finding: the delegation feature is ALREADY deterministic, except one gate

§2 above says CR-5 delegation is "100% dead for keyless players" and treats that
as the local model's one real justification. That is true. **What is new is
*why*, and it is not what §3.1 assumed.**

Every input the feature needs is already computed deterministically in mock:

| input | who supplies it | works in mock? |
|---|---|---|
| *is this a delegation?* | `delegation.detect_delegation` — a 7-verb table (`do something about`, `take care of`, `deal with`, `attend to`, `sort out`, `see to`, `handle`) | **YES — 7 of 7 rows matched, exercising 5 of the 7 verbs** *(`do something about` and `attend to` untested — test them in L-D)* |
| *which marshal?* | the same function's address recovery, validated against the live roster | **YES** |
| *which target?* | the same function — and `main.py`'s own comment calls it **authoritative over the LLM's** (*"this also corrects the live LLM's unreliable target resolution — playtest: 'deal with Kutuzov' mis-scouted Algarve"*) | **YES** |
| *which personality?* | the world | **YES** |
| *what the arm then does* | a deterministic re-issue — `f"{marshal} scout {scout_target}"` — re-parsed with **no LLM**, GR6 (`main.py`, the cautious arm) | **YES** |

`detect_delegation`'s own docstring says so in writing:

> *"Deterministic and LLM-free. Works whether the upstream parse succeeded
> (live: resolved to some action) or failed (mock: action unknown) — **the
> delegation verb in the raw text is the authority, not the parse.**"*

**Measured, mock, 1805 boot — all seven verbs, one per row:**

```
utterance                    personality target  match  resolved  arm    ARM IF BOOLEAN WERE TRUE
Ney, deal with Mack          aggressive  Mack    YES    False     ask -> aggressive
Davout, deal with Mack       cautious    Mack    YES    False     ask -> cautious
Soult, deal with Mack        literal     Mack    YES    False     ask -> ask          (correct either way)
Murat, take care of Mack     aggressive  Mack    YES    False     ask -> aggressive
Lannes, see to Mack          aggressive  Mack    YES    False     ask -> aggressive
Bernadotte, sort out Mack    cautious    Mack    YES    False     ask -> cautious
Massena, handle Mack         aggressive  Mack    YES    False     ask -> aggressive
```

Read the last two columns: **every row is `ask` today**, and every row would be
the marshal's own authored arm if the boolean were true. Soult is the control —
`literal` maps to `ask` in both, so a correct fix must leave him exactly where he
is.

And `classify_arm` is **personality × boolean and nothing else** — the parsed
verb never reaches it:

```
aggressive   False -> ask     True -> aggressive
cautious     False -> ask     True -> cautious
literal      False -> ask     True -> ask
sovereign    False -> ask     True -> ask
```

**So the entire three-way split that no keyless player has ever seen is gated on
one boolean**, `parse_resolved_to_action(parsed)`, which is documented as a
**mode** gate (guardrail (e), CR-5 §6.7 "live-only exposure").

### 6.2 ⛔ The obvious fix is a NO-OP — measured

My first instinct in conversation — *"delete the `mode == 'mock'` clause"* — is
**wrong, and would change nothing.** The predicate has three clauses, and for a
delegation in mock the parse is rejected at **clause 1 and clause 3**, never
reaching the mode check at all:

```
Ney, deal with Mack    success=False  mode=None   action=None    -> clauses 1 + 3 reject
Davout, deal with Mack success=False  mode=None   action=None    -> clauses 1 + 3 reject
Ney, attack Mack       success=True   mode='mock' action='attack' -> clause 2 rejects
```

The fast parser does not know `deal with` is a verb, so the parse **legitimately
fails**. Deleting the mode clause changes the ORDINARY order's verdict and leaves
every delegation exactly as dead as it is today. *(A second correction to the
record: the docstring's "the fast parser stamps `mock`" is true for a successful
parse and **not** for a failed one — `mode` is `None` there.)*

**The correct shape: the arm's gate must read the `DelegationMatch`, not the
parse.** The DelegationMatch *is* the deliberate evidence — the player used a
delegation verb, at a resolvable target, addressed to a real marshal. And that is
precisely the distinction the guardrail's own docstring draws, one step short of
the conclusion:

> *"The mock/fast parser can **incidentally** resolve a delegation to a real
> action when the remainder carries an action keyword (`deal with the attack on
> Wellington` -> attack) … In BOTH cases the LLM never applied the §6.2 table, so
> there is no bias to act on."*

The guard exists to reject an **incidental** resolution. A DelegationMatch is not
incidental. The guard was written against the wrong witness.

### 6.3 ⚠ THIS NEEDS THE USER'S WORD — it is not a builder's call

> **✅ RULED September 23, 2026: YES.** Taken by Claude under the user's delegated grant (*"make calls please"*); recorded, not separately confirmed by the user.
>
> **The ruling.** The deterministic delegation arms fire for a keyless player. The gate reads the `DelegationMatch`, not the parse. What does not change:
> - the literal arm still asks;
> - the incidental-keyword control must stay green;
> - the CR-5b flavor line stays live-only, so keyless players get the deterministic floor.
>
> **Why.** The default game is keyless and most players will not bring a key, and the three-way split is the VISION's own premise: marshals answer by personality. The store copy then has one fewer thing to reserve for BYOK, which position 14 discloses.
>
> **Landing.** **Update 3** ("the word is the order"), after the release, per `STATUS.md` ▶ NEXT UP, with the §6.4 `done_when` unchanged.
>
> **Re-open.** If player transcripts show a keyless delegation producing an attack the tester did not expect, restore the witness. It is a single seam.

**Do not build L-D on this memo alone.** Guardrail (e) is part of CR-5's
**blessed scope** (`COMMAND_ROBUSTNESS_SPEC.md` §6.3, blessed July 5, 2026), whose
own language is *"the bias is live-only"*. Flipping it changes what was blessed,
in a way a player can see. It is small, it is well-argued, and it is still the
user's ruling. Put the question as: *may the deterministic delegation arms fire
for a keyless player, or is the three-way split deliberately a live-mode feature?*

Three things the gate question must carry:

1. **What keyless players gain:** the mechanical three-way split — Ney charges,
   Davout scouts, Soult asks — on 7 verbs × the whole roster.
2. **What stays live-only regardless:** the **CR-5b flavor line**. The LLM
   composes that; keyless players get the deterministic floor, which already
   exists and is already register-gated. Nobody gets silence.
3. **What it costs the BYOK pitch:** if delegation works keyless, *"Smarter
   Parsing (optional)"* has one fewer thing to offer. Arguably that makes the
   store copy **more** honest, but it is a product decision and position 14 owns
   the disclosure.

### 6.4 The amended build order

| | slice | effort | condition |
|---|---|---|---|
| **1** | **L-1 — the prompt turns around** (§4) | 0.5 | **UNCONDITIONAL.** It cheapens the existing BYOK road on every escalated call whether or not any model ever ships, and it is the only realistic route to the latency bar if one does. Do it regardless of everything below. |
| **2** | **L-D — "The Boolean Road"** *(NEW)* | ~0.5 | **Behind the §6.3 user gate.** Re-key the arm's gate from the parse to the `DelegationMatch`. If this lands, **the local model's single justification is closed for a tenth of the cost and with no download, no latency, no licence question and no packaging risk.** |
| **3** | **L-0 + L-2 — the instrument and the ceiling probe** (§4) | 1.0 | **Only if L-D proves too narrow in play.** The 7-verb table covers what it covers; a player who writes *"Ney, do what you think best"* still falls through. Measure that gap in a played session before spending a session on the probe. |
| **4** | L-3..L-6, the build half (§4) | 4.0 | Only on a passing probe. Unchanged. |

**L-D's `done_when`** (falsifiable, and RED today on all four):

1. Under `LLM_MODE=mock` on the 1805 boot, the seven measured rows produce
   **aggressive / cautious / ask** per the marshal's authored personality — not
   `ask` for all seven.
2. `Soult, deal with Mack` still **asks** (the literal arm is correct in both
   modes and must not move), and `Ney, attack Mack` is **byte-identical** — an
   ordinary order must not acquire a bias.
3. The **incidental** case the guardrail was written against still degrades to
   ASK: a sentence with no delegation verb whose remainder carries an action
   keyword must not fire an arm. Pin it with the docstring's own example.
4. Every flipped pin is flipped **consciously** and named in the commit.

**The pin survey is already done — measured, so the 0.5-session estimate is not a
guess.** 49 references across 4 test files; 103 test functions in the two
delegation files. **The function signatures do not change** — only the *witness*
the call site passes — so every unit-level `classify_arm(p, False)` /
`route_arm(p, False)` pin stays green by construction.

**Expected to FLIP (≈4–6), all end-to-end mock-delegation assertions:**
`test_aggressive_and_cautious_ask_only_when_unresolved_mock` ·
`test_mock_delegation_degrades_to_ask_for_every_personality` ·
`test_nation_delegation_asks_for_every_personality` ·
`test_router_and_guardrail_e_untouched` · and possibly
`test_mock_mode_parse_is_never_resolved` (it pins the predicate itself, which L-D
need not change — if it stays green, that is evidence the fix went in at the
right seam).

**Must STAY GREEN — these are the controls, and they are the whole safety
argument:** `test_literal_always_asks_even_when_llm_resolved` ·
`test_neutral_and_unset_always_ask` · `test_literal_delegation_asks_not_attacks` ·
`test_literal_and_neutral_route_to_ask` · and above all
**`test_keyword_bearing_delegation_still_degrades_to_ask_in_mock`**, which is
*precisely* the incidental case §6.2 says the guardrail was written for. **If that
one goes red, the fix is wrong and reading the DelegationMatch was the wrong
witness after all — stop.** It is the single most informative test in the slice.

### 6.5 The prediction, labelled as a prediction

**On the probe: leaning negative, on the clock, not on the task.** Emitting any
valid action for a named marshal is well within a 1.5B model — that half I would
bet on. The problem is that the CPU must chew ~5,000 tokens before answering,
every command, and on a mid-range laptop that is plausibly ten seconds or worse
cold. With L-1's reorder the static prefix caches and the board state amortises
across the ~4 commands in a turn, which *might* bring the first command of a turn
to a few seconds and later ones under one — **but nobody has measured it, and
"might" is doing real work in that sentence.** That is exactly why L-2 measures
latency before accuracy and why the row dies cheap if it dies.

**On L-D: high confidence it works, because every input is already computed and
measured.** The uncertainty is not technical, it is the §6.3 ruling and the pin
count in (4).

### 6.6 What has NOT changed

Everything in §1–§5 above stands, including the three findings that make §7b
unrunnable as written, the licence table, and the headline that decides the row:
**9 of 9 measured "the game acts on an order you did not give" cells parse at
0.90–1.00 against a 0.70 gate and never reach any model tier.** A local model
was never the answer to *"make the game just work"* — the Command-Road Queue's
first four slices are. This section only makes the row's one real prize
reachable without it.
