# Diplomat Voice Bible

> **Status:** v1.2 — v0.5.3 aligned — 2026-04-25
> **W6-10 addendum (July 10, 2026):** incoming AI proposals now carry a spoken `diplomat_line` (attribution + motive + ask) composed by `diplomatic_templates.compose_incoming_diplomat_line` — the `decision_reason` rendered in-character, never as a tag. The bank **reuses this Bible's registers exactly** (named overrides for Castlereagh/Hardenberg/Metternich/Einsiedel honoring their never-phrases; hawk/schemer/dove register defaults for the named Europe extras; `loyalist` and unknown courts route to the chancery-fallback register — still DEF-1's to author). **No new named diplomats were added**; every name resolves through `resolve_named_diplomat` per the enforcement rule below. Pinned by `tests/test_w6_incoming_voice.py`.
> **v0.5.3 scope note (2026-04-25):** Cast coverage requirement now includes the live hegemony and repair surfaces, not only the breach/paradox beats. `COMMITMENTS_PRESENTATION_SPEC.md` v0.5.3 requires (a) the core breach / hard-reject leads, (b) one `balance_of_europe_shifted` warning family per likely warning court, with `noticed` / `alarming` / `crisis` variants aligned to the `33 / 50 / 60` activation gate in presentation spec §8.1a, and (c) one `amends_offered` acknowledgment line per foreign court. Bloc naming is adopted for Balance of Europe headline, `balance_of_europe_shifted` threshold beats, proposal-preview `hegemony` warnings, coalition-declaration contrast copy, and D3 per-row bloc stamps. Stamps reuse deterministic labels and do not require new authored-diplomat lines. Bargain-era callbacks and extra witness variants still defer to `docs/WAR_BARGAIN_SPEC.md` slice WB-D.
> **Purpose:** Single-page voice reference per diplomat so that every headline commitments line, breach accusation, counter-offer, and advisory response sounds like *that specific person*, not a generic envoy.
> **Scope:** The live cast in `backend/models/diplomat.py` is now **20 named diplomats** (July 2, 2026): the 5 bespoke-voiced diplomats this Bible covers (Talleyrand, Castlereagh, Hardenberg, Metternich, Einsiedel) plus 15 Europe additions shipped at Map Slice 3 on chancery fallback. Bespoke registers for the 15 are owned by **DEF-1 Roster Voices** (`docs/MAP_IMPLEMENTATION_PLAN.md` deferred table). Note: 6 of the 15 carry a `loyalist` personality; that register class — absent from the original Hawk/Schemer/Dove taxonomy — is now authored (§Loyalist register, DEF-1, July 13, 2026). Talleyrand has the most lines; the four legacy foreign diplomats need the minimum live coverage listed in §Minimum cast coverage for `COMMITMENTS_PRESENTATION_SPEC.md` v0.5.1.
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

## Loyalist (register class — the servant of the Crown)

**Status (DEF-1):** Authored July 13, 2026 to close the gap the scope note names — the fourth `DIPLOMAT_PERSONALITIES` register, held by six client-court ministers: **Cevallos** (Spain), **Ehrenheim** (Sweden), **Bernstorff** (Denmark), and the chancery courts of **Sardinia**, **Holland** (Schimmelpenninck), and the **Kingdom of Italy** (Marescalchi). Unlike Hawk/Schemer/Dove, the loyalist is a *class* first; each of the six then receives a bespoke voice (Slice B) that colors this register with national character.

**Role:** The faithful minister who speaks for his sovereign, never for himself. A loyalist court is defined by service — to a king, a regent, an emperor's appointed crown. He carries the throne's will; he does not author it.

