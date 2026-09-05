# Slice 11 review round — R2 — GR5, fog, the enemy AI, serialization

Read-only adversarial review of master `63924903` (FA slice 11, "The
Briefing Tells the Truth"), September 5, 2026.

> **⚠ READ THIS FIRST.** Seventeen of this round's twenty-three agents died
> on a session usage limit mid-run — every refuter for R1 and R2, and two of
> R3's four. The workflow's `survives: false` and its "Findings both refuters
> killed" heading are therefore ARTEFACTS of that failure, **not verdicts**:
> those rows were never judged at all. Every finding below was subsequently
> verified BY HAND against the shipped board, and the dispositions are in the
> boxed SLICE 11 REVIEW ROUND block in `BUG_FIXES.md`. Six of the ten were
> real; two were record errors; the P2 that two lenses found independently
> would have been buried if the empty `killed` list had been read as a
> judgement.


Transcribed verbatim from the agent's structured return value.

## The lens's own summary

I walked every new seam as an AI-lorded satellite and as a fogged observer, and round-tripped the new state. Most of the lens is clean: `record_vassal_break` is genuinely lord-aware (measured `always` for a France-lorded break, `partial_on_nation` for an Austria-lorded one, and the Austria line correctly goes invisible when I blind France to Bavaria); the `vassal_lost` headline refuses to fire for a foreign lord; the campaign-log fog arm gates on the vassal's own visibility; the folded `coalition_member_rows` keep each member's OWN fogging (measured on the 1805 boot: Britain and Russia come back `war_exhaustion: None` / `army_strength: 'Unknown'` while Austria at PARTIAL gets `0` / `~125,000 men`), and the restored `weak_link`/`Court X` counsel only ever nominates a court whose WE is already disclosed. Serialization is sound — `vassal_broke_free` with its `lord`/`exit` survives to_dict/from_dict and still leads the briefing after a load; a PRE-slice `nation_eliminated` row with no `lord` key does not crash the new arm; `captured_by`/`captured_turn` are both serialized and the ledger + prisoners surfaces read right after a round-trip; the retired `diplomatic_vassal_rebellion` had no `event_log` producer at the parent (verified with `git grep` at 3ee0be90), so no save carries it; `test_serialization_enforcement.py` is 19/19. All numbers the new `.gd` blocks read are `int()` on the backend, `COLOR_ERROR`/`_format_number`/`Utils.display_nation_name`/the `cannon_distant` cue all exist in the right scopes, and every new client read is null-guarded. Four findings survived, one of them a feature that is production-dead.

## Findings whose refuters DIED (4) — unjudged, not killed

The workflow labels these "killed". They were not: both refuters
errored on the usage limit, so `survives` computed False over an
empty verdict list. Each was verified by hand instead; see the
landing record for the disposition.

### [P2] FA-N33's client half is production-dead: it reads `captured_from`/`capture_choice` off the action, but the backend stamps them on the event

Refuter output: (none — both agents errored)

### [P3] The CRITICAL rebellion notification is the one surface in the break family left lord-blind, and now contradicts the dispatch line queued beside it

Refuter output: (none — both agents errored)

### [P3] The armistice exit's new `continue` dropped four mechanical tail effects, not the two briefing lines its comment names — the satellite's marshals are stranded under its ex-lord's flag forever

Refuter output: (none — both agents errored)

### [P4] `coalition_member_rows` copies whole war rows where the card reads six keys, nearly quadrupling `active_wars` on every HTTP response

Refuter output: (none — both agents errored)
