# Row MC — "Mon Cousin": the Order of the Marshalate

**Status:** BUILT and LANDED November 17, 2026 (row BA, session BA-6; the row's own record is this file).
**Code:** `backend/game_logic/precedence.py` (the whole row, ~1,550 lines; its docstrings are the design),
the R0 seam in `backend/models/marshal.py`, the seeding in `backend/models/world_state.py`, the surfaces
named in §4. **Tests:** `tests/test_mc_the_order_of_the_marshalate.py`. **Seams:** `tests/_ba6_seams.py`
(rows MC0, MCBOOK, MCSEEDS, MCBONDS, MCRANK, SILENCE). **Siblings:** `docs/JEALOUSY_SPEC.md` (the glory window, envy
and the petition channel this row stands beside and never replaces), `docs/AUTHORITY_CURRENCY_SPEC.md` (the
price of a title), `docs/MARSHAL_RECRUITMENT_SPEC.md` (a commissioned marshal's seat and history).

The Emperor addressed each marshal as "Mon Cousin". Before this row the court had a season's laurels and a
number between every two men, and nothing else: the number moved only by the battle's Win/Loss formula, and
no surface could say *why* two marshals were friends or enemies. This row gives the court an order, a memory
and a way to be wronged.

---

## 0. The gate record

**The user's words (November 17, 2026):** "ba-5 is done please assure its good dont leave any open items also
make sure the terrian background does not look ai genend even get assets if needed and look into marshal
relationships and mnake sure the pecking order and their relationships is engaing and well desinged", and,
after: "commit and push when done leave no open calls or anything make decisions yourself soundlt with
research".

**How it was decided.** Under the user's delegation: there was no plan gate and no question put back to the
user. Every fork below was settled by reading the code and the scenario, by the rules the user has already
set (events appear and authority bites; personality is character, not situation; history with teeth;
golden rule 6 — the executor is deterministic; golden rule 1 — one source for combat modifiers), and by a
measure (`tools/_ba6_series_arms_final.json` and the court count `tools/_ba6_court_rule_2026_11_17.json`, §8).

**What was found wrong before the row** (read from the code at `fdd4756f`):

1. A marshal's view of another moved only by the Win/Loss formula after a shared battle
   (`relationship.py`) and by the jealousy channel's own escalations. A battle that two marshals won side by
   side and a battle that one of them abandoned moved the number alike, or not at all.
2. There was no pecking order. The glory ladder ranked the season's laurels (an eight-turn window); nothing
   ranked the court itself, nothing kept a title, nothing said who stood above whom.
3. Nothing remembered a cause. The scenario authored forty-odd pairs with their views but no reason; an
   audience's card spoke of "a grievance" without naming the laurels it grew from, so the first audience of
   a campaign read as uncaused (§2.9).
4. Three of the authored enmities were 1806–1809's feuds, not 1805's: Davout and Bernadotte, Murat and
   Bernadotte, and Bernadotte and the Emperor opened Hostile (-2). Auerstedt (October 1806) was written
   into the opening of a campaign that begins in September 1805, so the game could not produce its own.
5. `Marshal.modify_relationship` read the *derived* view (a jealous man's live -1 included) and wrote it
   back as the stored one, so a +1 was swallowed and an escalation's -1 dropped a man two rungs (R0, §2.8).

---

## 1. The research the design rests on

Only what the scenario and the code themselves state; nothing here is history beyond the files.

**The order the seats follow.** `europe_1805.json` carries a top-level `seniority` key, `{nation: {name:
seat}}`, whose own comment calls France's seats "the order of the 1804 list of marshals (the decree's order
- a convention of the histories, not a formal precedence)". France: Murat 2, Masséna 5, Bernadotte 7, Soult
8, Lannes 10, Ney 12, Davout 13 (the list's own numbers: the gaps are the batons not in this scenario's
roster). Austria: Archduke Charles 1, Archduke John 2, Mack 3. Russia: Kutuzov 1, Buxhowden 2. Prussia:
Brunswick 1, Hohenlohe 2. "A baton given later is junior to every baton already given", and "a court left
out ranks its generals in roster order": the code reads both (`seat_of`, `seed_the_commissioned`).

**The causes, as the scenario words them.** `relationship_causes` is `{"A->B": cause}`, "true as of
September 1805: an incident where one is documented, a characterization where none is, never an invented
incident", and each direction carries its own wording where the two men saw it differently. Examples as
authored: Ney and Soult, "Montreuil and Saint-Omer: rival camps on the Channel coast, 1803-05"; Ney and
Lannes, "two soldiers risen from the ranks, alike in their dash"; Ney and Murat, "Moreau's Army of the Rhine
against Bonaparte's Army of Italy: old rivalries" (Murat's side reverses the clause); Lannes and Murat, "the
Guard's deficit, 1802" (Lannes: "Murat worked to have him removed"; Murat: "he pressed the accounts against
Lannes"); Murat and Bernadotte, "Brumaire, 1799: Murat cleared the Orangery; Bernadotte stood aside";
Bernadotte and the Emperor, "he stood aside at Brumaire, 1799, and has not been forgiven"; Davout and the
Emperor, "Bonaparte's man since Egypt, 1798"; Lannes and the Emperor, "Italy, 1796: friends ever since - he
alone still says 'tu'". Pairs with a man still in the recruitment pool (Grouchy, Suchet, Oudinot, Augereau,
Schwarzenberg, Hiller, Bagration, Bennigsen, Blücher and others) wait in the book for his commission
(§2.2). The scenario's own comment fixes the reading of three enmities: Auerstedt is October 1806, "and the
game can make its own Auerstedt".

