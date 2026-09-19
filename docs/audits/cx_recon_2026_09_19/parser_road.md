# CX-RECON — Census of the Parser Road (the mock / fast chain)

Read-only recon at `master` (`f7008582`). Every claim below is either a
`file:line` citation read at HEAD or the output of a probe committed under
`probes/` and actually run. Anything I could not establish is marked
**UNVERIFIED**.

> ⚠ **Tree provenance.** The working tree was clean when this task opened, but
> partway through it a sibling agent left an uncommitted 71-line addition to
> `backend/ai/clause_guards.py` ("CX slice 1 — A QUESTION NEVER ORDERS",
> `A_QUESTION_NEVER_ORDERS`, `_SUBJECT_WH_WORDS`, `_CONTRACTED_AUX_RE`,
> `_DELIBERATIVE_OPENER_RE`). I did not write it and did not touch it. I
> **re-ran the two headline measurements against the modified tree** and both
> reproduce byte-identically — escalation `24 / 392 (6.1%)`, 26 calls; the
> unreachable set `{march, propose_white_peace, pursue, reinforce, support}` —
> so nothing in this census depends on that edit. The line numbers cited for
> `clause_guards.py` symbols are the only ones that could have shifted; every
> other citation is in an unmodified file.

Probes (all read-only, `LLM_MODE=mock`, no network, real 1805 world built
through `backend/ai/parser_eval.build_world("1805")` +
`build_llm_game_state`, the same construction
`tests/test_command_robustness_cr1_eval_harness.py` uses):

| probe | what it measures |
|---|---|
| `probes/probe_parser_road.py` | one utterance per action through `CommandParser.parse`; `--raw` also shows the bare `_parse_with_mock` result; `--utt` / `--file` for ad-hoc batches |
| `probes/probe_reachability.py` | 65 action ids × a bank of natural phrasings — **the core deliverable's evidence** |
| `probes/probe_hazards.py` | 70 ordering / substring hazard rows |
| `probes/probe_confidence.py` | confidence distribution over the golden corpus + the real `_should_fallback_to_llm` predicate |
| `probes/probe_confidence_full.py` | the escalation gate on the **full** pipeline (after the pre-parse typo repair) |
| `probes/probe_prompt_size.py` | size of the escalation prompt on the live board |

Run any of them as:
`.venv/Scripts/python.exe <probe path>` from the repo root.

---

## 0. The shape of the road, corrected

The task brief says `backend/ai/llm_client.py -> backend/ai/parser.py`.
**There is no `backend/ai/parser.py`.** The parser is
`backend/commands/parser.py` (2,393 lines), and the fuzzy matcher is
`backend/utils/fuzzy_matcher.py`, not `backend/commands/fuzzy_matcher.py`.
The real order is:

```
CommandParser.parse                       parser.py:1594
  └─ repair_leading_verb_typo             llm_client.py:310   (PRE-parse rewrite)
  └─ CommandParser._parse_text            parser.py:1625
       ├─ normalize_sovereign_address     parser.py:287
       ├─ _split_sequential_orders        parser.py:136   (trial parses via fast_parse)
       ├─ LLMClient.parse_command         llm_client.py:841
       │    ├─ _parse_with_mock           llm_client.py:1273   ← THE CHAIN
       │    └─ _should_fallback_to_llm    llm_client.py:874    ← THE GATE
       ├─ validate_parse_result           validation.py:298
       ├─ _apply_fuzzy_matching           parser.py:964
       ├─ strategic upgrade               parser.py:~2000 (strategic_parser.py)
       └─ reparse_with_llm (CR-2 retry)   llm_client.py:967, called parser.py:1789
```

`_parse_with_mock` runs **always**, in every mode, including under
`LLM_MODE=anthropic` — the model is only ever a fallback
(`llm_client.py:858`, "Step 1: ALWAYS run fast parser first").

---

## 1. The ordered keyword chain

### 1a. Pre-chain: guards and early returns (in execution order)

These run **before** any action keyword is read, and several of them
`return` outright, so nothing below can see the sentence.

| # | line | what | note |
|---|---|---|---|
| 1 | `llm_client.py:1300` | `command_lower.startswith("cheat ")` → `cheat` | first, deliberately (a diplomat name in a cheat arg used to hijack it) |
| 2 | `llm_client.py:1341-1431` | **PARSE-NEG clause guards** (`clause_guards.py`) — `mentions_stand_down`, `strip_negated_clauses`, `strip_condition_clauses`, `strip_deferred_clauses` | exempt: `/debug`, `debug `, `save`, bare `load`, and **any question** (`is_question`). Clauses are blanked with **spaces, never spliced**, so downstream index arithmetic survives |
| 3 | `llm_client.py:1390` | conditional clause → `_refusal_result(..., "conditional")` | terminal |
| 4 | `llm_client.py:1396-1415` | negation/deferral with no executable residue → refusal | negation wins the label over deferral |
| 5 | `llm_client.py:1379-1388` | deferral + a *second* marshal in subject position → refusal `"two orders, one of them for a later turn"` | |
| 6 | `llm_client.py:1434` | `strip_leading_filler` ("no wait, …") | same-length blanking |
| 7 | `llm_client.py:1445` | `_war_purpose_keywords` → `_parse_set_war_purpose` | |
| 8 | `llm_client.py:1453` | `_repudiate_keywords` → `_parse_repudiate_bargain` | |
| 9 | `llm_client.py:1466` | `_common_peace_keywords` → diplomacy | |
| 10 | `llm_client.py:1473` | `_request_terms_keywords` → diplomacy | |
| 11 | `llm_client.py:1478` | `_diplomat_names` = talleyrand / **diplomat / envoy / minister / foreign minister / ambassador** → diplomacy | **no marshal guard** |
| 12 | `llm_client.py:1490` | `_break_keywords + _downgrade_keywords`, or `_mentions_treaty_break and not _addressed_marshal` | only the second arm is guarded |
| 13 | `llm_client.py:1499` | `_mentions_peace_intent and not _addressed_marshal` | guarded |
| 14 | `llm_client.py:1510` | `_war_keywords` (`declare war on`, `war on `, `war against `, **`invade `**, `launch war`, …) → diplomacy | **no marshal guard** |
| 15 | `llm_client.py:1521` | `_ultimatum_keywords` | **no marshal guard** |
| 16 | `llm_client.py:1530` | `_amends_keywords` | **no marshal guard** |
| 17 | `llm_client.py:1539` | `_ally_keywords` | **no marshal guard** |
| 18 | `llm_client.py:1560` | `_proposal_keywords and not _addressed_marshal` | guarded |
| 19 | `llm_client.py:1577` | `_mission_keywords` (`improve relations with`, **`charm `**, `gather intel on`, `gather intelligence on`, `spy on `, `undermine `, `reassure `, `send envoy to`, `send diplomat to`) | **no marshal guard** |
| 20 | `llm_client.py:1579` | `re.search(r'\bcourt\b(?!\s+martial)')` → diplomacy | **no marshal guard** |
| 21 | `llm_client.py:1597` | `is_question(original_text)` → `status` (via `question_desk.classify_question`) or `help` | reads the **original**, not the guarded copy |
| 22 | `llm_client.py:1625-1700` | executing-marshal extraction (roster scan + `Marshal <Name>` capture), position-aware via `_executor_eligible` | |
| 23 | `llm_client.py:1739` | `/debug` / `debug ` → `debug` | |
| 24 | `llm_client.py:1768` | `save*` / bare `load` → `meta_command` | |