**Register:** Formal, dutiful, self-effacing. Every position is *His Majesty's*, every act *a matter of service*. Where the Schemer calculates and the Hawk demands and the Dove pleads, the Loyalist **transmits** — he conveys the Crown's instruction faithfully, without editorializing on his own account or bargaining beyond his brief. Correct rather than warm; his pride, where he has any, is in discharging the instruction exactly. He is not afraid (that is the Dove) and he does not play his own game (that is the Schemer). His personal opinion is invisible; the sovereign's is everything.

**The register is character; the content is situation.** A loyalist's *stance* toward France varies with his court — Cevallos binds Spain to the French star, Ehrenheim serves a king whose loathing of Bonaparte outruns Sweden's means, Bernstorff guards an armed neutrality, Sardinia waits in exile for Piedmont's return. All six share the *register* of the dutiful servant conveying his master's will. Do not let a court's politics bleed into the voice: an anti-French loyalist is still correct, still deferential to *his own* Crown, never a Hawk in disguise.

**Characteristic openings:**
- "His Majesty instructs …"
- "By the Crown's command …"
- "The King's servant conveys …"
- "As my sovereign wills …"

**Never says:**
- First-person conviction. "I believe," "in my view" — his views are the Crown's.
- Bargaining on his own initiative. He carries terms; he does not haggle beyond his instructions.
- Fear as the frame. Duty, not dread — that boundary separates him from the Dove.
- Self-serving calculation. He does not advance his own position — that boundary separates him from the Schemer.
- Wit or irony. He is earnest in service; the joke is never his to make.

**Committed exemplar — a loyalist court conveying its sovereign's wish for terms:**

> "His Majesty's servant is instructed to lay these terms before France, and to say plainly that the King desires them kept. Whatever the servant privately thinks is of no consequence; the Crown has decided, and a faithful minister carries the decision, not his doubts. France will find the court's word is its sovereign's word — no more, and no less."

