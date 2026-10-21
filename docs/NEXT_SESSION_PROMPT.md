# NEXT SESSION PROMPT — Pre-Deploy S14 part 4: SF-RR7 "the morning of the peace" (SFR-B3, with DDB-X4)

> Overwritten each time a session hands off. Current hand-over: **October 20, 2026, after S14 part 3 ("the bond" —
> PC-R7 (ii)'s last piece, Chaumont) landed and PC-R7 CLOSED** (commits through the hook — `git log -2`).
>
> **What part 3 delivered** (`SYSTEMS_REFERENCE.md` §135; the row `BUG_FIXES.md` §PC PC-R7 — CLOSED; siblings
> PC-X52 … X60 FIXED; pins `tests/test_pc_rulings.py::TestPCR7::test_ii_the_bond_is_priced_and_biddable`,
> `test_ii_s_…`, `test_ii_t_…`, `TestTheS14Part3Siblings`):
> - **`backend/game_logic/bond.py`** is the ONE module (siblings PC-X52 … X68 FIXED — the truce's exits, the AI's letters, the pair exits, every surface that names the league's hold; X69 heads this part): a dated D5 directed record of `kind="bond"` (the payer pays a
>   co-belligerent its own subsidy a turn for 10 turns; she makes no separate peace with the common enemy while the
>   payer fights on). The league's paymaster mints it (`ai_paymaster_binds`, coalition step 4b) for the member that
>   would break ranks now and whom the bond would hold; France binds her own ally from the Cabinet ("Bind <ally> to
>   the War" — the new verb `bind_to_war`, GR5's one `mint_bond`).
> - **Priced on each surface at its own gold rate:** the break-ranks lines deeper (`ai_diplomacy.break_ranks_lines`,
>   the ONE read of P1's lines), the table's `coalition_bond` on her separate peace (the stream still owed), the
>   bilateral's `coalition_bond`; a separate peace inside the term is `bargain_reneged` against her
>   (`instruments._bond_verdict`). France's bid (`bond.bid_gold` — 1,000 gold for a fresh 400 bond, or a
>   compensation) offsets it — named by the counsel, offered at the table, staged by the Cabinet's "Outbid <payer>'s
>   Bond" (the wizard's structured `bond_bid`).
> - **The instruments:** `tools/_pc_s14p3_series_arms.py` (seams B D T L S): arm 0 byte-identical to the prior,
>   every read byte-identical alone, the mint alone moves the series (Britain binds Austria at turn 10; France's alarm
>   2 from [25]/[28] to [21]) — `BASELINE_SERIES` RE-PINNED with the record beside it; the historical records' links
>   read `SERIES_BEFORE_THE_BOND`; the DD-1 sweep and the fuzzer re-run; the Godot parse harness EXIT 0.
>
> **Traps part 3 paid for:**
> - The bash heredoc mangles regex backslashes (`\b` in an edit script): write every edit script with the Write tool
>   and run it with the venv Python (`python` is not on the bash PATH).
> - A new TABLE component moves two component-set pins (`tests/test_common_peace_acceptance.py`,
>   `tests/test_settlement_guided_terms_slice3.py`) and the spoken-blocker census (`tests/test_ca8_gate_closeout_
>   2026_08_07.py` — every negative-capable component needs a phrase); a new BILATERAL component goes in
>   `_generate_feedback`'s trackable set and `display_names.FEEDBACK_STRINGS` (both signs).
> - A new player verb is the full recipe (CLAUDE.md "Adding a new action") PLUS: the mock parser's war and peace
>   routes may claim the sentence first (`llm_client._names_the_bond` is the exclusion idiom); `main.gd`'s door rule
>   and `DIPLO_CABINET_CONTROLS`; the door census (`tests/test_wo_slice7_cabinet_door.py` — `FAMILY_ACTIONS` and the
>   Python mirror `_redirect_verdict`); the chip-honesty census (`tests/test_cn4_the_chip_honesty_census.py` —
>   `WIZARD_NATION`, the payloads, `_compose`'s named values, `_expected_echo`'s branches).
> - A structured wizard field needs `CommandRequest`, the override in `_command_parse`'s stage, the wizard's
>   `_structured_payload_for_action` — and its echo on `ECHO_IS_DISPLAY_ONLY` when the typed echo does less (the
>   census pins that set).
> - When `BASELINE_SERIES` moves: the drill-fix lineage pin gets one more link
>   (`tests/test_ai_drill_fix_2026_09_27.py`), and every historical record's link reads `SERIES_BEFORE_THE_BOND`
>   (eight files) — never the live series. Give each AI-reaching read its OWN seam: a shared read (`bond_on`) held
>   down makes every single arm inert.
> - `CLAUDE.md` stands at 61,920 bytes (cap 62,000): swap its live-state rows, shorten as you swap.
>
> **Nothing waits on the user before S15** (UXR-4, the code-signing certificate and AO's three questions are theirs).
> Paste everything below the line as the opening message of a fresh session.

---

Pre-Deploy S14 part 4 — SF-RR7 "the morning of the peace" (SFR-B3, ruled "Europe waits on Paris"; with DDB-X4) — build on master in the shared checkout `C:\Users\User\PycharmProjects\project-sovereign-map` (read `git log -2` for the head).

Read first: `docs/STATUS.md` ▶ NEXT UP, `docs/PRE_DEPLOY_PLAN.md` §2 S14, `docs/BUG_FIXES.md` rows SFR-B3 (the Score Finish table) and DDB-X4 (§DD-B), `docs/audits/DD_B_RULINGS_2026_10_14.md` §2 SFR-B3 and §3, `docs/SYSTEMS_REFERENCE.md` §135 (part 3 as built — the series idiom) and the Congress of Paris sections (GE-3), `docs/ENDGAME_PLAN.md` §2.3–§2.4, `backend/game_logic/congress.py` (`sitting`, the refusers' lowered gate, `_proclaim` — the signing), `backend/game_logic/coalition.py` (`process_coalition_turn` steps 6–7 — the brew's countdown and the declaration; `ARMED_PEACE_WATCH` = 45), the turn order (`world_state.advance_turn`'s coalition tick runs before the Congress's own tick in `turn_manager.py`), and `tools/_ge3_series_arms.py` (its `LEVERS` name constants `congress.py` no longer defines).

Scope — the design is ruled (rule the details at the head, measured; flag any reversal):
0. **The user's rule (October 20, 2026): diplomacy is never typed.** Anything new the player does is a Cabinet row or a row's `choices` (`backend/game_logic/cabinet_rows.py`), the door claims any typed form, and no line teaches typing.
1. **The hold:** while the Congress sits and fewer than two great powers refuse it, no new league declares against France — a brew's countdown holds at its last turn; the two-refuser lowered gate is untouched.
2. **The signing** (`congress._proclaim`) spends Europe's alarm to the Armed Peace watch (45) and dismisses any brew.
3. **The page** (the Imperial Peace's) names what the peace buys: the great powers' signatures, not the lesser courts' grievances ("a peace buys time, not immunity").
4. **PC-X69 (filed by part 3's census, heads this part):** the Congress's forced suit (`congress.court_must_sue` / `sue_due`, read above P1) ignores the league's bond — a great power the paymaster binds signs at the Congress unread and the renege arm brands her while her payer fights on. Rule what her suit is (the league's common act, or her priced separate peace) and pin it (`tests/test_vp2_the_imperial_peaces_morning.py::TestPCX69`).
5. **DDB-X4:** `tools/_ge3_series_arms.py`'s arms flip live levers (seams), the new rule's among them, and the dormancy proof re-reads byte-identical.
6. **Not taken (ruled):** minor courts signing with their patron (a rule change to §2.3's four courts).

Rules: reproduce each gap on a board before building (the PRESS arm's morning of the peace — `tools/score_run.py`'s PRESS arm and the `docs/audits/score_runs/2026_10_05_econ_gate` archive's day-before shape; `tests/fixtures/playtest_saves/fixture_ge3_pressburg.json`); the sibling sweep after every fix (CLAUDE.md Rule 10 — each sibling filed and fixed in this part or heading the next); every change that reaches the AI runs the attribution arms (`tools/_pc_s14p3_series_arms.py`'s idiom: one seam per change, never a module lever) with `BASELINE_SERIES` byte-identical (the ruling expects it: the rule is gated on a sitting or signed Congress) or every movement attributed and named; M1–M7 likewise; the DD-1 sign-ability sweep and the treaty fuzzer where `can_sign` or a ratifier moves; the Godot parse harness if a `.gd` changes. New serialized fields: `to_dict` / `from_dict` with `.get` defaults and `tests/test_serialization_enforcement.py`. Commit through the hook by explicit path, in the background: `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING git commit -F <msg> -- <paths>`; never `--no-verify`, never stash, reset or switch branches.

Done when the PRESS arm's morning of the peace carries no league formed against France, the alarm reads 45 after the signing, the page names what the peace buys — pinned in `tests/test_vp2_the_imperial_peaces_morning.py` (with `::TestDDBX4` for the live levers) — the rows SFR-B3, DDB-X4 and PC-X69 are FIXED, and STATUS ▶ NEXT UP names what follows (the Score Finish residue, SF-RR1 (ii) … RR6) with this file overwritten for it.
