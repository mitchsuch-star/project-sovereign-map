# FINAL AUDIT — the session author's hand-verified notes (September 1, 2026)

> **Companion to `FINAL_AUDIT_2026_09_01.md`.** These 37 notes were produced by
> the session author BY HAND, in parallel with the sixteen-lens fleet and
> independently of it — each reproduced by running the game or by opening the
> seam, never delegated. They are the reason 25 memo rows carry the
> AUTHOR-VERIFIED verdict, and several rows the fleet never found (the prisoner
> family HV-1, the letter-book's two-vocabulary cooldown HV-25, the Low
> Countries coastline HV-9) start here.
>
> Kept in full, including the two claims of my own that later measurement
> KILLED (HV-12's "live == mock", corrected in the memo §0.1; HV-10 reclassified
> from a naval defect to a harness blind spot) — a corrected claim is worth more
> on the record than a deleted one.

All reproduced by the session author, not delegated.

## HV-1 The game forgets its own prisoners (P2, defect)
Probe: 1805 world via TestClient with Mack `captured_by="France"`, strength 0, at Paris.
- `Ney, attack Mack` -> success False: "Region 'Mack' not found. Did you mean 'La Mancha'?"
  (a prisoner's name reaches the REGION fuzzy arm and gets a province guess; the WO-13 gate
  covers refused marshal matches but a captured marshal is not in the target roster at all)
- `Ney, pursue Mack` -> success TRUE: "Ney pursues Mack (at unknown). Moves to Swabia." — a
  standing PURSUE after a man in our custody; 2 AP spent; "(at unknown)" copy leak.
- `Davout, march to Mack` -> False: "No intelligence on Mack's position, Sire. Scout for him..."
  (wrong reason: he is our prisoner)
Seam: combat_executor.py:5097 (Unknown target arm) / strategic_executor target resolution;
PC15-4's fallen-name guard covers the PLAYER's own marshals only (executor.py pre-parse guard).
Fix shape: one predicate "named man is a prisoner (captured_by set)" at the target-resolution
seam used by attack/pursue/march, refusing with "X is a prisoner of <captor>" — GR5 both sides.
Test: test that each of the three verbs refuses a captured enemy target by name and spends no AP.

## HV-2 An end-turn-only player starves the popup queue (P2, defect)
Evidence: audit-ambient40 autosave at turn 41: `pending_marshal_petition` = jealousy_confrontation
queued TURN 3, still queued; `incoming_settlement_offer_popup` also queued; digest shows 0
marshal_petition popups in 40 turns. Mechanism: main.py `_apply_command_popup_contract`
(~:1355) — when the /command response carries `enemy_phase`, choice popups are DEFERRED "on
world"; they ride the NEXT /command response without enemy_phase. There is no GET route for
the queue (only /pending_objection, /pending_redemption, /pending_envoy, /mailbox). Client:
`_on_enemy_phase_dismissed` (main.gd:4340) shows dispatch and returns control; it never asks
for deferred popups. The END TURN button sends "end turn" (main.gd:1336). So a player who only
presses END TURN (a siege wait, a recruiting lull) never receives petitions, settlement offers,
coalition popups. On the ambient board it is 38 turns of silence.
Fix shape: on control return after the enemy-phase dialog, the client requests deferred popups
(new GET /pending_popups that pops the highest, or the existing stash-and-raise discipline fed
by a `deferred_popups` key built at the same seam). Test: two consecutive "end turn" commands
with a queued petition -> the petition reaches a response before the third command.
Harness note: the driver's ambient arms send only "end turn" — every ambient digest's
petitions=0 is THIS, not the jealousy system being quiet.

## HV-3 Reward erosion drives trust to 0 with no redemption audience (P2, tie-in defect)
Evidence: audit-ambient40 turn 41: Lannes trust 0, expectation 300 unmet since turn 4
(`expectation_grace_turn` 4, `last_expectation_seen` 300, no estate, no pension, 11 battles
won); `check_redemption_threshold(Lannes)` returns an event when called by hand — nothing ever
called it. Mechanism: world_state.py:6207 `marshal.modify_trust(-points)` (the ES-7 erosion
seam) is not followed by the redemption checker; the checker runs only at objection /
defiance / cavalry-limit / bombardment / strategic seams.
Fix shape: after erosion, `check_redemption_threshold` and append `{"type":"redemption_event",
...}` to the tick's tactical events (the cavalry-limit idiom) so the shared hoist delivers it.
Test: erode a marshal from 25 to <=20 through the dotation pass; assert the end-turn result
carries redemption_event.