### 1b. The action chain itself (first match wins)

Extracted mechanically from `backend/ai/llm_client.py` lines 1782-2222
(`probes/` transcript kept in the session; regenerate with the awk/regex in
§6). The line number is the `if`/`elif`.

| order | line | action | matcher (abbreviated) |
|---|---|---|---|
| 1 | 1787 | `help` | `_desk_text in ("help","help me","i need help","commands","what can i do")` or `== "?"` (exact, after the Berthier/Sire address is stripped) |
| 2 | 1795 | `end_turn` | `is_bare_end_turn(command_lower)` — **bare form only** (FA-6) |
| 3 | 1798 | `status` | `_desk_text == "status"` (exact) |
| 4 | 1802 | `cancel` | `"cancel order"`, `"cancel orders"`, **`"cancel "`**, `"halt order"`, `"abort order"`, `"belay that"`, `"belay"`, **`" halt"`**, **`", halt"`** |
| 5 | 1809 | `cancel` | whole command in `("halt","stop","cancel","abort")` |
| 6 | 1819 | `cancel` | `stand_down` (clause_guards) |
| 7 | 1824 | `charge` | `"glorious charge"` or (`\bcharge\b` **and** `"attack"` absent) |
| 8 | 1826 | `attack` | `"attack" in`, or `\bcharge\b`, or `\boccupy\b` |
| 9 | 1829 | `attack` | `bombard`, `barrage`, `shell`, `cannonade` |
| 10 | 1842 | `attack` | `\b(pursue|chase|hunt|intercept|harry|hound|shadow)\b`, or `hunt down`/`track down`/`give chase`/`go after` |
| 11 | 1860 | `attack` | `mentions_attack()` — `attack_vocabulary.BATTLE_VERBS ∪ CAPTURE_VERBS ∪ ATTACK_IDIOM_RE` |
| 12 | 1866 | `wait` | `"wait"`, `"stand by"`, or `\bpass(es)?\b` not matched by `PASS_AS_NOUN_RE` |
| 13 | 1873 | `set_fleet_posture` | `"home waters"` |
| 14 | 1879 | `move` (→SUPPORT) | `_guards_a_friendly_marshal` — guard/protect/cover/screen/shield + a **roster** name |
| 15 | 1882 | `hold` | `hold at all costs`, `hold your ground`, `hold position`, `hold the line`, `stand fast`, `stand firm`, `defend and hold`, `fortify and hold`, `secure and hold`, `anchor at`, **`guard`**, **`protect`**, (+`stand your ground`, `stand ground`) |
| 16 | 1890 | `hold` | **`"hold" in command_lower`** — bare substring |
| 17 | 1892 | `defend` | `"defend" in` |
| 18 | 1897 | `retreat` | `retreat` (¬screening) / `fall back` (¬destination) / `withdraw` (¬destination ¬pension ¬screening) / `_mentions_plain_retreat` |
| 19 | 1907 | `move` | ~30 destination idioms + `\bmove\b` + `\bgo(es)? (to|into|towards?|for)\b` (¬"go to war") + the possessive-corps form |
| 20 | 1948 | `scout` | `"scout"`, `"reconnaissance"`, `"recon"`, **`"acout"`**, **`"scou"`**, `\bobserv(e|es|ing)\b`, `\bkeep\s+watch\b` |
| 21 | 1969 | `build_fleet` | `_lays_down_a_keel` or `\b(build\|raise\|construct\|launch\|expand)\b.{0,20}\b(ship…)\b` or `build the fleet` |
| 22 | 1973 | `naval_diversion` | `_orders_the_diversion` or `draw off the fleet` / `draw them off` |
| 23 | 1977 | `naval_expedition` | `"expedition"`, `\bembark\b`, `\bland\b …(in\|at\|on)\b` (≤2-word window, ¬`land to`) |
| 24 | 1993 | `set_fleet_posture` | **`\bblockade\b`**, `home waters` (dead here — #13 already claimed it), or `\bfleet\b` + `\b(guard\|recall\|port\|station)\b` |
| 25 | 2007 | `recall_marshal` | **`\brecall\b`** ¬`_RECALL_IS_NAVAL_RE` |
| 26 | 2010 | `recruit_marshal` | **`"commission" in`** ¬pension, or `\brecruit\b.{0,12}\bmarshal\b`, or `\bappoint\b.*\bmarshal`, or `"marshalate"` |
| 27 | 2022 | `purchase_levy` | `\bsubstitutes?\b`, `\bremplacants?\b`, `purchase…levy`, `(buy\|hire\|purchase)…replacements?` — all ¬pension ¬"buy off" |
| 28 | 2030 | `recruit` | `"recruit" in`, `\braise\b` ¬pension, `"conscript"` |
| 29 | 2037 | `move` (→SUPPORT) | `"reinforce" in`, `\bsupport\b`, `_supports_a_friendly_marshal` |
| 30 | 2044 | `unfortify` | `"unfortify"`, `"abandon fortif"`, `"leave fortif"` — **before** fortify |
| 31 | 2046 | `fortify` | `"fortify"`, `"dig in"`, `"entrench"` |
| 32 | 2050 | `build` | **`"build "`**, `"construct "`, + 4 typo forms — **before** drill (the documented `build`/`train` rule) |
| 33 | 2053 | `restrain` | `"restrain" in` — **before** drill (contains `train`) |
| 34 | 2055 | `drill` | `"drill"`, **`"train"`**, `"exercise"` |
| 35-40 | 2059-2078 | `stance_change` | 3 compound lists, then `\baggressive\b` (¬"attack"), `\bdefensive\b`, `\bneutral\b` |
| 41 | 2089 | `repair` | **`"repair "`** (trailing space) or `"restore "` ¬`_mentions_abstract_restore` |
| 42 | 2098 | `economy` | `economy`/`treasury`/`finances`/`financial` ¬pension |
| 43 | 2101 | `garrison` | `\bgarrison\b` + 6 idioms |
| 44 | 2107 | `form_square` | 5 literals |
| 45 | 2112 | `break_square` | 6 literals |
| 46 | 2129 | `grant_region_to_vassal` | `\bcede\b`, or `\bgrant\b` ¬autonomy ¬pension ¬(independence/freedom/passage/access/amnesty/clemency/pardon) **and** `" to <known nation>"` |
| 47 | 2139 | `invest_vassal` | `invest in <nation>` / `invest in the <nation>` (live nation list) |
| 48 | 2151 | `change_autonomy` | **`"autonomy" in`**, or (make/set/turn) + (puppet/satellite/autonomous) |
| 49 | 2162 | `release_vassal` | `release <nation>` / `release the <nation>` / `release vassal` |
| 50 | 2171 | `make_vassal` | `"make vassal"`, `"vassalize"`, `"subjugate"` — **contiguous only** |
| 51 | 2178 | `grant_dotation` | `\bendow\b`, `"dotation"`, or `grant` + (estate/duchy/domain) ¬pension |
| 52 | 2194 | `revoke_pension` | `_mentions_pension` + `\b(revoke\|withdraw\|rescind\|stop\|end\|terminate\|cancel)\b` |
| 53 | 2198 | `grant_pension` | `_mentions_pension` (pension/rente/annuity) |
| 54 | 2204 | `sponsor_design` | `\b(sponsor\|subsidi[sz]e\|bankroll\|licen[cs]e)\b` |
| 55 | 2207 | `buy_off_design` | `\b(buy\|pay\|bought)\s+(off\|out)\b` |
| 56 | 2209 | `guarantee_nation` | `\bguarantee\b` **and** a known nation in the text |
| 57 | 2217 | `wait` | `_mentions_stay_put` — deliberately **last** |
| — | 2220 | *(add new actions here)* | |

The diplomatic sub-chain lives in `_parse_diplomatic_command`
(`llm_client.py:2578`), and its own ordered arms are at 2697 (`diplomatic_mission`),
2699 (`diplomatic_feasibility`), 2701/2763 (`diplomatic_advisory`), 2709
(`make_amends`), 2719 (`diplomatic_break`), 2725 (`diplomatic_downgrade`), 2735
(`diplomatic_declare_war`), 2741 (`diplomatic_ultimatum`), 2746
(`propose_common_peace`), 2753 (`request_terms`), 2765/2768 (`diplomatic_proposal`).

### 1c. Ordering hazards — MEASURED (`probes/probe_hazards.py`)

The known `build `/`train` example is **fixed and holding** (`build a training
ground in Paris` → `build`). These are the ones that are *not*:

**H1 — `"hold"` as a bare substring at 1890, above fortify / garrison / drill /
recruit.** Any sentence containing `stronghold`, `household`, `threshold`
becomes a HOLD. Measured:

```
Ney, garrison the stronghold          -> hold   (not garrison)
Ney, fortify the stronghold           -> hold   (not fortify)
Ney, drill the men at the stronghold  -> hold   (not drill)
Ney, recruit at the stronghold        -> hold   (not recruit)
Ney, the household troops are ready   -> hold
```

This is the exact class the chain's own comment at 1822 warns about
("Use `\b` word boundaries … e.g. 'bypass' matching 'pass'") and which
IQ-1/SW-1 already fixed once for `purchase`/`chase`.

**H2 — `"scou"` (4-char substring, no boundary) at 1948.** `Ney, scour the
countryside` → `scout`; `Ney, the scoundrels have fled` → `scout`.

**H3 — `"train"` at 2055.** `restrain` is guarded at 2053 but `constrain` and
`entrain` are not: `Ney, constrain the cavalry` → **drill**.

**H4 — the diplomatic pre-chain outranks every marshal verb, and only 3 of its
14 routes carry `_addressed_marshal`** (`llm_client.py:1294`; used at `:1491`,
`:1499`, `:1560` only). Measured, the marshal is **dropped**:

```
Ney, invade Swabia                 -> diplomatic_error     (marshal=None)
Ney, make war on Mack              -> diplomatic_declare_war (target=None)
Ney, hold the court of Vienna      -> diplomatic_mission
Ney, charm the locals              -> diplomatic_mission
Ney, escort the envoy to Vienna    -> diplomatic_proposal
Ney, the minister has arrived      -> diplomatic_proposal
Ney, court the enemy's flank       -> diplomatic_mission
```

`invade` is the player-plausible one: it is an ordinary military verb, it is
in `_war_keywords` with a trailing space only, and there is no marshal guard
on that route.

**H5 — unbounded single keywords owning whole sentences.**

```
\bblockade\b   (1993)  Ney, break the blockade at Ulm   -> set_fleet_posture
\brecall\b     (2007)  Ney, recall the men to the colours -> recall_marshal (target=Ney)
                       as I recall Ney is at Rhineland  -> recall_marshal (target=Ney)
"commission"   (2010)  Ney, commission a bridge at Ulm  -> recruit_marshal (target=Ney)
                       Ney, the commissioners have arrived -> recruit_marshal
"autonomy"     (2151)  give the men autonomy of movement -> change_autonomy
licen[cs]e     (2204)  Ney, licence the sutlers          -> sponsor_design
" halt"        (1802)  Ney, the advance is halting       -> cancel
```

**H6 — two branches require a trailing space and so miss their own bare verb.**
`build` (2050) and `repair ` (2089): measured, bare `build` → **unknown**,
`Ney, repair` → **unknown**, `repairs in Paris` → **unknown**. (`repair Paris`
and every region-panel chip string do work — see §5.)

**H7 — phantom targets survive on the HOLD family.** `Ney, guard the fleet
stores in port` → `hold` with `target="Fleet Stores In Port"`;
`Ney, guard the treasury wagons` → `target="Treasury Wagons"`. The executor's
region chokepoint refuses these (`executor.py:~566`, the WO-45 floor +
`_plausible_name_typo`), so the consequence is a refusal message, not a march
— but the phantom reaches the executor.

---

## 2. The confidence model and the escalation gate

### 2a. How confidence is assigned

`llm_client.py:2470-2490`, and it is the **only** place it is set in the mock chain:

| condition | confidence |
|---|---|
| cheat / debug / save-load | `1.0` (2475 region; set at the early returns) |
| action matched **and** marshal **and** target | `0.95` |
| action matched **and** (marshal xor target) | `0.9` |
| action matched, no identifier | `0.8` |
| `action == "unknown"` | `0.5` |
| any matched parse whose **leading comma-addressed token resolves to nothing known** | clamped to `UNRESOLVED_ADDRESS_CONFIDENCE = 0.55` (`:69`, applied `:2490`, predicate `_unresolved_address_token` `:562`) |
| diplomatic route | `0.95` fixed (`:2872`), `1.0` for the two error arms |

There is **no** scoring of whether the sentence *means* the keyword. A
confident number is a statement about how many identifiers were found, not
about correctness — which is why the PARSE-NEG family could ride out at 0.95.

### 2b. `_should_fallback_to_llm` (`llm_client.py:874`)

Returns **False** (no model call) when any of:

1. `self.provider_name == "mock"` (:900)
2. `not self.api_key` (:904)
3. `fast_result.confidence >= 0.7` (`LLM_FALLBACK_CONFIDENCE_THRESHOLD`, `:63`) (:908)
4. **`fast_result.refusal`** — PARSE-NEG's rule, and the file states it is a
   *deliberate deviation* from the filed prescription: a refusal is terminal
   in both modes, because under forced tool-use every reply must name an
   action, "which is how the forbidden order gets issued after all" (:911-925)
5. `game_state is None` (:928)
6. `fast_result.action in validation.NON_ORDER_ACTIONS` (:934) —
   `{help, status, debug, cheat, economy, treasury, finances, end_turn, meta_command}`
   (`validation.py:188`)

So the gate opens for **exactly two** fast-parser states: `unknown` (0.5) and
an unresolved leading address (0.55).

### 2c. How often the gate actually opens — MEASURED

`probes/probe_confidence.py` over the 392 1805-eligible golden-corpus rows,
with `provider_name`/`api_key` patched so the mock short-circuit does not mask
the predicate (no call is made):

```
conf 1.0   n=8    ( 2.0%)  kept
conf 0.95  n=158  (40.3%)  kept
conf 0.9   n=123  (31.4%)  kept
conf 0.8   n=52   (13.3%)  kept
conf 0.75  n=1    ( 0.3%)  kept
conf 0.55  n=4    ( 1.0%)  ESCALATES
conf 0.5   n=46   (11.7%)  ESCALATES
refusals (terminal, never escalate): 21
```

`probes/probe_confidence_full.py` then measures the **full** pipeline (with
`_parse_with_live_provider` replaced by a recorder — still no network), which
is the honest number because `repair_leading_verb_typo` runs first and rescues
the four typo rows:

```
utterances: 392
FULL-pipeline escalations to the LLM:  24  (6.1%)
answered deterministically:           368  (93.9%)
total recorded calls: 26   ← 2 utterances call TWICE (the CR-2 forced retry)
```

The 24 that reach the model are all genuine gaps — `deal with X` (the CR-5
delegation arm, which is *supposed* to go live), `cover the retreat`,
`fix bayonets`, `dig a hole`, `lay down a pontoon bridge`,
`mount a diversion on the left`, `break through enemy lines`, plus two
unresolved addresses (`Soutl,` / `Wittgenstein,`) and outright gibberish.

⚠ **Honest limit:** the golden corpus is a *regression* corpus, curated from
things that work plus known-bad rows. It is not a sample of what players type.
6.1% is a floor on real play, not an estimate of it. **UNVERIFIED:** the
escalation rate on an unseen human transcript.

### 2d. Calls per request

Up to **three** blocking live calls, each guarded:

1. the parse (`parse_command` :858)
2. `reparse_with_llm` (:967), called from `parser.py:1789` after a confident
   fast parse hard-fails in the fuzzy pass — declines if
   `fast_result_dict["llm_error"]` (:1002)
3. `generate_berthier_recovery` (`llm_client.py:1120`, called `main.py:3543`
   and `:3691`) — reads `llm_error` for the same reason

### 2e. Cost shape — MEASURED (`probes/probe_prompt_size.py`)

On the live 1805 board (126 regions, 8 player marshals, 4 visible enemies):

```
system prompt              chars=177     ~44 tok
user/parse prompt          chars=16,582  ~4,146 tok
PARSE_TOOL json schema     chars=2,860   ~715 tok
TOTAL per escalation       chars=19,619  ~4,905 tok   (~4 chars/token, approximate)
```

Prompt section sizes:

```
Examples                    3,423     Diplomatic Commands       1,880
Flavor Line (CR-5b)         1,693     Strategic Commands        1,541
Cardinal Directions         1,568     Personality Rules         1,558
Valid Actions               1,248     Valid Regions             1,214
Output                        561     Ambiguity Scoring           501
Cancel Command                407     Your Marshals               399
Strategic Score               239     Enemy Forces                202
```

`model="claude-haiku-4-5"`, `max_tokens=1000`, parse call pinned to
`temperature=0` with `tool_choice` forced to `PARSE_TOOL`
(`providers.py:477-491`, `:837-850`). **No prompt caching anywhere** —
`grep -n "cache_control\|anthropic-beta" backend/ai/*.py` returns nothing;
`CLAUDE.md` records this as a deliberate, settled decision.

---

## 3. Identifier resolution layers

Five layers, in order. **Every one of them runs on the mock road too** —
`_apply_fuzzy_matching` is fed the mock dict, not just an LLM dict.

### L1 — `_name_match_patterns` (`llm_client.py:420`)
Lowercase + camelCase-split alias + hyphen-to-space alias. Public alias at
`:443`. Ungated by design (it is exact-form expansion, not fuzzy).

### L2 — `unique_name_tokens` (`llm_client.py:445`) and `_match_known_name` (`:485`)
Surname tokens ≥4 chars that identify **exactly one** candidate. Uniqueness is
computed over the candidate SET, so `archduke` (owned by two) is dropped while
`charles` and `john` are admitted. `allow_last_name=True` is passed **only**
for the enemy roster (`:2289`), never for regions. Position-aware ranking:
full-name beats token, after-`to` beats elsewhere, earliest beats latest.

### L3 — `FuzzyMatcher` (`backend/utils/fuzzy_matcher.py`)
`AUTO_CORRECT_THRESHOLD = 80`, `SUGGEST_THRESHOLD = 60` (`:30-31`);
short names ≤4 chars drop to `70/50` (`:34-35`). `_get_best_score` (`:51`)
uses `fuzz.ratio`, and for queries or candidates ≤4 chars takes
`max(ratio, partial_ratio)` — **partial ratio is what rewards a short word for
being contained in a long name**, and is the root of the whole
`relieved→Rhineland` / `Moon→Morocco` family.

### L4 — `_plausible_name_typo` (`parser.py:635`)
The shape gate: `len(word) >= 4`, **same first letter**, edit distance ≤2 at
≥6 chars else ≤1. Sibling `_correction_survives` (`executor.py:225`) wraps it
behind three flip levers (`executor.py:220-222`,
`ENEMY_DIRECTION_GATE_ACTIVE` / `BROAD_DIPLOMATIC_GATE_ACTIVE` /
`MARSHAL_DIRECTION_GATE_ACTIVE`, all `True`).

### L5 — the seams, and which are gated

| # | seam | file:line | gated by |
|---|---|---|---|
| 1 | LLM-supplied marshal slot | `parser.py:1069` | `_plausible_name_typo` (`:1084`) ✅ |
| 2 | addressed token, meta-action path | `parser.py:1150` | `_plausible_name_typo` (`:1165`) ✅ |
| 3 | word-scan marshal candidates | `parser.py:1256` | length-Δ ≤2 **and** first letter (inline, `:1271-1276`) ✅ |
| 4 | target: enemy auto-correct | `parser.py:1367` → `:1404` | `_plausible_name_typo` ✅ |
| 5 | target: region auto-correct | `parser.py:1371` → `:1408` | `_plausible_name_typo` ✅ |
| 6 | target: near-enemy edit-distance arm | `parser.py:~1385` | `_closest_by_edit_distance` + `_introduced_by_article` + `_is_targetable_enemy` ✅ (gated Aug 30, 2026) |
| 7 | free-text target scan | `parser.py:1524` → `:1552` | `_plausible_name_typo` + `_articled` + `_NON_TARGET_WORDS` ✅ |
| 8 | strategic region target | `parser.py:~2015` → `:2023` | `_plausible_name_typo` ✅ |
| 9 | strategic marshal target | `parser.py:2029` → `:2037` | `_plausible_name_typo` ✅ |
| 10 | `executor._fuzzy_match_marshal` | `executor.py:442` → `:451` | `_correction_survives` ✅ |
| 11 | `executor._fuzzy_match_region` | `executor.py:569` → `:584` | `_plausible_name_typo` + `_MIN_FUZZY_TARGET_LEN` floor ✅ |
| 12 | `executor._broad_fuzzy_diplomatic_check` | `executor.py:686` → `:695` | `_correction_survives` ✅ |
| 13 | `executor._fuzzy_match_enemy` | `executor.py:768` → `:779` | `_correction_survives` ✅ |
| 14 | `StrategicExecutor` region resolver | `strategic_executor.py:161-170` | `_plausible_name_typo` + single-token gate ✅ |
| 15 | `StrategicExecutor._closest_marshal_name` | `strategic_executor.py:197-223` | `_plausible_name_typo` + ≤3-word gate ✅ |
| 16 | **`naval_executor` landing-region fallback** | **`naval_executor.py:577`** | ❌ **UNGATED** |

**Finding — seam 16.** `naval_executor.py:576-579` calls
`self._executor.fuzzy_matcher.match(target, list(world.regions.keys()))` with
no threshold override and **no `_plausible_name_typo`**. Measured against the
live 126-province board, that call returns:

```
Pass -> Nassau   (75, plausible_typo=False)
Line -> Berlin   (86, plausible_typo=False)
Guns -> Brunswick(75, plausible_typo=False)
Rear -> Bearn    (75, plausible_typo=False)
Moon -> Morocco  (75, plausible_typo=False)
```

i.e. exactly the WO-2 family the other fifteen seams were gated to stop.
⚠ **I could not demonstrate it reaching that call from a typed sentence** —
the parser's own gates null the target first (`land Soult in Moon` → target
`None`, `land Soult in the line` → target `None`, `land Soult in Munsterr` →
already corrected to `Munster` upstream). So: the seam is **ungated by
construction**, its **reachability from the typed road is UNVERIFIED**, and
anything that ever hands `naval_expedition` a target the parser did not
validate (a client payload, an LLM parse, a future chip) walks straight into
it.

