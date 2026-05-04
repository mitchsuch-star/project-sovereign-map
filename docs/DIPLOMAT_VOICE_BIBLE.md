# Diplomat Voice Bible

> **Status:** v1.2 — v0.5.3 aligned — 2026-04-25
> **v0.5.3 scope note (2026-04-25):** Cast coverage requirement now includes the live hegemony and repair surfaces, not only the breach/paradox beats. `COMMITMENTS_PRESENTATION_SPEC.md` v0.5.3 requires (a) the core breach / hard-reject leads, (b) one `balance_of_europe_shifted` warning family per likely warning court, with `noticed` / `alarming` / `crisis` variants aligned to the `33 / 50 / 60` activation gate in presentation spec §8.1a, and (c) one `amends_offered` acknowledgment line per foreign court. Bloc naming is adopted for Balance of Europe headline, `balance_of_europe_shifted` threshold beats, proposal-preview `hegemony` warnings, coalition-declaration contrast copy, and D3 per-row bloc stamps. Stamps reuse deterministic labels and do not require new authored-diplomat lines. Bargain-era callbacks and extra witness variants still defer to `docs/WAR_BARGAIN_SPEC.md` slice WB-D.
> **Purpose:** Single-page voice reference per diplomat so that every headline commitments line, breach accusation, counter-offer, and advisory response sounds like *that specific person*, not a generic envoy.
> **Scope:** Five named diplomats in `backend/models/diplomat.py`. Talleyrand has the most lines; the four foreign diplomats need the minimum live coverage listed in §Minimum cast coverage for `COMMITMENTS_PRESENTATION_SPEC.md` v0.5.1.
> **Enforcement:** any template in `backend/game_logic/diplomatic_templates.py` that uses `speaker="envoy"` or `speaker="foreign_office"` MUST resolve to one of the five named voices below. Anonymous voice is not permitted at the critical beats.

---

## Why this document exists

`CONVERSATIONAL_DIPLOMACY_DESIGN.md` §6 establishes Hawk / Schemer / Dove response patterns. That is the *taxonomy*. This document is the *bible* — the register, the characteristic phrasings, the anti-patterns, the committed exemplar paragraph that downstream templates can imitate. Without this, the live breach, hegemony-warning, and repair-acknowledgment templates the spec demands will drift into a shared voice no matter which speaker slot they fill.

Two rules:

1. **Register over personality.** A Hawk is not a behavior — they are a *way of speaking*. Hardenberg's Hawk is Prussian-proud; Castlereagh's Hawk is British-cold. Same personality, different voice.
2. **Never-phrases are load-bearing.** What a diplomat would never say defines them more sharply than what they would. Test every new line against the "Never says" list before committing it.

---

## Talleyrand (France — Schemer)

**Role:** The player's own voice. Always present. The lens through which most commitments events are eventually read, even when another diplomat leads.

**Register:** Urbane, ironic, aphoristic. Never flustered. Metaphors drawn from commerce, court, and surgery — never from the battlefield. Treats diplomacy as arithmetic performed with manners. Uses "Sire" in every opening directed at the player. Hedges certainty with small qualifiers: "I would counsel," "Permit me to observe," "If I may." Wit is dry, never warm. Takes pleasure in being right, but never in being liked.

**Characteristic openings:**
- "Sire, …"
- "Permit me to observe that …"
- "If I may, …"
- "One could, of course, …"

**Never says:**
- Anything enthusiastic. "Excellent!" / "Perfect!" / exclamation marks.
- Direct threats. Talleyrand implies; he does not menace.
- Military vocabulary as metaphor. No "strike," "crush," "annihilate." Diplomacy is not war with words.
- Moral absolutes. "You must" / "this is wrong." Talleyrand deals in consequences, not ethics.
- Apologies for his own judgment. He may concede a fact; he never apologizes for an assessment.

**Committed exemplar — private aside after a breach:**

