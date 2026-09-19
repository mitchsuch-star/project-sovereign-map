# VERDICT:CXR1-6 — REFUTED as filed

**Finding:** *"A question now pre-empts an open envoy letter and the refusal
never mentions it"* (lens `question-guard`, P3, claimed player-reachable and
claimed shipped by row CX).

**Verdict: REFUTED as filed.** The *tightening* the lens explicitly declines to
file reproduces exactly as stated. The *defect it does file* — the copy — does
not survive three measurements:

1. **It is not row CX's.** The identical refusal copy is what IQ-7's own
   documented case (`should i accept?`, landed September 18, the day before row
   CX) gets on the shipped tree. Before row CX that same line got the
   12,717-character COMMAND REFERENCE — so CX-2 **improved** the very copy the
   row condemns.
2. **"Nothing says the letter is still waiting" is false at the client**, three
   ways, measured. On the default path the shrug is **never printed at all**:
   the response carries `incoming_proposal`, the client re-mounts Prussia's
   letter as a modal and returns from `_on_command_result` *before*
   `_display_result`.
3. **"Every sibling refusal names the matter" is false** — 1 of 6 siblings I
   drove on the same board names it, and that one names it for a different
   reason (the player named a rival court).

The suggested fix is measured to attach a diplomatic nag to **9 of CX-2's own
twelve questions** and reds **0** pins, which is the worst combination
available.

---

## 1. My reproduction — not the one I was given

Everything below was driven through `POST /command` on the **shipped 1805
board** via `TestClient(main.app)` with the `world` / `game_state` / `parser`
triple swapped. `LLM_MODE=mock`; zero network calls. Probes are committed
beside this file: `probes/v6_harness.py`, `v6_find_letter.py`, `v6_repro.py`,
`v6_payload.py`, `v6_siblings.py`, `v6_blast.py`, `v6_fixsim_plugin.py`, with
their raw `.log` / `.json` output.

**The board.** I did *not* reuse the lens's board. One `end turn` from a
historical-seed boot puts an `incoming_proposal` on the desk:

```
BOARD: turn 2  dialogue {"type": "incoming_proposal",
                         "options": ["accept_ai_proposal","reject_ai_proposal","counter_ai_proposal"]}
context: {"proposal": {"type":"open_borders","proposer_nation":"Prussia", ...},
          "source_nation": "Prussia", "acceptance_score": 27}
GET /mailbox -> 3 letters: Prussia ACTIVE, Ottoman WAITING, Portugal WAITING
```

Every utterance below runs from the **same serialized snapshot** of that board.

### 1a. The tightening — reproduces exactly as filed

| utterance | `shipped` | `cx1_off` (`A_QUESTION_NEVER_ORDERS=False`) |
|---|---|---|
| `is accepted` | shrug, **no state change** | `Prussia: PEACE → OPEN_BORDERS` |
| `had better accept` | shrug, **no state change** | `Prussia: PEACE → OPEN_BORDERS` |
| `why not accept` | shrug, **no state change** | `Prussia: PEACE → OPEN_BORDERS` |
| `accept` (control) | `PEACE → OPEN_BORDERS` | `PEACE → OPEN_BORDERS` |

Confirmed: CX-1 stops three phrasings that previously signed a treaty out of a
question, and the letter stays answerable (`accept` on the next line still
signs). The lens is right not to file this, and right that it is IQ-7's
fail-closed rule working.

### 1b. The COPY — the filed half — is PRE-EXISTING, and CX made it better

The decisive control is the line **IQ-7 pass 3 was itself landed for**, quoted
in `dialogue_routing.py:175-181`: *"Measured with Portugal's open-borders
letter current: `should i accept?` SIGNED THE TREATY."* Four arms, same board,
same snapshot:

