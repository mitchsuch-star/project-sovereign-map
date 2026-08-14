> **Plan of record for LLM access & monetization (ROADMAP position 14, the
> Steam page row, and the shippable build).** Produced August 14, 2026 by a
> 5-agent research workflow (Steam examples / Valve policy / cost model /
> player sentiment / synthesis) under the user's directive to "assure we have
> plans for how people can use llm or buy tokens, use other steam games as
> example". The v1 ruling this memo recommends: **mock-default + reframed
> BYOK, sell nothing AI-related in EA; local-model parsing is the v2
> flagship; token packs are never built.** Section 6 lists the six questions
> that stay with the owner.

# Ink & Iron — AI Provisioning & Pricing Recommendation Memo

**Prepared for:** Steam Early Access release planning
**Date:** August 14, 2026
**Scope:** How the game provisions, prices, discloses, and degrades its LLM parser fallback (Claude Haiku 4.5, sub-0.7-confidence commands only; deterministic mock parser is the default and the executor is always deterministic).

---

## 1. The Landscape: Shipped Steam AI Games and What Their Models Did to Them

| Game | Provisioning model | LLM surface | Outcome |
|---|---|---|---|
| **AI Roguelite** ($14.99) | Hybrid ladder: free cloud default → optional ~$15/mo sub → BYOK (OpenRouter/custom) → local models (Kobold/Oobabooga) | Core engine (unbounded) | **Best-received cost architecture in the category.** Positive overall; sub grumbling exists but is tolerated *because* the free default exists |
| **Uncover the Smoking Gun** ($19.99, KRAFTON) | Dev-paid, bundled | Bounded, finite interrogation game (GPT-4o) | **Very Positive, 96%** — the strongest dev-paid result. Works because content is finite: the player finishes, the per-copy cost is capped |
| **GalCiv IV — AlienGPT** (Stardock) | Dev-paid, server-side, free to owners | Content generation only, never turn AI | Positive; cost is a non-topic because there is no visible meter. **The only shipped grand-strategy comp**, and it confines the LLM to a narrow seam exactly as we do |
| **Suck Up!** ($16.99) | Dev-paid bundled (EA era: ~10,000 tokens ≈ 40–50 h, then paywall; 1.0: uncapped but model downgraded) | Unbounded persuasion chat | **Mixed (~62%).** Players punished the token paywall AND the silent model downgrade ("they speak… like robots") |
| **Whispers from the Star** ($9.99) | Dev-paid bundled + **40–60 min/day play cap** to control API costs | Unbounded chat | 82% positive but a standing consumer-rights fight in the forums over rationing a paid product |
| **Vaudeville** ($19.99) | Dev-paid bundled (suspected GPT-3.5 for cost); unofficial local-model path | Unbounded suspect chat | **Mixed, 48%** — cheap-model quality problems land on the game's review score |
| **AI2U / Yandere AI GF Sim** (~$10–15) | Full arc: BYOK-only → dev-hosted **consumable tokens (re-buy the game to refill)** → walked back to one-time purchase **with player compensation** ("NO MORE TOKENS" patch) | Unbounded chat | 89% positive *after* retiring tokens. The one documented full retreat from consumable inference on Steam |
| **AI Dungeon** (F2P + $9.99–$99.99/mo tiers) | Subscription + monthly credits | The whole product | Sustains a business; **Mixed (~52)** on Steam; "credits run out fast" is a permanent review-section irritant; concurrents declining |
| **Retail Mage** ($4.99) | Dev-paid bundled; price cut from $15 to de-risk | Unbounded improv sandbox | 80% of only ~45 reviews; needed a 1,000× internal cost reduction to be shippable at all |
| **1001 Nights (EN)** | BYOK-only (OpenAI) | Core storytelling | Tolerated by an art-game audience; broke when OpenAI changed key formats — BYOK rots without maintenance |
| **SYNTHASIA** (EA) | BYOK-first (explicitly lists Anthropic) + local (Ollama/LM Studio) | AI game master | Too early for data; notable as the Anthropic-BYOK precedent |
| **Bot Colony** (2014) | Dev-hosted NLU servers, one-time price | Core dialogue | **Shut down**: $524/mo servers vs. ~2 sales/day. The original "the servers outlived the revenue" cautionary tale |

