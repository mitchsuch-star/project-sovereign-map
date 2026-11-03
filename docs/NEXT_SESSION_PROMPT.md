# NEXT SESSION PROMPT — Row AU "Authority as a currency": AU-1 the books and the figure (the first of seven slices, before S15)

> Overwritten each time a session hands off. Current hand-over: **November 3, 2026 — AU's design gate is RULED**
> (`docs/AUTHORITY_CURRENCY_SPEC.md` §4 the rulings, §4.1 the eighteen readings, §5 the design contract, §6 the
> seven slices, §7 AU-1's plan; the gate's record §8; Rule 9 §9). The user took the historically fuller option on
> the band (purchases down to 60), the pushes (the card, the order, the letter, plus crowns and offices), the pulls
> (the Chancellor at any standing, the Claims of the Army, the word broken, the Host's Complaint, two dated letters)
> and regrowth (the Te Deum, the Bulletin, the Return, the honour's payback, the Show); the recommended default on the
> display (a chip, the morning dent, one quote, the word "Authority"), the courts (parked, flipped by the user's word
> in AU-4) and the placement (all seven slices before S15, about 6.8 sessions, each its own commit and review).
>
> **FIRST — the user's confirmation of the eighteen readings (§4.1), before any code.** Each is one line to reverse;
> the ones that change the build's shape: the two floors (purchases refuse under grip 60, the letters' Declines keep
> 71, the Claims never under 80); the Word priced by the marshal's trust tier (2/3/4/5) with a loss-only stake and no
> defiance roll; the Te Deum in `cleanup_war_end` once per twelve turns per lord; the ring of 24 moves and the `held`
> dict on `AuthorityTracker` with `restore()`; the word "Authority" (the letters' "standing" lines re-worded); the two
> dated letters not armed until the user reads their forks (AU-2c); the slices' order (AU-3a may come before AU-2b).
>
> **THEN — AU-1 the books and the figure (§7; about 1.5 sessions; one commit through the hook; then stop for the
> user's review).** In this order:
> 1. **The instrument on HEAD, before any mechanic.** `tools/_standing_trace.py`, a twin of `tools/_moments_trace.py`
>    (install / uninstall; wrap `WorldState.advance_turn` for a morning row {turn, standing, grip, presence, the
>    courts' table, each marshal's grace clock}; wrap `AuthorityTracker.modify_authority` and the eight direct writers
>    — `authority.py:88/116/120`, `vindication.py:327`, `disobedience.py:2095`, `strategic_executor.py:4085`,
>    `meta_executor.py:1809`, `main.py:8343` — for a move row {turn, delta, cause, site}; `residual` = the turn's
>    change − the sum of moves; the summary into `meta["standing_trace"]`); the driver flag `--standing-trace`
>    (in-process; `--http` "unmeasured"); `ai_v_sweep.py`'s per-turn row gains `authority` / `grip` /
>    `nation_authority`; the HEAD record `tools/_standing_before_final.json` on the 55 arms (`tools/_affairs_measure.py
>    run`, the RE-6 set) plus `rf3_commanded_enacts` and the passive sweep — `residual` must name the five direct
>    writers on HEAD and read 0 after step 2.
> 2. **The books.** `backend/game_logic/standing.py` — `standing_of`, `move(world, lord, delta, cause, party="")`
>    (the player's tracker or `nation_authority`, as `reforms._spend_authority` splits today), `quote` (=
>    `reforms.authority_line` + `ledger.charges_grip_clause` + a Presence clause), `refusal` (the 60 gate — "" or the
>    reason), `spend`, `regrow` (keyed cooldowns in `held`, ceiling 95), `payload`, `ai_refusal` (the floor 30 and
>    three diplomatic points, extracted from `reforms.ai_purse_refusal:1256–1263`), `courts_move()` returning False.
>    `AuthorityTracker.authority` becomes a property over `_authority` (the setter clamps, appends to `moves` with the
>    caller's cause or "unattributed", stamps the morning's turn, fires the 70/50/30 events on every crossing and
>    re-arms on the way up); `moves` (24) and `held` in `to_dict` / `from_dict` (`from_dict` assigns `_authority` —
>    no phantom move on load); `restore(snapshot)` called by the strategic rollback at `strategic_executor.py:4085`;
>    `reforms._spend_authority`, `world_state._apply_sovereign_capture_consequences` and
>    `diplomacy.modify_nation_authority` delegate to `standing.move`; every one of the 32 write sites passes a cause
>    from `display_names.AUTHORITY_CAUSES` (in the creditor's voice; the battle rows carry `battle_name`);
>    `standing.quote` replaces `moments._plan_authority`'s inline copy and feeds `reforms.terms_line`; the
>    SAVE_FORMAT row.
> 3. **The figure and the dent.** One key `authority` on `build_base_response` (`main.py:716`) — {value, label, grip,
>    presence, moves[≤ 5]}, all ints; the hand-copy in `main.gd:6211–6264` (the join trap its own comment warns
>    about) and a join test; the code-built chip beside `dp_label` in `top_bar.gd._ready` (the Cancel-button
>    precedent, no `.tscn` edit), set from `update_diplomatic_fields`, tinted by line (gold ≥ 85, plain 71–84, amber
>    under 71, red under 50), the tooltip from `moves` and the lines (85 / 80 / 70 / 60 / 30); the dent clause appended
>    to `authority_label` in `dispatch.py:6001–6016` (the NPC-27 tail: both views, no client edit, a quiet morning
>    byte-identical, stamped at build because the stored dispatch is frozen) — "Your authority: 87 (Strong) — down 9
>    since yesterday: Ney honoured (−4), the field at Elchingen under your own hand (−5)"; a crossing of 85 adds "the
>    Presence falls below 85"; the threshold box's `title` / `message` keys (today it prints "Authority Changed" with
>    no text); the letters' "standing" button lines re-worded "authority"; the frames at both scales.
> 4. **The pins and the records.** `tests/test_standing_books.py` (an AST census: no `.authority =` outside the
>    tracker; a cause census: no production write with an empty cause; `residual` 0 on a scripted run; quote = apply
>    on a law and a letter; the rollback round-trip), `test_serialization_enforcement.py` and the played-world census,
>    the two-view dent pin, the join frame, `BASELINE_SERIES` byte-identical through the series rig
>    `tools/_standing_series_arms.py` (function seams in `tests/_standing_seams.py`; arm AUB the writer's passthrough;
>    no levers — the ratchet is at 231 of 231). The rows `BUG_FIXES.md` §AU: AU-1 the box prints no text (P2); AU-2
>    the events fire only on an objection answer; AU-3 an authority-priced Accept is free at the floor; AU-4
>    `group_orders.authority_of`'s default 75 against the table's 60 (owned by the AU-4 slice); AU-5 the grip's flat
>    75 for every court (owned by the AU-4 slice). The rules `SYSTEMS_REFERENCE.md` §169; the landing record spec
>    §6.1; STATUS's AU-1 line; the plan and roadmap rows; this prompt rewritten for AU-2a.
>
> **THEN — AU-2a the hits** (§6), after the user's review: the Chancellor `bites: "floor"`, the Claims, the breach,
> the Host's Complaint, the stakes told, the reach re-run; then AU-2b, AU-2c, AU-3a, AU-3b, AU-4; then S15 with
> RE3-6 / RE3-7 at its head (RE3-9 the same).
>
> **Traps the row has paid for (do not re-discover):** the ratchet has NO headroom — levers 231 of 231 (seams are
> named functions), functions over 500 lines 28 of 28, `WorldState.to_dict` 497 of 500 (every new field on the
> tracker), CLAUDE.md within 62,000 LF bytes (pay a row by a trim); `strategic_executor.py:4085` rewrites the
> tracker's figure and answers directly (restore the ring with it); `headline_lead_memory`'s carry-over whitelist
> (`dispatch.py:3799–3815`) drops any new key; the stored dispatch is frozen and `GET /dispatch` re-serves it; the
> `authority` payload must be added to `main.gd`'s hand-copy or the chip stays blank; `get_imperial_grip` is uncached
> (compute once per nation per morning); `reforms.authority_line` is pinned by `test_rf4a_the_laws_tab.py` (wrap it,
> never change it); 62 test files read the tracker (`test_v2b_session1.py`, `test_severity_modifiers.py`,
> `test_napoleon_np4_peril.py:256–258` the capture shock, `test_r1_pipeline_enforcement.py:278–305` the field's
> ±5 — their VALUES do not move at AU-1, only their causes); the spec, `SYSTEMS_REFERENCE.md`, `BUG_FIXES.md`,
> STATUS, the plan and the roadmap are CRLF — edit through Python on bytes and assert each replacement matches once;
> `Path.write_text` turns LF into CRLF — write bytes; the shell heredoc eats long blocks and `\n` — write scripts with
> the Write tool; the deck JSON files are hand-formatted — insert text, never re-dump; the series rig's `prior` is
> HEAD's baseline (`git show`); attribute a series move by event; commit with
> `env -u PYTHONDONTWRITEBYTECODE git commit -F <file>` from Bash in the background (the hook runs ruff and the full
> suite, about ten minutes; never `--no-verify`); a Godot engine run is one per machine.