| arm | `should i accept?` |
|---|---|
| `shipped` | `Berthier sets down his pen. "I cannot answer that from the dispatches, Sire."` + `What I CAN do today: Ney, attack Mack …` — **identical shrug, names no letter** |
| `iq7_off` (`A_QUESTION_NEVER_ANSWERS=False`) | **`PEACE → OPEN_BORDERS`** — proves IQ-7's lever, not CX's, owns the route away from the dialogue |
| `prerow` (CX-1 lever off + pre-row lead regex + CX-2 desk off) | **the 12,717-char `COMMAND REFERENCE`** — also names no letter, and is strictly worse |
| `cx1_off` | the shrug (CX-1's lever does not reach this line — it carries `?`) |

So *"a question refused while a letter is open, with no mention of the letter"*
has been the behaviour since **September 18**, one commit family before row CX,
for every line `A_QUESTION_NEVER_ANSWERS` catches. Row CX-1 widened *which*
lines land there; row CX-2 replaced the manual with a sentence and a counsel
list. **`shipped_by_this_row` is false for the defect that was filed.**

---

## 2. "Nothing says the letter is still waiting" — measured FALSE at the client

### 2a. The response re-raises the letter itself

`v6_payload.py`. Every response on that board — the three questions, `status`,
and an ordinary `Ney, attack Mack` — carries:

```
incoming_proposal: {"from_nation": "Prussia", "diplomat_name": "Hardenberg",
                    "proposal_type_display": "Open Borders Agreement", ...}
pending_envoy_count: 3
pending_lapsing_count: 3
```

This is the R4 popup passthrough (`build_base_response`), not anything the
question route added.

`main.gd:2676` — `_response_has_incoming_proposal_route` returns **true**
whenever `incoming_proposal` is non-null and its `from_nation` is not the
nation the player has explicitly dismissed. It is a `_post_hud_response_routes`
entry, and `main.gd:2855` returns from `_on_command_result` **before**
`_display_result` at `2898` — the client's own comment at `main.gd:2576` states
this as the contract: *"every entry there returns from `_on_command_result`
BEFORE `_display_result`"*.

**So on the default path the player never sees the shrug at all.** They type
`is accepted`, Prussia's letter mounts as a modal with Accept / Reject /
Counter-offer / Not Now, and the command line stays disabled until they answer
(`set_input_enabled(true)` is below the early return).

### 2b. The only path that reaches the shrug announces the letter in words

To reach the typed road with this letter open the player must first press
**"Not Now"** (`incoming_proposal_popup.gd:177`), which sets
`_dismissed_proposal_nation`. That button's own handler
(`main.gd:5779-5784`) prints:

```
Setting aside Prussia's proposal. Click the envoy badge to revisit.
```

### 2c. And the badge stays lit on the shrug's own response

`pending_envoy_count = 3` rides the shrug response and is copied into
`diplo_data` at `main.gd:4241`, then `_set_pending_envoy_count` →
`open_envoys_button.text = "Open Envoys (3)"` and
`top_bar.update_diplomatic_fields`.

The player has been told where the letter is, by the dismissal line and by a
live count on the very response, and on the un-dismissed path they are handed
the letter itself. The row's premise does not hold.

---

## 3. "Every sibling refusal names the matter" — measured FALSE (1 of 6)

`v6_siblings.py`, same board, Prussia's letter current:

| line | names Prussia? | what came back |
|---|---|---|
| `grant the petition` | **no** | *"Berthier peers at the dispatch with concern. I cannot make sense of this…"* |
| `do not accept` | **no** | *"Then no order goes out, Sire — I have relayed nothing…"* |
| `asdf qwerty` | **no** | *"Sire, I must confess this order eludes me…"* |
| `Ney, fortify` | **no** | executes normally |
| `accept the petition` | yes | **signs the treaty** (matter guard yields — separate matter, not this row) |
| `accept austria's offer` | **yes** | *"that answer would be delivered to Prussia … answer Prussia first, or set this matter aside"* |

Only the last names the letter, and it does so because the line **named a rival
court** — that is `court_mismatch_refusal_for_a_petition`, a misdirection guard,
not "a refusal that names the standing matter". Three non-question refusals on
the same board, none of them touched by row CX, say nothing about the letter
either. If this is a defect it belongs to the **soft-stop contract**, whose
written rule (`main.py:3182-3192`, WO-7) is the opposite: *"a pending SOFT-STOP
dialogue must not wall off the ordinary road … the sentence goes exactly where
it goes when nothing is pending."*

**A fourth correction:** the row cites *"IQ-7's own rule is that an unaccepted
phrasing is re-prompted in place."* That rule is scoped in writing to one
family. `dialogue_routing.py:1140-1152`: *"For a CLIENT petition only (Slice H's
ally petition is untouched, **and so is every other family** …)"*. An
`incoming_proposal` is not a client petition.

