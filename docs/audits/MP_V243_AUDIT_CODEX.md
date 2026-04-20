# Memory and Pressure v2.4.3 Audit — GPT-5 Codex, 2026-04-20

## Executive summary
REQUEST-CHANGES. The phase row is current, but the spec ensemble is not yet implementation-ready because the v0.5.1 presentation trim is still contradicted by live normative examples and handoff prose, the `commitment_paradox` rename is not canonicalized across save/UI/backend surfaces, and the promised commitments notice pipeline (priority tier, icon, label, template, named-diplomat resolution) does not line up with current rails. The highest-risk failure mode is that two implementers can both "follow the spec" and still ship incompatible UIs: one reintroducing cut spotlight/callback infrastructure, the other following the trimmed single-voice notice contract.

## Dimension scorecard
Evidence anchors are the finding IDs below; the table counts unique issues, not repeated mentions of the same defect.

| Dimension | Verdict | Blocker count | Major | Minor |
|-----------|---------|---------------|-------|-------|
| 1. Internal consistency | BLOCKER | 1 | 2 | 1 |
| 2. UI fidelity | BLOCKER | 1 | 4 | 0 |
| 3. Fuzzy edges | RISKY | 0 | 1 | 3 |
| 4. Code snippet correctness | RISKY | 0 | 1 | 2 |
| 5. Implementation plan coverage | READY | 0 | 0 | 1 |
| 6. Voice / copy fidelity | BLOCKER | 1 | 1 | 1 |
| 7. Dangling references | BLOCKER | 1 | 1 | 0 |
| 8. Scope drift | RISKY | 0 | 1 | 1 |
| 9. Phase-row truth | READY | 0 | 0 | 0 |

## Event trace matrix (UI fidelity §2)
Live-code reality check below. `MISSING` means the chain is not fully specified or not backed by current code.

