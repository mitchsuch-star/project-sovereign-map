# NEXT SESSION PROMPT — Pre-Deploy S8: DD-1 "The Table and the Treaty", Step 3 THE VERBS

> Overwritten each time a session hands off. Current hand-off: **October 11,
> 2026, after S7 Slice B landed `treaty.can_sign`, the ratifier's spine** —
> the ONE verdict read by every surface that shows a letter, a chip, a price
> or a counsel line AND by the ratifier, which keeps no guard of its own;
> `stamp_option` writes both key pairs and the `closed_clause` marker. **DD1-1
> … DD1-4 + DD1-12 FIXED (all twelve DD1 rows closed); SFR-B1 / B2 / B5 /
> D34 FIXED; the sweep 11 / 2 → 0 / 0 on every committed arm and the three
> seeds; the fuzzer and the shuffle still 0; the diplomacy pillar 8.5 on a
> re-read of its eight feeding arms; `BASELINE_SERIES` byte-identical.**
> Landing record `docs/PRE_DEPLOY_PLAN.md` §3.1 "DD-1 S7 landing record,
> Slice B"; rules `SYSTEMS_REFERENCE.md` §108; pins
> `tests/test_dd1_s7_can_sign.py` (25) + `tests/test_dd1_sign_ability_sweep.py`
> re-seated to 0 / 0. Routing authority: `docs/PRE_DEPLOY_PLAN.md` §2 (the
> order — S7 STRUCK; S8 = DD-1 Step 3 the verbs; S7b = CODE-3 + DD-C) → §3.1
> (DD-1); `docs/STATUS.md` ▶ NEXT UP and the `CLAUDE.md` LIVE STATE line
> point there. The Score Finish residue (`SCORE_FINISH_SPEC.md` §3 Step 9)
> stays PAUSED behind the plan until S14.
>
> Paste everything below the line as the opening message of a fresh session.

---

**Pre-Deploy S8 — DD-1 "The Table and the Treaty", Step 3: THE VERBS.** Routing authority = `docs/PRE_DEPLOY_PLAN.md` §2 → §3.1 "The verbs". Work directly on master per `CLAUDE.md`'s workflow; commit and push at the clean slice. `git fetch origin` first and read `git log -3 --stat` before touching anything. **The head of this session is CODE-1 batch 4** (`docs/CODE_HEALTH_PLAN.md` §CODE-1 — the batch the plan names after batch 3; batch 5, the 116 levers in the `game_logic` modules over 3,000 lines, rides the head after this one). Record which batch you take in the landing record.

**Read first, in this order:** `docs/PRE_DEPLOY_PLAN.md` §3.1 "The verbs" and the three landing records under it (S6: what the instruments said; S7 Slice A: the one exit; S7 Slice B: the verdict and what was found fixing); `SYSTEMS_REFERENCE.md` §107 (the one exit — the truce's rule the announce half must name) and §108 (the verdict every new verb's chip and refusal must read); `docs/BUG_FIXES.md` §Step 8 rows **SFR-D42** (an ally keeps a liberated French home province, unannounced, and it cannot be asked back — `Talleyrand, ask Spain to give back Provence` → "I await your instructions"), **SFR-D40** (the allegiance auction gives no way to bid — `Talleyrand, bid for Sardinia`), **SFR-D28** (a truce with Austria left Bavaria's war running under four French corps, unannounced — its ENTRY half landed in Slice A as DD1-8; the ANNOUNCE half is this slice's); `docs/AI_INTENT_SPEC.md` §12.6 (the allegiance auction — "announced as in-play and biddable by both sides") and §4.2d; `docs/ADDING_CONTENT.md` + the `CLAUDE.md` "Adding a new action" recipe (twelve steps — the corpus row, the routed-order-words regeneration, the display maps).