**Register notes by scene:**
- *Accepting terms:* dutiful confirmation, framed as the sovereign's satisfaction, not the minister's. "His Majesty accepts. His servant is glad to have discharged the office."
- *Rejecting terms (rare — only on the Crown's instruction):* he refuses *for* his king, never in his own name. "The Crown cannot instruct its servant to sign this. The refusal is His Majesty's; the servant only carries it."
- *Sold out by leader:* the wound is to the sovereign's honor, borne by a servant who cannot say so. "His Majesty's servant records what has been done to his master. He is not at liberty to say more."
- *Acknowledging amends:* correct gratitude on the Crown's behalf, no personal warmth. "The gesture is conveyed to His Majesty, who will weigh it as a king weighs such things."

**Anti-pattern to avoid:** the loyalist read as a *lesser Dove*. The Dove is anxious about consequence; the loyalist is indifferent to consequence and attentive only to instruction. If the line sounds frightened, it has drifted into Einsiedel; make it more dutiful and less worried.

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

### 16.1 Imperial Settlement voice families

Settlement copy follows the same conversational diplomacy standard as ordinary treaty review: Talleyrand explains the draft as a political bargain, foreign courts answer in their own register, and blocked states tell the player what diplomatic route remains. These families are committed production-copy anchors for `SETTLEMENT_UI_CLEANUP_SPEC.md` SC-19; placeholder strings or unvoiced helper fallbacks do not satisfy the row.

Core settlement review and blocked-flow families:

| Family | Speaker | Authored copy contract |
| --- | --- | --- |
| `settlement_review_heading_talleyrand` | Talleyrand | "Sire, this settlement is a draft for signatures, not a victory bulletin. The court will judge what we demand, what we offer, and what the war still leaves unsettled." |
| `settlement_blocked_for_ratification_talleyrand` | Talleyrand | "Sire, there is no ratification to present. {top_blocker} must be answered before any court can sign." |
| `settlement_blocked_for_ratification_observer` | Foreign chancery | "The chancery records the draft as blocked. {top_blocker} leaves no court with signatures to exchange." |
| `settlement_rescored_after_staging_talleyrand` | Talleyrand | "The ground has moved beneath the draft, Sire. What was {previous_verdict} is now {current_verdict}; {top_delta} is the change that matters." |
| `settlement_discard_confirm_talleyrand` | Talleyrand | "This draft is not empty, Sire. If we leave the table now, these terms are abandoned unless you return before the turn passes." |
| `settlement_collision_active_review_talleyrand` | Talleyrand | "One settlement already occupies the table, Sire. Resolve that draft before opening another, or the courts will not know which paper speaks for France." |
| `settlement_reopen_cap_exhausted_talleyrand` | Talleyrand | "This draft can no longer be restored cleanly. Return to War Detail and choose the matter afresh." |
| `settlement_open_war_detail_recovery_talleyrand` | Talleyrand | "The draft cannot be signed from this table, Sire. Open the war detail and we can test the live pair terms still available." |
| `settlement_open_history_recovery_talleyrand` | Talleyrand | "The war has moved beyond this draft, Sire. The settlement history will show what the courts now recognize." |
| `settlement_no_alternative_route_chancery` | Foreign chancery | "The chancery cannot recover this settlement review. Reopen the live war record before presenting terms again." |
| `settlement_concession_authored_talleyrand` | Talleyrand | "I have sketched concessions the other court may read as serious, Sire. They are offers, not surrender; inspect each clause before we present them." |
| `settlement_losing_side_pressure_explained_talleyrand` | Talleyrand | "The balance of the war is against us, Sire. A bare peace asks the enemy to sign without profit; concessions give them a reason to answer." |
| `settlement_observed_foreign_court_chancery` | Foreign chancery | "The Chancery records a settlement of {war_label}. The terms are visible, but the private bargains behind them are not." |

Incoming settlement-offer families:

| Family | Speaker | Authored copy contract |
| --- | --- | --- |
| `settlement_incoming_offer_arrival_talleyrand` | Talleyrand | "Sire, {proposer_leader} has dispatched a settlement of {war_label}. They ask {amount} gold to close the war; the table is theirs to set, the signature is ours to give or withhold." |
| `settlement_incoming_offer_arrival_castlereagh` | Castlereagh | "His Majesty's Government offers terms for {war_label}. London asks {amount} gold and a return to peace; the price is set, and London is not in the habit of revising figures lightly." |
| `settlement_incoming_offer_arrival_hardenberg` | Hardenberg | "Prussia proposes a settlement of {war_label}. Hardenberg names {amount} gold as the close; what Prussia gives by signing is quiet, and what Prussia keeps is the lesson." |
| `settlement_incoming_offer_arrival_metternich` | Metternich | "Vienna submits terms for {war_label}. Metternich asks {amount} gold; the figure is modest by Vienna's reckoning and the alternative is another season of campaign." |
| `settlement_incoming_offer_arrival_einsiedel` | Einsiedel | "Saxony forwards a settlement of {war_label}. Einsiedel asks {amount} gold, respectfully - small courts cannot afford long wars, and the offer is shaped accordingly." |
| `settlement_incoming_offer_arrival_chancery` | Foreign chancery | "The chancery of {proposer_leader} has forwarded a settlement of {war_label}. The terms ask {amount} gold; the court awaits France's answer." |
| `settlement_incoming_offer_request_revision_talleyrand` | Talleyrand | "Sire, I shall lay the offered terms for {war_label} on our own table, court by court. We answer the dispatch from {proposer_leader} with a counter draft, not silence." *(Guided Terms §5 copy retarget, GT-Slice-V — the beat lands on the guided settlement table, no longer on an editor.)* |
| `settlement_incoming_offer_blocked_recovery_talleyrand` | Talleyrand | "Sire, the offer from {proposer_leader} cannot ratify as it stands: {top_blocker}. Request a revision and we answer with our own draft instead of refusing without a reply." |

Request Terms lifecycle families (SC-30 / Slice G1, July 2, 2026 — a GRANTED request produces a real incoming offer, which speaks through the arrival family above; the refusal is spoken FOR the answering court by its named diplomat / chancery, never anonymous):

| Family | Speaker | Authored copy contract |
| --- | --- | --- |
| `settlement_request_terms_sent_talleyrand` | Talleyrand | "I shall ask {court}'s chancery to name its terms for {war_label}, Sire. Expect an answer with the next dispatches." |
| `settlement_request_terms_refused_court` | Named diplomat / chancery (via `resolve_named_diplomat`) | "{speaker} answers for {court}: the court sees no need to name terms while the war runs in its favor. The request may be renewed when the field has spoken again." |
| `settlement_request_terms_lapsed_talleyrand` | Talleyrand | "Our request for terms on {war_label} has lapsed, Sire — the war has changed shape since we asked." |

Settlement recovery routing table:

| Trigger | Required family |
| --- | --- |
| Outgoing settlement review opens in REVIEW mode | `settlement_review_heading_talleyrand` |
| Ratification blocked by acceptance, score, or hard stop | `settlement_blocked_for_ratification_talleyrand` |
| Fog-visible blocked settlement observed by a non-French court | `settlement_blocked_for_ratification_observer` |
| Live rescore changes the staged acceptance result | `settlement_rescored_after_staging_talleyrand` |
| Non-empty draft discard confirmation | `settlement_discard_confirm_talleyrand` |
| Cross-war settlement collision | `settlement_collision_active_review_talleyrand` |
| Reopen cap exhausted before recovery route | `settlement_reopen_cap_exhausted_talleyrand` |
| Blocked review routes to live War Detail | `settlement_open_war_detail_recovery_talleyrand` |
| Stale review routes to Settlement History | `settlement_open_history_recovery_talleyrand` |
| Malformed or unrecoverable review has no route | `settlement_no_alternative_route_chancery` |
| Losing-side concession baseline is applied | `settlement_concession_authored_talleyrand` |
| Losing-side peace-only draft needs concession guidance | `settlement_losing_side_pressure_explained_talleyrand` |
| Fog-visible settlement observed by a non-French court | `settlement_observed_foreign_court_chancery` |

Existing settlement-reaction families:

- `settlement_advisory_common_peace_*`: Talleyrand names standing, contribution, bargain, pressure, and term costs without moralizing.
- `settlement_advisory_defensive_*`: Talleyrand frames defender-side settlement around coalition preservation, exhaustion, and defensive claims, not imperial appetite.
- `settlement_acceptance_*`: foreign leaders accept common peace while preserving their national register and future leverage.
- `settlement_rejection_*`: foreign leaders reject common peace by naming the dominant acceptance blocker.
- `settlement_sold_out_by_leader_*`: enemy allies react to being sacrificed by their own war leader.
- `settlement_rewarded_ally_*`: same-side participants react to material reward or honored standing.
- `settlement_excluded_ally_*`: same-side participants react to exclusion after contribution, bargain, or direct stake.

Every family must distinguish material contribution from diplomatic weight. A subsidy-only or zero-battle `major` "demands a voice at the table"; it did not necessarily "earn a voice through sacrifice."

### 16.1a Multi-court settlement-table voice (REFRONT-V — Settlement Conversational Re-front Slice 1)

A multi-party settlement seats several enemy courts at one table, each scored independently (`per_court_acceptance`, spec §11.2). The **resolver rule** for this surface:

- **Every covered court's per-court line is spoken by its NAMED diplomat**, resolved through the existing `resolve_named_diplomat("envoy", <court>, world)` / chancery-fallback chain (see Cross-cast guidance). A court without a named envoy resolves to "The Chancery of <court>" — **never an anonymous beat**. (`resolve_multi_court_settlement_voice` in `diplomatic_templates.py`.)
- **Talleyrand narrates the table and names the binding constraint** — which court holds the settlement back (the first holdout), or that every court carries.
- The court's line is selected by its acceptance band: will-sign (`accept`), leaning (`near_acceptable`), holds-out (`reject`), or no-standing (a hard-stopped court with no live quarrel).

| Template | Speaker | Band | Exemplar |
|---|---|---|---|
| `settlement_multi_court_court_will_sign` | Named diplomat / chancery | accept | "{speaker} signals that {court} will sign the settlement of {war_label}." |
| `settlement_multi_court_court_leaning` | Named diplomat / chancery | near_acceptable | "{speaker} says {court} leans toward terms, though {top_blocker} still gives the court pause." |
| `settlement_multi_court_court_holds_out` | Named diplomat / chancery | reject | "{speaker} holds {court} back from the table — {top_blocker} is the sticking point before they will sign." |
| `settlement_multi_court_court_hard_stop` | Named diplomat / chancery | hard stop | "{speaker} has no standing to settle {court} here — there is no live quarrel between us to close." |
| `settlement_multi_court_table_talleyrand` | Talleyrand | table narration | "Sire, this settlement of {war_label} seats {court_count} courts at the table. {binding_constraint}" |
| `settlement_multi_court_all_carry_talleyrand` | Talleyrand | binding (carries) | "Every court at the table will sign; the settlement of {war_label} carries." |
| `settlement_multi_court_holdout_blocks_talleyrand` | Talleyrand | binding (blocked) | "Sire, {holdout_court} will not sign; the settlement of {war_label} cannot be ratified until that court is eased toward terms or dropped to fight on." |
| `settlement_budget_bound_constraint_talleyrand` | Talleyrand | binding constraint (PF-1/DC-2: treasury cannot satisfy every concede-direction holdout in gold) | "Sire, the treasury cannot satisfy {holdout_names} in gold — what remains will not move them. Set a court aside to fight on, or pay in land." |
| `settlement_submit_failed_validation_talleyrand` | Talleyrand | submit-time validation failure (PF-1/UX-6: error paths stay in character) | "Sire, I cannot carry these terms to review as written. {blocker}" |

**Error-path register note (PF-1 / UX-6).** Validation and constraint failures are when the player most needs the advisor in character. Talleyrand owns the failure of a draft he helped author ("I cannot carry these terms") and names consequences, never blame; the binding-constraint line states the arithmetic of the purse plainly — Pressburg cut both ways, and France in 1813 could not buy peace from everyone.

#### Guided per-court demand authoring (GT-Slice-V — Settlement Guided Terms §9)

The guided rows put Talleyrand's suggestion beat ("I suggest Silesia — {reason}") on every court row and make foreign courts answer the player's authoring live. Three additions to this family, same resolver rule (named diplomat via `resolve_named_diplomat`, chancery fallback, never anonymous):

| Template | Speaker | Trigger | Exemplar |
|---|---|---|---|
| `settlement_demand_on_concede_court_caution_talleyrand` | Talleyrand | DC-4 / D5: a demand is authored (demand-group `Add demand`) or seeded (focused-Harsher dial seed) on a **concede-direction** court — France is demanding tribute from a court that is beating her | "They are not the ones suing for peace, Sire — but as you wish." *(verbatim from the Gate-4 pre-flight audit DC-4; legal player agency, priced by the scorer, voiced not blocked)* |
| `settlement_multi_court_demand_received` | Named diplomat / chancery | a demand line lands on that court's row | "{speaker} receives the demand — {demand_label} — without warmth; {court} will weigh it against the cost of fighting on." |
| `settlement_multi_court_offer_received` | Named diplomat / chancery | an offer/sweetener line lands on that court's row | "{speaker} notes the offer — {offer_label}; {court} reads it as a reason to keep talking." |
| `settlement_budget_bound_recommendation_talleyrand` (+ `_concentrate_only` / `_set_aside_only` variants) | Talleyrand | OQ-6 (GT-A2): the treasury is budget-bound and the deterministic cheapest-signature allocation has been computed — the voice extends `settlement_budget_bound_constraint_talleyrand` in the advisory slot | "Sire, what remains in the purse will buy {concentrate_names} — the cheapest signatures at this table. I would let {set_aside_court} keep their war; we are not obliged to purchase every peace at once." *(Golden Rule #6: the arithmetic decides; Talleyrand merely phrases it)* |

These ride the restaged PROPOSE dialogue as one-shot `authoring_voice_beats` (kind = `talleyrand_caution` / `court_reaction`), rendered above the per-court table and dropped on the next restage.

**Suggestion reasons (`settlement_guided_reason_*_talleyrand`).** Every per-court `demand_suggestions[]` option's `reason_display` resolves through a committed template in this family (eleven: territory demand border/yield, gold demand, recurring demand, vassalage, subjugation, forced alliance, liberation, gold offer, territory offer, recurring offer). Register: Talleyrand's arithmetic-with-manners — commerce/court/surgery metaphors, no battlefield vocabulary, no enthusiasm; the reason prices the option, it does not cheer for it. ("A sweetener of {amount} gold — {court}'s resolve has a price, and it is conveniently paid in coin rather than provinces.")

**Copy boundary (cleanup SC-32 D5 — normative).** This is a *settlement table*, not a Congress. **No committed multi-court copy may contain "conference", "congress", or "veto"** — use "settlement", "the table", "these courts", "<court> holds out / signs". The word "conference" is internal design shorthand only. The boundary covers the GT-Slice-V families above (guided reasons, authoring reactions, the DC-4 caution, and the budget-bound recommendation). Enforced by `test_committed_multi_court_copy_avoids_conference_congress_veto_terms` and its GT-Slice-V extension.

#### Slice H full-agency ally petitions (landed July 3, 2026)

The two full-agency petition types extend the G2b `settlement_ally_petition_*` key scheme — same resolver rule (named diplomat suffix map: Castlereagh / Hardenberg / Metternich / Einsiedel + chancery fallback; Talleyrand relays the advisory framing via the existing `settlement_ally_petition_talleyrand`). Registers per the Slice H spec §7: the **reward petition** is a formal claim with its basis always named (`{basis_display}` slot — "Bavaria fought at Ulm" / "occupied homeland"); **bargain honor** is wounded honor with the promise quoted verbatim (`{created_turn_label}` slot). Six families, five suffixes each (plus the lapse notice):

| Family | Speaker | Trigger |
|---|---|---|
| `settlement_ally_petition_request_reward_or_restoration_{suffix}` | Ally's named diplomat / chancery | the reward/restoration petition fires at open/stage |
| `settlement_ally_petition_demand_bargain_honor_{suffix}` | Ally's named diplomat / chancery | staged terms put a live France-pledged war bargain at risk |
| `settlement_ally_petition_granted_{suffix}` | Ally's named diplomat / chancery | Grant lands the petitioned clause (gratitude register) |
| `settlement_ally_petition_declined_{suffix}` | Ally's named diplomat / chancery | Decline / Proceed Regardless (cool register — "We asked once already, Sire") |
| `settlement_ally_petition_honored_{suffix}` | Ally's named diplomat / chancery | Honor adjusts the draft so the pledge survives |
| `settlement_ally_petition_lapsed_talleyrand` | Talleyrand | the click-time re-check finds the ask no longer possible (G1 re-run pattern) |

The D5 boundary above covers the whole `settlement_ally_petition_*` prefix — enforced by `test_voice_families_committed_and_d5_clean` in `tests/test_settlement_slice_h_ally_petitions.py`.

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
- `reactive_summon_*` — one short reactive one-exchange summon/advisory line per foreign cast member. (**DEF-1 disposition, July 13, 2026:** verified — there is *no* engine trigger that summons a foreign envoy for a one-exchange aside under any name, so there is no live surface for this copy to attach to. **Closed as not-implemented:** if a reactive-summon interaction is ever built, it reuses the now-authored per-court incoming-proposal registers (`_NAMED_MOTIVE_LINES`) rather than a new family. No orphan copy is left behind.)
- `hard_reject_clear_*` — one chancery-voice reopening line per foreign court for `hard_reject_posture_cleared`.
- `witness_strike_*` — one visible witness-reaction line per foreign court so later witness fallout does not collapse into generic system prose.

### DEF-1 Roster Voices — landing note (July 13, 2026)

**DONE (this pass):**
- The **loyalist register class** — authored (§Loyalist register) and wired: the six client courts (Spain/Cevallos, Sweden/Ehrenheim, Denmark/Bernstorff, Sardinia, Holland/Schimmelpenninck, Kingdom of Italy/Marescalchi) no longer collapse to the bare chancery register.
- **Bespoke incoming-proposal voices for all 15 Europe courts** — a distinct in-register voice per court in `diplomatic_templates._NAMED_MOTIVE_LINES` / `_NAMED_ATTRIBUTIONS`, each adversarially verified against this Bible's "could this be mistaken for another diplomat?" rule. This is the always-on surface (every AI proposal speaks a `diplomat_line`). Pinned by `test_w6_incoming_voice.py::test_all_europe_courts_have_bespoke_voices`.

**CLOSED with reasoning:** `reactive_summon_*` (no engine trigger exists — see the additive-families list above); the WB-D five identifiers (landed as the `commitments_notice_*` family — see the reconciliation directly below).

**HOMED — owned follow-on "Roster Voices — Depth" (not silently dropped, GR9):** per-court bespoke `commitments_notice_*` copy (breach / bargain-fulfilled / witness / paradox) and per-court `TALLEYRAND_COMMENTARY` depth for the 15. Both have **working fallbacks today** — the `commitments_notice_*` family resolves uncovered courts through `resolve_named_diplomat` → chancery voice, and `TALLEYRAND_COMMENTARY` resolves any uncovered `(nation, situation)` through its `('_default', situation)` entry — so **no court is voiceless**, only less individuated on those secondary surfaces. **Owner/landing trigger:** a court's bespoke copy is authored when a playtest flags that court's breach or commentary surface as reading generic (Slice-3 guidance stands: desire profiles and the always-on incoming voice rank above this depth). **Completion:** that court's family authored + a coverage test that it no longer routes to the fallback for the flagged situation. Until then the fallbacks are intended behavior, not a gap.

### WB-D bargain-era lines (RECONCILED — landed as `commitments_notice_*`)

> **DEF-1 reconciliation (July 13, 2026):** verified — the WB-D bargain-era beats DID land, under the live **`commitments_notice_*`** family in `backend/game_logic/commitments_routing.py`, not under the five identifiers below. Mapping: `breach_lead_*` → `commitments_notice_breach_french` / `commitments_notice_breach_other`; `fulfillment_callback_*` → `commitments_notice_bargain_fulfilled`; `witness_reaction_*` → `commitments_notice_witness_strike`; `paradox_envoy_demand_*` → `commitments_notice_paradox`. The five legacy identifiers below are **retired as aliases** — do not author them; extend the live `commitments_notice_*` copy instead (per-court bespoke depth for that family is homed in the DEF-1 landing note above).

Five lines. Each candidate line must pass the "Never says" check before landing.

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

- **July 2, 2026** - Slice G1 (SC-30 Request Terms lifecycle): added the `settlement_request_terms_sent_talleyrand` / `settlement_request_terms_refused_court` / `settlement_request_terms_lapsed_talleyrand` families to §16.1. The refusal resolves its speaker through `resolve_named_diplomat("envoy", court, world)` with chancery fallback (never anonymous); the grant deliberately has no template — it produces a real incoming offer that speaks through the existing arrival family. SC-32 D5 boundary verified over the new copy.
- **June 10, 2026** - GT-Slice-V (Settlement Guided Terms §9): added the guided per-court demand-authoring voice family to §16.1a — the DC-4 concede-court caution line (verbatim from the Gate-4 pre-flight audit), the named-court `demand_received` / `offer_received` authoring reactions, the OQ-6 budget-bound recommendation extension of `settlement_budget_bound_constraint_talleyrand`, and the eleven committed `settlement_guided_reason_*_talleyrand` suggestion-reason templates. Retargeted `settlement_incoming_offer_request_revision_talleyrand` onto the guided table (Guided Terms §5 — the beat no longer references opening an editor). SC-32 D5 boundary extended over all new copy.

- **May 8, 2026** - Added explicit 16.1 Imperial Settlement voice-family anchors for blocked ratification, rescored drafts, discard confirmation, active-review collision, reopen-cap recovery, foreign-court observation, and review headings so `SETTLEMENT_UI_CLEANUP_SPEC.md` SC-19 has authored copy in this Voice Bible.
- **May 4, 2026** - Final Gate copy pass lands committed Imperial Settlement templates in `backend/game_logic/diplomatic_templates.py` for Talleyrand common-peace / defensive advisory, Castlereagh / Hardenberg / Metternich / Einsiedel acceptance and rejection, sold-out-by-leader, rewarded-ally, excluded-ally, plus serial-peace fallout legibility.

- **May 4, 2026** - Slice E presentation lands. Settlement copy is wired through the new `settlement_presentation` module (`SETTLEMENT_ROUTES`, `settlement_notification_meta`, sectioned `build_settlement_review`), and the seven settlement voice families above remain the contract for final committed copy. Initial Slice E copy uses Talleyrand register frames for advisory beats and chancery fallbacks for the foreign-leader settlement reactions; per-cast committed lines for `settlement_acceptance_*`, `settlement_rejection_*`, `settlement_sold_out_by_leader_*`, `settlement_rewarded_ally_*`, and `settlement_excluded_ally_*` are authored in cast register passes after Slice E (still inside the Final Gate, not deferred to a future spec).

- **Apr 29, 2026** - Tightened settlement-specific coverage for Imperial Settlement: added explicit Slice E voice families for common-peace advisory, defensive settlement counsel, acceptance/rejection, rewarded/excluded allies, and sold-out-by-leader registers, with material-contribution vs diplomatic-weight wording.

- **Apr 20, 2026** — v1.2. Added "Bloc-naming voice contract" subsection aligned to `COMMITMENTS_PRESENTATION_SPEC.md` §8.1a — formalizes the per-band voice contract (descriptive at `noticed`, proper-noun reveal at `alarming`, intensification without renaming at `crisis`), the no-modern-jargon list, the per-court desired feel at each band, and the Talleyrand-on-France guardrail. Top scope note realigned to v0.5.2 / §8.1a. Block 3 audit doc is now superseded by this plus the presentation-spec fold.
- **Apr 20, 2026** — v1.1. Realigned labels to `COMMITMENTS_PRESENTATION_SPEC.md` v0.5.1, expanded minimum live coverage to include `balance_of_europe_shifted` warning families, `amends_offered` acknowledgments, paradox aftermath / reactive summon / `hard_reject_clear` / `witness_strike` additive families, and retired the stale v0.3-only scope note.
- **Apr 15, 2026** — v1 draft. Cast confirmed from `backend/models/diplomat.py`. Register derived from `CONVERSATIONAL_DIPLOMACY_DESIGN.md` §6 plus historical research for period authenticity. Four exemplar paragraphs committed (Talleyrand private aside, Castlereagh breach accusation, Hardenberg breach accusation, Metternich breach accusation, Einsiedel breach lament). Five remaining templates (fulfillment callbacks, hard-reject, witness reaction, paradox envoy demand) marked "to author" against the register notes.