| Engine event | Payload | Tier | Icon | Label | Template / copy | Voice | Surface | Review-route |
|--------------|---------|------|------|-------|------------------|-------|---------|--------------|
| `commitment_paradox` | Legacy `world.alliance_paradox_popup` payload with `attacker/defender/..._preview` only (`backend/game_logic/diplomacy.py:2123-2131`) | blocking hard-stop (`backend/models/dialogue_manager.py:46-51`) | MISSING | MISSING | legacy inline `message` string only | Talleyrand framing only; staged spurned-envoy aftermath is MISSING | legacy `alliance_paradox_popup` route (`godot-client/project-sovereign/scripts/main.gd:226-228`, `godot-client/project-sovereign/scripts/alliance_paradox_popup.gd:27-49`) | MISSING |
| `hard_reject_posture_triggered` | dispatch/log payload exists (`backend/game_logic/diplomacy.py:844-859`) | `HIGH` dispatch, not CRITICAL notice (`backend/game_logic/dispatch.py:1111`) | MISSING | generic chancery string only | dispatch formatter exists (`backend/game_logic/dispatch.py:1246-1251`); no `commitments_notice_*` family | `foreign_office` emitted, but no named-court resolver | dispatch + campaign log only | MISSING |
| `hard_reject_posture_cleared` | dispatch/log payload exists (`backend/game_logic/diplomacy.py:403-416`) | `MEDIUM` dispatch (`backend/game_logic/dispatch.py:1112`) | MISSING | generic reopen string only | dispatch formatter exists (`backend/game_logic/dispatch.py:1253-1258`) | `foreign_office` emitted, but no named-court resolver | dispatch + campaign log only | MISSING |
| `diplomatic_treaty_broken` (`french_breach`) | payload exists with `end_reason_family` and generic `speaker_attribution="foreign_office"` (`backend/game_logic/diplomacy.py:775-809`) | generic `HIGH` notification / dispatch (`backend/game_logic/diplomacy.py:786-793`, `backend/game_logic/dispatch.py:1082`) | generic `BRK` only (`godot-client/project-sovereign/scripts/notification_bar.gd:34-35`) | generic `Treaty Broken` only | generic break copy only (`backend/game_logic/dispatch.py:1042`, `backend/campaign_log.py:673-687`) | wrong speaker contract for this family; spec wants injured-party `envoy` | notification collector + dispatch + campaign log | MISSING |
| `diplomatic_treaty_broken` (other families) | payload exists (`backend/game_logic/diplomacy.py:775-809`) | generic `HIGH`, not NORMAL persistent notice for non-fault families (`backend/game_logic/dispatch.py:1082`) | generic `BRK` only | generic `Treaty Broken` only | only `obsolescence_or_external` / `counterparty_reversal` get differentiated copy (`backend/game_logic/dispatch.py:1037-1042`, `backend/campaign_log.py:673-687`) | generic / unresolved | notification collector + dispatch + campaign log | MISSING |
| `commitment_paradox_resolved` | log event only (`backend/commands/diplomatic_executor.py:2781-2792`, `2869-2878`) | MISSING | MISSING | MISSING | campaign-log one-liner only (`backend/campaign_log.py:520-530`, `689-692`) | no `speaker_attribution` on emitter | campaign log only | MISSING |
| `witness_strike_recorded` | dispatch payload exists (`backend/game_logic/diplomacy.py:814-824`) | fallback `MEDIUM` because no explicit priority entry (`backend/game_logic/dispatch.py:1231-1244`, `1300-1303`) | MISSING | MISSING | dispatch one-liner exists | skeletal / unvoiced only | Morning Dispatch only | MISSING |
| `diplomatic_treaty_broken` (`defensive_refusal_termination`) | MISSING in live emitters; only spec/plan name the family (`docs/RELIABILITY_COMMITMENTS_SPEC.md:724`, `docs/RELIABILITY_IMPLEMENTATION_PLAN.md:196`) | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING |
| Make Amends (`standard` / grievance variant) | MISSING; no `amends_offered` emitter found in the backend sweep, and no `reparations_cooldown` field exists in `backend/models/world_state.py` or `backend/commands/diplomatic_executor.py` | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING |
| Balance of Europe headline | MISSING in ledger payload; builder returns only `nations`, `treaties`, `threat_coalition`, `talleyrand` (`backend/game_logic/diplomatic_ledger.py:54-60`) | n/a | n/a | MISSING | MISSING | n/a | MISSING on Nations tab; Godot still renders `NATION OVERVIEW` and separate `COALITION THREAT` tab (`godot-client/project-sovereign/scripts/diplomatic_ledger.gd:181-322`, `403-485`) | n/a |

## Findings
1. `F1`
Severity: BLOCKER
Location: `docs/COMMITMENTS_PRESENTATION_SPEC.md:252-266, 526-555, 571-603, 615-653`; `docs/RELIABILITY_COMMITMENTS_SPEC.md:692, 764, 1120`
Observation: The trimmed presentation contract says v0.5.1 ships a single-voice notice surface with "no new tier, no typographic split, no reveal cadence" and no N+1 callback, but the worked examples still require a "turn-N spotlight" with split voice and next-morning callback. The core commitments spec also still says DG-4 events emit a "spotlight" and need "spotlight and notice copy."
Impact: An implementer cannot tell whether spotlight/split-voice/N+1 are cut or still live. That ambiguity directly affects scene design, payload schema, notification routing, and test scope.
Suggested fix: Rewrite every remaining live example and cross-spec handoff to the v0.5.1 contract. Replace `spotlight` with `notice` where the event is still live, remove all next-turn callback language, and make the paradox example show only the in-popup after-choice aside.

2. `F2`
Severity: BLOCKER
Location: `docs/COMMITMENTS_PRESENTATION_SPEC.md:19, 214, 709, 746`; `backend/game_logic/diplomacy.py:2123-2135`; `backend/models/world_state.py:497, 668-673, 3271, 3578`; `godot-client/project-sovereign/scripts/main.gd:226-228, 776-782`; `godot-client/project-sovereign/scripts/alliance_paradox_popup.gd:27-49`
Observation: The docs say the canonical type is `commitment_paradox` on a dedicated `commitment_paradox_popup.{tscn,gd}` surface, but live code still serializes `alliance_paradox_popup`, pushes `"alliance_paradox"`, registers `alliance_paradox_popup.tscn`, and renders a single-label popup.
Impact: The rename is not a coherent contract. Save migration, Godot routing, payload naming, and the popup field schema are all ambiguous at the point where implementers need a single source of truth.
Suggested fix: Canonicalize `commitment_paradox` immediately. Define the exact popup payload fields for the three-beat scene, keep `alliance_paradox*` as read-only alias-on-load behavior only, and update the live-code/spec references to name one canonical surface.

