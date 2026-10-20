# NEXT SESSION PROMPT — Pre-Deploy S14 part 3: PC-R7 (ii)'s last piece — the coalition's no-separate-peace bond

> Overwritten each time a session hands off. Current hand-over: **October 20, 2026, after S14 part 2 ("declared
> goals" — the war's articles) landed** (commits through the hook — `git log -2`).
>
> **What part 2 delivered** (`SYSTEMS_REFERENCE.md` §134; the row `BUG_FIXES.md` §PC PC-R7 — OPEN for the bond, its
> pin named; siblings PC-X33 … X42 FIXED, PC-X43 … X45 OPEN at this part's head; pins `tests/test_pc_rulings.py::TestPCR7::test_ii_m_*` … `test_ii_r_*`,
> `TestTheS14Part2Siblings`):
> - **`backend/game_logic/declared_goals.py`** is the ONE module: the War Purpose card's second step names up to two
>   ARTICLES (a province of the target, an indemnity, a client), each priced at the declaration in
>   `coalition.TREATY_ANNEX_ALARM_PER_PROVINCE` (8; a client 8 a province it carves) on the declarer's slot, stored as
>   `declared_terms` on the war-objective record (saved deep); the first button is "Declare war — <purpose>, no
>   articles". GR5: `war_council._declare_design_war` declares the design's provinces (`design_articles`).
> - **At the table:** `settlement_scoring` reads the tier legitimacy's surprise without the proposing side's declared
>   articles (`undeclared_terms`); the PROPOSE mount's empty draft opens on `declared_draft`; the guided rows lead with
>   "Declared at the war: X" (`guided_suggestions`); the counsel's table road prices the declared draft first
>   (`build_settlement_preview(…, declared_when_empty=True)`).
> - **At the peace:** `settle_at_peace` at every treaty seam (the player's table, the AI's table and pair exit, the
>   bilateral `_ratify_war_end`, the truce's signed exits) and `sweep_concluded` (from `_cleanup_old_war_objectives`)
>   for the roads with none; a dropped article refunds half its alarm, named on the aftermath line.
> - **The instruments:** `tools/_pc_s14p2_series_arms.py` (A / L / R / O, six arms) — every arm byte-identical to
>   `BASELINE_SERIES`, the reach non-empty; the DD-1 sweep A = 0 / B = 0 on all nine arms; the fuzzer 0 violations; the Godot parse harness EXIT 0.
>
> **Traps part 2 paid for:**
> - The ratchet counts functions over 500 lines and `campaign_log.filter_campaign_log` sits at 499: a new event type's
>   fog rule goes in a module constant (`_PURPOSE_EVENT_TYPES`), never a wrapped tuple in the function.
> - The dialogue-chain census pins the arm count (`tests/test_code2c_the_dialogue_choice_is_staged.py`, 74 now): an
>   added or folded `ctx.action` arm moves it — update the count and its docstring in the same change.
> - The closed answer grammar takes only an exact label, a unique head word or a registered keyword: a new dialogue
>   step needs its words in `dialogue_routing.DIALOGUE_ACTION_KEYWORDS` (the drivers type "Conquest", answer "1").
> - The series children import lazily — never edit `backend/` while `tools/_pc_s14p2_series_arms.py` (or any arm
>   tool) runs.
> - `RatifyTreatyContext` is a slotted dataclass: a new stage field is declared `field(init=False)` and read with
>   `getattr(ctx, …, None)`.
> - The bash heredoc still breaks on prose with quotes: every doc section through the Write tool, then a short
>   Python appender; a manual run from this shell needs `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING`.
> - `CLAUDE.md` stands 73 bytes under its 62,000-byte cap: swap its live-state rows, shorten as you swap.
>
> **Nothing waits on the user before S15** (UXR-4, the code-signing certificate and AO's three questions are theirs).
> Paste everything below the line as the opening message of a fresh session.

---

Pre-Deploy S14 part 3 — PC-R7 (ii)'s last piece, "the bond" (Chaumont, 1814) — build on master in the shared checkout `C:\Users\User\PycharmProjects\project-sovereign-map` (read `git log -2` for the head).

Read first: `docs/STATUS.md` ▶ NEXT UP, `docs/PRE_DEPLOY_PLAN.md` §2 S14, `docs/BUG_FIXES.md` §PC row PC-R7, `docs/audits/PEACE_CONUNDRUM_2026_10_15.md` §40 J and §46 J, `docs/SYSTEMS_REFERENCE.md` §133–§134 (parts 1–2 as built) and §122–§127, `COALITION_SPEC.md` §6a (the loyalty term) with `ai_diplomacy.coalition_break_ranks_reason` / `court_own_readiness` / `coalition_loyalty_penalty`, `coalition._process_british_subsidy` / `projected_paymaster_subsidy` (the paymaster's subsidy the bond is priced from), and `backend/game_logic/instruments.py` (`grant_directed_sponsorship`'s `kind="neutrality"` record, `process_instruments`' renege arms — the D5 records the bond rides).

Scope — the design is pre-decided here (rule the details at the head, measured; flag any reversal):
0. **First, the user's rule (October 20, 2026): diplomacy is never typed.** The door's last typed-only diplomacy gets its UI: PC-X43 Make Amends (a Cabinet row on the wronged court, both variants priced, the executor's refusals as the row's reasons), PC-X44 repudiating a war bargain (a row on the ally's page through the existing `confirm_repudiate_bargain` confirmation), PC-X45 the bid's sum (a sum control on Bid for Their Allegiance; the door stops saying "or type"). Each verb then leaves `main.gd`'s `DIPLO_NO_HOME_KEYWORDS` for the Cabinet's family (the door claims it and names the row — PC-X42's pattern, `declared_goals.war_purpose_action` + the wizard arm + `tests/test_wo_slice7_cabinet_door.py`). Pins `tests/test_pc_rulings.py::TestTheS14Part3Rows`. No hint, line or doc may tell the player to type diplomacy.
1. **The bond (Chaumont):** when a league stands with two or more members at war with France, the paymaster (the `paymaster` design's court) may bind a member — a D5 directed record of a new `kind="bond"` beside `"neutrality"`: the payer buys the member's commitment NOT to sign a separate peace, for a term, at a subsidy per turn, priced from the paymaster's own subsidy (`projected_paymaster_subsidy` — derived, never invented). Minted by the AI's paymaster through the same function the player would call (GR5), dated, serialized, shown on the instruments line and the Diplomatic Ledger.
2. **What it binds:** the bonded member's break-ranks read (`coalition_break_ranks_reason`) tightens by the bond's strength (its thresholds read deeper while the term runs), its row at the table carries the bond as a named component (in `settlement_scoring`'s per-court read, priced, beside the loyalty term), the bilateral's `coalition_loyalty_penalty` reads it too, and breaking it (a separate peace inside the term) is `bargain_reneged` against the member through the instruments' renege arm (the strongest grievance).
3. **France bids against it:** the compensation clause (`territory_compensate`) or gold at the table offsets the bond's component — priced, never a veto; the counsel names the bid ("the bond costs her 12 at the table; Franconia pays it").
4. **Then SF-RR7 "the morning of the peace"** (SFR-B3, ruled "Europe waits on Paris"; with DDB-X4, the Congress's series arms flipping live levers) if the part has room; otherwise it heads part 4, named in STATUS.

Rules: reproduce each gap on a board before building (the Vienna-held board and the ulm board, `tests/fixtures/pc_boards/`); the sibling sweep after every fix (CLAUDE.md Rule 10 — each sibling filed and fixed in this part or heading the next); every change that reaches the AI runs the attribution arms (`tools/_pc_s14p2_series_arms.py`'s idiom: function seams and data seams, never a new lever) with `BASELINE_SERIES` byte-identical or every movement attributed and named; the DD-1 sign-ability sweep and the treaty fuzzer re-run where `can_sign` or a ratifier moves; the Godot parse harness if a `.gd` changes. New serialized fields: `to_dict` / `from_dict` with `.get` defaults and `tests/test_serialization_enforcement.py`. Commit through the hook by explicit path, in the background: `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING git commit -F <msg> -- <paths>`; never `--no-verify`, never stash, reset or switch branches.

Done when PC-X43 … X45 are FIXED (no diplomatic verb left on the door's no-home list) and the bond is minted by the paymaster, priced at the table and in the break-ranks read, reneged as a broken bargain and biddable by France — pinned in `tests/test_pc_rulings.py::TestPCR7::test_ii_the_bond_is_priced_and_biddable` — the PC-R7 row is CLOSED, and STATUS ▶ NEXT UP names what follows with this file overwritten for it.
