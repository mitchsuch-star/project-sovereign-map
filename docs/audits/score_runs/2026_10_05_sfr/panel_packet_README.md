# THE PANEL PACKET — read only what is in this folder

You are one of three blind scorers (SCORE_FINISH_SPEC.md §4.5). You have NOT
seen any previous score, and you must not look for one: do not open STATUS.md,
CLAUDE.md, SCORE_MANDATE_PLAN.md, the audit memos, prior runs or the git log.

In this folder:
- checklist.json — every item, its kind, whether it was measured, its mark and its evidence line;
- scores.json — the anchor score per pillar from the frozen rule (§4.4), and the directional;
- census_by_pillar.json — the open defect rows per pillar, with the P1s;
- findings_rate.json — rows filed per 10 turns played, beside the score (never subtracted);
- digests/ — the arms' digest.md files (one block per turn: the orders, the replies, the battles, the popups, the ledger, the dispatch);
- frames/ — the client frames and their index, when the client arm ran.

Your job, per pillar:
1. Mark each EYES item you can judge from the digests (pass / fail / cannot judge), citing a digest line.
2. Take the anchor score as given. Adjust it by −0.25, 0 or +0.25 for FEEL only, citing ONE digest line or frame.
3. Return JSON: {"pillar_key": {"anchor": x, "adjust": -0.25|0|0.25, "eyes": {"C2": {"pass": true, "cite": "..."}}, "cite": "one line", "flag": "optional: something a human should check"}}.
A flag never moves a score. The median and the spread of the three panels are what gets published.