3. `F3`
Severity: MAJOR
Location: `docs/COMMITMENTS_PRESENTATION_SPEC.md:215-220, 281-309, 410-417, 717, 720`; `backend/notifications.py:24-62`; `godot-client/project-sovereign/scripts/notification_bar.gd:30-42`; `backend/game_logic/diplomatic_templates.py:1-200`; `backend/game_logic/dispatch.py:1037-1114, 1231-1303`
Observation: The presentation spec promises commitments-specific priority mapping, icon keys, player-facing labels, templates under `commitments_notice_*`, and mandatory named-diplomat resolution. Current rails still expose only generic notification types and icon codes, `diplomatic_templates.py` has no commitments family, and `witness_strike_recorded` falls back to default `MEDIUM`.
Impact: Even if the engine emits the right events, the UI cannot render the promised commitments vocabulary consistently. The player-facing layer would degrade to generic treaty/chancery strings with no stable icon or attribution contract.
Suggested fix: Add one explicit routing table shared across notifications, dispatch, campaign log, and ledger: event family -> priority -> icon key -> player label -> template key -> speaker resolver -> review target. Implement the `commitments_notice_*` family and make `notification_bar.gd` understand the commitments icon set.

4. `F4`
Severity: MAJOR
Location: `docs/COMMITMENTS_PRESENTATION_SPEC.md:216, 403-413`; `backend/game_logic/diplomacy.py:775-783, 844-850`; `backend/game_logic/dispatch.py:1042, 1071`
Observation: The spec says `diplomatic_treaty_broken` with `end_reason_family=french_breach` is a CRITICAL notice led by the injured party's named `envoy`, while `hard_reject_posture_triggered` is `foreign_office`. Live breach emission writes `speaker_attribution: "foreign_office"` for the breach event itself and does not include resolved diplomat metadata.
Impact: The sharpest breach event cannot render the required voice. A French breach against Prussia would currently read like an anonymous chancery bulletin rather than Hardenberg's accusation, which is a material presentation mismatch.
Suggested fix: Emit the canonical voice role per family at the backend source. `french_breach` should carry `speaker_attribution="envoy"` plus nation context sufficient to resolve the victim diplomat; hard-reject families can keep `foreign_office`. Centralize the resolver so notices, logs, and popups do not guess differently.

5. `F5`
Severity: MAJOR
Location: `docs/RELIABILITY_COMMITMENTS_SPEC.md:964-967`; `docs/RELIABILITY_IMPLEMENTATION_PLAN.md:154`; `backend/game_logic/diplomacy.py:1817-1829, 1849-1858`; `backend/display_names.py:344`
Observation: The v2.4.3 enum is `hegemony_pressure` plus `unknown_baseline`, with `concern_pressure` only as a read alias. Live code still returns `rival_pressure` from both reason emitters, and the display-name table still exposes `rival pressure`.
Impact: Tests, campaign-log explanations, save compatibility, and advisory/presentation code will disagree on the allowed enum set. This is precisely the kind of string drift the audit prompt asked to stop before implementation.
Suggested fix: Update deterministic emitters and display-name mappings to the v2.4.3 enum now. Keep only deserialization/display fallback aliases for `concern_pressure` and older values.

6. `F6`
Severity: MAJOR
Location: `docs/RELIABILITY_COMMITMENTS_SPEC.md:1006-1046`; `docs/RELIABILITY_IMPLEMENTATION_PLAN.md:222-225`; `backend/game_logic/diplomatic_ledger.py:54-60`; `godot-client/project-sovereign/scripts/diplomatic_ledger.gd:181-322, 403-485`
Observation: The spec and plan make the Balance of Europe headline a shipped surface, including the "no hegemon" case and the `BREWING`/`DECLARED` split. The live ledger builder still returns the old four-tab payload with no headline field, and the Nations tab still prints `NATION OVERVIEW` while coalition status remains in a separate threat tab.
Impact: One of the new hegemony-era player readouts has no validated surface path. Builders would have to invent the payload shape and rendering rules instead of implementing a settled contract.
Suggested fix: Add a concrete `balance_of_europe` payload block to the ledger backend and render it at the top of the Nations tab. Keep the Threat tab for detailed coalition data only, not for the headline itself.

