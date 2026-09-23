# First Contact + The School of War Refresh — landing record (September 23, 2026)

> **Status:** LANDED September 23, 2026, on master, in ONE commit (first contact +
> the School of War + the IQ-10 re-shoot). **Rules of record:**
> `docs/SYSTEMS_REFERENCE.md` §54 (first contact) and §55 (the unbreakable
> lesson). Defect rows: `docs/BUG_FIXES.md` §First Contact & the School of War.
> Tests: `tests/test_first_contact_keyless.py` (114) ·
> `tests/test_tutorial_unbreakable_2026_09_23.py` (23, driven).
>
> **User direction:** a keyless first-contact report (92 wild sentences at the
> shipped fast parser) → *"is there anything we should do before build?"* →
> *"build these, and for the tutorial do diplo in it too; make sure they can't
> break the tutorial — I had issues of not being able to finish tasks because
> conditions in game grabbed it"* → *"make sure it explains naval and other
> weird concepts like pushback, general relationships etc."*

## 1. The report, reproduced

Every claim was re-driven at the real `POST /command` on the shipped 1805 boot
(scratch `probe_a.py`, fresh world per sentence, state snapshot around each):

| Family | Before (measured) | After |
|---|---|---|
| Greetings (`hello`, `hi`, `good morning`, `bonjour Berthier`, `hey there`) | the three-template shrug ("I cannot interpret that order… 'Ney, attack Mack', perhaps?") | Berthier bows, names this morning's first counsel, and the **three doors** (`what can I do` / `status` / `help`) + F1 + Esc |
| The pause menu (`quit`, `exit`, `restart`, `menu`, `main menu`, `options`, `settings`, `new game`, `start over`, `pause`, `load game`, `how do I save`) | the shrug; `how do I save` printed the 12k manual | one line: the Emperor's own affairs are on the pause menu — **press Esc**; nothing relayed |
| Undo (`undo`, `undo that`, `can I undo that`, `go back`, `take that back`, `oops`) | the shrug | "no unsaying an order once relayed"; names `cancel <marshal>` (the real holder when one has a standing order) and the pause menu |
| Stuck (`what now`, `now what`, `what next`, `I'm stuck`, `im stuck`, `I am lost`, `no idea what to do`, `any suggestions`, `advise me`, `help me`, `I don't know`, `?`) | the shrug; `I don't know` drew the PARSE-NEG prohibition line; `help me` the manual | the options desk — *"These orders would be carried out today, Sire:"* (ONE source with `what can I do`) |
| The goal (`win the war`, `how do I win`, `how do we win the war`, `what is the goal`, `how does this work`) | the shrug / the manual | the open-ended campaign named honestly (reads `sandbox_mode`; turns honest by itself when the Victory Pass lands) + today's counsel + the three doors |
| `build a tank` | *"Example: 'build supply depot at Lyon'"* — Lyon is not on the map | the player's capital (`economy_executor.example_region`) |
| `send the submarines to London` | *"Try: 'Ney, attack London' or 'Ney, move to London'"* — a march the Royal Navy shuts | the road law's own verdict + THE ADMIRALTY pointer; no march offered |
| `Ney, move to London` (the order the shrug suggested) | **ACCEPTED** — walked Ney to Lorraine, route → Normandy → London (FA-46 one verb over: `march to London` was refused, `move to London` was not) | refused at 0 AP with the same naval verdict as the strategic verb |
| `destroy Austria` / `destroy Prussia` | *"Bernadotte cannot attack Bavaria — they are our ally"* (the verb fuzzy-matched into Deroy) | *"Austria is a nation, not a province. Name a province — theirs are …"* |
| `how many men do I have` and six phrasings | the unanswered tail | the whole army, strongest first, with the Ledger pointer |
| `is Mack strong` / `is Mack dangerous` | the unanswered tail (`how strong is Mack` was answered) | the strength answer |
| `nuke Vienna` | `'Ney, move to Vienna'` | the corps with the shortest LAWFUL road, and `attack` only where we are at war |

Zero of these move the board: every pin reads AP, every marshal's ground and
strength, and the dialogue slot around the sentence.

## 2. What was built (first contact)

