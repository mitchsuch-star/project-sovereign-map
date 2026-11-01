# NEXT SESSION PROMPT — Row RE "Affairs of State": RE-H LANDED in full (the user's review first), then RE-C the Correspondence

> Overwritten each time a session hands off. Current hand-over: **November 1, 2026 — RE-H the Haiti letter LANDED in two
> commits: H0 the bill alone (`247e4e27`), then the squadron** (rules `SYSTEMS_REFERENCE.md` §164.1 / §164.2; the records
> `RECURRING_EVENTS_SPEC.md` §22.1 / §22.2; each its own commit through the hook; the row before S15 by the user's ruling
> of October 31 — §0c). **The deck carries four letters:** the Arch-Chancellor's Letters, the Host's Claims, Berthier's
> Memorial and the Haiti letter — Decrès writing when Britain has had France blockaded four of the last twelve mornings,
> the Emperor holds court at home, 25 sail lie in port and the chest holds 1,500. **The Haiti letter wears two forms, frozen
> at delivery:** the bill (600 gold and the day's action: flour and muskets by two frigates) when no British hunter is at
> sea, the squadron under the blockade (500 gold, the action and five of the line at the odds printed on the button — 36 in
> 100 at war against Britain's 100 sail, 62 with a Grand Diversion's window); against either, "Ferrand must hold alone" at
> standing 100 → 97. Accepted, five sail leave port (the Admiralty names them at sea), drill at sea while the home fleet
> rots, and four turns later ONE amber line lands on the morning's dispatch in both views — home whole with the men, or five
> of the line lost; the next letter remembers which. **The user's word at the plan's review** ("we want to make sure these
> events are good, have conditions that make them appear and don't make the game repetitive … fun factor high") amended P16
> for this letter: `bites: "floor"` — the letter arrives at full standing. **Measured:** on 52 runs it arrives on 16 (15 of
> the 21 passive runs — the campaign's FIRST affair at T6–T9 — and the treaty road twice), never while the Emperor marches,
> never at peace with Britain; the squadron tree reproduces that reach byte for byte, and the squadron sails on the `haiti`
> family alone (historical: letter T7, HOME T11 at 36 in 100, drew 18; austerlitz: letter T14, CAUGHT T18, drew 93;
> marengo: never due). The brakes against repetition are authored: cap 2 an act, cooldown 12, the pulse's gap of five
> mornings from any letter of state, four chapters that never repeat in a row, two exhibits alternating, the two forms by
> the sea's state, the file closing at Ferrand's death (T76).
>
> **FIRST — the user's review of RE-H, before any code:** the readings of §22.1 (ten) and §22.2 (eight), each a line to
> reverse — P16 amended for this letter alone; the squadron drills at sea; the fate's morning line pulled forward from RE-R;
> "no hunter at sea" REFUSES the squadron's quote (a squadron at 100 is a sale; the bill is that road); the fallback form
> `{}`; the `haiti` measure family — and the rulings on RE3-6 (the Crown fires nowhere since S14k), RE3-7 (the roads since
> S14j / S14k), RE3-9 (190 untracked `.import` files). Build nothing on those three rows.
>
> **THEN — RE-C the Correspondence (§12b.1 the contract; §16b 1.25 sessions; §22.3 what it inherits), the home of the
> letters, on today's unsplit `dispatch_view.gd` (§0c); its own commit, records §23 / `SYSTEMS_REFERENCE.md` §165 / finds
> `BUG_FIXES.md` §REC with the census's pillars.** The goal line: a page the player WANTS to re-read, not a loop — every
> letter of state laid before him, the answer he gave, what it did and what came of it; read-only but for "Read the
> letter ▸". The list, from §12b.1: the builder `moments.correspondence(world)` — a fresh dict read from
> `world.moments["state"]` plus the deck and the fleet record, NEVER the event log (it rolls at 500 rows and is full by
> T21 on three saves); `GET /dispatch` gains `payload["correspondence"]` with `first_open.attach` (a GET — the POST rule
> does not apply); the page as a new node subtree with its own page state in `dispatch_view.gd` (`_on_dispatch_received`
> and `refresh_pinned` rewrite `content_label` from every GET and must respect the open page; `clamp_ceiling_override`
> raises the 700 × 500 ceiling as `_raise_letter_ceiling` does; at 2.0 the clamp gives the page 394 px — the buttons stand
> outside the scroll); the Button in the Dispatch's action row — "The Correspondence (1 standing)" / "(a squadron at sea)"
> in amber when it has news, like the Envoys badge — and "◂ The Dispatch" to close; the sections, one column, each entry a
> plain slip in ink (the inner field of `old-parchment_alpha.png` as a `region_rect`): **ON THE DESK (n)** — "SEALED ·
> answer by {date}" with the arms or the monogram, the title and the writer, the two `button_line`s, "Read the letter ▸"
> (`POST /mailbox/activate` after `close_view()`, as Open Envoys does); **ANSWERED** (newest first) — "{DATELINE} ·
> {TITLE}" with the device right-aligned, the apostille in IM Fell italic with the seal glyph at 18 px "{caption}. — N."
> (lapsed: "Filed unanswered — {caption}", sepia, no seal; withdrawn: "Set aside for {moment} — nothing was spent"), then
> the `receipt`, then the `echo` dated the answered turn + 1 or "At sea — five of the line; word expected about {date}"
> (from the row's `home_by`; no hourglass glyph) and then the fate from `outcome_line` in rubric, the chips as `[url]`
> links (the court's Cabinet page by a new signal into the wizard's `open_for_nation`, ADMIRALTY ▸ / LAWS ▸ on the
> existing `ledger:6` / `ledger:7` doors, Read the letter ▸; repeated chips told apart by `click#N` for the DD-B
> instrument); **IN THE OFFING** — the Watch's at most two "may" lines (`affairs.watch`), text only, no pips; **LEFT
> UNANSWERED / SET ASIDE** — one dim line each (rows passed for premise, forsworn, verdict or before_save never show);
> **the closing record and the 1825 line** from the Haiti template's `closing` when the file closes (§6.5); the empty
> states ("No letter of state lies on the desk, Sire." / "Nothing has yet been answered." / "Nothing is gathering,
> Sire."); the two pointers in ("No pending envoys at this time." gains ", and the Correspondence (the Dispatch) keeps
> every letter answered."; the mailbox panel's footer button); `first_open.SCREENS` gains `correspondence` with the line
> §12b.1 authors (≤ 220); every row named by `moments.letter_title` / `affairs.title_of(e, row)` — the frozen FORM's title
> (REH-2's sibling, noted in §22.2's sweep); a pre-RE save shows its captions only; on an unarmed world the button is
> hidden; no badge beyond the button's count, no sound, no hotkey, no new endpoint. **DD-B:** `click Dispatch` (or `key
> Alt+R` — a bare `key R` types into a caret-holding line), then `click Correspondence`. **Pins:** the builder on crafted
> rows (standing, Not Now, answered, lapsed, withdrawn, a squadron at sea and then its fate, the closing record on a closed
> file), the pre-RE save, the unarmed world, the page state surviving a GET and a `refresh_pinned`, the ceiling, the
> first-open line, the pointers; **the frames** at both scales through the IQ10 pipeline and the readability record. Then
> RE-R the reactions (its SITUATION renderers in today's scripts; the fate line already landed — §16b's RE-R row).
>
> **Traps the row has paid for (do not re-discover):** the spec and `SYSTEMS_REFERENCE.md` are CRLF files — append
> through Python in the file's own endings, never `cat >>`; the shell heredoc eats a long block or its backslashes (write
> it with the Write tool, or build strings with `chr(13)` / `chr(10)`); the OPS table binds each apply function at import,
> so a seam on `moments._apply_squadron` does not bite — seam `naval.detach_squadron` (AFS); a Decline is forbidden the
> `squadron` op; `refresh_letter` re-plans the FROZEN form (a hunter gone closes the Accept with the refusal, never a
> silent re-plan); a crafted board built at turn 1 on the ARMED boot reads the boot's morning memo — pop
> `world.__dict__["_affairs_memo"]`; the Haiti letter premises on the boot board (the Emperor home, blockaded, 45 sail)
> once the chest passes 1,500 — a pin that wants another letter's morning keeps the fleet under 25 sail or the Emperor
> afield; the reply to `/respond_to_objection` carries NO `pending_objection` key (the driver reads `objection_kept` +
> `choices`); the record tool's standing figure reads "Authority N → M" (REH-1); `--affair lapse` leaves the letter IN
> THE MAILBOX; the judge files a purse named in passing as `context_drift`; the sweep tool must NOT be launched with
> `-X utf8`; the bytecode pins need `PYTHONDONTWRITEBYTECODE` unset; the road control is the in-tree seam
> (`--seam backend.game_logic.affairs:armed=False`), no clone; the series rig's committed record is the squadron
> landing's — its `prior` is H0's standing series and its arms 0 / AF0 reproduce RE-3's (the chain pin in
> `tests/test_ai_drill_fix_2026_09_27.py` reads it that way; re-running the rig overwrites the record — re-read the pin
> before you do); RAM is the limit at 16 GB (the suite's eight workers beside no driver); the deck hash reds
> `test_moments_pacing.py` AND `test_affairs_reach.py` until the measure is run again (`tools/_affairs_measure.py run` +
> `record` — the `haiti` family rides both, `tools/ai_v_sweep.py --all`, `tools/_vp1_road_arms.py` armed and control,
> Road I answered, `tools/_affairs_first_arrival_probe.py`, `tools/_affairs_series_arms.py`); the frames:
> `tools/iq10_capture_payloads.py --only moments`, then `tools/iq10_run_captures.py --only affair_letter_santo_domingo
> --date …` at both scales and once `--physical --physical-scale auto`, then `tools/uxr0_readability_report.py
> <index> --record docs/audits/uxr0/readability_affairs_<date>.json`; `build_letter` / `refresh_letter` pass a STATUS
> ROW as `occ` (RE2-1); the Decree is priced in AUTHORITY; HC-0 (no calendar read in mechanics — `calendar_label` is
> display only); no seed read in `moments.py`; every number to Godot an `int`; every answer a button; the hook runs the
> full suite in parallel (~10 min) — commit from Bash in the background with `env -u PYTHONDONTWRITEBYTECODE git commit
> -F <file>` and edit no tracked file while it runs; CLAUDE.md sits at its byte cap (every added line is paid for by a
> trim; measure with `tr -d '\r' < CLAUDE.md | wc -c` against 62,000).
>
> **Open with the user, unchanged:** RE3-6, RE3-7, RE3-9 (above); the certificate (`INK_IRON_SIGNTOOL_ARGS`); S14d's A1
> as applied; AO's three questions (`REFORMS_SPEC.md` §5a); SF-NAV-1-D1.