### Also worth naming

- `_resolve_enemy_addressee` (`parser.py:402`) — the WO-1 addressee refusal.
  Consults the **exact enemy roster before** the region carve-out (`:487`),
  which is what stops France commanding the Prussian marshal `Brunswick`. Its
  typo arm is `_plausible_name_typo`-gated (`:494`).
- `modding/validator.py:1053, 1091` — the durable half: a scenario that
  authors a NEW marshal-named-after-a-province collision is refused at boot.
  The gate closes today's collisions "by lexical accident", not by knowing
  `Gascony` is a place (`executor.py:270-274`).

---

## 4. **CORE DELIVERABLE** — per-action reachability from the mock parser

Measured by `probes/probe_reachability.py` over all **65** ids in
`VALID_ACTIONS ∪ META_ACTIONS ∪ PARSER_ONLY_META`, on the real 1805 world.
"Reached" means the id appears as `action` (or as `diplomatic_data["action"]`)
from `_parse_with_mock` and/or `CommandParser.parse`.

### 4a. Reachable (60 of 65)

| action | reachable | a phrasing that reaches it | chain line |
|---|---|---|---|
| `attack` | ✅ | `Ney, attack Mack` · `Ney, storm Swabia` · `bombard Swabia` | 1826/1829/1842/1860 |
| `break_square` | ✅ | `Ney, break square` | 2112 |
| `build` | ✅ | `build a depot in Paris` | 2050 |
| `build_fleet` | ✅ | `build ships` · `lay down a ship` · `raise a fleet` | 1969 |
| `buy_off_design` | ✅ | `buy off Prussia` | 2207 |
| `cancel` | ✅ | `Ney, cancel order` · `halt` · `Ney, stop attacking` | 1802/1809/1819 |
| `change_autonomy` | ✅ | `grant Holland autonomy` | 2151 |
| `charge` | ✅ | `Murat, charge` | 1824 |
| `cheat` | ✅ | `cheat gold 1000` | 1300 |
| `debug` | ✅ | `/debug counter_punch Ney` | 1739 |
| `defend` | ✅ | `Ney, defend` | 1892 |
| `diplomatic_advisory` | ✅ | `Talleyrand, assess our situation` | 2701/2763 |
| `diplomatic_break` | ✅ | `break treaty with Prussia` | 2719 |
| `diplomatic_declare_war` | ✅ | `declare war on Prussia` | 2735 |
| `diplomatic_downgrade` | ✅ | `downgrade relations with Prussia` | 2725 |
| `diplomatic_error` | ✅ | `Talleyrand, attack Mack` | 2641 |
| `diplomatic_feasibility` | ✅ | `Talleyrand, what would it take to ally with Prussia?` | 2699 |
| `diplomatic_mission` | ✅ | `improve relations with Prussia` · `gather intelligence on Austria` · `court Prussia` | 2697 |
| `diplomatic_proposal` | ⚠ | `propose peace with Austria` — **see 4c** | 2765/2768 |
| `diplomatic_ultimatum` | ✅ | `issue ultimatum to Prussia` | 2741 |
| `drill` | ✅ | `Ney, drill the men` | 2055 |
| `economy` | ✅ | `economy` · `treasury` | 2098 |
| `end_turn` | ✅ | `end turn` | 1795 |
| `form_square` | ✅ | `Ney, form square` | 2107 |
| `fortify` | ✅ | `Ney, fortify` · `dig in` · `entrench` | 2046 |
| `garrison` | ✅ | `Ney, garrison Paris` | 2101 |
| `grant_dotation` | ✅ | `endow Ney with Swabia` | 2178 |
| `grant_pension` | ✅ | `grant Ney a rente` · `pension Davout` | 2198 |
| `grant_region_to_vassal` | ✅ | `cede Tyrol to Holland` | 2129 |
| `guarantee_nation` | ✅ | `guarantee Saxony` | 2209 |
| `help` | ✅ | `help` · `?` · `commands` | 1787 |
| `hold` | ✅ | `Ney, hold position` | 1882/1890 |
| `invest_vassal` | ✅ | `invest in Holland` | 2139 |
| `make_amends` | ✅ | `make amends with Prussia` | 2709 |
| `make_vassal` | ⚠ | `vassalize Holland` — **see 4c** | 2171 |
| `meta_command` | ✅ | `save` · `load` | 1768 |
| `move` | ✅ | `Ney, move to Alsace` · `go to Alsace` · `head for Alsace` | 1907 |
| `naval_diversion` | ✅ | `order the diversion` | 1973 |
| `naval_expedition` | ✅ | `land Soult in Munster` · `embark Soult for Munster` | 1977 |
| `propose_common_peace` | ✅ | `propose a common peace with Austria` · `settle with Austria` | 2746 |
| `purchase_levy` | ✅ | `purchase a levy for Ney` · `buy substitutes for Ney` | 2022 |
| `recall_marshal` | ⚠ | `recall Murat` — **see 4c** | 2007 |
| `recruit` | ✅ | `Ney, recruit infantry` | 2030 |
| `recruit_marshal` | ✅ | `commission Suchet` | 2010 |
| `release_vassal` | ⚠ | `release Holland` — **see 4c** | 2162 |
| `repair` | ✅ | `repair the damage in Paris` | 2089 |
| `repudiate_bargain` | ✅ | `repudiate bargain` | 1453 |
| `request_terms` | ✅ | `request terms from Austria` | 2753 |
| `restrain` | ✅ | `Murat, restrain yourself` | 2053 |
| `retreat` | ✅ | `Ney, retreat` · `pull back` · `fall back` | 1897 |
| `revoke_pension` | ✅ | `revoke Ney's rente` | 2194 |
| `scout` | ✅ | `Ney, scout Swabia` · `observe Swabia` | 1948 |
| `set_fleet_posture` | ✅ | `blockade the enemy` · `guard home waters` | 1873/1993 |
| `set_war_purpose` | ✅ | `set war purpose against Austria` | 1445 |
| `sponsor_design` | ✅ | `sponsor Prussia against Austria` | 2204 |
| `stance_change` | ✅ | `Ney, go aggressive` | 2059-2078 |
| `status` | ✅ | `status` · (any FACT question, via the desk) | 1798/1597 |
| `unfortify` | ✅ | `Ney, unfortify` | 2044 |
| `unknown` | ✅ | `asdf qwerty zzz` | — |
| `wait` | ✅ | `Ney, wait` · `stay put` · `Ney, pass` | 1866/2217 |