* **`backend/ai/first_contact.py`** — ONE source for the vocabulary the mock
  chain routes on and the copy the help executor prints: anchored whole-line
  patterns (greeting / escape_menu / undo / options / goal), the address
  stripped, literal-argument meta-commands (`save …`, `load`, `debug`) declined
  by the route itself, fail-closed. Sited in `_parse_with_mock_chain` BEFORE the
  guards and the question arm (`how do I win` is a syntax question to the manual
  otherwise). Confidence 0.9 — never escalates to the LLM; GR6.
* **The shrug names its doors** (`THREE_DOORS`), the marshal-only shrug names
  the player's CAPITAL (`_home_example`), and the place-only shrug walks the
  road law first (`_place_suggestion`: `strategic.plot_route` +
  `issuance_road_refusal` over every fielded corps; the shortest lawful road is
  named; a refusal names the sea and THE ADMIRALTY).
* **The tactical `move to` belt reads the road law** (`movement_executor`): the
  belt's own two plotting calls were `plot_route`'s ladder; the verdict is now
  read before an AP is charged. The AI's road is byte-identical (verdict is
  player-only) — `BASELINE_SERIES` and M1–M7 unchanged.
* **The question desk**: `how_many` gains the `is <X> strong|dangerous|…` arm
  (name4); a new subjectless `own_army` kind answers the whole army.
* **A verb is never a place**: `attack_vocabulary.guard_attack_verb_forms()`
  (every attack verb + inflections) joins the fuzzy target scan's skip list.
* **The example province is on the map**: `economy_executor.example_region`;
  the manual's `repair Lyon` → `repair Lorraine`.
* Corpus +9 rows (`first-contact-*`, mock arm; `is Mack strong?` keeps its
  question mark so the CX-1 both-arms pin holds).

## 3. What was built (the School of War)

Eighteen cards (was fifteen), mirrored in `tutorial_state.STEPS`, driven headless
by `tools/tutorial_overlay_harness.gd`:

