# The Answer-Binding Shuffle — DD-1 S6, the third instrument (October 11, 2026)

*Pre-Deploy S6, `docs/PRE_DEPLOY_PLAN.md` §3.1 "The instrument" 3. Tool
`tools/answer_binding_shuffle.py`; record `docs/audits/dd1/answer_binding.json`;
ledger `tests/data/answer_binding_known_misbinds.json`; pin
`tests/test_dd1_answer_binding_shuffle.py`; rules `SYSTEMS_REFERENCE.md` §106.3;
row `BUG_FIXES.md` DD1-9. Nothing fixed — the slice measures.*

## What was measured

Three letters from three courts — Prussia's alliance (relations 60), Denmark's
non-aggression pact (20), Saxony's open borders (0), each at the relation its
treaty needs so SF-V1 does not withhold it — delivered through the real
producer (`ai_diplomacy.deliver_ai_proposal`) in **every delivery order** (six),
on a fresh board each row (the boot cloned through the save road); then every
typed answer and every button sent through the real endpoints (`POST /command`,
`POST /respond_to_diplomatic_dialogue`, `POST /mailbox/activate`, `POST
/mailbox/respond`) and the outcome read against the shipped contract (IQ-7's
closed grammar, CA9's court guard, W6-0 / FA-N5's identity binding):

| the form | the court it names | the contract |
|---|---|---|
| `accept` / `yes` / `reject` / `counter` | none | binds to the letter on TOP |
| `accept Prussia's offer` / `reject the offer from Denmark` / `we shall accept Saxony's offer` / `decline Prussia's alliance` | the named court | answers it when it is on top; REFUSED naming it when it is queued (the letter-book tail), nothing promoted, nothing applied |
| `Prussia, yes` | the named court | answers it on top; re-prompted otherwise |
| `accept X's offer if the others agree` / `shall we accept?` / `accept later` / `accept tomorrow` | — | relays nothing (fails closed) |
| a button with the letter's own `dialogue_id` | that letter | answers it |
| a button with a QUEUED letter's id | that letter | refused as stale, nothing applied |
| a button with no id | — | the letter on top |
| `mailbox/respond {mailbox_id}` | that item | answers it (a routine small court) or refuses it whole ("too weighty") |

**312 rows over six orders.** A misbind is an answer applied to a court other
than the one named, a bare answer applied to a non-current letter, a refusal
naming the wrong court, or a fail-closed line that relayed anything.

## The reading

- **308 of 312 bound.** Every bare answer took the letter on top; every named
  answer for a queued court was refused *naming that court* with the
  letter-book tail and nothing moved; every stale button id was refused
  (`stale_dialogue`); `mailbox/activate` brought every queued letter up and
  the named answers then bound to it; every fail-closed line relayed nothing;
  `mailbox/respond` answered Denmark's and Saxony's letters and refused
  Prussia's alliance whole (*"That matter is too weighty to answer from the
  letter-book, Sire"* — by design, not a misbind).
- **4 misbinds, one class: `decline <court>'s pact`.** With Denmark's
  non-aggression PACT queued or on top, the line is not read as an answer at
  all — `pact` is not among the closed grammar's matter nouns
  (`_CLOSED_MATTER_NOUNS`: offer, terms, petition, ultimatum, settlement, peace,
  alliance …), so `closed_answer` claims nothing, the court guard reads no
  addressee shape it governs, and the line falls to the order desk: *"Berthier
  clears his throat. 'Forgive me, Sire …'"* / *"Sire, I must confess this order
  …"*. Nothing moved — the failure is closed — but a diplomatic answer in the
  player's own words was shrugged at as an order, and the queued court was
  never named. Beside it, `decline Prussia's alliance` and `decline Saxony's
  offer` bind. → **DD1-9.**

## The done-when

§3.1: *the answer-binding shuffle reads 0 misbinds.* **NOT met: 4, one class.**
The pin runs the whole shuffle live (about a minute) and holds the ledger as a
ratchet; it asserts the done-when NOT met so it is re-seated on purpose.

## How to re-read

```
.venv/Scripts/python.exe tools/answer_binding_shuffle.py --list        # every row
.venv/Scripts/python.exe tools/answer_binding_shuffle.py --write-ledger # after a fix (the count must fall)
```
