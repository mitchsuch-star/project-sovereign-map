# NEXT SESSION PROMPT — Row RE "Affairs of State": RE-C LANDED (the user's review first), then RE-R the reactions; row AU queued after RE

> Overwritten each time a session hands off. Current hand-over: **November 1, 2026 — RE-C the Correspondence LANDED**
> (rules `SYSTEMS_REFERENCE.md` §165; the record `RECURRING_EVENTS_SPEC.md` §23; one commit through the hook), after
> RE-H the Haiti letter in three commits the same day (`247e4e27` H0 the bill alone, `2b47a93a` the squadron,
> `98bb5910` Decrès to headquarters — §22, §164); the row before S15 by the user's ruling of October 31 (§0c). **The
> deck carries four letters** (the Arch-Chancellor's Letters, the Host's Claims, Berthier's Memorial, the Haiti letter in
> its two forms) **and now a home:** a page of the Morning Dispatch, "The Correspondence (1 standing)" in the action row
> (amber with news, "(a squadron at sea)" while five of the line are out, absent on a world without a deck), one column of
> parchment slips — ON THE DESK (the letters that wait, their answer-by date, both priced answers, Read the letter ▸),
> IN THE OFFING (the Watch's lines), ANSWERED newest first (the apostille "{caption}. — N." with the seal, the receipt,
> the echo dated the next morning or "At sea — five of the line; word expected about {date}." and then the fate in
> rubric, the chips Bavaria ▸ / Admiralty ▸ / Laws ▸), LEFT UNANSWERED / SET ASIDE (one dim line each), the closing record
> when the Haiti file closes; "◂ The Dispatch" turns back. Read-only but for Read the letter ▸; no badge, no sound, no
> hotkey, no new endpoint. **Measured at RE-H (55 runs, unchanged by RE-C — the page stores nothing):** the Haiti letter
> on 24 runs; the letters traded places and the total per campaign barely moved (the pulse's gap and the cooldowns set
> the volume, not the deck's size).
>
> **FIRST — the user's review, before any code:** RE-H's readings (§22.1 ten, §22.2 eight, §22.4 ERR-5 and the trade of
> mornings) and RE-C's twelve (§23.2: Not Now is the client's; the caption derived; the Watch read pure; Read the letter ▸
> on the desk only; the closing record from the morning after `ends` — P13's earlier close is not built; the set-aside
> section's three kinds; a slip is a node subtree; the ceiling is the letter's; the device at 24 px; the pointer clause;
> the Strategic Ledger's first-open road; the at-sea line in the echo's place), and the rulings on RE3-6, RE3-7, RE3-9.
> Build nothing on those three rows. **Row AU — authority as a currency, the push and the pull — is queued AFTER RE and
> before S15** (`docs/AUTHORITY_CURRENCY_SPEC.md`; the gate first, in its own session, after RE-5). Do not start AU
> before RE-5 closes.
>
> **THEN — RE-R the reactions (§12c the contract; §16b 0.75 sessions), its own commit; records §24 /
> `SYSTEMS_REFERENCE.md` §166 / finds `BUG_FIXES.md` §RER.** The budget on every template: at most one line per surface
> per letter, at most three per letter across all surfaces over three turns, one Gazette COURTS line per letter, no new
> rail notice beyond the arrival's own, the only sound the seal. The list, from §12c and §16b's row: **the SITUATION
> key** `situation["affair_receipt"]` in `dispatch._build_situation` beside `law_sink` / `act_sink` — the answers'
> receipts the morning after (the squadron's FATE line `affair_fate` already landed at RE-H, amber in both views;
> the receipt line is plain), rendered in BOTH views that print the Staff's line (`dispatch_view.gd`'s dispatch page
> and the terminal's morning dispatch in `main.gd`), with a two-view pin like `test_rf4b_the_laws_everywhere.py`'s;
> **the COURTS predicate in `compose_issue`** (`gazette.py`) — one line per letter from the answered row's `press`
> through the shared one-liner (`campaign_log.py`), gated per row (an affair's `arrived` row never prints; a squadron
> letter prints its `outcome` row, not its `answered` row), never in `filter_campaign_log` (499 lines against the cap
> of 500); **the echo on the answer's own response message** (`moments.answer` — already the court's reply or the
> minister's acknowledgement; confirm every template's `echo` reaches it and the Haiti letter's two forms read right);
> **`HOST_REMARKS` and `remark_by`** — the host court's remark on the player's answer, written into the row at the
> answer (`remark_by` ≤ 40, the state row's field §12b.1 names; RE-C reads none today and tolerates its absence — once
> written, the Correspondence's answered slip may print it after the echo, one line, inside the budget); **the
> `remember` board line** on the next occurrence of the same template, read from the previous occurrence's row (RE-3
> authored the copy; confirm it renders on the second letter of each template and on the Haiti letter's second form);
> **the noise census** as a pin (≤ 1 line per surface per letter, ≤ 3 per letter, one COURTS line, measured on the
> `tools/_affairs_measure.py` arms through the trace — the record tool prints the surfaces per occurrence). Nothing
> here adds a popup, a sound or a rail notice. **Pins:** the SITUATION key on the morning after an answer and never
> twice; the two renderers; the COURTS line once per letter and never for an arrival; the echo on the response; the
> remark in its slot; the remember line on the second letter; the census on the measured arms; the frames of the
> dispatch's SITUATION block with a receipt (both scales). **Then RE-6 the Edicts** (E1–E3 as offers under the one
> register; §6.2's citations owed before arming; RE-6's head re-sizes against S14j's economy), **then RE-5 the close**
> (the Mode C walk on 8007: a sealed letter, the Correspondence read, a squadron sailed and settled; the reach review
> with RE3-6 / RE3-7 and §22.4's pulse-versus-deck reading) — then AU.
>
> **Traps the row has paid for (do not re-discover):** the spec, `SYSTEMS_REFERENCE.md`, `BUG_FIXES.md`,
> `MODDING_FORMAT.md`, `first_open.py`, `iq10_run_captures.py` and CLAUDE.md are CRLF files — edit through Python with
> the file's own endings, never `cat >>`; a write by a RELATIVE path raised `Errno 22` on `moments.py` tonight — write
> by the absolute path; the shell heredoc eats a long block or its backslashes (write scripts with the Write tool and
> run them by path; build strings with `chr(13)` / `chr(10)`); `GET /dispatch` must not mutate
> (`tests/test_ux23b_the_desk_is_quiet.py`) — a builder that reads the Watch passes `record=False`; the OPS table binds
> each apply function at import (seam `naval.detach_squadron`, not `moments._apply_squadron`); a Decline is forbidden
> the `squadron` op; `refresh_letter` re-plans the FROZEN form; the morning's pick is the premise that has stood LONGEST
> (`affairs.pick`); the commanded driver's `diplomacy: accept` makes peace with Britain by T10–T19 (the Haiti latch
> empties) — measure a marching France at war with `--diplomacy decline`; a crafted board built at turn 1 on the ARMED
> boot reads the boot's morning memo — pop `world.__dict__["_affairs_memo"]`; the Haiti letter premises on the boot
> board (blockaded, 45 sail) once the chest passes 1,500 — a pin that wants another letter's morning keeps the fleet
> under 25 sail; a `fit_content` RichTextLabel built in a `.gd` must be added, in the SAME function, to a local
> container that is added to an `@onready` node under the scene's ScrollContainer (`tests/test_uxr2_scroll_where_unbounded.py`
> follows `add_child` chains four hops deep), and setting `fit_content = true` on a label the function did not build
> counts as a toggle; a scene-authored ScrollContainer needs a `custom_minimum_size` (the floorless-scroll ratchet sits
> at 8); sizes only by `theme_type_variation` (`Caption`, `Lead`, `BodyLarge`), never `[font_size]`; every
> `Utils.bb_button_chip(` url expression needs a REVIEWED row in `tests/test_cn4_the_chip_honesty_census.py` keyed by
> (file, expression); `refresh_pinned` / `_on_pinned_dispatch` carry pinned literals (`tests/test_uxr_d4_the_side_desk.py`)
> and `main.gd` may gain no new `top_bar.close_all_screens()` site unclassified in its `CLOSE_SITES`; the IQ10 harness's
> `press` matches a Button's text EXACTLY (a button whose text carries a count is driven with `{"call": method}`); the
> parse harness is run by `Start-Process` from PowerShell (`Godot_v4.4.1-stable_win64.exe --headless --quit --path
> godot-client/project-sovereign --script ../../tools/godot_parse_check.gd`) and its report's 24-hour guard reads the
> scripts' mtimes; the frames: `tools/iq10_capture_payloads.py --out <dir> --only moments`, then
> `tools/iq10_run_captures.py --payload-dir <dir> --only correspondence --date … --out-dir …` at both scales and once
> `--physical --physical-scale auto`, then `tools/uxr0_readability_report.py <physical>/index.json --record
> docs/audits/uxr0/readability_<label>_<date>.json --surfaces a,b,c`; the reply to `/respond_to_objection` carries NO
> `pending_objection` key; the record tool's standing figure reads "Authority N → M"; `--affair lapse` leaves the letter
> IN THE MAILBOX; the sweep tool must NOT be launched with `-X utf8`; the bytecode pins need `PYTHONDONTWRITEBYTECODE`
> unset; the road control is the in-tree seam (`--seam backend.game_logic.affairs:armed=False`); the series rig's
> committed record is the squadron landing's; RAM is the limit at 16 GB; the deck hash reds `test_moments_pacing.py`
> and `test_affairs_reach.py` until the measure is run again (the chain `tools/playtest_runs/reh3_2026_11_01/chain.sh`
> ran in six minutes); `ruff` is not on the Bash PATH (`.venv\Scripts\python.exe -m ruff check backend/`); the hook
> runs the full suite in parallel (~10 min) — commit from Bash in the background with
> `env -u PYTHONDONTWRITEBYTECODE git commit -F <file>` and edit no tracked file while it runs; STATUS keeps at most
> seven session entries (archive the oldest to `docs/archive/STATUS_2026_Q4.md`, newest first); CLAUDE.md sits at its
> byte cap (every added line is paid for by a trim; `tr -d '\r' < CLAUDE.md | wc -c` against 62,000).
>
> **Open with the user, unchanged:** RE3-6, RE3-7, RE3-9 (above); the certificate (`INK_IRON_SIGNTOOL_ARGS`); S14d's A1
> as applied; AO's three questions (`REFORMS_SPEC.md` §5a); SF-NAV-1-D1.