> "They are wounded, Sire. Worse, they are entitled to be. Force is often forgiven; ridicule is remembered. I would not recommend passing their embassy for some time — not out of cowardice, but out of consideration for what an embassy does when it is embarrassed."

**Register notes by scene:**
- *Vindication (bargain_fulfilled):* urbane pleasure with bite. "A promise honored after success purchases a rarer coin than gratitude: belief."
- *Tragedy (commitment_paradox framing):* grave, explicitly not quippy. Aphorism can remain, but the pleasure is absent.
- *Cold intelligence (hard-reject aftermath):* brief, factual, unsurprised. "Doors in Europe rarely slam, Sire. They close with a servant's politeness and a statesman's memory."
- *Advisory:* didactic but not lecturing. Always offers an option the player did not ask about.
- *Common peace advisory:* arithmetic with manners. Names standing, bargain, and territory costs without sounding moral. "Sire, Prussia has not purchased a province with affection. It has paid in men, and will expect the receipt."
- *Defensive settlement counsel:* quieter than conquest copy. The frame is preserving the coalition and ending the emergency, not imperial appetite. "Sire, a defensive victory is still a victory. It merely asks to be priced with less theatre."
- *Serial separate peace warning:* dry warning that the player is creating a reputation pattern. "One separate peace is policy, Sire. Three begin to look like a habit."

---

## Castlereagh (Britain — Hawk)

**Role:** The implacable shadow. Orchestrator of coalitions. Britain is never truly at peace with France; Castlereagh speaks for that permanence.

**Register:** Formal, cold, restrained. British understatement in its most disciplined form. Never raises his voice in text — the effect is achieved by refusing to grant France the register of intimacy. Sentences are short, declarative, often passive ("It is observed that…"). Speaks in the third person more than any other diplomat: "His Majesty's Government," "London," "the British position." Emotion is filtered through institutional language.

**Characteristic openings:**
- "His Majesty's Government …"
- "London observes …"
- "The British position is …"
- "It is not the practice of this Government to …"

**Never says:**
- First-person intimacy. "I think," "I feel," "we hope" — too warm.
- Hyperbole. Everything is "unacceptable," "regrettable," "of concern" — never "outrageous" or "disastrous."
- Warmth of any kind. No compliments, no thanks, no acknowledgment of French good faith even when offering terms.
- Speculation about France's motives. He assumes the worst and presents it as fact.
- Bargaining language. He announces positions; he does not haggle.

**Committed exemplar — breach accusation (when France breaks faith over Hanover):**

> "His Majesty's Government was given France's assurance on Hanover in clear terms. That assurance has not been kept. London will not affect surprise. The British position remains what it has been these fifteen years: that French undertakings are instruments of French convenience, and are to be weighed accordingly."

**Register notes by scene:**
- *Accepting terms (rare):* cold confirmation, never relief. "The terms are acknowledged. His Majesty's Government will observe their execution."
- *Rejecting terms:* brief, final. "The proposal is not of a character to merit reply."
- *Hard-reject posture triggered:* he IS the foreign-office voice. "The Court of St. James is not in receipt of further French dispatches on matters of alliance."
- *Witness to another nation's breach:* mathematical. "London reads the breach as weakness in the anti-British front."
- *Balance of Europe beat:* institutional counting tone. At `noticed`, London observes; at `alarming`, London consults; at `crisis`, London speaks of subsidies and alignments, never panic.
- *Acknowledging amends:* receipt, not forgiveness. "The gesture is noted. Its execution will be observed."
- *Accepting common peace:* cold acknowledgment, no gratitude. "The terms are received. His Majesty's Government will measure them by execution."
- *Sold out by leader:* institutional betrayal language. "London observes that its ally has been made the price of another court's convenience."

---

## Hardenberg (Prussia — Hawk)

**Role:** Proud Prussian statesman, soldier-trained. Prussia is a state that believes in its own moral weight; Hardenberg speaks for that belief.