**Corrections the reads established (do not re-derive):** the auction lives in `ai_diplomacy.py` (grep `allegiance`; the minor offers the best pact the relation permits through `best_ratifiable_treaty` when the player wins the bid — SF-V1); the three verbs go through the shared executor (GR5 — the AI bids and asks back through the same functions, never a second implementation); every new chip reads `treaty.can_sign` for its availability and every refusal speaks in words (`treaty.names_a_raw_code` is the pin's regex); a new dialogue type needs the `main.gd` dtype whitelist; the truce's followers are the clients that `follow_the_lord` moves (§107.1) — the announce half says, on the armistice's confirm AND in the dispatch, which satellites' wars the truce leaves running and which it binds.

**Slice C — the verbs, one at a time, each landed with its attribution test:**
1. **`ask <ally> to return <province>`** (SFR-D42): a liberated French home province held by an ally (the ally entered it as a liberator — `nation_starting_regions[player]` names it ours; the ally holds it). Priced by the acceptance formula (an ally at war beside us, the province's worth, relations), or refused with the clause (the ally's own homeland, a province it took by its own war purpose). A new `diplomatic_` action through `VALID_ACTIONS`, the parser's keyword chain, the executor, `_action_costs`, the display maps, the corpus row, `python -m tools.gen_routed_order_words`; a wizard chip under the ally's card; the AI asks back through the same function (GR5) when a court's home province is held by its own ally.
2. **`bid for <court>`** (SFR-D40): on an OPEN allegiance auction (AI_INTENT_SPEC §12.6 — announced "in play"), the player bids relations / gold / a guarantee; the auction resolves at its own tick by the existing `best` comparison; the winner's pact arrives through SF-V1's net. A chip on the auction's notice; the refusal when no auction is open names the court.
3. **The truce's followers announced** (SFR-D28's announce half): the armistice's `proposal_confirm` and the morning dispatch name the satellites whose wars the truce BINDS (`follow_the_lord`) and the allies whose wars it LEAVES RUNNING ("Bavaria stays at war with Austria — four French corps stand in Swabia under the truce"); through `get_peace_commitment_conflicts`'s follower line (SR-1b) and the dispatch's treaty event.

**Done when:** each verb reaches through the typed road AND a chip; the corpus gate passes; `python -m tools.gen_routed_order_words` regenerated; `tools/sign_ability_sweep.py` still 0 / 0 (the new chips are polled by it — re-record if the verdict counts move, with the reason); the fuzzer and the shuffle 0; `BASELINE_SERIES` byte-identical or re-recorded once with the verb's reach counted (the AI never bids or asks back in v1 unless GR5 says it must — §3.1's own rule); the three SFR rows struck with their pins.

**Records the commit carries:** `PRE_DEPLOY_PLAN.md` §3.1 "DD-1 S8 landing record, Step 3" + the §2 S8 row struck, `STATUS.md` ▶ NEXT UP (seven ▶ blocks at most — move the oldest to `docs/archive/STATUS_2026_Q4.md`, newest first), the `CLAUDE.md` LIVE STATE line (62,000-byte cap, lower-only; the ratchet also wants it within 8,000 of the cap — it sits at the cap now, pay for a new row by shortening an older one), `SYSTEMS_REFERENCE.md` §109, `BUG_FIXES.md` rows struck, `docs/SAVE_FORMAT_REFERENCE.md` for any new serialized field (the auction's bids will need one), this file rewritten for S7b (CODE-3 + DD-C).

**Traps.** A Bash heredoc turns `\b` into a BACKSPACE byte, a `'` inside an inline `python - <<EOF` aborts the command, and a heredoc with non-ASCII prose aborts outright — write every script AND every doc append with the Write tool, run it by path. `git add -A` never; the hook runs ruff + the full parallel suite (~6 min, the three dd1 pins run live instruments): commit in the background with a message file, never `--no-verify`, never edit a tracked file while it runs. `ruff` is not on Bash's PATH — `".venv/Scripts/python.exe" -m ruff check backend/`. The console is cp1252: every tool reconfigures stdout to UTF-8. **The fuzzer's live pin (`test_dd1_treaty_fuzzer.py::TestTheInstrumentLive`) walks differently per PYTHONHASHSEED** — a failure that does not reproduce is a hash-seed walk; reproduce with `PYTHONHASHSEED=<n> pytest -k test_two_seeds` for n in 0…5 before fixing anything. The silent-handler ratchet (`test_code_health_ratchet.py`, cap 367) counts every `except Exception` that neither logs nor re-raises — do not add one. `score_run check` rewrites four archive files — run `check` only on a scratch `--out`, never on `docs/audits/score_runs/`. `core.autocrlf=true`: keep each file's own newline. Never kill a `-m backend.main` process. The blind census files stay blind.

**Do not:** change balance, re-score, touch the Score Finish residue, add a lever (land a change with its attribution test instead), edit a committed blind file, weaken a gate, tune the instruments to the fixes, give a new verb a refusal in a snake_case key.