---

## 4. Would the suggested fix ship a regression? Yes — and no pin would stop it

The fix as written: *"When `is_question` claims a line and a dialogue is
current, the desk's answer should carry the standing matter's one-line
reminder."*

**Blast radius (`v6_blast.py`), against CX-2's own twelve questions, on the
turn-2 board with the letter open:**

```
11 of 12 are claimed by the question guard
 9 of those get a REAL desk answer
```

So `where is Ney`, `what's my income`, `how many men does Davout have`,
`what can I build here`, `who is winning`, `what does Austria want`,
`am I at war with Prussia`, `how much is a battalion` and
`what happens if I attack Mack` would each grow *"Prussia's letter waits in
Envoys"* — every question, every turn a letter is open, with **three letters in
the book** so the "standing matter" is ambiguous besides. That is IGR-F's own
complaint (*"a surface that eats your orders"*) one notch down, arriving on the
answers CX-2 exists to deliver.

**Pins: I implemented the fix as stated in memory and ran the owning files.**
`probes/v6_fixsim_plugin.py` patches `_route_unanswered_question` **and** the
answered-question producers to prepend the reminder whenever
`world.pending_diplomatic_dialogue` is set; nothing on disk was touched.

```
pytest tests/test_cx1_a_question_never_orders.py \
       tests/test_cx2_berthier_answers_the_board.py \
       tests/test_iq7_review_round.py -p v6_fixsim_plugin
[FIXSIM] CXR1-6 suggested fix installed
661 passed in 86.30s
```

**Zero red.** I will not claim a pin it does not red. What that measurement
actually says is worse for the fix than a red would be: every fixture in the
three owning files builds a **fresh boot board with no pending dialogue**
(`test_cx2…::ask`, `build_world("1805")`, no `end turn`), so the entire fix is
**invisible to 661 tests by construction**. The nearest pin,
`TestTheShrugTeachesWhatWorks::test_no_shrug_proposes_a_war_on_a_court_we_are_at_peace_with`,
asserts literally `assert "Prussia" not in message` — it stays green only
because its board has no letter; on the board this row is about, the fix puts
"Prussia" in the shrug. That is one `end turn` away from being the pin that
reds, and nothing today would tell anyone.

---

## 5. What I would keep

One P4 note, not a row: bare **`why not`** now answers *"What you want is in
the campaign log (press L)"* (`_QUESTION_TOPICS` maps the word `why` → `log`).
Measured, the pre-row answer was *"Berthier peers at the dispatch with concern.
I cannot make sense of this…"* — also not an answer, and neither executes
anything. It is also the safe residue of closing a real P1: `why not retreat`
and `why not attack Mack` are the two sentences CX-1 was landed for, and they
retreated the whole army and fought a battle.

## 6. Field verdicts

| field | filed | measured |
|---|---|---|
| reproduces as stated | — | tightening **yes**; copy claim **no** |
| severity | P3 | **P4 at most**, and not this row's |
| player_reachable | true | only behind a deliberate **"Not Now"**, whose own line names the letter |
| shipped_by_this_row | true | **false** — IQ-7 pass 3 (Sept 18) owns the route; CX-2 improved the copy from the 12,717-char manual |