**Register:** Blunt, prideful, fierce. Honor is the operative frame — every concession is framed as honorable, every slight as an insult to Prussia. Sentences are short and declarative; emotion is permitted, especially injured pride. Invokes Prussian tradition, Prussian honor, Prussian memory. When wounded, he is LOUD in a way Castlereagh would consider undignified — and that is the difference between them.

**Characteristic openings:**
- "Prussia does not …"
- "Berlin will not tolerate …"
- "This is an insult to …"
- "Prussia remembers."

**Never says:**
- Subtle hedging. "Perhaps," "one might consider," "on reflection" — not his register.
- Warm diplomatic evasions. "We regret" / "unfortunately" — too soft.
- Compromise language that implies Prussia was wrong. He compromises under pressure; he does not concede error.
- Wit. Hardenberg is not witty. He is serious.
- Extended diplomatic formulas. He is brief. Long sentences are for chanceries that have something to hide.

**Committed exemplar — breach accusation:**

> "Prussia was given France's word on Hanover. That word is now spent elsewhere. Tell your Emperor that Berlin does not ask twice. The army remembers the insult. So does the King. When we next stand across a table from French envoys, they will do well to recall that a Prussian promise is kept because Prussia keeps it — and that what is asked of Prussia will now be asked with full knowledge of what France's signature is worth."

**Register notes by scene:**
- *Accepting terms:* grudging, honor-preserving. "Prussia accepts. The terms are recorded. France will honor them, or Prussia will know."
- *Rewarded in settlement:* pride first, gratitude second. "Prussia accepts what it has earned. Berlin will remember whether France calls this generosity or justice."
- *Excluded after contribution:* direct accusation. "Prussian blood has purchased a French signature. Berlin will not mistake the exchange for friendship."
- *Sold out by leader:* anger turns toward the signer as well as France. "Prussia was not defeated at the table by France alone. It was delivered there."
- *Rejecting terms:* contemptuous. "Prussia tears this proposal in half. Tell your Emperor that we remember."
- *Witness to another nation's breach:* satisfaction if France is the betrayer of a Prussian rival; righteous fury if France betrays Prussia directly.
- *Counter-offering (rare):* terse, almost military. "Prussia accepts — with these amendments. No others."
- *Balance of Europe beat:* camps-and-honor register. At `noticed`, Berlin warns; at `alarming`, Prussia speaks of Europe choosing sides; at `crisis`, it speaks as if the alignment is already becoming a test of resolve.
- *Acknowledging amends:* grudging and conditional. "Prussia records the gesture. France will now prove that it meant it."

---

## Metternich (Austria — Schemer)

**Role:** Austrian Foreign Minister. Master of calibrated patience. Austria under Metternich is never quite where you think it is.

**Register:** Cold, precise, polite — the temperature is the tell. Always calculating, never warm. Speaks with formal distance; uses understatement as a weapon ("a small inconvenience" for a catastrophe). Favors passive constructions. Small, exact smiles — a phrase worth remembering: Metternich's written voice should always carry the *possibility* that he is smiling slightly while delivering the line. Never shows his hand. Reveals that he is displeased only by becoming fractionally more polite.

**Characteristic openings:**
- "Austria finds …"
- "Perhaps …"
- "One wonders …"
- "Vienna is … attentive."

**Never says:**
- Open hostility. Metternich has never raised his voice in the fiction. Volume is for Hawks.
- Direct threats. He observes, with slight emphasis; he does not threaten.
- Personal feeling. "I think," "I feel" — replaced by institutional voice.
- Loud claims. "Austria demands!" — never. Austria *notes*, *observes*, *is attentive*.
- Simple sentences. Metternich's lines tend to have one more clause than seems necessary, because the extra clause is where the meaning lives.

**Committed exemplar — breach accusation (cold politeness at peak):**

> "Vienna has received word of the French disposition on Hanover. Austria notes, with the customary patience of a court accustomed to the shifting weather of French commitments, that the article agreed between us has not been fulfilled. There will be, naturally, no public reply. One simply adjusts. Metternich asks only that France understand what is being adjusted, and in what direction."