**The titles of victory, as the code names them.** `title_name`: "Duke of <the field>" and, for a man already
a duke, "Prince of <the field>" ("the Field" where no place is known); `estate_style` reads the ducal style
an estate gives him (`dotation.derive_title`, the dotation's own honorific). A title names the field the
laurel was won on, because the laurel carries its place (`jealousy._GLORY_PLACE`, §2.3).

---

## 2. The design, part by part

### 2.1 The order of precedence

`order_of_precedence(world, nation)` sorts the court by `(-tier, seat, name)`. **Tier** (`tier_of`): 2 a
prince, 1 a duke (a title of victory in `Marshal.honours`, or an estate's ducal style), else 0. **Seat**
(`seat_of`): the authored seat, else `LATER_BATON` (100) plus his place in the roster. So titles come first,
then the order of the 1804 list, later batons after. The court is the nation's marshals who are not the
sovereign, not a client's general (`contingent.is_clients_general`) and either standing or held captive
(`in_the_court`): **a captive keeps his place, marked** (`captive: true` on the payload), because a man taken
at Ulm is still a marshal of the Empire. `place_in_the_order` returns `(his place, of how many)`, `(0, 0)`
outside the court. Seam `the_order_of_precedence_stands`.

### 2.2 The book of incidents

`world.marshal_ledger` is `{"A|B": {"incidents": [...], "won": n, "lost": n}}` keyed by the two names
sorted. Every incident is `{turn, kind, place, a, b, a_to_b, b_to_a[, note, note_a, note_b]}` where `a_to_b`
is what A's view of B moved by and `b_to_a` the reverse: **a cause is kept per direction** (a founding
incident carries `note_a` and `note_b`, so Lannes and Murat each keep their own wording). One writer moves a
view with a cause, **`note`**; one recorder, **`record`**, writes the moves the older writers make (the
Win/Loss roll, an escalation, a council breach). A pair keeps `BOOK_KEEP` = 4 incidents; the founding one (a
`seed`) is never dropped. `INCIDENT_LINES` holds one sentence per kind in the staff's voice, read from either
man's side (`incident_line`).

**AGAINST and FOR kinds.** `cause_of(world, viewer, other)` answers "why does he feel as he does": the
latest incident that *moved his view*, or that *speaks the way his view leans* — an AGAINST kind
(`shared_defeat, blamed_the_lead, blame_laid, silence, passed_over, under_junior, escalation, harsh_words,
breach, friendly_fire, claim_rebuked, laurels`) read for a Rival or Hostile, a FOR kind (`shared_victory,
brothers, rescue, blame_taken, thaw, mediated, decreed`) read for a friend. A slight to a man already a
Rival, which the floor stopped from moving, still names why he feels so. **Same-turn tie-break:** among
incidents of one turn, the one that moved his view outranks one that only fed it, then the later in the book
(a defeat blamed and a junior's lead in the same battle read as the defeat). A founding cause is read bare;
any other is read with "(turn N)". Seam `the_book_keeps_its_incidents`; down, no book is kept and no
surface names a cause.

**The opening's seeding** (`seed_the_book`, called from `WorldState.from_scenario`): the authored seats,
the 1805 reading (§2.5), and a founding incident for every authored pair with its authored cause (a pair
with no cause reads "an old history between them"); a cause between a marshal and a man still in the pool
waits in the book under `waiting` and is handed to him by `seed_the_commissioned` at his commission, which
also seats him after every baton already given.

### 2.3 Renown

`bank_renown(marshal, points)`, called from the one glory chokepoint `jealousy._append_glory`: every laurel
a marshal wins is banked for good (`Marshal.renown`); a defeat that costs glory costs one renown (floor 0).
The sovereign banks none. The season's glory is untouched — it still drives envy and the crown — so the
court now has two clocks: the eight-turn laurels and the lifetime renown. The laurel also records *where*
it was won (`_GLORY_PLACE`, written by `record_battle_glory`) so a title and an audience can name the field.
`renown_order` ranks the court by renown, its order breaking ties. Seam `a_marshal_banks_his_renown`.

### 2.4 Titles of victory

`victory_earns`, called from `record_battle_glory` for the man who *led* a victory: a decisive win worth
`DUKE_POINTS` (3) glory, or `PRINCE_POINTS` (4) for a man already a duke, **away from the Emperor's eye**
(not shadowed) puts the next title in the Emperor's gift for `TITLE_DUE_TURNS` (8): `Marshal.title_due =
{tier, name, place, turn, expires}`. It lapses silently if unconferred (`_lapse_titles`). The player
confers it (`confer_title`, the Generals chip, `POST /confer_title`); the price goes **through
`standing.buy`** with the cause `title_conferred` — `DUKE_PRICE` 3 authority, `PRINCE_PRICE` 5, raised by the
buy's recency — and lands whole or not at all (a refusal pays nothing and writes nothing). On conferring:
the honour is written to `Marshal.honours`, his trust rises `TITLE_TRUST` (3), his expectation of a dotation
rises (`dotation.raise_expectation(..., "title")`).

**Who is passed over, and who is not** (`_would_pass_over`): a marshal of the same court who stood above him
in the order and would stand below him after it, **whose renown is within `RIVAL_DEEDS` (2) of his** (a
senior with clearly fewer laurels knows the title was earned), **and who is not his friend** (a friend, +1 or
better, is glad of it); a peer already of the new rank keeps his place above. Each remembers it: his view of
the new duke falls one rung with the floor at Rival (-1) — **a slight makes a Rival, never by itself a
Hostile** (`passed_over`). The confer quote says all of it beforehand (`confer_quote`: price, refusal, who
will hold it against him). **The AI courts confer theirs** (`_courts_confer`) by the same rule and at the
same price in their own authority, skipping any buy the court cannot afford. Seams `titles_of_victory`,
`ai_courts_confer_titles`.

### 2.5 The two-way bonds

A bond is written by `after_shared_battle`, called from `relationship.py` after the Win/Loss roll for **both
sides** of every battle (golden rule 5: the courts of the AI are the same code), over the court's own men
only (a client's general fights beside them but holds no place and no bond). Deterministic: no rule here
draws a random number.

- **Brothers in arms** (`brothers_in_arms`): friends (+1 both ways) who share their `BROTHERS_AT` (4th)
  victory in a *real* battle (the glory ladder's own bar, `jealousy.is_laurel`; a skirmish makes no
  brothers) become Devoted (+2 both ways). The count is `won` on the pair's book row.
- **The shared defeat** (`a_shared_defeat_sours`): a defeat (the other side's victory, or this side's line
  broken) shared by two or more of the court's corps **sours the view of the man who led it** — a
  Professional or Rival view falls a rung, never below Rival by this road; a friend forgives the first
  (`lost` on the row) and holds the second against him — **unless the Emperor took the field himself**
  (the sovereign among the participants: nothing sours). On the player's side the account asks first (§2.7).
- **The rescue** (`a_rescue_mends`): a corps that came up to a comrade's battle he was hard pressed in
  (his side's men fewer than the foe's) and did not see it lost is owed: the lead's view of the man who came
  rises a rung, even from Hostile; once in `BOND_COOLDOWN` (6) turns a pair.
- **The silence** (`a_silence_is_remembered`): a Hostile comrade who stood within reach — on the field or
  one province from it, never a scan of the map — and did not march to the guns while the battle was lost or
  hung, **or while the lead was hard pressed, won or not** (`a_silence_is_remembered_when_pressed`, row
  SILENCE: his side's men fewer than the foe's — the rescue's own reading, `_hard_pressed`), is remembered:
  the lead's view of the silent man falls a rung (**the Auerstedt rule**: Davout won at Auerstedt outnumbered
  two to one, and Bernadotte, within reach, did not come; the danger he was left in was the wrong, not the
  result). A man under a support order on the lead, broken, in recovery or captive is not silent;
  `BOND_COOLDOWN` applies. *The pressed clause is the court count's find (§8): as first built, "lost or hung"
  only, ten AI-played French campaigns recorded no French silence at all.*
- **Serving under a junior** (`serving_under_a_junior_rankles`): a senior (a lower place in the order) who
  fought under a junior's lead, and is not his friend, holds it against him — Rival at worst; once in
  `JUNIOR_COOLDOWN` (8) turns a pair; never with the Emperor present. The attack card says so beforehand
  (§2.11).
- **A quarrel cooling** (`old_quarrels_cool`, `_cool`): a Rival view (-1) that *a quarrel of the campaign
  made* — an incident of play with a negative move on his side — cools to Professional (0) after
  `THAW_TURNS` (12) turns with no incident between them. **Never an authored one:** a pair whose only
  history is the founding seed is character and does not fade; a Hostile view never cools by time alone; a
  live envy (`jealous_of`) or an escalation of level 2 or more holds it.

**The 1805 reading** (`the_seeds_read_as_of_1805`): Davout and Bernadotte, Murat and Bernadotte, and
Bernadotte and the Emperor open as Rivals (-1), not Hostile (-2) (`SEEDS_AS_OF_1805`). **R0**
(`the_bond_writes_the_stored_view`, `Marshal.modify_relationship`): the writer moves the *stored* view; a
jealous man's derived -1 is never baked in.

### 2.6 Titles' price and the order's meaning in the field

`CONSEQUENCE` says what a view means in the field, read off what the game already does
(`combat_executor._RELATIONSHIP_SCALING`, the Hostile reinforcement bar, the SUPPORT objection ladder):
Devoted, half again his weight in a joint fight; Friendly, a quarter more; Professional, his full weight;
Rival, half his weight and a support order beside him resented; Hostile, nothing in a joint fight and he will
not march to his guns unless ordered. The row *says* these; it computes none of them. Golden rule 1 stands:
no combat modifier is calculated here.

### 2.7 The account

A joint defeat of two or more of the **player's** corps with the Emperor absent queues an account
(`world.marshal_accounts`, a list of `{lead, others, place, turn[, named]}`) instead of souring at once.
The petition channel offers the oldest waiting account when it is free (`_push_accounts`, tier "audience");
the card asks whose the defeat was: **The Emperor takes it** (`ACCOUNT_PRICE` 2 authority through
`standing.buy`, cause `blame_taken`; nothing sours; the lead's trust +`ACCOUNT_TRUST` 2), **It falls on the
lead** (the others hold it against him as `sour_on`; his trust -2), **It falls on another** (the lead's view
of the senior of the others falls a rung; that man's trust -2; the rest are spared), **Let it lie** (free;
they hold it against the lead as they will). An account that waited `ACCOUNT_SHOWS_FOR` (3) turns unseen is
let lie; one whose lead is gone is dropped. Seam `an_account_follows_a_joint_defeat`.

### 2.8 The claim

A marshal of the player's court, untitled, whose renown is at least `CLAIM_RENOWN` (6) and **stands
`CLAIM_GAP` (3) places or more above his place in the order** (`trails_his_deeds`) asks for his due, once in
`CLAIM_COOLDOWN` (12) turns, when the petition channel is free (`_check_claims`). The card offers three
answers: **Create him Duke of <his best field>** (`best_field`, the place of his largest laurel in the
window; `DUKE_PRICE`, trust +3, the seniors he passes hold it against him), **Not yet** (free; trust -2;
no new claim for twelve turns), **Rebuke his presumption** (trust -4; he holds it against the man who stands
above him with less renown: `claim_rebuked`). A claim retires if its man is gone or has been given a title
meanwhile (`claim_retirement_reason`). Seam `a_marshal_claims_his_due`.

### 2.9 The audience names its cause (GRD-17)

An envious marshal's audience card names the laurels he resents — "He has not forgotten X's laurels at
<field> (turn N)" (`jealousy._laurels_place`) — so an audience is never about nothing; the quiet answer
("grievance runs its course") says what follows, read off the same standing-cost rule the card's own option
quotes (`_standing_cost_detail`), instead of one constant line. A temporary grievance shows on the Generals
screen one rung lower than its stored view and is marked `temporary`, with the laurels as its cause. Seam
`an_audience_names_its_cause`.

### 2.10 The AI courts

The courts confer by the §2.4 rule (`_courts_confer`) and are souring, rescuing and remembering by the §2.5
rules on their own corps, because `after_shared_battle` takes both sides' men. They are not asked an account
(the account is the player's) and make no claims; a defeat shared in an AI court sours its lead at once
(`sour_on`).

### 2.11 The attack card's court line

`order_quotes` (the attack card, `q["note"]`) appends `precedence.order_card_line(world, lead, joining)` over
the corps that would answer the guns (`force["joining"]`): a senior who "ranks above X and will resent
serving under him"; a marshal Rival or Hostile to the lead with the field consequence in the staff's words;
a marshal devoted to the lead with his. A friend of rank above says nothing of rank. Seam
`the_card_names_the_court`; down, the card is silent on the court.

### 2.12 The objection voices (GRD-17) and GRD-31

`strategic_executor.IDLE_OBJECTION_VOICES` gives Ney, Murat, Lannes and Masséna each his own line when he
objects to sitting idle where all four said the same sentence (the lines that carry a reading — "We outnumber
them", "we have the advantage" — are unchanged; a marshal with no voice keeps the old line). Seam
`each_aggressive_man_objects_in_his_own_voice`. GRD-31 (`defiance.get_defiant_action`): a cautious marshal
who defies a PURSUE fortifies where he stands, as he does when he defies an attack, a support or a march
(seam `a_cautious_man_defies_a_pursuit_by_fortifying`). Both are ruled in
`docs/audits/OPEN_CALLS_RULED_2026_11_17.md` §2.

---

## 3. The numbers

Every constant of `precedence.py`:

| Constant | Value | Meaning |
|---|---|---|
| `BOOK_KEEP` | 4 | incidents a pair keeps (the founding one stays) |
| `TITLE_DUE_TURNS` | 8 | a title stays in the Emperor's gift this long |
| `DUKE_POINTS` | 3 | glory (unshadowed) a victory needs to earn a ducal title |
| `PRINCE_POINTS` | 4 | ...and a princely one, for a duke |
| `DUKE_PRICE` / `PRINCE_PRICE` | 3 / 5 | authority, the base of `standing.buy` |
| `TITLE_TRUST` | 3 | his trust, on the day |
| `ACCOUNT_PRICE` / `ACCOUNT_TRUST` | 2 / 2 | the Emperor takes the defeat on himself / the trust either way |
| `ACCOUNT_SHOWS_FOR` | 3 | turns an account waits for the channel before it lies |
| `CLAIM_RENOWN` | 6 | renown a claimant needs |
| `CLAIM_GAP` | 3 | places his renown stands above his place in the order |
| `CLAIM_COOLDOWN` | 12 | turns between one man's claims |
| `CLAIM_REFUSED_TRUST` / `CLAIM_REBUKED_TRUST` | 2 / 4 | "not yet" / a rebuke |
| `THAW_TURNS` | 12 | quiet turns before a Rival view cools |
| `BOND_COOLDOWN` | 6 | a rescue or a silence between one pair |
| `JUNIOR_COOLDOWN` | 8 | serving under a junior, per pair |
| `BROTHERS_AT` | 4 | shared real victories that make friends Devoted |
| `RIVAL_DEEDS` | 2 | a senior whose renown is within this of the new title's man feels passed over |
| `SENIORITY_UNSET` | 0 | no authored seat |
| `LATER_BATON` | 100 | a marshal with no authored seat ranks after the list, in roster order |
| `SEEDS_AS_OF_1805` | three pairs | Davout-Bernadotte, Murat-Bernadotte, Bernadotte-Napoleon: -1 (was -2) |

---

## 4. What the player sees, surface by surface

- **The Generals screen** (`marshal_management.gd`; payload `GET /marshal_overview` →
  `build_marshal_overview` → `marshal_overview._build_court` → `precedence.card_fields`; `order_payload` at
  the response's `order`, built in `backend/main.py` beside the glory ladder): the court in its order
  (switchable to renown, or the season's laurels), each row with place, seat, style, renown and its place,
  crown, envy, captive mark and a "trails his deeds" flag; under the rows, **the court's live pairs**
  (`live_pairs`, at most three: open quarrels and strongest bonds, the freshest first); on a marshal's card,
  **his bonds in both directions** (`bonds_of`: the view, what the other feels, the cause with its turn, and
  what the view means in the field — the sovereign's bond shows no consequence) and his **honours**. A
  marshal with a title in the gift shows **the confer chip** (`title_due`: the name, the turns left, the
  price, whether it is affordable and why not, the line naming who will hold it against him), which sends
  `POST /confer_title` (`api_client.gd confer_title`).
- **The attack card** (§2.11): one clause on the court beforehand, in `note`.
- **The campaign log:** `marshal_bond` ("X's view of Y: Rival — <why>."), `title_in_the_gift` ("A title of
  victory is in the Emperor's gift: X, Duke of Y (8 turns)") and `title_conferred` ("Marshal X is created
  Duke of Y — passed over: ..."), all three the player's own court's (the fog filter lets a nation's own
  through, `campaign_log.py`), in the `command` category.
- **The petitions:** the account and the claim ride the marshal-petition channel as tier "audience" cards
  (§2.7, §2.8); an envious marshal's audience names the laurels (§2.9).
- **The authority causes:** `display_names.AUTHORITY_CAUSES` reads `title_conferred` ("X created Duke of Y")
  and `blame_taken` ("the defeat at <field> taken on the Emperor's own name") on the books of authority.

---

## 5. The save

Held-only: nothing is written while empty, so a save of a world with no court history is byte-for-byte what it
was (`Marshal.KEPT_ONLY_WHEN_HELD_FIELDS` for the marshal's five; the world's two are conditional entries in `WorldState.to_dict`). `Marshal`: `seniority` (int, 0 unset),
`renown` (int), `honours` (list of `{tier, name, place, turn}`), `title_due` (dict or none),
`last_claim_turn` (int). `WorldState`: `marshal_ledger` (the book, §2.2) and `marshal_accounts` (the waiting
accounts, §2.7). Every `from_dict` reads with a default, so an old save loads as an empty court. The
fields are listed in `docs/SAVE_FORMAT_REFERENCE.md`; `tests/test_serialization_enforcement.py` holds the
round trip.

---

## 6. The seams

Each is a zero-argument function returning `True` in the game, held down by `tests/_ba6_seams.py`; with all
of them down the court is the commit before (`fdd4756f`), and a board recorded before the row replays under
the rules it was recorded under.

| Row | Seam | What it gates | Down means |
|---|---|---|---|
| MC0 | `marshal.the_bond_writes_the_stored_view` | R0: `modify_relationship` reads and writes the stored view | the derived view is read, as before |
| MCBOOK | `precedence.the_book_keeps_its_incidents` | the book, its causes on every surface, the seeds' founding incidents | no book is kept; no surface names a cause |
| MCBOOK | `precedence.a_marshal_banks_his_renown` | renown | no renown |
| MCBOOK | `precedence.the_order_of_precedence_stands` | the order, captives kept in it | no order; passing-over, serving under a junior and the claim idle |
| MCBOOK | `precedence.an_audience_names_its_cause` | the audience's laurels and its quiet answer (GRD-17) | the audience says nothing of its cause |
| MCBOOK | `precedence.the_card_names_the_court` | the attack card's court line | the card is silent on the court |
| MCSEEDS | `precedence.the_seeds_read_as_of_1805` | three enmities read as Rivals | the scenario's earlier -2 |
| MCBONDS | `precedence.brothers_in_arms` | a fourth shared victory makes friends Devoted | no brothers |
| MCBONDS | `precedence.a_shared_defeat_sours` | the lead of a shared defeat is held to account | nothing sours |
| MCBONDS | `precedence.a_rescue_mends` | the man who came up is owed | no rescue |
| MCBONDS | `precedence.a_silence_is_remembered` | the Auerstedt rule | silence is forgotten |
| MCBONDS | `precedence.old_quarrels_cool` | a quarrel of play cools in twelve turns | quarrels hold |
| MCBONDS | `precedence.serving_under_a_junior_rankles` | a senior under a junior's lead | no resentment of rank |
| MCRANK | `precedence.titles_of_victory` | a title enters the gift; confer; the seniors' memory | none offered or conferred |
| MCRANK | `precedence.ai_courts_confer_titles` | the courts confer by the same rule | only the player's court confers |
| MCRANK | `precedence.a_marshal_claims_his_due` | the claim | no claim |
| MCRANK | `precedence.an_account_follows_a_joint_defeat` | the account before the souring | a joint defeat sours at once |
| SILENCE | `precedence.a_silence_is_remembered_when_pressed` | a silence is remembered when the lead was hard pressed, won or not | only a battle lost or hung |
| GRD | `defiance.a_cautious_man_defies_a_pursuit_by_fortifying` | GRD-31 | a pursuit's cautious defier sulks |
| TELL | `strategic_executor.each_aggressive_man_objects_in_his_own_voice` | GRD-17's voices | the one line |

---

## 7. The tests

`tests/test_mc_the_order_of_the_marshalate.py` (55 tests, one class per part): **TheOpening** (the order of
France is the list of 1804; the courts' senior general first; every authored pair has its founding incident
and cause; the three enmities read as 1805; seam down reads the earlier values; every seam down is the commit
before), **TheBook** (`note` moves the stored view and writes the cause; a floor stops a move and never
pushes a view back; the book keeps four and the founding one), **RenownAndTheOrder** (a laurel banked, a
defeat costs one; a captive keeps his place marked; his place trails his deeds), **TitlesOfVictory**
(earned only by a decisive victory away from the Emperor; the price, the honour, who resents it; a slight
never makes a Hostile; a friend is glad; the title lapses; a court confers its own; a duke becomes prince),
**TheBonds** (brothers; a skirmish makes none; the shared defeat; a friend forgives once; an account first on
the player's side; the Emperor's presence; the rescue mends even a Hostile; the silence; a senior under a
junior; the card; a quarrel of play cools and an authored one does not), **TheAccountAndTheClaim**,
**TheAuerstedtRuleReadsItsNamesake** (a victory won hard pressed remembers the silence; one won with the odds
forgets it; seam down reads only a battle lost or hung; the rescue and the silence read ONE pressure),
**TheCourtsWordsSayTheRule**, **TheRosterLineKeepsItsFigure** and **TheCardCarriesTheCourt** (§8.3: the brothers' count, the roster line's figure, the court and the honours on the card),
**TheAudienceNamesItsCause**, **TheScreensAndTheSave** (the card and the order; a temporary grievance marked
and named; the court round-trips a save; an old save reads an empty court; the log's three rows; the
endpoint confers). Also `tests/test_ba6_the_rulings.py` (GRD-31, GRD-17's voices, the court forms' tie order)
and `tests/_ba6_seams.py`, which `tests/_oct27_seams.py` folds in.

---

## 8. The measure

The row's measure is the session's one measure (`BATTLE_DIORAMA_SPEC.md` §15.25: the keyed probe, the commanded
band, the day's sweep, the ambient ten seeds, the AI-France harness and the deploy gate, on BA-6's cumulative
ladder TELL → MC0 → MCBOOK → MCSEEDS → MCBONDS → GRD → WS → MCRANK → PEACE → SILENCE, every chain alone on a
frozen copy), and one count of its own. What it says of the court:

- **Every seam down is the commit before** (`fdd4756f`) on every surface: the keyed probe identical on every key
  (jena and marengo, forty turns, 212 keys a turn), the band 28 / 28 / 27, the day's sweep 72 cells of 72, the
  ambient ten seeds and the harness entry for entry BA-5's.
- **What of the court moves the world.** The keyed benchmark's per-turn series against the prior
  (`tools/_ba6_series_arms_final.json`): taken alone, **MCSEEDS** diverges from turn index 12 and **MCBONDS**
  from 16 (WS, the battle's rows, from 17); **MC0, MCBOOK, MCRANK and SILENCE alone are byte-identical**. The
  book, the order, renown, the titles, the claim and the account change no AI's choice in the benchmark's forty
  turns: they are the court's memory and the player's own decisions. What moves the world is the 1805 reading
  (three enmities a rung warmer, so other corps march beside each other) and the bonds (a view that moves
  changes who answers whose guns — `combat_executor._RELATIONSHIP_SCALING`).
- **The band** (the deploy gate's difficulty guard, 23–28; CMD-H / CMD-A / CMD-M): 28 / 28 / 27 at arms 0,
  TELL, MC0 and MCBOOK; **27 / 26 / 26 at MCSEEDS**; 28 / 27 / 28 at MCBONDS and at every arm after it,
  ALL included (`tools/_ba6_band_2026_11_17.json`).
- **The gate:** **MET on the final tree** — arm ALL: story classes 10 of 10, Hesse promoted on marengo (34), the roster in three readings, no annexation outside aim on the ambient record or in the harness; arm 0 reads as BA-5 left it (Hesse on lodi 33 and marengo 39, two readings).

### 8.1 The court count — what a played court does

`tools/_ba6_court_count.py` puts a counter on every write of the court (the book's recorder, the titles'
offers and confers, the accounts, the claims) and runs the AI-France harness's own campaign on its ten seeds,
forty turns each (335 French battles): France is played by the courts' own AI, so this is a court that is
never steered — the player's court as the rules alone make it. The record and its rule:
`tools/_ba6_court_rule_2026_11_17.json`.

| Over ten campaigns | France (the player's court) | The AI courts |
|---|---|---|
| shared victories noted | 181 | 5 |
| a rescue mends a view | 92 | 1 |
| brothers in arms (friends made Devoted) | 55 | — |
| a senior resents serving under a junior | 22 | 18 |
| envy escalates (the older jealousy rule) | 30 | 12 |
| a quarrel of play cools | 4 | 13 |
| a shared defeat sours the lead | (the account asks first: 1 asked) | 33 |
| a silence is remembered (the Auerstedt rule) | **0 as first built → 2** | 20 |
| a title in the gift / conferred | 48 / (the player's to confer) | 32 / 31 |
| a claim | 9 | — |

**The court neither freezes nor melts.** At the opening the French court's one-way views among its marshals
are fourteen Rival and four Friendly, none Devoted and none Hostile. At turn forty every seed holds both warmth
and friction: Devoted 4 to 16, Hostile 1 to 6, Rival 3 to 13 (the rule's clause 3: at least one Devoted and two
Rival or worse — 10 seeds of 10, on both arms below). A campaign makes its own brotherhoods and its own feuds out
of the ones of 1805.

### 8.2 The find, and its rule (BA6-X9)

The count's first run found that **the Auerstedt rule never fired for France**: the silence was remembered only
when the lead's battle was lost or hung, and an AI-played France, which wins most of its battles, recorded none
in ten campaigns. The rule could not fire on its own namesake: Davout won at Auerstedt, outnumbered two to one,
while Bernadotte stood within reach and marched to neither field — the wrong was the danger he was left in, not
the result. A rule was written before the data (its text is the record's `rule`): the candidate remembers the
silence ALSO when the lead was hard pressed (his side's men fewer than the foe's — the rescue's own reading,
`_hard_pressed`), won or not; arm A is the row down, arm B up.

| Clause | Reading | |
|---|---|---|
| 1 — the Auerstedt rule lives (B records a French silence) | A 0, **B 2** (both on ulm) | pass |
| 2 — it does not swamp the court (B's silences ≤ a quarter of its rescues) | 2 against 92 (cap 23) | pass |
| 3 — the court stays alive (reported, both arms) | A 10 of 10, B 10 of 10 | pass |
| 4 — the game holds (the band and the gate with the row up) | the band at ALL 28 / 27 / 28; the gate MET (the chain re-taken with the row up) | pass |

**Pick: built** — `precedence.a_silence_is_remembered_when_pressed`, row SILENCE, last on the ladder; the
courts' twenty silences are unchanged (every one of them a battle lost or hung), so the AI's own feuds were
already alive and only the player's court was deaf to the rule.

### 8.3 The lived court on the screen

A court that has lived (thirty turns of an AI-played France — capture group `the_court` in
`tools/iq10_capture_payloads.py`; shots `generals_court` and `generals_court_order` in
`tools/iq10_run_captures.py`) was shot on the Generals screen at the five sizes and read by the four instruments
with the battle's surfaces (`BATTLE_DIORAMA_SPEC.md` §15.25). The order it showed: Murat Duke of Hungary,
Masséna Duke of Bohemia and Lannes Duke of Moravia first (titles first), then Bernadotte, Soult, Ney and Davout
by the 1804 seats; three live quarrels under the rows, each with its cause and turn and what it means in the
field ("brings nothing to a joint fight and will not march to his guns unless ordered"). **It found three faults
of the row's own presentation, each fixed before the record:**

- **BA6-X13** — the spec (§4) promises a marshal's honours on his card, and the client rendered them nowhere; on
  the default Generals screen his style, his place in the order and his renown were not on his card at all
  (`_court_line` stood only in the page layout). The card's body now opens with **THE COURT** ("6th of 7 in the
  order · seat 12 · renown 7 (4th)"), and the line names his honours with their turns.
- **BA6-X11** — the brothers' cause said "a third victory together" where the rule makes brothers at the fourth.
- **BA6-X12** — a long place beside a wide status badge cut the roster line at the place and lost the strength;
  the line keeps the strength alone where it does not fit (the place rides the hover).

**One blind reader** (Sonnet, the frames only: the order, Ney's card, his bonds, and an attack card with the
court's line) read the court at **legibility 7, causes 8, stakes 7, engagement 6, historical flavour 8** — "each
bond has a date and a reason", "the obedience stakes are clear", "Massena ranks above Bernadotte and will resent
serving under him" read as a cost of the order. What holds engagement at 6, in the reader's words: dense small
text that "reads like a ledger", no visual web of the rivalries, the roster's selection digits read as a second
order. **Ruled under the delegation:** the web of rivalries is **CLOSED for this row** (a new surface; the order,
the live pairs and each card's bonds carry the same facts, and it stays on record as the reader's first lever);
the roster keeps its digits as the selection keys (UI-6's ruling; the order view ranks); the order card's court
line keeps its words (the field consequence is the staff's reading, never a computed figure — golden rule 1).