### 4b. **NOT reachable from the mock parser (5 of 65)**

| action | status | what actually happens | evidence |
|---|---|---|---|
| `pursue` | **LLM-only** | the chain returns `attack` (line 1842); `strategic_parser` then stamps `strategic_type = "PURSUE"` | `Ney, pursue Mack` → `action=attack, strategic_type=PURSUE` |
| `support` | **LLM-only** | chain returns `move` (1879/2037); upgraded to `strategic_type = "SUPPORT"` | `Ney, support Davout` → `action=move, strategic_type=SUPPORT` |
| `reinforce` | **LLM-only** | identical to `support` | `Ney, reinforce Davout` → `action=move, strategic_type=SUPPORT` |
| `march` | **LLM-only** | chain returns `move` (1907); upgraded to `strategic_type = "MOVE_TO"` | `Ney, march to Alsace` → `action=move, strategic_type=MOVE_TO` |
| `propose_white_peace` | **unreachable, full stop** | 4 phrasings tried; two become a *different* action, two shrug | see below |

**On the first four:** this is the documented design — the mock emits a base
action and the strategic layer upgrades it (`llm_client.py:1879` comment,
"Strategic parser upgrades to SUPPORT"; `providers.py` remaps the LLM's
`pursue`→attack / `march`,`support`,`reinforce`→move at the provider seam per
`CLAUDE.md` CR-3). They exist in `VALID_ACTIONS` **solely so the live model has
a word for them**. That is coherent, but it means four of the 56 entries in the
`## Valid Actions` prompt block (~1,248 chars of every escalation) describe
actions the deterministic layer will never produce and the provider
immediately rewrites.