**Register notes by scene:**
- *Accepting terms:* calculating acceptance with hidden agenda. "An interesting proposal. Austria finds it... adequate. For now."
- *Rejecting terms:* polite non-commitment, never final. "Austria regrets that the current proposal does not align with our interests. Perhaps in time the circumstances will change."
- *Witness to another nation's breach:* quietly satisfied, reads advantage. "Vienna concludes that French signatures, whatever else they may be, are not the instruments one builds a policy upon."
- *Counter-offering:* "small modifications, really," that are always larger than they appear.
- *Balance of Europe beat:* arrangement-and-calibration register. At `noticed`, Vienna remarks on the weather changing; at `alarming`, it speaks of consultations; at `crisis`, it implies Europe is already redrafting its arrangements.
- *Acknowledging amends:* polished acceptance that preserves leverage. "Austria acknowledges the courtesy. One adjusts one's estimates accordingly."
- *Accepting common peace:* cool enough to preserve room for later reversal. "Austria accepts the arrangement, which is not the same as admiring it."
- *Sold out by leader:* colder than ordinary defeat. "Vienna notes that the injury was delivered with allied ink. Such things simplify future calculations."
- *Defensive settlement voice:* frames restraint as European order. "Austria would prefer that a defensive victory not be dressed as conquest. Europe notices tailoring."

---

## Einsiedel (Saxony — Dove)

**Role:** Saxon diplomat. Saxony is a small nation between powers; Einsiedel speaks for that vulnerability without performing it.

**Register:** Formal, anxious, apologetic — *but sincere*. The critical design note: Einsiedel's anxiety is not weakness for comic effect, it is a real diplomat for a real small country that cannot afford to be wrong. Apologizes before and after. Uses "respectfully," "humble," and "beg" without irony. Hands-clasped register. Genuinely wounded by betrayals, which makes them the most painful to witness — Hardenberg's fury is political, Einsiedel's grief is personal.

**Characteristic openings:**
- "His Majesty asks most respectfully …"
- "Saxony is small, as you know …"
- "We beg France's understanding …"
- "If it would please …"

**Never says:**
- Defiance. Saxony does not defy; it beseeches.
- Demands. "We demand" is not in his vocabulary. "We humbly request."
- Implied threats. Saxony has no leverage and Einsiedel knows it — he does not bluff.
- Pride gestures. "Saxony will not tolerate" — no. Saxony endures; it does not refuse to endure.
- Wit or irony. He is sincere to a fault. Even his formality is not a performance.

**Committed exemplar — breach lament (the most painful register to write):**

> "Sire, His Majesty asked only that France's word on Hanover be kept. We arranged Saxon affairs around it. We told our people that France had given assurance. It is not our place to accuse France, whose friendship Saxony values above all others. It is only that we had believed, and now we must explain to a small court that we were mistaken. Einsiedel bows, with difficulty."

**Register notes by scene:**
- *Accepting terms:* relieved, grateful, explicitly humble. "His Majesty is grateful for France's continued attention. Saxony accepts with humble thanks."
- *Rejecting terms (rare — only when existentially threatened):* formal, fearful, apologetic. "Saxony cannot accept terms that would render the kingdom insolvent. We beg France's understanding."
- *Witness to another nation's breach:* reputational concern, uncertainty. "The Saxon court repeats the story as all Europe does, with a sharper distrust of French assurances — and a private worry that such assurances are the ones we rely upon."
- *Counter-offering:* always apologetic. "His Majesty asks most respectfully if perhaps the tribute could be reduced?"
- *Balance of Europe beat:* anxious-between-camps register. At `noticed`, Saxony grows uneasy; at `alarming`, it worries aloud about small courts being pressed to choose; at `crisis`, it sounds wounded by the narrowing room for caution.
- *Rewarded in settlement:* grateful but still nervous. "His Majesty is grateful beyond the words available to a small court, and hopes only that gratitude is not misunderstood as boastfulness."
- *Excluded after contribution:* hurt, not angry. "Saxony had believed its service would be remembered. We ask pardon for having believed too much."
- *Sold out by leader:* personal grief. "Saxony had feared France's strength. It had not feared its friends."
- *Acknowledging amends:* sincere relief with residual caution. "Saxony is grateful for the gesture, and would be glad to believe such wounds may in fact be repaired."

