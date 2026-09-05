# Slice 11 review round — R1 — attack the fix

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

I read the complete 2291-line diff, then probed the shipped tree at 63924903 rather than reasoning from the comments. Most of the slice holds up under attack: both garrison-event producers stamp `region`, so the FA-23 carve-out is live; `_build_forces` has no strength filter and the `prisoners` payload keys (`name`/`captor`/`captured_turn`) match both new client readers exactly, so FA-32 is live; the bombardment event carries every key the widened `own_mauled` arm reads and `pre` is derived from live marshal strength, so FA-25 works; `coalition_member_rows` is a snapshot taken after every row is fully built, has no cycle and no nesting, adds ~9KB to a 13.6KB payload, and I measured coordination=3 pairs / weak_link=Austria on the 1805 boot where both were previously empty; the FA-N14 home-soil gate is genuinely boot-dormant (France's 28 controlled provinces are exactly her 28 starting ones); and the FA-2 war exit briefs end to end through a real `advance_turn` — headline, rail line and campaign-log row all correct. But FA-N33's CLIENT half is production-dead: the new `move` arm reads `captured_from`/`capture_choice` off the top-level action dict while the backend stamps them on `events[0]`, and the pin meant to prove it is a source-text grep for the wrong expression. Two smaller defects follow: the new campaign-log fog arm is narrower than its three siblings, and the armistice exit's new `continue` drops four tail effects, not the two its comment names.

## Findings whose refuters DIED (3) — unjudged, not killed

The workflow labels these "killed". They were not: both refuters
errored on the usage limit, so `survives` computed False over an
empty verdict list. Each was verified by hand instead; see the
landing record for the disposition.

### [P2] FA-N33's client arm reads `captured_from` off the action dict; the backend only ever stamps it on `events[0]`, so the fix ships production-dead

Refuter output: (none — both agents errored)

### [P3] The new `vassal_broke_free` fog arm reads only the vassal's visibility, so a rebellion against a fully visible foreign lord is hidden while the same court being bribed away is shown

Refuter output: (none — both agents errored)

### [P3] The armistice exit's new `continue` skips four tail effects, not the two its comment names — the freed nation's assimilated corps stay under the lord's flag forever

Refuter output: (none — both agents errored)