**On `propose_white_peace`** — this one is a real hole:

```
propose a white peace with Austria  -> diplomatic_proposal   (success=True!)
white peace with Austria            -> diplomatic_proposal   (success=True!)
propose white peace                 -> unknown
offer a white peace to Austria      -> unknown
```

`grep -n "white_peace\|white peace" backend/ai/llm_client.py
backend/commands/parser.py` returns exactly **one** hit —
`parser.py:827`, the `valid_actions` membership list. No keyword branch
anywhere produces it. It is in `VALID_ACTIONS` (`validation.py:89`),
`META_ACTIONS` (`:167`), `DIPLOMATIC_ACTION_ALLOWLIST` (`:236`) and the LLM
prompt's action list. It is reachable only from the settlement UI. The worst
half is not the shrug: it is that the two *natural* phrasings quietly produce
a **generic proposal to Austria** and report success.

### 4c. Reachable, but the natural phrasing misses

| utterance | expected | measured |
|---|---|---|
| `offer an alliance to Prussia` | `diplomatic_proposal` | **unknown** |
| `propose an alliance with Prussia` | `diplomatic_proposal` | **unknown** |
| `demand Venetia from Austria` | `diplomatic_proposal` (demand tone) | **unknown** (works only as `Talleyrand, demand …`) |
| `make Holland a vassal` | `make_vassal` | **unknown** |
| `grant independence to Holland` | `release_vassal` | **unknown** |
| `bring Murat back` | `recall_marshal` | **unknown** |
| `Ney, take Vienna` | `attack` | **unknown** — *deliberate*, `attack_vocabulary.py:57-64` |
| `Ney, secure Vienna` | `hold` | **unknown** — *deliberate*, same block |