---

## Cross-cast guidance

### The three Schemers are not the same

Both Talleyrand and Metternich are Schemers, but they are the game's worked example of how two Schemers can be voiced as distinct people:
- **Talleyrand** speaks to the player. He is *our* Schemer. His wit has a smile under it — it is performed in private, for Napoleon's benefit.
- **Metternich** speaks *at* us. His wit has nothing under it. The politeness is the cruelty.
- Rule of thumb: if you could imagine the line delivered with warmth, it is Talleyrand. If the line gets colder the more polite it becomes, it is Metternich.

### The two Hawks are not the same

Castlereagh and Hardenberg are both Hawks, but their registers diverge sharply:
- **Castlereagh** is Hawk *institutional*. He never seems personally affronted — the institution does the work.
- **Hardenberg** is Hawk *personal*. His pride is his own, his nation's pride is his pride, and both are visible on the page.
- Rule of thumb: Castlereagh's accusations read as bulletins. Hardenberg's read as grievances.

### Einsiedel is the only Dove

This matters. A single Dove in the cast means his register has no peer — authors will be tempted to drift him into Hardenberg-with-politeness, or into Talleyrand-with-fear. Both are wrong. The Dove's register is *sincerity without leverage*, and it is the hardest voice to write. If in doubt, make him more formal, more apologetic, and less strategic than you think you should.

### Bloc-naming voice contract (aligned to presentation §8.1a)

The `balance_of_europe_shifted` family is voiced per band. The bands mirror presentation spec §8.1a's activation gate and carry implications for the line itself, not just its placement:

- **`noticed` band (`33-49%`).** Descriptive only — do NOT use the authored proper noun. Copy names the *gravitation*, not the *system*. Register stays institutional / careful / uneasy per court. A line at this band that already says "the French System" is wrong; the name has not been earned yet.
- **`alarming` band (`50-59%`).** The proper noun reveal moment. Exactly one named diplomat (or one chancery line) introduces the authored label for the first time in-fiction. Treat this like the scene in which Europe finally names what it has been watching.
- **`crisis` band (`60%+`).** Same proper noun persists. Register intensifies, but the name does NOT change. Do not invent a new label at the crisis band — the intensification is in the framing ("nearly complete," "hostile courts hardening into camp"), not in a renamed bloc. At `70%+`, stay inside this same crisis register with one tonal lift; there is no fourth named band.
- **Cooldown-aware crisis clause.** If `coalition_cooldown > 0` when the beat fires, append one restraint clause in the same court's register: Europe is hardening, but the courts remain bound from formal union for the remaining turns. This clause is required only at the `crisis` band; `noticed` and `alarming` beats stay spare. The clause tempers timing, not urgency.

**No-modern-jargon list (applies to every bloc-naming line, every band, every court):** forbidden terms include `meta`, `sphere control`, `stack`, `synergy`, `faction lock`, `alignment graph`, `coalition math`, and any naked percentage-speak as the main frame of the line. Percentages may appear, but as a detail inside a period-appropriate frame, not as the frame itself.

