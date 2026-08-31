# Row REV — the open follow-ups

> Everything the August 30, 2026 whole-systems review **left open**, with the
> reason it was left. Landing records for what was FIXED are
> `docs/BUG_FIXES.md` §Whole-Systems Review (REV) and §THE VISUAL PASS —
> those are authoritative and this file does not repeat them.
>
> Four items. None is blocked on a gate; two are content decisions, one is a
> staging problem, one needs a human ear.

---

## REV-V3 — the rail's unmapped tail (the big one)

**33 of the backend's 57 notification types have no renderer join**, so they
arrive on the notice rail as the anonymous priority pill — "INF", "NEW" or
"ALT" — naming neither the subject nor the matter. The player scans that rail
by icon.

Measured Aug 30, 2026 (re-measure before starting; the census is a one-liner —
see `TestTheRailNamesEveryRowItShows` in `tests/test_review_2026_08_30.py`):

```
alliance_cascade_war, ally_settlement_petition, bankruptcy_escalation,
coalition_brewing, coalition_cooldown_ended, coalition_dissolved,
coalition_member_peaced, coalition_murmurs, coalition_threat_tension,
counter_punch_earned, defection_cascade, diplo_auto_downgrade,
drill_cancelled, estate_confiscated, estate_lost, forced_retreat_order_voided,
friendly_fire_trust, incoming_settlement_offer, jealousy_confrontation,
manpower_depleted, manpower_replenished, marshal_commissioned,
marshal_defied_order, nation_eliminated, nation_formed,
reckless_cavalry_action, rente_defaulted, rivalry_confrontation,
sabotage_discovered, settlement_terms_request_result, strategic_order_complete,
vassal_courting_detected, vassal_loyalty_critical
```

**Why it was filed rather than fixed:** choosing 33 glyphs and 33 three-letter
codes is a content decision about what each row should look like, not a bug
fix, and inventing them mid-review would have been 33 unreviewed judgements
smuggled into a correctness pass.

**Where the work goes.** Two maps in
`godot-client/project-sovereign/scripts/notification_bar.gd`:
`TYPE_ICONS` (the three-letter label) and `TYPE_ICON_SVGS` (the Phosphor
glyph). Both keyed on the backend's type string.

Constraints that already have pins — read them before editing:

* Every glyph named must EXIST at
  `godot-client/project-sovereign/assets/ui/icons/phosphor/<name>.svg`. A name
  with no SVG renders nothing, which is worse than the pill it replaced. The
  available set is small (~50); list it before choosing.
* A row needs BOTH a label and a glyph. A label-only join is a half-join —
  that mistake was made and caught by the floor pin during the review.
* Assert against the backend's own CONSTANTS (`from backend.notifications
  import ...`), never against strings typed into the test, so a rename on the
  producer side breaks the test instead of silently un-joining the rail.
* Some rows may be legitimately rail-exempt. If so, say which and why in an
  explicit exempt set — do not leave them unmapped and undocumented, because
  the next census cannot tell "exempt" from "forgotten".

**Completion definition:** every notification type a player can receive
carries a label and a glyph, or appears in a documented rail-exempt set with
its reason; the floor pin becomes a full census pin (unmapped set == exempt
set); the glyph-exists pin still passes.

---

## REV-F1 — `battles_this_turn` is wiped on load (plausible only)

`world.battles_this_turn` is serialized for mid-turn saves
(`world_state.py`, `to_dict`) and then force-cleared by
`save_manager.load_game` (`world.battles_this_turn = []`, ~line 188). The V2-2
once-per-pair engagement check on the glorious charge reads exactly that list,
so a mid-turn save/load would let a marshal charge a pair he had already
engaged this turn.

**Why it is not fixed:** of the two adversarial refuters, one CONFIRMED the
mechanism and the other REFUTED the consequence as masked by another guard —
so it never reached the confirmed set. That disagreement is the work: settle
it by experiment, not by reading. Save mid-turn after a charge, reload, and
try the same charge again.

If it is real, the fix is almost certainly the one three of its neighbours
already carry: make it a documented NON-clear in `load_game` (the file has a
list of them with reasons — `diplomatic_trust_applied`, `attacks_this_turn`,
`objection_popups_this_turn`, and `in_combat_this_turn` as of this review),
since the field is serialized and cleared at the real turn boundary anyway.
If it is masked, say where by, and delete the row.

---

## REV-V4 — two flow fixes never staged on screen

Both are ORDERING fixes, not renders, and both are pinned by tests
(`tests/test_review_2026_08_30.py`). Neither has been seen by a human.

1. **A fresh capture question no longer swallows the end-turn report.** When a
   capture is mounted DURING end-turn processing, the response carries the
   question alongside `enemy_phase`, the strategic reports and the Morning
   Dispatch. It is now stashed and raised when control returns
   (`pending_capture_response` + `_show_pending_capture_choice`, the NA-6b
   idiom).
2. **The Morning Dispatch shows on the interrupt tail.** The end-turn route
   that passes through an input-requiring interrupt early-returns out of both
   dismissal handlers ahead of their own `_show_pending_dispatch()` calls, so
   the briefing was stashed and never shown.

**Why they were not staged:** (1) needs a capture that lands inside end-turn
processing. The attempt made during the review — Ney at Milan under a standing
march into undefended Austrian Tyrol — was pre-empted when Archduke Charles
attacked Ney first and took Milan. Staging is the whole difficulty; the fixes
themselves are small.

**How to stage it** (sandboxed pair, `SOVEREIGN_PORT=8007` +
`INK_IRON_SAVE_DIR` in a temp dir — NEVER the player's 8005; `DEBUG_MODE=true`
for the debug verbs):

* `debug set_location <marshal> <region>` teleports; `debug set_controller`
  and `debug freeze_enemies` are the two that make this reliable — freeze the
  enemies so nobody pre-empts the march, then give the marshal a standing
  `march to <undefended enemy province>` and end the turn.
* For (2), any end turn that produces a strategic interrupt will do; the
  question is only whether the dispatch appears after it.

**Completion definition:** a screenshot of each, in `docs/audits/`, showing
the end-turn report intact with the capture question after it, and the
dispatch on an interrupt turn.

---

## UX23-R9 — three bugle cues owe a human ear

Carried over from the Aug 23 row (`docs/BUG_FIXES.md` §UX23-B). The capped
audio cues were verified by an envelope probe
(`tools/audio_envelope_probe.gd`) — durations and onsets are measured — but
whether a capped bugle still sounds like a finished phrase is the one thing
the probe cannot answer. Needs a person to listen to three cues and say yes or
no.
