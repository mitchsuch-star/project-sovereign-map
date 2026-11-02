# NEXT SESSION PROMPT — Row RE "Affairs of State": RE-R LANDED (the user's review first), then RE-6 the Edicts; row AU queued after RE

> Overwritten each time a session hands off. Current hand-over: **November 2, 2026 — RE-R the reactions LANDED** (rules
> `SYSTEMS_REFERENCE.md` §166; the record `RECURRING_EVENTS_SPEC.md` §24; one commit through the hook), after RE-C the
> Correspondence (`009eae6e`, §23 / §165) and RE-H the Haiti letter in three commits (`247e4e27`, `2b47a93a`, `98bb5910`;
> §22 / §164); the row before S15 by the user's ruling of October 31 (§0c). **Three tiers of §16b are closed:** the letter
> (four recurring letters in the dress), the home (the Correspondence page of the Dispatch) and the reactions — an answer's
> voice and its wake: the minister's echo or the marshal's remark as the response's second green line, the morning's plain
> SITUATION receipt in both views, the Moniteur's one COURTS line (the arrival never; a lost squadron the paper's lie), the
> `remember` line last on the next letter's board, and the seal pressing in the live client at last (RER-1: its key never
> left the backend). The budget held: two lines beyond the answer's own, no popup, no rail card, no sound.
>
> **FIRST — the user's review, before any code:** RE-H's readings (§22.1, §22.2, §22.4), RE-C's twelve (§23.2) and
> RE-R's eight (§24.2: the echo as the response's second line; the remark's speaker and fallbacks; the receipt plain and
> prefix-less, none for a lapse; THE COURTS' predicate; the remember line's same-subject rule; the forwarded key; the
> census as a pin), and the rulings on RE3-6, RE3-7, RE3-9. Build nothing on those three rows. **Row AU — authority as a
> currency, the push and the pull — stays queued AFTER RE and before S15** (`docs/AUTHORITY_CURRENCY_SPEC.md`; the gate
> first, in its own session, after RE-5).
>
> **THEN — RE-6 the Edicts (§6.2 E1–E3 the offers; §16b 1.75 sessions; §0b Q2 ruled them in, in principle), its own
> commit; records §25 / `SYSTEMS_REFERENCE.md` §167 / finds `BUG_FIXES.md` §RE6.** The Edicts are the player's OWN
> offers under the one register — decrees he takes rather than bills he answers, each an effect for a term: **E1 the
> Magazines** (supply capacity ×1.25 for 8 turns — 2,500 gold, 1 admin; when a war-intent against the lord is foregrounded
> or at war with a corps drawing campaign pay), **E2 the Remounts** (cavalry recruit price ×0.8 for 8 turns — 1,500 gold,
> 1 admin; the cavalry pool under 60 % of its cap), **E3 the Camps of Instruction** (drill morale +5 for 8 turns — 2,000
> gold, 1 admin; at peace with every great power six turns and the Charges at the golden peace, rate ≤ 60 — the golden
> peace's recurring purchase, the one thing in the deck that touches a rich peace). **Open before arming, by the spec's own
> word:** (a) **RE-6's head re-sizes the Edicts against S14j's economy** (France levels 18–32k at T40, the courts 146–193k —
> `SYSTEMS_REFERENCE.md` §159) and measures that rung's spend of the courts' war chests per seed (the EAD-6 reopening Q2
> named) BEFORE E1–E3 are armed; a shape change re-escalates through §0b's table; (b) **the citations owed** (§6.2's
> "citation owed before arming" on each: the campaign magazines, the remount purchases after the winter campaigns, the
> camps of Boulogne 1803–05) — write the `source` rows as §6.1 / §6.5 did; (c) **an effect that expires is a second
> lifecycle** (REFORMS §4) — the one engine question: a timed modifier on supply / recruit price / drill morale that ends
> on its own, written on the world where the laws' upkeep lives, serialized (`SAVE_FORMAT_REFERENCE.md`), surfaced on the
> LAWS book or the Correspondence's answered slip ("Decreed until {date}"), and never a `WorldState` field without its
> `to_dict` / `from_dict` and the enforcement pin; (d) the register (P12): a writer's line (Daru for the Magazines and the
> Camps? the Grand Écuyer / Caulaincourt for the Remounts — the Voice Bible first), a counsel line, the echo, the SITUATION
> and COURTS lines and the Correspondence row for each; (e) the pulse: the Edicts are offers, not bills — the pacing of §7
> (first / gap / cap_act) and the brakes of §14 apply as to any template; measure on the same arms (`tools/_affairs_measure.py
> run/record`, the sweep, the roads armed and control, the probe, the series rig) and report the reach per arm and the
> gold converted (§14's economy gate: converting, not draining). **Pins:** each offer's premise clause by clause on crafted
> boards; the effect applied for exactly its term and gone after; shown = applied; the alarm untouched; the lockstep; the
> validator's refusals; the frames in the dress at both scales; `BASELINE_SERIES` re-pinned with its attribution if it
> moves. Then **RE-5 the close** (the Mode C walk on 8007: a sealed letter, the Correspondence read, a squadron sailed and
> settled; the reach review with RE3-6 / RE3-7, §22.4's pulse-versus-deck reading and P13's earlier close) — then AU.
>
> **Traps the row has paid for (do not re-discover):** the spec, `SYSTEMS_REFERENCE.md`, `BUG_FIXES.md`,
> `MODDING_FORMAT.md`, `first_open.py`, `gazette.py`, `iq10_run_captures.py` and CLAUDE.md are CRLF files — edit through
> Python with the file's own endings, never `cat >>`; a write by a RELATIVE path raised `Errno 22` once — write by the
> absolute path; the shell heredoc eats a long block AND turns `\\n` into a real newline (it broke the capture tool
> tonight) — write scripts with the Write tool and run them by path, and never put a backslash escape in a heredoc;
> `GET /dispatch` and the morning build must not mutate (`tests/test_ux23b_the_desk_is_quiet.py`) — a builder that reads
> the Watch passes `record=False`; `compose_issue` is a pure read (`test_hc_g_gazette.py`); the OPS table binds each
> apply function at import (seam `naval.detach_squadron`); a Decline is forbidden the `squadron` op; `refresh_letter`
> re-plans the FROZEN form; the morning's pick is the premise that has stood LONGEST (`affairs.pick`); the commanded
> driver's `diplomacy: accept` makes peace with Britain by T10–T19; a crafted board built at turn 1 on the ARMED boot
> reads the boot's morning memo — pop `world.__dict__["_affairs_memo"]`; the Haiti letter premises on the boot board once
> the chest passes 1,500 — a pin that wants another letter's morning keeps the fleet under 25 sail; a pin that wants the
> SECOND letter of a template crafts its row (the engine's own second arrival waits on the pulse behind the Haiti letter);
> `world.marshals` spells "Massena" without the accent; `world.notifications` is a `NotificationCollector` (no `len`);
> the one-liner's `moment` arm is shared with the campaign-log screen — the Gazette maps affairs locally
> (`_affair_courts_line`), never there; `filter_campaign_log` is 499 lines against a cap of 500 — touch it for nothing;
> the client censuses: a code-built `fit_content` RichTextLabel must chain `add_child` to an `@onready` node under the
> scene's ScrollContainer in ONE function; a scene ScrollContainer needs `custom_minimum_size`; sizes by
> `theme_type_variation` only; every `bb_button_chip(` url expression needs a `test_cn4` REVIEWED row; the two-view pin
> idiom is `test_rf4b_the_laws_everywhere.py`'s (`_func` body indexes); the IQ10 `press` verb matches a Button's text
> EXACTLY (`{"call": method}` when the text carries a count); the parse harness via `Start-Process`; the frames:
> `tools/iq10_capture_payloads.py --out <dir> --only moments`, then `tools/iq10_run_captures.py --payload-dir <dir>
> --only <id> --date … --out-dir …` at both scales and once `--physical --physical-scale auto`, then
> `tools/uxr0_readability_report.py <physical>/index.json --record docs/audits/uxr0/readability_<label>_<date>.json
> --surfaces a,b`; the reply to `/respond_to_objection` carries NO `pending_objection` key; the record tool's standing
> figure reads "Authority N → M"; `--affair lapse` leaves the letter IN THE MAILBOX; the sweep tool must NOT be launched
> with `-X utf8`; the bytecode pins need `PYTHONDONTWRITEBYTECODE` unset; the road control is the in-tree seam
> (`--seam backend.game_logic.affairs:armed=False`); the series rig's committed record is the squadron landing's; RAM is
> the limit at 16 GB; the deck hash reds `test_moments_pacing.py` and `test_affairs_reach.py` until the measure is run
> again (the chain `tools/playtest_runs/reh3_2026_11_01/chain.sh` ran in six minutes — RE-6 arms new templates, so the
> hash WILL move and the whole chain must run); `ruff` is not on the Bash PATH (`.venv\Scripts\python.exe -m ruff check
> backend/`); the hook runs the full suite in parallel (~11 min) — commit from Bash in the background with
> `env -u PYTHONDONTWRITEBYTECODE git commit -F <file>` and edit no tracked file while it runs; STATUS keeps at most seven
> session entries (archive the oldest to `docs/archive/STATUS_2026_Q4.md`, newest first — done tonight for RE-1's); CLAUDE.md
> sits at its byte cap (`tr -d '\r' < CLAUDE.md | wc -c` against 62,000 — every added line is paid for by a trim).
>
> **Open with the user, unchanged:** RE3-6, RE3-7, RE3-9 (above); the certificate (`INK_IRON_SIGNTOOL_ARGS`); S14d's A1
> as applied; AO's three questions (`REFORMS_SPEC.md` §5a); SF-NAV-1-D1.