* **VII. The Cabinet** (gate 3) — the diplomacy lesson. The chip **opens the
  REAL F1 wizard on Austria** (`open_cabinet` signal → `main.gd
  _on_tutorial_open_cabinet` → `diplomacy_wizard.open_for_nation`); typed
  diplomatic verbs are redirected to that door by ruling G1, so a typed chip
  would have taught a dead route. The step completes when the mission the
  wizard confirms is LIVE: the base response's `talleyrand_mission_summary`
  turns from the backend's own sentinel `"None"` to `Gather Intelligence →
  Austria` (`_pred_mission_started`). The card states the cost (1 DP/turn of
  5), the D ledger and the mailbox.
* **IX. The Marshalate** (gate 5 — FA-42 forbids a second gate-4 card; it shows as "waiting" from the moment VIII completes — self-releasing) — the muster's WILL JOIN /
  WILL NOT line; the G card (trust, glory, skills, relationships); *"Ney and
  Soult are at odds — two marshals at odds bring half their weight"* (the
  authored −1 pair); the glory ladder and envy — DORMANT in the lesson and the
  card says so; the Reward chip and reward expectation.
* **XVI. The Wooden Wall** (gate 10, self-releasing) — the naval rule, taught
  on a lesson that authors no fleet and SAYS so: the Royal Navy's Channel, the
  crimson SHUT link, THE ADMIRALTY (T, then 7), `build ships`, blockade + the
  Continental System, expeditions, the Grand Diversion, Normandy and Lisbon.
* **Pushback** on IV/V: a marshal may push back against an order that offends
  his character; TRUST is the currency; low trust → DEFIANCE and the hearing.
* **First contact** on I and XVII: Tab completion, province-click chips, the
  three doors, Alt+key, L and N, the notice rail, Esc.
* **Unbreakable:** (1) a refusal of the card's OWN suggested order releases the
  step at once with the reason on the next card (`main.gd` calls
  `note_sent(command)` at the three send sites; `_refused_our_order` reads the
  refusal — never the payload, which ships no command echo); (2) every card but
  the last carries **Skip this lesson ▸**; (3) the gate+2 catch-up stays as the
  floor and now says so on the next card.
* The driver gains a `missions: begin|decline` dial; both lesson scripts open
  the Cabinet on loop 3 under `begin`.

## 4. Driven, not asserted

`tests/test_tutorial_unbreakable_2026_09_23.py` records real responses from
the real tutorial scenario (through `/new_game {"scenario":"tutorial"}` and
the client's own answer endpoints) and feeds them to the real
`tutorial_overlay.tscn`:

| Path | Result |
|---|---|
| The idle Emperor — thirteen `end turn`s | handoff reached by turn 12; on every response the card is ≤ gate+2; every card but the last offered the skip chip |
| The refused order — Jellacic in Munich, then the card's own `Senarmont, move to Munich` | I → II → III on the refusal, *"The war refused that order — … The school moves on."* |
| A refusal of some OTHER order (`Ney, move to Rhineland`, already there) | the card stays on II |
| The Skip chip / the Cabinet chip | releases with a word / `cabinet_opened == ["Austria"]` |
| The Cabinet lesson — `gather intel on Austria` then "Begin mission" | the staging response (a question) leaves VII; the confirm completes it → VIII; the door chip renders once the gate is reached |
| The committed lesson script end to end | every one of the 18 cards seen in order, handoff reached, zero skips |

The backend mirror's "floor" claim was corrected while pinning it: the mirror
reports the latest gate the turn has reached, which runs AHEAD of the card
inside a turn (turn 1: the card is on I, the mirror says III). What holds is
that its gate is one the turn has reached, and both name the handoff at the
end. The `test_fa_slice17_f` step-number pin flipped 10 → 12 consciously.

## 5. Found in passing

* **A typed `yes` to Talleyrand's mission confirm draws the shrug** — the
  `mission` dialogue is answered by its buttons (or the wizard); filed FC-X1,
  not fixed here.
* The HC-5 instrument tokens (THE ADMIRALTY, Reward, Design rows) must stay on
  card XVII — its pins caught their move to the new cards; restored.

## 6. Sweeps and gates

* `tools/_sweep_first_contact.json` — **19 of 20 killed, 0 INERT**; FC-18 (the
  belt stops reading the verdict) reported BROKEN by the sweep tool twice while
  the same mutation applied by hand turns 5 of 7 move-road pins RED (verified,
  then reverted) — the tool mis-reads its junit report when the failing
  assertion carries a non-ASCII message (the naval verdict's em dash); a tool
  quirk, recorded here, not a weak pin.
* `tools/_sweep_tutorial.json` — **10 of 10 killed, 0 INERT** (the refusal
  release, the sent-line comparison, the skip chip and its click, the Cabinet
  chip, the mission sentinel, the catch-up floor, the mirror, the driver dial,
  main.gd's `note_sent`).
* The driven tutorial pins under the sweep's own flags (`-p no:randomly`):
  the engine's defiance and combat rolls are UNSEEDED (`[DEFIANCE] Roll …`),
  so a driven path must answer whatever popup comes (`Recorder.settle`) and
  end turns until the turn advances (`end_turn_until`) rather than assume
  the sequence — the first cut assumed it and went red under that flag.
* Parse harness EXIT=0 (53 scripts incl. `tools/tutorial_overlay_harness.gd`);
  boot smoke 0 SCRIPT ERROR; ruff clean; the golden corpus green under BOTH
  arms of the CX-1 lever (`is Mack strong?` keeps its question mark for that
  reason); `BASELINE_SERIES` + M1–M7 unchanged (the belt's verdict is
  player-only).

## 7. The IQ-10 re-shoot

All 82 surfaces at Interface Scale 1.0 and 2.0 — **164 frames**
(`docs/audits/IQ10_<ID>[_X2]_2026_09_23.png`), every machine record read:
**0 buttons off the logical viewport, 0 clipped labels, 0 `<null>`, 0 raw
nation tags.** IQ10-X1 (the top bar at 2.0) and IQ10-X2 (the grant reason
above the fold) are confirmed closed on the frames. Two instrument facts
learned the hard way: the runner's `--out-dir` must be ABSOLUTE (a relative
`docs/audits` crashed every Godot shot with an access violation and left
stray `spec.json`/`index.json` beside the frames), and one 164-frame Godot
process on a box with ~2.7 GB free RAM dies mid-batch with a null-allocation
crash — the re-shoot ran as 32 chunked per-scale processes with a retry
(one chunk needed it, while a second Godot process was contending for the
`.godot/imported` cache — never run two Godot processes on the project at
once).