**The pattern that matters for us:** every no-BYOK dev-paid game with *unbounded* LLM usage either capped play (Whispers), downgraded models (Vaudeville, Suck Up 1.0), or drifted to Mixed. The two dev-paid successes (Uncover the Smoking Gun, AlienGPT) bound the LLM to a finite, low-frequency surface. **Ink & Iron's parser fallback is that shape by construction** — ≤1 call per typed command, only below the confidence gate, ~$0.003 a call, and the game is fully playable at $0 in mock mode. We are architecturally in the winners' column before making any pricing decision. Also load-bearing: **consumable token packs are the one model with a documented retreat-and-compensation event (AI2U)**, and the AI Roguelite ladder (free default → optional paid → BYOK → local) is the best-reviewed architecture — of which we already ship the two most important rungs.

---

## 2. Valve Policy Constraints That Bind Us

1. **AI disclosure is mandatory and ours is "Live-Generated."** The parse clarifications and the CR-5b flavor line are player-visible runtime AI text, so we check the live-generated box and must describe guardrails (Jan 2024 policy, Jan 2026 clarification scoping it to content "consumed by players"). Our guardrail story is unusually strong and should go into the Content Survey nearly verbatim: temperature 0, forced tool-use schema so no free text reaches mechanics, deterministic executor owns all outcomes, a register/parroting gate on the single cosmetic string, opt-in player-supplied key, fully playable with AI off. Claude-assisted *development* is explicitly exempt and needs no disclosure. Note the Shift+Tab Overlay report tool applies to live-AI games — another reason the flavor line's register gate matters.
2. **In-game sales must be Steam Wallet.** If we ever sell anything AI-related in-game, it goes through `ISteamMicroTxn` or the Inventory Service (the latter avoids standing up a trusted payment server, which matters since our backend is a local FastAPI process). DLC cannot model refillable credits (one-time entitlement); Recurring In-Game Billing exists but one agreement per user per game.
3. **No external payment links inside the Steam build,** and since September 2024 no external links in store-page description text either. A "buy credits on our site" button is the clear-violation tier.
4. **BYOK sits in an unregulated gray zone with shipped precedent and zero observed enforcement** (CyberWaifu, AI Roguelite's official OpenAI-key option announced in Steam News, ChatWaifu). The mandatory "Requires 3rd-Party Account" flag likely doesn't apply because the account is optional, but we should voluntarily disclose it in the description.
5. **Refunds:** if we ever sell credit packs, unspent credits are auto-refundable only if we opt in; either way we must poll `GetReport` daily and claw back on the five reversal states — we'd eat inference already burned against refunded credits.
6. **Provider side (Anthropic, not Valve):** proxying under our own key to power a game feature is expressly permitted (Commercial Terms A.1 "power products and services"); **reselling API access is not** (D.4). Any purchasable unit must be denominated in game-native terms ("orders," "parses"), never Anthropic tokens. We're responsible for all activity under our key (D.5), so a proxy needs per-player rate limits and input caps.

---

## 3. Our Cost Reality

The unit economics are almost comically small because the LLM surface is a parser, not a companion:

| Scenario | LLM calls | Cost @ Haiku 4.5 ($1/$5 per MTok, ~2,000 in / 200 out) |
|---|---|---|
| One LLM-routed command | 1 | **$0.003** |
| 2-hour session (25% routing) | 30 | **$0.09** |
| 40-hour campaign | 600 | **$1.80** |
| 100-hour heavy user | 1,500 | **$4.50** |
| Worst case (100% routing), 100 h | 6,000 | $18.00 |

Rule of thumb: **~$0.045 per play-hour normally, ~$0.18 worst case.** Three implications:

- **A dev-paid tier is affordable per-median-user but actuarially unbounded per-grognard.** This genre produces 1,000-hour players; 1,000 h × $0.045 = $45 of cost against a one-time price — exactly the tail that broke Suck Up! and rationed Whispers. Any dev-paid arm needs a structural bound (a monthly fair-use parse cap), not hope.
- **Rate limits are a non-issue; the spend cap is the constraint.** Anthropic's Start tier sustains ~1,000 parses/min (~4,000 average-concurrent players) but only ~166K parses/month under its $500 spend cap ≈ 5,500 sessions/month. A successful EA launch needs the automatic Build→Scale promotion. Prompt caching is currently a no-op for us — our ~2,000-token prompt is under Haiku 4.5's 4,096-token cacheable minimum (`cache_control` silently does nothing below it).
- **BYOK players pay pennies.** A player's own key costs them ~$1.80 per full campaign — cheaper than any pack we could sell — which is both the pitch and, per AI Roguelite's dev, the reason heavy users always defect from paid tiers to keys. That defection is *fine* for us: we're not trying to run inference as a profit center.

---

## 4. The Options

### A. Pure BYOK (status quo)
- **Pros:** zero cost, zero liability (each player is their own Anthropic customer), zero Valve friction, already shipped (in-game Settings → `/config/llm` → the `LLMClient.create` seam), sidesteps Anthropic resale terms entirely. SYNTHASIA precedent for an Anthropic key picker.
- **Cons:** it is a conversion killer at Steam scale — Hilary Mason's lesson from the AI2U arc: "you simply cannot get nearly a million people to download a demo if the first step is 'go create an OpenAI account.'" Worse on Steam specifically: the phrase "API key" pattern-matches to the Steam API-key trade-hijack scam that community guides have trained users to fear. And BYOK rots (1001 Nights broke on OpenAI's key-format migration).
- **Effort:** none. **Risk:** low technical, moderate perception (must never market with the words "API key").