## HV-4 The live parser interprets idioms the corpus pins as refusals (P3, harness/corpus)
`Ney, cover the retreat` -> live action=defend (ambiguity 25); `Ney, fix bayonets` -> live
action=charge (ambiguity 8). Corpus rows (parser_golden_corpus.json ~:3461, :3472) expect
`success: false` + "Unknown action" in BOTH modes; they were written July 18 against the FAST
parser's silent-wrong arms (retreat / masonry repair). Mock 548/548; live 527/531 (these two
rows x 2 worlds). Both live readings are defensible. Disposition: mark both rows `mock_only`
(the fast-parser pin stays) or add a `live` expectation block; decide whether idiom
interpretation is wanted (VISION says "every input gets a response").

## HV-5 Two incoming offers in one turn: the first answer is refused as stale (P2, defect)
audit-flagship-mock lines 130-133, 227-229, 263-265, 339-341: the driver answers Russia's
`armistice_losing` and the reply is "Sire, another matter has arrived since — this concerns
Britain. Your earlier answer was not delivered; the ma…" (4x in 24 turns), because an
`incoming_settlement_offer` PREEMPTED the standing dialogue. The client would show the same
refusal to a player who answered the first popup. Whether the preempted offer is answerable
later (mailbox) needs the routing lens; the refusal names no road back.

## HV-6 The letter-book re-asks the same declined court every 4 turns (P3, design)
flagship-mock: Ottoman open borders at turns 2,6,10,14,18,22; Saxony 3,8,12,16,20,24 — six
identical asks after six declines; 38 letters in 24 turns. Across nine arms: Ottoman 22,
Portugal 21, Saxony 20, Hesse 17, PapalStates 16. The IGR-F 3-turn court cooldown makes a
4-turn drip; a declined court neither escalates nor sweetens nor stops.

## HV-7 Digest banner headlines are harness artifacts (harness, P4)
`enemy phase: ... — ========================================` = first line of the AI
COUNTER-PUNCH banner message (combat_executor.py:4164); `[Shield] ...` / `[Square broken — ...
breaks formation to attacks]` rows likewise the first line of multi-line messages. The client
renders enemy actions from `action_type` (enemy_phase_dialog.gd:121 `_format_action`), never
`message`, so these never reach the screen. The driver's `first_line` should skip banner /
bracket lines. (The "breaks formation to attacks" grammar IS in a backend string — check if any
client surface renders it.)

## HV-8 Numbers across the nine arms
battles / unopposed captures / letters / petitions:
ambient-austerlitz 39/23/24/0 · ambient-ulm 18/23/11/0 · ambient40 41/27/14/0 ·
flagship-live 22/4/17/8 · flagship-mock 41/9/38/16 · latewar-t20 15/22/0/0 ·
naval 36/21/13/10 · propose 14/3/6/0 · tutorial 5/0/0/0.
Massena (latewar) was ground to <100 men over turns 27-28 by 4-7 attacks a turn from three
Austrian corps and was destroyed by turn 30 (not immortal; but the AI spent ~10 attacks on a
stub). Paget (3,547 men at the end) walked ~10 French homeland provinces unopposed in 8 turns.