7. `F7`
Severity: MAJOR
Location: `docs/SAVE_FORMAT_REFERENCE.md:12-14, 107-109, 224-226`; `backend/models/world_state.py:494-502, 3253-3275, 3560-3579`
Observation: The save reference still says format version 1.0, "Compatible with: Phase 4 Commands/QoL/Popups + Diplomacy Button Session A", documents `diplomatic_reliability` as per-pair, and still names `alliance_paradox_popup`. Live `WorldState` stores nation-level `diplomatic_reliability`, `betrayal_history`, `next_episode_id`, and the pending dispatch queue.
Impact: Anyone using the save reference as the migration or serialization contract will write the wrong tests and the wrong compatibility logic. This is a direct spec/live-code mismatch, not just stale commentary.
Suggested fix: Refresh `docs/SAVE_FORMAT_REFERENCE.md` before the next implementation session. Document the current live schema, add the legacy alias note for `alliance_paradox_popup`, and include planned v2.4.3 additions such as `reparations_cooldown` once their shape is locked.

8. `F8`
Severity: MINOR
Location: `docs/COMMITMENTS_PRESENTATION_SPEC.md:415`; `docs/RELIABILITY_COMMITMENTS_SPEC.md:319, 996`; `backend/models/world_state.py` (no bloc-cache field found in sweep)
Observation: A few failure-mode contracts are still verbal rather than operational: `loyalist` must "fail loudly" but no warning/exception shape is named, the non-France-hegemon guard must "emit a debug log" but no logger or rate limit is specified, and the per-turn bloc cache is referenced without naming where it lives on `WorldState`.
Impact: Two implementers can land different telemetry and failure behavior while both believing they followed the spec.
Suggested fix: Add one short runtime-behavior note naming the logger (`backend.game_logic.coalition`, `DEBUG`, once per turn), the cache home (for example `world._bloc_members_cache` patterned after `_active_nations_cache`), and the explicit fail-loud behavior for unsupported diplomat personalities.

## Missing artifacts
- `godot-client/project-sovereign/scenes/commitment_paradox_popup.tscn` does not exist in the repo, even though the audit prompt treats it as a live reality-check surface and both `COMMITMENTS_PRESENTATION_SPEC.md` and `RELIABILITY_IMPLEMENTATION_PLAN.md` require it.
- `godot-client/project-sovereign/scripts/commitment_paradox_popup.gd` does not exist in the repo for the same reason; the only popup in tree is the legacy `alliance_paradox_popup.gd`.
- `backend/game_logic/diplomatic_templates.py` has no `commitments_notice_*` template family. The plan does schedule this under C-lite, so this is a current-code gap, not an unscheduled helper.
- I did not find a named-diplomat resolution helper in the backend. The plan does schedule it under C-lite.
- I did not find `world.get_power_tier`, `world.get_bloc_members`, `_top_overlord`, or `_calculate_hegemony_pressure` in live code. The plan does schedule them under B-Hegemony.
- I did not find `WorldState.reparations_cooldown` or any `amends_offered` emitter in live code. The plan does schedule them under B-B7 / B-B4.
- I did not find any major missing helper named by the specs that is both absent and completely unscheduled. The plan covers most of the missing runtime pieces; the bigger problem is that the live-code reality check surfaces named in the prompt are still pre-v2.4.3.