### B. Dev-paid, bundled in the purchase price
- **Pros:** the cleanest player promise; the two best-reviewed AI games on Steam (Uncover the Smoking Gun, AlienGPT) are dev-paid with bounded surfaces, and our surface is bounded per-command even though campaigns are unbounded in hours.
- **Cons:** unbounded lifetime liability against a one-time price (the $45 grognard); requires standing up a real proxy server (our backend is local — a proxy is new infrastructure), Anthropic account scaling, per-player abuse controls, and a refund/claw-back posture. Failure modes are the documented review-killers: silent model downgrade (Suck Up 1.0, Nothing Forever's Curie incident — a *safety* event, not just quality) or rationing (Whispers).
- **Effort:** high (proxy service, auth binding to Steam identity, metering, ops). **Risk:** medium-high; it's the model that has hurt the most games.

### C. Token-pack microtransactions
- **Pros:** revenue precedes cost; cleanest liability match on paper.
- **Cons:** **the one model with a documented full retreat under player pressure (AI2U's "NO MORE TOKENS" patch plus compensation).** Selling $0.003 parses in $3.99 packs reads as pay-per-thought microtransactions in a premium single-player strategy game — Steam's most reliably review-bombed pattern. Running dry mid-battle is terrible UX for an item worth a third of a cent. Plus MTX server obligations and refund claw-backs (§2), and careful denomination to stay clear of Anthropic's resale clause.
- **Effort:** high. **Risk:** highest of all options. **Do not build.**

### D. Subscription
- **Pros:** actuarially sound at trivially low prices ($2.99/mo covers a 50 h/month hardcore player with margin); Steam's Recurring In-Game Billing makes it mechanically possible in-store.
- **Cons:** a subscription for a *parser* in a single-player strategy game is culturally indefensible — AI Dungeon (Mixed, declining) is what a metered service looks like even when the AI *is* the product. For us the subscription would gate a convenience worth ~$0.09/session. The value story collapses on contact with the forums.
- **Effort:** medium. **Risk:** high reputational. **Do not build as a parser tier** (see v2 for the only version worth revisiting).

### E. Local-model fallback
- **Pros:** the credible "works forever" answer that the Stop Killing Games constituency (1.4M signatures; strongest in exactly our genre) actually wants. inZOI proves a **0.5B on-device model works for a narrow structured task** — and intent classification of typed orders is far easier than open NPC chat. AI People's arc (cloud credits → local escape hatch) and AI Roguelite's local tier show it ships and satisfies. Would out-position every dev-paid competitor on the preservation axis.
- **Cons:** real engineering (llama.cpp/GGUF integration in the FastAPI backend, forced-schema constrained decoding to mirror the tool-use contract, model selection and eval against the golden corpus); quality risk if done badly — Portopia's dead local parser earned 15% positive, though our failure mode is softer because the deterministic parser still owns the floor and the executor owns all outcomes; support burden and VRAM/CPU variance.
- **Effort:** high (a real slice with its own gate). **Risk:** low if gated on beating the golden corpus, because degradation lands on mock, not on garbage.

### F. Hybrid ladder (AI Roguelite pattern, adapted)
- **Pros:** the best-reviewed architecture in the category, and we already ship rungs 1 (deterministic free default — stronger than AI Roguelite's "free cloud models," ours is offline and infinite) and 3 (BYOK). Each additional rung is optional and independent.
- **Cons:** each rung added is its own project; the dev-paid rung imports option B's infrastructure.
- **Effort:** incremental by rung. **Risk:** lowest overall — no rung gates the game.

---

## 5. Ranked Recommendation

**Ranking: F (hybrid ladder, built incrementally) > A (pure BYOK, the v1 core) > E (local model, the v2 flagship) > B (dev-paid, only ever as a bounded courtesy tier) > D (subscription) > C (token packs — never).**

The decisive facts: our LLM is a garnish on a deterministic product (the market's winning shape — Smoking Gun, AlienGPT); our fallback is *the deterministic parser, not a worse LLM* — unique in this market and the exact antidote to the Suck Up/Nothing Forever degradation failure; and our true answer to "what happens when the servers go away?" is "nothing — you lose a convenience, not the game." That answer is a marketable differentiator several of the surveyed games died on the wrong side of.

### v1 (Early Access): Mock-default + reframed BYOK. Sell nothing AI-related.

1. **Default = full game, offline, no AI.** No account, no key, no meter, forever. This is already true; make it the loudest sentence on the store page.
2. **Keep BYOK exactly as shipped, but rename every player-facing surface.** Never "API key" (Steam scam pattern-matching). Settings panel heading: **"Smarter Parsing (optional) — Connect your Anthropic account."** One-line answers to the three fears the AI2U threads catalogued: *cost* ("typical cost: under $2 for an entire campaign, billed by Anthropic to you"), *security* ("stored only on this PC, sent only to Anthropic, never to us"), *setup* (link to a one-page guide; per Steam's link rules, in-game docs or the designated website field, not the store description body).
3. **Do not build a proxy, packs, or a subscription for EA.** The parser upgrade is worth $0.09/session; no monetization of it survives contact with a strategy audience, and EA's job is review score.
4. **File the Steam AI disclosure with the strong guardrail story** (§2.1) and mirror it honestly on the page — 89% of surveyed players read AI disclosures; Uncover the Smoking Gun proves specific, narrow, honest disclosure coexists with Very Positive.

**Store-page disclosure draft** (for the AI Generated Content Disclosure section and the About block):

> **AI Content Disclosure.** Ink & Iron is a deterministic strategy game. All game rules, combat, economy, and AI opponents are conventional hand-authored code — no AI model ever decides an outcome. The complete game works offline forever, with no account, no subscription, and no AI required.
>
> Optionally, you may connect your own Anthropic account in Settings. When you do, unusually-phrased typed orders that the built-in parser can't confidently read are interpreted by a language model (Claude) running at fixed settings, restricted to choosing among the game's predefined orders; it may also phrase a marshal's one-line spoken acknowledgment. It cannot invent actions, alter rules, or affect outcomes. If it is unavailable — no connection, no account, or you simply never enable it — the game continues on its built-in parser. This feature is off by default; any usage is billed by Anthropic directly to your account (typically under $2 for a full campaign).

**UI touchpoints (where the game says what the AI does and costs):**
- **Main menu → Settings → "The Parser (AI)"** (exists): rename per above; add the three-fears copy and a "typical campaign cost" line; show live status (Connected / Not connected / Key rejected).
- **First campaign start without a key:** one non-modal Berthier line, once ever: "Sire, the staff will read your orders as written. Should you wish the clerks to puzzle out *unusual* phrasings, see Settings — The Parser." (Latched; never nags. Mirrors the reactive-but-discoverable discipline already used for the Reward gate.)
- **On key entry:** confirmation states scope and cost: "Connected. Used only when an order needs interpretation — a fraction of a cent per order, billed by Anthropic to you."
- **On any live-parse failure** (401/429/timeout): the response carries a quiet one-time-per-session notice: "The clerks could not reach the wire; your order was read as written." — then normal mock behavior. Never silence, never a blocking modal, never auto-retry loops (the ParseResult.llm_error one-call guarantee already enforces the bound).

**Failure-mode story (the part we advertise):** invalid key → fast parser, status shown in Settings; credits exhausted at Anthropic → same; offline → same; Anthropic deprecates the model pin → same, plus a patch. In every case the player loses one convenience — the sub-gate fallback — and keeps the entire game. This is already the shipped behavior; v1's work is *saying so* at the three touchpoints above and on the store page, because the market rewards the answer only if it's visible.

### v2 (post-EA evolution, in order):

1. **Local small-model parsing ("Smart Parsing — Offline").** A bundled ~0.5–3B GGUF (inZOI precedent) doing constrained-decode intent classification behind the same confidence gate, gated on beating the live-parse rows of the golden corpus before it ships. This converts "degrades gracefully" into "never degrades," completes the preservation story, and adds a fourth rung no strategy competitor has. This is the highest-value v2 investment.
2. **Optional dev-paid courtesy tier — only if EA telemetry says BYOK friction is real.** If a meaningful fraction of players who *try* to enable live parsing bounce off Anthropic signup, consider a bounded included allowance (e.g., N live parses/month per Steam account through a proxy, monthly refill, then fall back to mock — never a paywall on play). Anchor: $9.99-equivalent net covers ~155 normal hours; the cap kills the whale tail. This imports real infrastructure (proxy, Steam identity binding, abuse limits, claw-backs) — do not build it speculatively.
3. **Never:** token packs (AI2U), a parser subscription (AI Dungeon's review profile), silent model downgrades (Suck Up 1.0), or daily rations (Whispers). If a paid tier ever exists it gates *quality* (e.g., future narration flourishes), never the *capability* to issue orders.

---

## 6. Open Questions for the Owner

1. **Does the EA build enable the BYOK field on day one, or ship it dark for Round 0 testers first?** (Disclosure checkbox is required either way once it ships; mock-only would not trigger it.)
2. **Store-page positioning:** do we lead with "no AI required, works offline forever" as a headline differentiator (leaning into the Stop-Killing-Games audience), or keep it inside the disclosure block to avoid foregrounding "AI" at all for the 31% negative-sentiment cohort? The research supports leading with it; it's a taste call.
3. **Do we want any telemetry on parser routing** (share of commands hitting the gate, BYOK enable/bounce rates) to inform the v2 courtesy-tier decision? This is new instrumentation with its own privacy-disclosure line.
4. **Local model appetite:** is v2.1 (bundled GGUF) worth a design gate now so it can be specced against the golden corpus, or does it wait for post-EA evidence that players ask for it? (AI Roguelite's forums say they will ask.)
5. **The CR-5b flavor line under the live-AI report tool:** comfortable shipping it as-is under the register gate, or do we want a settings toggle ("plain acknowledgments") as an extra guardrail to cite in the Content Survey?
6. **Anthropic terms re-check at ship time:** BYOK sidesteps the commercial terms today; if the v2 courtesy tier is ever built, we should re-read the then-current terms (resale clause D.4, flow-down obligations) before the proxy goes live — flagging now so it lands on that slice's gate, not as a surprise.
---

## 7. Addendum (Aug 14, second session) — the Pax Historia comp, examined at the owner's challenge

**The challenge:** *"what about Pax Historia, they do well — but you think
this won't play on Steam?"* Researched rather than answered from memory.

**What Pax Historia is (verified Aug 14, 2026):** a YC-backed,
BROWSER-based alternate-history sandbox (paxhistoria.co, **not on Steam**)
where **the LLM is the entire game engine** — every turn ships the whole
world state to the model (~100 BILLION tokens/week across the player
base). Monetization: consumable tokens (~$1 ≈ 15–20 min of play, one free
per day) + a "Pax Patron" subscription ($6–$56/mo) + a 10% creator
rev-share on popular presets. Quality reviews are mixed ("prompt
engineering dressed up as a grand strategy game"; one outlet scored it
59) — the MODEL does well; the craft reception is contested.

**Why their token model works there and would fail here — four
structural facts, each inverted in our case:**

1. **Tokens are their COGS pass-through; ours would be a markup on
   nothing.** Their compute IS the game and it is genuinely expensive —
   players understand buying fuel. Our whole campaign costs ~$2 of
   parser calls; metering that reads as a shakedown, and the AI2U
   retreat is what that looks like on Steam.
2. **F2P web funnel vs premium purchase.** Their players pay $0 up
   front and opt into spend; a Steam buyer has already paid $20–30, and
   the premium contract ("I bought the game") is exactly what metered
   AI violates — the documented review-bomb pattern (AI2U, Suck Up!,
   Whispers).
3. **The web is what makes $1 microtokens possible.** Direct payments,
   no 30% cut, no Steam Wallet MTX plumbing, no consumable-refund
   claw-backs, no external-payment-link ban. On Steam every one of
   those constraints applies.
4. **They are not on Steam — and that is the evidence, not an
   accident.** AI Dungeon runs the same shape (sub + credits) and
   sustains a real business off-platform while its Steam presence sits
   at Mixed. Same product, two venues, opposite reception. The model
   lives where its funnel and rails exist.

**So the claim is narrower than "AI monetization can't play on Steam":
metering the PARSER in a premium single-player title is the failure
pattern; metering AI CONTENT in an F2P web sandbox is Pax Historia's
success pattern.** The §5 ruling stands unchanged.

**What IS transferable (the owner's instinct is right about this half):**
Pax Historia proves players pay real money for AI-driven strategy
CONTENT when the model generates the value. The Ink & Iron-shaped
version of that is already reserved by §5-v2-3's "quality, never
capability" line — concretely, a post-EA **"Campaign Chronicler"
premium tier** (LLM-written Gazette prose over the HC-G deterministic
skeleton, marshal banter, alt-history campaign narration; dev-paid,
bounded per campaign, sold as deluxe/DLC — a content tier, not a
meter on orders). That is a candidate for the position-14 gate's §6
list, NOT a v1 item; recorded here so the door has a name.

---

## 8. Addendum (Aug 14, second session) — distribution venues, ruled at the owner's question

*"Should I list elsewhere than Steam?"* **Steam stays primary; the plan
is engineered for its review culture and the grand-strategy audience is
Steam-native. itch.io becomes the NAMED Round-0 channel** (instant
upload, no review gate, BYOK-comfortable — spend the tester round there,
not the Steam page's one first impression). **GOG is a post-EA option**
(the DRM-free "no account, no AI, yours forever" catalog fit; curated,
so apply with EA review proof in hand). **Epic: skip** (no indie
strategy discovery). **A web version is REJECTED as a listing choice**
— it is a different business (Pax Historia's venue solves the F2P
token-funnel problem this game deliberately does not have) and would
re-architect the local client/backend for months to compete on someone
else's terms. Queue impact: none — LLC+Steamworks position 2, page 14;
Round 0 (position 11) ships via itch or direct zip.