## HV-9 The Low Countries coast is mislabelled (P2, map authoring — verify visually)
Registry europe.json anchors (pixel x east, y south): London (753,612) · Normandy (848,669) ·
Artois (949,639, r75, France) · **Friesland (946,556, Holland)** straight NORTH of Artois ·
**East Frisia (997,536, Hanover)** · **Westphalia (1053,570, Hanover)** · Oldenburg (1081,516,
Hanover) · Flanders (1105,610, France) · Osnabruck (1144,546) · Brabant (1149,652) · Amsterdam
(1166,592) · Hanover (1200,484) · Gelderland (1253,598) · Brunswick (1284,534).
Drawn-border adjacency (walkability): Artois ↔ {Friesland, East Frisia, Westphalia, Picardy,
Normandy, Paris, Champagne}; Westphalia ↔ {Artois, Picardy, Flanders, Oldenburg, East Frisia}.
The real coast runs Artois → Flanders (Dunkirk/Belgium) → Zeeland → Holland → Friesland → East
Frisia → Oldenburg → Hanover; on this map Flanders sits EAST of Oldenburg and three Dutch/German
names sit on the Belgian coast touching Artois and Picardy. Consequences: Hanover (British ally)
owns three provinces on France's Channel coast at boot; "Ney, march to London" routes
Flanders → Westphalia → Artois → Normandy (audit-naval turn 6); the Flanders 12k Channel depot
(DEF-6) is 250 px from the strait it guards. Fix shape: a rename pass over the six coastal
polygons in europe.json (single source for renderer + create_europe_regions) with matching
europe_1805.json ownership + the scripts/tests that name Flanders; needs the owner's eyes on the
lookup bitmap first (Region_114/107/104/085/109/106). Do NOT re-run build_region_key_from_psd
--adjacency-only (CLAUDE.md).

## HV-5 correction
dialogue_manager.preempt keeps the displaced dialogue (returns via queue promotion); the refusal
"Your earlier answer was not delivered; the matter before you awaits your decision."
(diplomatic_executor.py:3425) does not SAY the earlier matter comes back -> P3 legibility, not a
lost offer.

## HV-10 The Grand Diversion resolves silently (P3, naval legibility — needs the lens)
audit-naval turn 5: "order the diversion" -> Admiralty quote popup -> answer 1 -> NO result
line reaches the digest (digest.jsonl holds only the quote and two later "already attempted"
refusals); turn 7 "already attempted". Whether the strait opened or the fleet fought at
readiness 40 was never narrated on any digest surface (dispatch/notification). Verify in
naval.py resolver + dispatch beats; may be a driver blind spot (naval_line key).

## HV-11 copy
tactical_executor.py:481 "[Square broken — X breaks formation to attacks]" — `_action_display_name`
returns a conjugated verb; the sentence wants the infinitive. Player-facing (own marshals).
"DISPATCH: [!] Bernadotte's Counter-Punch opportunity has expired!" led the morning dispatch on
audit-naval turn 6 (a stale notification promoted to headline).

## HV-10 reclassified: a HARNESS blind spot, not naval silence (P4 harness)
naval_executor._execute_naval_diversion's confirmed arm returns `result = dict(outcome)` whose
`message` IS the narrated result (naval.py:1466 resolve_diversion builds the line) plus a
`naval_diversion` event. The driver's drain() (tools/playtest_driver.py:1194) only SCANS follow-up
responses for further popups; a follow-up's `message` is never written to the digest. So every
answer-then-result surface (clarification confirms, naval quote-then-confirm, CR-2 asks) shows
the question in the digest and never the outcome. Fix: digest the follow-up message as a
"↳ result:" line. Player-facing: the client prints the follow-up response normally.