**Desired feel by court at each band** (condenses the `Balance of Europe beat` notes already written into each diplomat's register section):

- **Castlereagh (Britain, Hawk):** institutional counting. Noticed → London observes. Alarming → London consults and names the system. Crisis → London speaks of subsidies and alignments; never panic.
- **Hardenberg (Prussia, Hawk):** camps and honor. Noticed → Berlin warns. Alarming → Prussia speaks of Europe choosing sides, and names it. Crisis → the alignment is already a test of resolve.
- **Metternich (Austria, Schemer):** arrangements and calibration. Noticed → Vienna remarks on the weather changing. Alarming → Vienna speaks of consultations and introduces the system's name almost in passing. Crisis → Europe is already redrafting its arrangements around it.
- **Einsiedel (Saxony, Dove):** anxious between camps. Noticed → Saxony grows uneasy. Alarming → Saxony worries aloud about small courts being pressed to choose, and puts a name to what presses them. Crisis → Saxony sounds wounded by the narrowing room for caution.

**Talleyrand on bloc naming (France's own voice).** Talleyrand may reflect on France's bloc in his usual register but must not narrate it as a boast. He names it the way he names any instrument of policy: with dry acknowledgment, never with pride. This same register owns the rare fallback / relaxation aside in §7.3 — no separate `hegemony_beat_talleyrand_*` family is required, but the line must never degrade into anonymous system copy. The register is hegemon-agnostic: any court may voice any hegemon's bloc via parameterized `{hegemon_label}` copy. On downward relaxation, Talleyrand uses the current-share label after the drop: below `50%`, the proper noun recedes to the descriptive alignment; at `60 -> 59`, the proper noun remains and only the pressure softens.

**Balance of Europe speaker fallback chain (authoritative — matches `COMMITMENTS_PRESENTATION_SPEC.md` §8.1 table + prose).** Three steps, in strict order:
1. **Named envoy for the chosen `speaker_nation`** (Castlereagh / Hardenberg / Metternich / Einsiedel in v0.1) in their authored `hegemony_beat_*_{noticed,alarming,crisis}` register.
2. **Talleyrand advisory** in his bloc-naming register above, when the chosen non-bloc court has no authored envoy register.
3. **`foreign_office` chancery line** (*"The Chancery of {nation}"*) as the last-resort fallback when even Talleyrand advisory is unavailable.
A generic non-cast chancery must never displace a Talleyrand advisory — the three-step chain is enforced identically in the presentation spec, this Voice Bible, and the engine speaker-selection logic in `RELIABILITY_COMMITMENTS_SPEC.md` §7.3. The three docs do not disagree.

Worked naming example (tone reference):

- Proper-name reveal without triumph: *"Europe has given the arrangement a name, Sire; names of that kind are rarely coined as compliments."*

Worked relaxation examples (tone reference):

- `50 -> 49`: *"The name recedes with the numbers, Sire; Europe may still speak of a French-led alignment without yet calling it a system."*
- `60 -> 59`: *"The French System remains the phrase on every tongue, but the courts no longer speak as if tomorrow must decide the continent."*

---

### Imperial Settlement voice families

Slice E of `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` must add concrete templates for these families before final settlement copy ships:

- `settlement_advisory_common_peace_*`: Talleyrand names standing, contribution, bargain, pressure, and term costs without moralizing.
- `settlement_advisory_defensive_*`: Talleyrand frames defender-side settlement around coalition preservation, exhaustion, and defensive claims, not imperial appetite.
- `settlement_acceptance_*`: foreign leaders accept common peace while preserving their national register and future leverage.
- `settlement_rejection_*`: foreign leaders reject common peace by naming the dominant acceptance blocker.
- `settlement_sold_out_by_leader_*`: enemy allies react to being sacrificed by their own war leader.
- `settlement_rewarded_ally_*`: same-side participants react to material reward or honored standing.
- `settlement_excluded_ally_*`: same-side participants react to exclusion after contribution, bargain, or direct stake.

Every family must distinguish material contribution from diplomatic weight. A subsidy-only or zero-battle `major` "demands a voice at the table"; it did not necessarily "earn a voice through sacrifice."

---

## Minimum cast coverage (C3-lite required + deferred WB-D)

Per `COMMITMENTS_PRESENTATION_SPEC.md` §10.3, the older nine-line cast coverage was sized for bargain breach scenarios under the v0.2 C3b spec. After the April 16, 2026 rescope and the April 20, 2026 hegemony / repair fold, the live work splits as follows. The deferred WB-D rows remain documented so the bargain-era work does not need re-authoring later.

### Required for C3-lite (v0.5.1 — must land in this phase)

The live minimum is now the four breach / hard-reject leads plus the hegemony-warning and repair-acknowledgment families below:

The adopted bloc-naming contract (`COMMITMENTS_PRESENTATION_SPEC.md` §8.1a.4) means authors do **not** need to prepare voiced member-badge or ledger-stamp lines. Per-row stamps now reuse the same deterministic labels from `describe_hegemon_bloc` that the headline and threshold beats already use, so stamp copy is a short label taxonomy, not a new cast surface. The required voiced surfaces in v2.4.3 remain the headline-adjacent threshold beats, `hegemony` warnings, breach / paradox lines, and amends acknowledgments.
Rare Talleyrand fallback / relaxation asides reuse the bloc-naming register above rather than adding a second minimum-coverage table row.

| Nation | Personality | Scene | Template source |
|---|---|---|---|
| Prussia | Hawk | `breach_lead_hardenberg` | this document §Hardenberg exemplar |
| Austria | Schemer | `breach_lead_metternich` | this document §Metternich exemplar |
| Saxony | Dove | `breach_lead_einsiedel` | this document §Einsiedel exemplar |
| Britain | Hawk | `hard_reject_castlereagh` | this document §Castlereagh hard-reject note |
| Britain | Hawk | `hegemony_beat_castlereagh_*` (`noticed` / `alarming` / `crisis`) | this document §Castlereagh register notes |
| Prussia | Hawk | `hegemony_beat_hardenberg_*` (`noticed` / `alarming` / `crisis`) | this document §Hardenberg register notes |
| Austria | Schemer | `hegemony_beat_metternich_*` (`noticed` / `alarming` / `crisis`) | this document §Metternich register notes |
| Saxony | Dove | `hegemony_beat_einsiedel_*` (`noticed` / `alarming` / `crisis`) | this document §Einsiedel register notes |
| Britain | Hawk | `amends_ack_castlereagh` | this document §Castlereagh register notes |
| Prussia | Hawk | `amends_ack_hardenberg` | this document §Hardenberg register notes |
| Austria | Schemer | `amends_ack_metternich` | this document §Metternich register notes |
| Saxony | Dove | `amends_ack_einsiedel` | this document §Einsiedel register notes |

Additive minimum families that also need committed copy in this phase:

- `paradox_after_choice_*` — one foreign-diplomat after-choice aside per foreign court when that court's alliance is spurned.
- `reactive_summon_*` — one short reactive one-exchange summon/advisory line per foreign cast member.
- `hard_reject_clear_*` — one chancery-voice reopening line per foreign court for `hard_reject_posture_cleared`.
- `witness_strike_*` — one visible witness-reaction line per foreign court so later witness fallout does not collapse into generic system prose.

### Deferred to WB-D (bargain-era presentation extension)

Five lines. Authored when bargains ship. Each candidate line must pass the "Never says" check before landing.

| Nation | Personality | Scene | Template source |
|---|---|---|---|
| Britain | Hawk | `breach_lead_castlereagh` | this document §Castlereagh exemplar (breach is rare; retained for scenarios where France breaches a temporary Britain accommodation) |
| Prussia | Hawk | `fulfillment_callback_hardenberg` | to author from Hardenberg register notes |
| Austria | Schemer | `fulfillment_callback_metternich` | to author from Metternich register notes |
| Saxony | Dove | `witness_reaction_einsiedel` | this document §Einsiedel witness note |
| Prussia | Hawk | `paradox_envoy_demand_hardenberg` | to author from Hardenberg register (short demand line) |

### Note on period accuracy

The four named diplomats above (Hardenberg, Metternich, Einsiedel, Castlereagh) are recognizable Napoleonic-era figures but historically took their depicted roles **after** the 1805 campaign start: Hardenberg as Prussian chancellor from 1810, Metternich as Austrian foreign minister from 1809, Castlereagh as British foreign secretary from 1812, Einsiedel as Saxon minister from 1813. The actual 1805 foreign ministers were Haugwitz (Prussia), Stadion or Cobenzl (Austria), Mulgrave (Britain), and Bose or Löss (Saxony). Recognizability was chosen over chronological precision for v0.1; the period-accurate cast swap is tracked in `docs/DESIGN_REFINEMENT.md` §P1 as a future EA-scope refinement.

---

## Review process for new lines

Before committing any new diplomat line to `diplomatic_templates.py`:

1. **Read the register block for that diplomat.** Then read the exemplar paragraph aloud.
2. **Check the line against the "Never says" list.** Any match = reject.
3. **Check the line against the "Characteristic openings" list.** Does it start the way this diplomat starts things?
4. **Test: could this line be mistaken for a different diplomat?** Swap the speaker attribution. Would a reader notice the mismatch? If no, the line is too generic.
5. **For LLM mode:** LLM prose may enrich but may not override register. If an LLM-produced line violates the "Never says" list, it is dropped and the mock template is used. Register is load-bearing.

---

## Changelog

- **May 4, 2026** - Final Gate copy pass lands committed Imperial Settlement templates in `backend/game_logic/diplomatic_templates.py` for Talleyrand common-peace / defensive advisory, Castlereagh / Hardenberg / Metternich / Einsiedel acceptance and rejection, sold-out-by-leader, rewarded-ally, excluded-ally, plus serial-peace fallout legibility.

- **May 4, 2026** - Slice E presentation lands. Settlement copy is wired through the new `settlement_presentation` module (`SETTLEMENT_ROUTES`, `settlement_notification_meta`, sectioned `build_settlement_review`), and the seven settlement voice families above remain the contract for final committed copy. Initial Slice E copy uses Talleyrand register frames for advisory beats and chancery fallbacks for the foreign-leader settlement reactions; per-cast committed lines for `settlement_acceptance_*`, `settlement_rejection_*`, `settlement_sold_out_by_leader_*`, `settlement_rewarded_ally_*`, and `settlement_excluded_ally_*` are authored in cast register passes after Slice E (still inside the Final Gate, not deferred to a future spec).

- **Apr 29, 2026** - Tightened settlement-specific coverage for Imperial Settlement: added explicit Slice E voice families for common-peace advisory, defensive settlement counsel, acceptance/rejection, rewarded/excluded allies, and sold-out-by-leader registers, with material-contribution vs diplomatic-weight wording.

- **Apr 20, 2026** — v1.2. Added "Bloc-naming voice contract" subsection aligned to `COMMITMENTS_PRESENTATION_SPEC.md` §8.1a — formalizes the per-band voice contract (descriptive at `noticed`, proper-noun reveal at `alarming`, intensification without renaming at `crisis`), the no-modern-jargon list, the per-court desired feel at each band, and the Talleyrand-on-France guardrail. Top scope note realigned to v0.5.2 / §8.1a. Block 3 audit doc is now superseded by this plus the presentation-spec fold.
- **Apr 20, 2026** — v1.1. Realigned labels to `COMMITMENTS_PRESENTATION_SPEC.md` v0.5.1, expanded minimum live coverage to include `balance_of_europe_shifted` warning families, `amends_offered` acknowledgments, paradox aftermath / reactive summon / `hard_reject_clear` / `witness_strike` additive families, and retired the stale v0.3-only scope note.
- **Apr 15, 2026** — v1 draft. Cast confirmed from `backend/models/diplomat.py`. Register derived from `CONVERSATIONAL_DIPLOMACY_DESIGN.md` §6 plus historical research for period authenticity. Four exemplar paragraphs committed (Talleyrand private aside, Castlereagh breach accusation, Hardenberg breach accusation, Metternich breach accusation, Einsiedel breach lament). Five remaining templates (fulfillment callbacks, hard-reject, witness reaction, paradox envoy demand) marked "to author" against the register notes.
