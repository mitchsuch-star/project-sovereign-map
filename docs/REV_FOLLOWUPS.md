# Row REV — the open follow-ups

> Everything the August 30, 2026 whole-systems review **left open**, with the
> reason it was left. Landing records for what was FIXED are
> `docs/BUG_FIXES.md` §Whole-Systems Review (REV) and §THE VISUAL PASS —
> those are authoritative and this file does not repeat them.
>
> **Worked August 31, 2026 — three of the four are CLOSED.** Landing record =
> `docs/BUG_FIXES.md` §THE FOLLOW-UPS (August 31, 2026), authoritative;
> pins `tests/test_rev_followups_2026_08_31.py` (22); sweep
> `tools/_sweep_rev_followups.json`, 20 mutations, 20 killed, 0 inert.
> The struck rows below are kept for their reasoning, not as work.

---

## ~~REV-V3 — the rail's unmapped tail~~ ✅ CLOSED August 31, 2026

**33 of the backend's 57 notification types have no renderer join**, so they
arrive on the notice rail as the anonymous priority pill — "INF", "NEW" or
"ALT" — naming neither the subject nor the matter. The player scans that rail
by icon.

**Why it was filed rather than fixed:** choosing 33 glyphs and 33 three-letter
codes is a content decision about what each row should look like, not a bug
fix, and inventing them mid-review would have been 33 unreviewed judgements
smuggled into a correctness pass.

**What the re-measure found, and why the number moved.** The review's census
diffed the two maps against `backend/notifications.py`'s constants. An AST
census over every `create_notification` producer says the live figure is
**34**, and the two sets differ by seven rows in both directions: four live
types the constant list could not see (`armistice_expired`,
`marshal_last_stand`, `vindication_expired` — bare string literals at the
producer — and `settlement_summary`, derived from `SETTLEMENT_ROUTES`), and
three of the filed 33 that no producer has ever emitted
(`jealousy_confrontation` and `rivalry_confrontation` are marshal-petition
dialogue kinds; `vassal_loyalty_critical` was superseded before it shipped).

**Landed:** the three literals promoted to constants (values unchanged); the
three dead ones documented in a new `notifications.RAIL_EXEMPT_TYPES` with
their reason; 34 rows joined in both maps, 66 keys each, identical sets; the
floor pin replaced by a full two-directional census, plus pins against a
fourth dynamic producer, a typo'd map key, and a join that spells the
priority default it replaces.

---

## ~~REV-F1 — `battles_this_turn` is wiped on load~~ ✅ REAL, NOT MASKED · FIXED August 31, 2026

`world.battles_this_turn` is serialized for mid-turn saves
(`world_state.py`, `to_dict`) and then force-cleared by
`save_manager.load_game`. The V2-2 once-per-pair engagement check on the
glorious charge reads exactly that list, so a mid-turn save/load would let a
marshal charge a pair he had already engaged this turn.

**Why it was not fixed:** of the two adversarial refuters, one CONFIRMED the
mechanism and the other REFUTED the consequence as masked by another guard —
so it never reached the confirmed set. That disagreement is the work: settle
it by experiment, not by reading.

**The experiment settled it.** Through the typed command path, five seeds,
byte-identical per seed: Ney (recklessness carried from an earlier turn)
attacks Wellington to a stalemate, then charges — refused, "has already
engaged". Save, reload, charge — the full 2× GLORIOUS CHARGE lands. Every
other gate on that path survives the round trip. The refuter's likely error:
charge→save→load→charge IS masked (a charge zeroes serialized recklessness);
attack→save→load→charge is not. Fixed as a documented NON-clear, the fifth in
`load_game`'s list; two pins asserting the clear were flipped consciously.

---

## ~~REV-V4 — two flow fixes never staged on screen~~ ✅ STAGED AND SEEN August 31, 2026

Both are ORDERING fixes, not renders, and both were pinned only by source
greps. Evidence now: `docs/audits/REV_V4_*_2026_08_31.png` plus the terminal
transcripts, produced by `tools/rev_v4_signoff_screenshot.gd` driving the
real `main.tscn` against a sandboxed backend.

**⚠ This row's own staging recipe was WRONG, and that is why the review's
attempt failed.** A standing march cannot produce the capture question: an
automated hop passes `auto_secure=True` (IGR-X5) and takes the province in
silence. The review misattributed the failure to Archduke Charles attacking Ney first. The
one route that mounts a question inside `advance_turn` is an **occupation
completing** — attack a FORTIFIED province, which is occupied rather than
captured, and `_process_tactical_states` finishes it inside the turn advance.
For flow (2), the order must be issued from TWO hops out or it resolves on
the spot and produces no end-turn report at all. Both traps are now
reachability pins, since nothing had pinned that these shapes exist.

---

## UX23-R9 — three bugle cues owe a human ear · **OPEN**

Carried over from the Aug 23 row (`docs/BUG_FIXES.md` §UX23-B). The capped
audio cues were verified by an envelope probe
(`tools/audio_envelope_probe.gd`) — durations and onsets are measured — but
whether a capped bugle still sounds like a finished phrase is the one thing
the probe cannot answer. Needs a person to listen to three cues and say yes or
no.

**Prepared August 31, 2026.** `tools/ux23_r9_audition_render.gd` renders the
three cues exactly as the game plays them — the registry's `db` trim, its
`max_s` cap and the 0.8 s fade `_fade_stop` applies at the cap — into
`audition/ux23_r9/` (gitignored; regenerate rather than commit):

```
audition/ux23_r9/reveille_capped_4.2s.wav
audition/ux23_r9/to_the_color_capped_5.2s.wav
audition/ux23_r9/fanfare_capped_5.2s.wav
audition/ux23_r9/ux23_r9_all_three.wav      <- one file, ~20s, all three
```

Regenerate with:

```bash
"C:/Users/User/Downloads/Godot_v4.4.1-stable_win64.exe/Godot_v4.4.1-stable_win64.exe" --path godot-client/project-sovereign --script ../../tools/ux23_r9_audition_render.gd
```

**Completion definition (unchanged):** a person confirms each ends on a phrase
rather than mid-figure; if one does not, its `max_s` moves to the next phrase
boundary and the measured value is recorded in `MUSIC_SOUND_SPEC.md` §1a.
**Behaviour test: none is possible** — that is the point of the row.