## HV-12 Live parser == mock parser on the flagship script (working_well)
audit-flagship-live vs audit-flagship-mock, first 37 commands (the live arm's whole span):
37/37 identical command + ✓/✗ mark and identical message prefixes. The two live corpus misses
(HV-4) are idiom interpretations the corpus forbids, not misreads.

## HV-13 A sued-for peace ratified enemy occupation of the homeland (observation, P3 — lens to judge)
audit-propose: France (passive, losing) proposed peace to Austria on turn 22; Austria accepted
the same enemy phase in which it took Provence and Languedoc unopposed. Final autosave (turn
25): PEACE with Austria; Austria holds Swabia, Lyonnais, Languedoc, Provence — three of them
French homeland — with no clause returning them (active_treaties has no France|Austria entry
carrying clauses in the record printed; verify what the ratified terms were). The driver
confirmed the proposal_confirm blind; the terms preview is on the popup the digest does not
print (HV-10's family). Question for the diplomacy lens: does the generated bilateral peace on
the LOSING side ever include a homeland-return clause or price the occupied homeland, and was the
player shown that the peace freezes the occupation?

## HV-14 Arm endings (for §3)
ambient historical 40t: 6 provinces, treasury 4,683, net -299 · ambient ulm 24t: 13 provinces,
22,182, -1,459 · ambient austerlitz 24t: 8 provinces, 10,164, -1,215 (seed variance is real:
a passive France ends at 6 / 13 / 8) · flagship mock 24t: 26 provinces, 15,735, 41 battles,
111 popups, Ney a prisoner, Napoleon's corps broken · flagship live 12t: 29 provinces, 20,088,
22 battles, 37/37 commands identical to mock · propose 24t: 22 provinces, 30,343 (+2,234/turn
at peace), Austria signed turn 22 holding three homeland provinces · latewar t20→30: 6
provinces, Paris still French, Paget walked the west · naval 20t: 23 provinces, 23,877, the
Diversion consumed turn 5 (outcome not digested — HV-10), no landing ordered from a yard ·
tutorial: completed 10 turns, 5 battles, Kienmayer captured turn 2 then "Unknown target"
turn 3, the famine headline 7 turns running.

## HV-15 The fleet's two P1 parsing claims REPRODUCE on the shipped (mock-default) parser
TestClient /command, fresh 1805 world each time, mock parser:
- "Davout, attack next turn" -> ok=True, turn 1->2: THE TURN ENDED (4 AP forfeited).
- "Ney, delay the attack on Mack" -> attacked NOW: muster, Ney marched Rhineland->Swabia, AP 4->3.
- "Ney, attack Mack later" -> same: attacked now.
- "Ney, blockade Vienna" -> fleet posture guard->blockade ("The fleet stands out to sea on
  blockade. Austria and Russia are closed...") — a marshal order became a naval posture.
- "Ney, attack Mack and Davout scout Swabia" -> only the attack ran; Davout joined the muster
  (moved to Swabia), never scouted; nothing said the second clause was dropped.
- "Kienmayer, attack Mack" -> honest: "There is no Marshal 'Kienmayer' in the order of battle,
  Sire. Whom did you intend?" (the fleet's addressee-drop claim did NOT reproduce in this form;
  refuters to narrow).
HV-15b Live mode does NOT rescue either P1: with CommandParser(use_real_llm=True) both
sentences resolved the same way and the Anthropic API was never called (the fast parser's
keyword match clears the 0.7 confidence gate, so the LLM is never consulted) — the
PARSE-NEG family: meaning-blind keyword confidence, this time for the deferral tense and the
"next turn" substring.

## HV-16 The "enemy colours on French soil" streak resets while the enemy never leaves
audit-ambient40 dispatch headlines: t20 "3 turns", t21 "4", t25 "8", t28 "11", then t36 "3
turns" and t37 "4" — a reset to 3 at turn 36 while French provinces went 7 -> 6 and the
enemy had stood on French soil continuously since turn 18. Supports the narration finder's
claim that the streak is keyed to the LEADING province, not to the condition.

## HV-17 The blockade floor raises a beaten fleet (confirms the naval finder)
naval.py:76-77 READINESS_TICK=5, READINESS_BLOCKADE_FLOOR=50; the per-tick pass for a
BLOCKADED nation is `readiness = max(READINESS_BLOCKADE_FLOOR, readiness - READINESS_TICK)`
(naval.py:~1573). A fleet beaten to 40 (the Diversion's failure readiness) that is under
blockade reads max(50, 35) = 50 on the next tick: the floor is a ratchet UP for a beaten fleet.

## HV-18 Cannon-fire interrupt options carry hidden trust costs (confirms the strategic finder)
strategic.py cannon_fire response: "continue_order" -> trust -2 ("Non-literal acting literal"),
"hold_position" -> trust -3, applied via marshal.trust.modify before the reply; the client's
interrupt_popup.gd option table (lines ~24-40) carries labels only ("Continue as Ordered",
"Hold Position", "March to the Guns") with no cost, so the player learns the price only in the
result message after choosing. Fix shape: stamp `trust_cost` per option in the interrupt
builder (strategic.py) and render it in the label, the way petition arms carry `cost`.

## HV-19 Pre-checks of three fleet P2s (seams opened, not fully reproduced)
- main.py:3028/3032: the tactical- and strategic-objection early returns call
  `_build_result_response(result, world)` with the default `drain_popups=True` (main.py:462),
  so a queued popup is popped into a response whose client route is the objection modal —
  the IGR-X7 non-draining fix (`drain_popups=False`) covered the capture routes only. Whether
  the objection route renders popup keys is the refuters' question.
- dispatch.py contains the word "bombard" ZERO times: no headline/sub-beat class for a
  bombardment day (the narration finder's P2 — bombardment casualties never reach the
  dispatch or the Gazette).
- dispatch.py has no garrison-assault class either (only the "region_taken" remedy copy names a
  garrison) — an enemy assault on a French garrison that FAILS is invisible unless a province
  changes hands (the narration finder's other P2).

## HV-20 The enemy-colours streak is keyed on the leading REGION (confirms the narration P2)
dispatch.py:~919 `_add("enemy_on_our_soil", identity=f"enemy_on_our_soil:{region_name}", ...)`
— the standing-class streak (PC-7's per-identity counter) restarts whenever the province chosen
to lead changes, which is HV-16's measured 11 -> 3 reset on the ambient board. Fix shape: key
the identity on the CONDITION ("enemy_on_our_soil") and carry the region as a display field.

## HV-21 A refused aggressive first-step attack leaves the order standing (seam confirmed)
strategic_executor.py:2134-2153: an aggressive marshal at favorable odds auto-attacks through
`self._executor.execute({... "_strategic_execution": True})`; on `result.get("success")` the
order continues; otherwise `return result` — the refusal (crossing gate, terrain gate, AP
pre-gate) is returned verbatim, `marshal.strategic_order` is neither cleared nor mentioned,
and the 2-AP order stands. Contrast the blocked-path arm above it (:2104), which clears the
order and SAYS "awaits new orders". Refuters to reproduce with a SHUT crossing target.

## HV-22 The economy converges as designed and the peace dividend is visible (working_well + one question)
audit-ambient40 net/turn: +1,961 (t1) -> +839 (t15) -> -120 (t16) -> about -250 through t28 while
28->27 provinces (EB-1 Charges of Empire absorbing the passive surplus, treasury peaking at
25,115 on t15), then -1,200..-1,800 as the homeland falls (t29-33), ending 4,683 at 6 provinces.
audit-propose: net -687 at t21 in war -> +2,270 the turn Austria signed (t22) and +2,234 after
— a legible peace dividend. audit-flagship-mock: +2,300 early, ~0 by t11-18 with 28-30
provinces, negative after Ney's capture. QUESTION for the economy lens: with 20-25k banked and
nothing to spend on in a passive campaign, what does the chest DO — the sink is war (recruits,
depots, rentes), so a peace-time chest is inert by design (EC-P3 §golden peace).

## HV-23 Driver option gating (narrows the routing finder's harness claim)
tools/playtest_driver.py `_enabled()` (:592) IS honoured by the objection chooser (:738) and
the petition chooser (:824); the finder's claim is specifically the diplomatic-dialogue
chooser (~:1069) pressing a disabled option — refuters to confirm on that arm only.

## HV-24 Two seams behind fleet claims, opened
- naval_executor.py:60-66 (build ships): the ONLY explanation the message offers for a
  readiness figure is "new crews come aboard green at 40; only sea-time makes a navy" — the
  blockaded-nation tick (naval.py:~1573, -5/turn to the floor) is never named, so a player
  laying keels under blockade reads 69 -> 63 -> 58 (audit-naval t1-t3) as the price of building.
- combat_executor.py:8311-8330 (_attempt_region_capture): `has_fort` is the ONLY gate between
  "occupation timer" and INSTANT CAPTURE; the garrison check lives in the callers. Homeland
  provinces ship with no fortification and (outside capitals) no garrison, so any column at
  war flips one per move — Paget's 3-a-turn walks (audit-latewar-t20) and Archduke John's
  Provence -> Languedoc (audit-propose t22) are the rule, not a bug. Design question (P3):
  should a homeland province offer a militia/levy resistance or a 1-turn occupation timer?
- Stub attacks (audit-latewar-t20): Massena was attacked 2x (t25), 4x (t26), 4x (t27, losses
  56/63/2/1), 1x (t28) — eleven AI attacks over four turns on a corps under a hundred men.

## HV-25 The letter-book's 4-turn drip: the type cooldown is written in one vocabulary and read in another
Probe (1805 world, TestClient): turn 2 envoy digest row 0 = mailbox_id 2, `proposal_type`
"friendly_gift", RENDERED as "Ottoman: Open Borders Agreement"; POST /mailbox/respond reject
-> "You have rejected Ottoman's proposal" and the cooldown store reads
{'Ottoman|nation': 3, 'Ottoman|friendly_gift': 6}. The six-turn TYPE cooldown is keyed on the
stable P-rule label (friendly_gift) while the letter the player sees, and the court's next
ask, carry the rewritten terms type (open_borders) — so only the 3-turn NATION cooldown binds
and the same court is back at turn+4 (HV-6: Ottoman at 2, 6, 10, 14, 18, 22). The IGR-F memo
warned of exactly this vocabulary split. Seams: ai_diplomacy.apply_rejection_cooldowns (:383)
writes `{nation}|{proposal_type}`; `_is_on_cooldown` (:326) reads the same key — so the
mismatch is in WHICH label each caller passes (mailbox decline passes the stable label; the
producer's check passes the rewritten one, or vice versa). Fix shape: ONE label at both
seams (the stable context key), pinned by a test that declines a letter and asserts the same
court's same ask is blocked for TYPE_REJECTION_COOLDOWN turns.
HV-25b (mechanism, read at ai_diplomacy.py:803-812 and :1024-1046): a cool court's routine
asks ROTATE through two stable labels — "friendly_gift" (a gift-wrapped low-tier ask whose
terms["type"] maps to open_borders when relation < 0) and "open_borders" — that render as the
SAME "Open Borders Agreement" letter. Declining one writes `{court}|friendly_gift: 6`; the
court's next ask carries the other label and is blocked only by `{court}|nation: 3`, so the
identical visible ask returns at turn+4 with both cooldowns technically honoured. Fix shape:
key the TYPE cooldown on the ask's TARGET STATE (terms["type"] / _ASK_TARGET_STATE) or on the
low-tier family, so a declined "Open Borders" blocks every wrapper of it for 6 turns.

## HV-26 The alliance-paradox refusal names no road through (P3 legibility)
diplomacy.py:4676-4683 builds the HARD_STOP "Making peace with Austria while allied with
Bavaria (who is still at war with Austria) creates a diplomatic contradiction."; the bilateral
confirm consumer (diplomatic_executor.py:~3927) returns exactly that `display` as the whole
message. It never says what WOULD work (a common peace through the Cabinet's settlement route
that seats Bavaria too, or ending the alliance first). audit-propose hit it 2x, flagship-mock 1x,
latewar 1x.

## HV-27 No combat seam raises trust — the trust warning's remedy is not a lever (confirms the drama finder)
Backend-wide literal positive trust writes: defiance.py:308 (+2, a defiance proven right),
strategic.py:2522 (+5, a LITERAL completing an order), turn_manager.py:811-824 (the autonomy-
return outcomes +40/+25/+15/+5), trust.py:177 (a test stub). No write in combat.py /
combat_executor.py / relationship.py. The warning at world_state.py:12095 tells the player to
"give him a battle he can win"; a won battle moves glory and relationships, not trust.
(Variable-based writes at the objection seams — `marshal.trust.modify(trust_change)` — carry
the "trust his judgment" half; verify their sign paths before rewriting the copy.)

## HV-28 A DISMISSED marshal is mourned as destroyed (confirms the drama finder, P3)
disobedience.py:~1756 dismiss arm -> world.destroy_marshal(name, cause="dismissed") writes a
tombstone {nation, turn, location, cause:"dismissed"} (world_state.py:2631-2636); main.py:931's
pre-parse guard renders every tombstone as "Marshal X is lost to us, Sire — his corps was
destroyed at <location>" without reading `cause`. Fix: branch the sentence on `cause`.

## HV-29 The Rebuke's intel pause is dead by one underscore (confirms the save/turn finder, P3)
jealousy.py:2724 writes `marshal.literal_intel_paused_turn`; marshal.py:663/1661/1857 declare
and serialize `literal_intel_paused_turn`; world_state.py:2884 (the fog pass) reads
`getattr(marshal, "_literal_intel_paused_turn", None)` — a different attribute, never set. The
Rebuke arm's promised obsessive-patrol pause never fires. One-character fix + a test that a
rebuked literal's fog lift is suppressed on the named turn.

## HV-30 The C3 auto-advance guard rides the save (confirms the save/turn P4)
world_state.py:7318/8210 serialize `auto_advanced_to_turn`; the guard blocks a typed "end turn"
on the turn auto-advance already processed, so Continue from an autosave written by an
auto-advanced turn absorbs the player's first End Turn with the "already advanced" message.
Fix: clear it in load_game's transient block (it is per-session UI state, not world state).

## HV-31 Only the first end-turn interrupt is asked (confirms the strategic P3)
strategic.py:309-316 pass 2 over deferred marshals: `if report.get("requires_input"): break`
— a second marshal's interrupt in the same end turn is never raised; his order's turn is
spent on whatever the loop left him with. Fix: queue the remaining interrupts (the client's
interrupt_queue already exists) rather than break.

## HV-32 Cannon fire is nation-blind (confirms the strategic P3)
strategic.py:2268 `world.get_battles_within_range(marshal.location, 2)`; world_state.py:4904
filters by distance only — no nation/side filter — so an aggressive French marshal "rushes to
join" an Austria-vs-Prussia quarrel two provinces away, and a cautious one asks the player
about it. Fix: filter to battles where a side is the marshal's nation or its allies.

## HV-33 The administrative role has no player road back (confirms the drama "missing")
disobedience.py:1514 promises "Troops frozen for future restoration"; the ONLY writer of
`marshal.administrative = False` is the DEBUG cheat toggle at meta_executor.py:1541. No verb,
petition arm or turn-tick returns him. Either build the return verb (1 admin AP, at the
capital) or stop promising it in the option text.

## HV-34 The `garrison` verb feeds no stability (confirms the tie-in finder, P3)
world_state.py:6330 `garrison_bonus = 5 if self._has_marshal_in_region(region.name,
region.controller) else 0` — stability growth credits a MARSHAL standing in the province,
never a `garrison_detachment` left by the player's garrison verb, so "garrison it" as the
remedy for unrest is a lie on the tooltip. Fix: `or region.garrison_detachment`.

## HV-35 The stale-answer refusal drops the answer and names no road back (confirms HV-5, P3)
diplomatic_executor.py:3421-3431: when the dialogue on top is not the one answered, the
response is `stale_dialogue: True` + "Your earlier answer was not delivered; the matter before
you awaits your decision." and carries the NEW dialogue. The displaced one returns later by
queue promotion (dialogue_manager.preempt), but nothing tells the player that, and the
driver's `--diplomacy accept` arm is refused every time a second offer lands the same turn.

## HV-36 Only a SOVEREIGN's captivity reaches the peace table (confirms the tie-in, P2)
diplomatic_templates.py:3606-3616 (stage 4b, the Brétigny rule): `prisoner_return` demands and
sweeteners are generated ONLY for `is_sovereign` marshals. Ney, a prisoner of Austria from
turn 23 of audit-flagship-mock, is priced by the scorer and applied by a ratified clause if
someone authors one, but no generator ever proposes his release — the player must know the
clause exists. Fix: extend stage 4b to any held marshal with a lower rank than the sovereign
term, priced at the existing ransom seam.

## HV-37 War purpose display keyed on the PAIR (seam opened; the finder's claim)
war_status.py:157 reads `world.war_objectives[diplo_key]` (the France|opponent pair key); a
purpose staged against a coalition war's LEADER pair is invisible on the other members' rows.
Refuters to confirm with a staged purpose in a coalition war.

## HV-12 CORRECTION (the harness finder was right, my claim was vacuous)
tools/playtest_runs/audit-flagship-live/server_console.log shows exactly ONE Anthropic call in
12 turns: "Soult, deal with the Austrians" -> action=unknown, ambiguity 72 (the CR-5
delegation ASK). The other 36 commands were resolved by the FAST parser at >= 0.7 confidence
and never reached the LLM in either arm — so "37/37 identical" measures fast-parser
determinism, not live-parser equivalence. The flagship script has no sentence the fast parser
cannot resolve, which is itself the finding: the live parser is a fallback that ordinary
scripted phrasings never exercise, and the two P1 misreads (HV-15) are exactly the sentences
it would have needed to see. Retract "live == mock" as evidence of parser quality; keep the
corpus (527/531 live) and HV-15b as the live-mode evidence.