The alliance pair is the sharpest: `_proposal_keywords` (`llm_client.py:1543`)
carries `"propose alliance"` and `"offer alliance"` as **contiguous**
substrings, so inserting the English article `an` defeats both. Same shape as
`make Holland a vassal` against `"make vassal"` (2171) — the contiguity defect
class that F6 already fixed once for `change_autonomy` (see the comment at
2145: *"the old list required CONTIGUOUS phrases … so 'change Holland autonomy
to autonomous' … fell through to Unknown"*).

`grant independence to Holland` is the most interesting, because the code
**knows about it and routes it nowhere**: `llm_client.py:2133-2135` excludes
`"independence"` from `grant_region_to_vassal` with the comment *"abstract-object
idioms are excluded — 'grant independence to Holland' is a release phrasing,
not a cede"* — but `release_vassal` (2162) only matches `release <nation>`, so
the phrasing the comment names has no home at all.

### 4d. ⚠ The coverage gate does not cover what it claims

`tests/test_command_robustness_cr1_eval_harness.py:40` holds a **hand-written**
`MOCK_REACHABLE_ACTIONS` list (53 entries), and the gate at `:187` iterates
**only that list**. Comparing it to `VALID_ACTIONS ∪ META_ACTIONS ∪
PARSER_ONLY_META` (65):

Correctly absent (matching my measurement): `march`, `pursue`, `support`,
`reinforce`, `propose_white_peace`, `unknown`.

**Incorrectly absent — measured mock-reachable but outside the gate:**
`diplomatic_downgrade`, `diplomatic_feasibility`, `grant_region_to_vassal`,
`propose_common_peace`, `purchase_levy`, `recruit_marshal`.

Of those six, corpus coverage measured by counting `expected.action` +
`expected.diplo.action` across all 447 entries:

```
diplomatic_downgrade     0 entries     ← mock-reachable, ZERO coverage, invisible to the gate
propose_common_peace     0 entries     ← mock-reachable, ZERO coverage, invisible to the gate
diplomatic_feasibility   1
grant_region_to_vassal   3
purchase_levy            3
recruit_marshal          3
```

So the gate whose stated purpose is *"adding a new action to the parser without
corpus coverage fails CI"* has two mock-reachable actions with no corpus row at
all, because the list it walks is maintained by hand and has drifted. The fix
shape is to **derive** the list (walk `VALID_ACTIONS` and probe, or at minimum
assert the hand list ⊇ measured-reachable).

Corpus size note: the brief says 447 entries; measured `len(entries) == 447` ✅
(CLAUDE.md's "686" is the live-mode eval count, a different number).

---

## 5. The click road converges cleanly

`godot-client/project-sovereign/scripts/region_panel.gd:128-144` turns every
chip into a **typed command string** — `order:<verb>:<Name>` becomes
`"<Name>, <verb>"` (`:134`), `do:<command>` is emitted verbatim (`:140`). I ran
all 19 distinct chip strings the panel can emit (`:272`, `:332`, `:372-382`,
`:412`, `:424`, `:441`, `:462`, `:517-521`, `:545-557`) through the real
parser:

```
recruit {infantry,cavalry,artillery} in Paris   -> recruit      (target=Paris)
buy substitutes for Ney                         -> purchase_levy(marshal=Ney)
build {depot,fort,training ground,market,
       stables,watchtower} in Paris             -> build        (target=Paris)
repair buildings in Paris / repair Paris        -> repair       (target=Paris)
build ships                                     -> build_fleet
Ney, {fortify,unfortify,drill,scout}            -> the matching action
Ney, attack Mack                                -> attack       (target=Mack)
land Soult in Munster                           -> naval_expedition (Soult/Munster)
```

**19/19 parse correctly.** No finding here — worth recording as a negative
result, because it means the click road is not carrying any hidden parser debt.

---

## 6. Reproducing the chain table

```bash
cd C:/Users/User/PycharmProjects/project-sovereign-map
.venv/Scripts/python.exe <scratchpad>/cx_recon/probes/probe_reachability.py
.venv/Scripts/python.exe <scratchpad>/cx_recon/probes/probe_hazards.py
.venv/Scripts/python.exe <scratchpad>/cx_recon/probes/probe_confidence_full.py
.venv/Scripts/python.exe <scratchpad>/cx_recon/probes/probe_prompt_size.py
# ad hoc:
.venv/Scripts/python.exe <scratchpad>/cx_recon/probes/probe_parser_road.py \
    --raw --utt "Ney, garrison the stronghold"
```

---

## 7. What the census implies for the two design questions

Stated as measurements, not recommendations.

**Would a text predictor / autocomplete have something to predict from?**
Yes, and the vocabulary is already enumerable without a model: 57 ordered
branches, ~56 action ids, the live 126-region list, the live player roster, the
fog-filtered enemy roster and the live nation list are all already computed per
request in `_extract_known_nations` (`llm_client.py:536`) and
`build_llm_game_state`. The client already keeps `command_history` with
KEY_UP/KEY_DOWN recall (`main.gd:349, 929, 1010-1034`) and the backend keeps
`world.command_history` (`context_carryover.py:221`).
⚠ One collision to know about: **`KEY_TAB` is already bound** — it toggles the
terminal panel (`main.gd:959` and `main.gd:1161`), so TAB-to-accept is not free.
`fuzzy_matcher.py:242-248` carries a Phase-6 TODO describing precisely this
feature ("Godot autocomplete dropdown UI … Tap/click to select … Tab to accept").

**Is routing to the LLM worth it, as built?** The measured facts:
the model sees **6.1%** of corpus utterances (24/392, `probe_confidence_full.py`),
each costing ~**4,900 approximate prompt tokens** with **no caching**, up to
**3 blocking calls** per request in the worst case; and of those 24, the ones
that are *supposed* to be there are the CR-5 delegation arm (`deal with X`) plus
genuinely un-modelled deeds (`cover the retreat`, `fix bayonets`). The rest are
phrasing gaps of the kind §4c catalogues — which the deterministic chain could
absorb, since each is one keyword or one article away.
The gate's shape is also worth naming: it opens on **`unknown` (0.5)** and
**unresolved-address (0.55)** only. It cannot open on a *confidently wrong*
parse, because confidence counts identifiers rather than measuring meaning
(§2a). Every hazard in §1c ships at 0.8-0.95 and is therefore, by construction,
invisible to the model no matter how good the model is. That is the single
most load-bearing fact in this census.

---

## 8. Findings, ranked

| # | severity | finding | evidence |
|---|---|---|---|
| 1 | **P2** | `propose_white_peace` is unreachable from any typed phrasing, and the two natural ones silently become a generic `diplomatic_proposal` reporting success | §4b; `grep` shows one hit, `parser.py:827` |
| 2 | **P2** | The CR-1 coverage gate walks a hand-written list that has drifted; `diplomatic_downgrade` and `propose_common_peace` are mock-reachable with **zero** corpus rows and are invisible to it | §4d; `tests/test_command_robustness_cr1_eval_harness.py:40, :187` |
| 3 | **P2** | Diplomatic pre-routes outrank every marshal verb and only 3 of 14 carry `_addressed_marshal`; `Ney, invade Swabia` → `diplomatic_error` with the marshal dropped | §1c H4; `llm_client.py:1294, 1490, 1499, 1560` |
| 4 | **P3** | Contiguity defects: `offer an alliance to Prussia`, `propose an alliance with Prussia`, `make Holland a vassal` all → unknown. Same class F6 fixed for `change_autonomy` | §4c; `llm_client.py:1543, 2171` |
| 5 | **P3** | `"hold"` as a bare substring (1890) eats `stronghold`/`household`/`threshold` above fortify/garrison/drill/recruit | §1c H1 |
| 6 | **P3** | `grant independence to Holland` is excluded from `grant_region_to_vassal` *by a comment that calls it a release phrasing* and matches no release branch | §4c; `llm_client.py:2133-2135` vs `:2162` |
| 7 | **P3** | Unbounded keywords own whole sentences: `\bblockade\b`, `\brecall\b`, `"commission"`, `"autonomy"`, `licen[cs]e`, `" halt"` | §1c H5 |
| 8 | **P3** | `naval_executor.py:577` is the one ungated fuzzy seam of sixteen. Ungated **by construction**; ⚠ reachability from the typed road **UNVERIFIED** | §3 L5 seam 16 |
| 9 | **P4** | `"scou"` / `"acout"` (4-char, unbounded) match `scour`, `scoundrel` | §1c H2 |
| 10 | **P4** | `build` and `repair ` require a trailing space, so the bare verbs shrug | §1c H6 |
| 11 | **P4** | `"train"` at 2055 catches `constrain` / `entrain` (only `restrain` is guarded) | §1c H3 |
| 12 | **INFO** | `pursue`/`support`/`reinforce`/`march` are LLM-only ids by design, rewritten at the provider seam; they occupy ~4 of 56 entries in the prompt's action list | §4b |
| 13 | **INFO** | All 19 region-panel chip strings parse correctly | §5 |
| 14 | **INFO** | Confidence measures identifier count, not meaning, so a confidently-wrong parse can never reach the model | §2a, §7 |

### Corrections to the task brief
- `backend/ai/parser.py` does not exist → `backend/commands/parser.py`.
- `backend/commands/fuzzy_matcher.py` does not exist → `backend/utils/fuzzy_matcher.py`.
- Corpus entry count 447 ✅ confirmed (CLAUDE.md's 686 is the live-eval figure).