## Cross-spec value table
| Contract | RELIABILITY_COMMITMENTS_SPEC | Other spec / plan | Live code | Status |
|----------|------------------------------|-------------------|-----------|--------|
| Passive hegemony ladder | `1/3/5/8` at the 30/40/50/60 buckets (`docs/RELIABILITY_COMMITMENTS_SPEC.md:301-307`) | `docs/COALITION_SPEC.md:119, 835, 841`; plan helper/tests at `docs/RELIABILITY_IMPLEMENTATION_PLAN.md:107-109, 126-129` | no `_hegemony_pressure_for_share` in `backend/game_logic/coalition.py` sweep | Docs match; code absent |
| Hegemony share thresholds | `30% / 40% / 50% / 60%` (`docs/RELIABILITY_COMMITMENTS_SPEC.md:295-307`) | plan B-Hegemony tests (`docs/RELIABILITY_IMPLEMENTATION_PLAN.md:126-129`) | absent from live coalition code | Docs match; code absent |
| `bilateral_betrayal_mod` | `-6 per active strike` (`docs/RELIABILITY_COMMITMENTS_SPEC.md:19, 870-895, 1191`) | `docs/RELIABILITY_IMPLEMENTATION_PLAN.md:34, 140-150` | live decision path still uses old reliability contribution and no hegemony/betrayal collapse (`backend/game_logic/diplomacy.py:1634-1668`) | MISMATCH |
| Composite floor with DG-4 grievance term | `-60` when `grievance_modifier` is live (`docs/RELIABILITY_COMMITMENTS_SPEC.md:899-905`) | merge-order gate agrees (`docs/RELIABILITY_IMPLEMENTATION_PLAN.md:277-285`) | no grievance term / floor in live formula | Docs match; code absent |
| Make Amends (standard) | `200g + 1 DP`, 10-turn cooldown, strike removal (`docs/RELIABILITY_COMMITMENTS_SPEC.md:547-559`, changelog echo at `1410`) | `docs/RELIABILITY_IMPLEMENTATION_PLAN.md:177, 293` | no `reparations_cooldown` field and no `amends_offered` emitter found | Docs match; code absent |
| Make Amends (grievance variant) | `400g + 2 DP` (`docs/RELIABILITY_COMMITMENTS_SPEC.md:599, 678, 1195, 1377`) | `docs/RELIABILITY_IMPLEMENTATION_PLAN.md:195, 291` | absent from live code | Docs match; code absent |
| `decision_reason` enum | `hegemony_pressure`, `unknown_baseline`, alias-on-read `concern_pressure` (`docs/RELIABILITY_COMMITMENTS_SPEC.md:964-967`) | plan alias note agrees (`docs/RELIABILITY_IMPLEMENTATION_PLAN.md:154`) | `backend/game_logic/diplomacy.py:1828-1829, 1858` still returns `rival_pressure`; `backend/display_names.py:344` still displays it | MISMATCH |
| `end_reason_family` | `defensive_refusal_termination` added in §8.8.7a (`docs/RELIABILITY_COMMITMENTS_SPEC.md:724, 1195`) | plan agrees (`docs/RELIABILITY_IMPLEMENTATION_PLAN.md:196, 203, 291`) | no differentiated emitter/formatter found in `diplomacy.py`, `dispatch.py`, or `campaign_log.py` | Docs match; code absent |
| Coalition headline states | `BREWING` and `DECLARED` are distinct Balance-of-Europe cases (`docs/RELIABILITY_COMMITMENTS_SPEC.md:1028-1035`) | `docs/COALITION_SPEC.md:835, 841` uses the same state names | no Balance-of-Europe headline render path exists in the ledger | Docs match; render absent |
| Speaker role contract | `envoy`, `foreign_office`, `talleyrand`; `system` reserved for log-only use (`docs/COMMITMENTS_PRESENTATION_SPEC.md:403-414`) | Voice Bible covers only the 5 named diplomats; no loyalist register | live emitters mostly use unresolved `foreign_office`; no shared resolver found | MISMATCH / unresolved |

## Recommendation
REQUEST-CHANGES. Before the next coding session, the docs need one cleanup pass that does three things: remove the lingering spotlight/split-voice/N+1 language from all live normative sections, canonicalize the `commitment_paradox` rename and alias/migration rules end-to-end, and write the commitments rail contract as a single unambiguous mapping from event family to priority, icon, label, template, speaker resolver, surface, and review target. `CLAUDE.md` is already aligned, so this is not a roadmap problem; it is a contract-clarity problem. Once those fixes land and the save reference is refreshed, the implementation plan itself is in good enough shape to start coding.
