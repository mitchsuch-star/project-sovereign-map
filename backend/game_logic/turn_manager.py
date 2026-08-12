"""
Turn Manager for Project Sovereign
Handles turn progression and game loop

Includes Enemy AI turn processing:
- After player ends turn, enemy nations take their turns
- Each nation gets N actions (configurable)
- Uses same executor as player (building blocks principle)

PHASE 5.2 STRATEGIC COMMANDS:
This file will integrate strategic order processing.
See docs/PHASE_5_2_IMPLEMENTATION_PLAN.md Section 11 for integration code.

Strategic orders process at START of player turn:
1. After enemy phase completes
2. After turn advances
3. BEFORE player can issue new commands

Add _process_strategic_orders() method that calls StrategicOrderProcessor.
"""

from typing import Dict, Optional
from backend.models.world_state import WorldState, VICTORY_REGION_FRACTION
from backend.commands.strategic import StrategicOrderProcessor
from backend.utils.debug import debug_print


def get_defeat_imminent_state(world: WorldState) -> Optional[Dict]:
    """Return deterministic near-defeat state aligned with live loss rules."""
    if getattr(world, "game_over", False):
        return None

    # EC-6a sandbox: the loss rules this warning is aligned with are
    # disabled on Europe worlds — "the campaign ends" would be a false
    # promise. Gated here at the single source so the dispatch reader
    # and its DEFEAT_IMMINENT_WARNING notification go quiet together.
    if world.sandbox_mode:
        return None

    player_regions = list(world.get_player_regions())
    living_marshals = [
        marshal for marshal in world.get_player_marshals()
        if marshal.strength > 0
    ]

    region_count = len(player_regions)
    marshal_count = len(living_marshals)
    if marshal_count != 1 and region_count != 1:
        return None

    if marshal_count == 1 and region_count == 1:
        message = (
            "France is one blow from defeat: only one army and one region remain. "
            "If either is lost, the campaign ends."
        )
        severity = "critical"
        notification_title = "France Near Collapse"
    elif marshal_count == 1:
        message = (
            f"France has only one surviving army left under {living_marshals[0].name}. "
            "If it is destroyed, the campaign ends."
        )
        severity = "warning"
        notification_title = "One Army Remains"
    else:
        message = (
            f"France holds only one region: {player_regions[0]}. "
            "If it falls, the campaign ends."
        )
        severity = "warning"
        notification_title = "One Region Remains"

    return {
        "message": message,
        "severity": severity,
        "notification_title": notification_title,
        "living_marshal_count": int(marshal_count),
        "living_marshals": [marshal.name for marshal in living_marshals],
        "controlled_region_count": int(region_count),
        "controlled_regions": player_regions,
    }


class TurnManager:
    """
    Manages turn progression and game state updates.

    Turn cycle:
    1. Start turn (apply income, check events)
    2. Player commands
    3. End turn (resolve actions, advance turn)
    4. Check victory/defeat
    """

    def __init__(self, world: WorldState, executor=None):
        """Initialize turn manager with world state and optional executor."""
        self.world = world
        self.executor = executor  # CommandExecutor for strategic orders (Phase 5.2)

    def end_turn(self, game_state: Optional[Dict] = None) -> Dict:
        """
        End turn and advance.

        Processes:
        1. Enemy AI turns (all enemy nations take actions)
        2. Tactical state processing (drill, fortify, retreat for ALL marshals)
        3. Turn advancement
        4. Autonomous marshal actions (at START of new turn, before player acts)
        5. Victory/defeat check

        Args:
            game_state: Game state dict for executor (required for enemy AI)
        """
        old_turn = self.world.current_turn

        # C3 fix: Prevent double end_turn when auto-advance already processed this turn.
        # Scenario: auto-advance fires on last AP (executor.py), ending turn N → N+1.
        # Then player's "end turn" command arrives, calling end_turn() again on turn N+1.
        # The _auto_advanced_to_turn flag is set by auto-advance and cleared by any
        # non-end-turn player action, so it only blocks the immediate double-end.
        # July 2026 AI audit: the guard also CONSUMES the flag — a turn-number
        # check alone cannot distinguish the stale duplicate end-turn from a
        # deliberate "pass the new turn" press, and the flag previously only
        # cleared on non-end-turn commands, so End Turn soft-locked until the
        # player issued some other command. Now the first press after an
        # auto-advance is absorbed (the stale-duplicate case) and any further
        # press genuinely ends the new turn.
        if self.world._auto_advanced_to_turn >= old_turn:
            self.world._auto_advanced_to_turn = 0
            debug_print(f"[C3 GUARD] turn {old_turn} already auto-advanced, absorbing duplicate end-turn")
            return {
                "turn_ended": old_turn,
                "next_turn": self.world.current_turn,
                "victory_check": {"game_over": False, "result": None, "reason": ""},
                "message": (
                    f"The turn already advanced to {self.world.current_turn} when your last "
                    f"action point was spent. Order 'end turn' again to pass turn "
                    f"{self.world.current_turn}."
                ),
                "events": [],
            }

        # ════════════════════════════════════════════════════════════
        # CURRENT-TURN OFFER LAPSE — before enemy phase / AI diplomacy
        # Offers that the player did not answer this turn auto-lapse.
        # ════════════════════════════════════════════════════════════
        lapsed_offers = self.world.dialogue_manager.lapse_pending_offers()
        if lapsed_offers:
            self.world.incoming_proposal_popup = None  # Clear paired popup cache
            from backend.notifications import DIPLOMATIC_PROPOSAL
            from backend.game_logic.ai_diplomacy import (
                apply_acceptance_cooldown, apply_lapse_type_cooldown,
            )
            self.world.notifications.dismiss_by_type(DIPLOMATIC_PROPOSAL)
            lapsed_nations = set()
            for lapse in lapsed_offers:
                nation = lapse["nation"]
                if nation and nation not in lapsed_nations:
                    # Treat unanswered offers like a soft deferral so the same
                    # nation cannot immediately resend during this end-turn.
                    apply_acceptance_cooldown(nation, self.world)
                    lapsed_nations.add(nation)
                # W6-10 anti-monotony: an ignored ask of type T also blocks
                # T itself for 6 turns (stable P-rule label from the
                # dialogue context — never the rewritten terms type).
                if nation:
                    apply_lapse_type_cooldown(
                        nation, lapse.get("proposal_type", ""), self.world)
                self.world.log_event({
                    "type": "offer_lapsed",
                    "nation": nation,
                    "offer_type": lapse["offer_type"],
                    "proposal_type": lapse["proposal_type"],
                    "turn": int(self.world.current_turn),
                })

        # ════════════════════════════════════════════════════════════
        # JEALOUSY v3.2 — AUTONOMOUS GLORY ATTACKS (spec §7, §0.2 item 7)
        # Warned-and-unrestrained aggressive marshals attack as the turn
        # closes, BEFORE the enemy phase — the enemy answers after. Any
        # player order to the marshal this turn already cleared the
        # warning (executor hook).
        # ════════════════════════════════════════════════════════════
        jealousy_attack_results = []
        if game_state and hasattr(self, 'executor'):
            from backend.game_logic import jealousy as _jealousy
            jealousy_attack_results = _jealousy.process_autonomous_attacks(
                self.world, self.executor, game_state)

        # C3 fix: Track whether advance_turn has been called this cycle
        _advanced = False

        # ════════════════════════════════════════════════════════════
        # BUG #2 FIX: CHECK VICTORY BEFORE ENEMY PHASE
        # If game is already over (player won/lost), skip enemy phase
        # ════════════════════════════════════════════════════════════
        pre_enemy_victory_check = self._check_victory_conditions()
        if pre_enemy_victory_check["game_over"]:
            debug_print(f"\n[GAME OVER] {pre_enemy_victory_check['reason']} - skipping enemy phase")
            self.world.game_over = True
            self.world.victory = pre_enemy_victory_check["result"]
            # Skip to turn advancement without enemy phase
            self.world.advance_turn()
            _advanced = True
            tactical_events = self.world.get_last_tactical_events()
            result = {
                "turn_ended": old_turn,
                "next_turn": self.world.current_turn,
                "victory_check": pre_enemy_victory_check,
                "message": f"Turn {old_turn} complete - {pre_enemy_victory_check['reason']}",
                "tactical_events": tactical_events,
                "lapsed_offers": lapsed_offers or [],
            }
            self._clear_game_over_modal_state()
            return result

        # ════════════════════════════════════════════════════════════
        # ENEMY AI TURN PHASE: All enemy nations take their turns
        # ════════════════════════════════════════════════════════════
        enemy_phase_results = None
        if game_state:
            enemy_phase_results = self._process_enemy_turns(game_state)

            # BUG #2 FIX: Check if enemy achieved victory during their turn
            if enemy_phase_results and enemy_phase_results.get("enemy_victory"):
                enemy_victory = enemy_phase_results["enemy_victory"]
                debug_print(f"\n[GAME OVER] {enemy_victory['message']}")
                self.world.game_over = True
                self.world.victory = "defeat"
                # Still advance turn but game is over
                if not _advanced:
                    self.world.advance_turn()
                    _advanced = True
                tactical_events = self.world.get_last_tactical_events()
                result = {
                    "turn_ended": old_turn,
                    "next_turn": self.world.current_turn,
                    "victory_check": {
                        "game_over": True,
                        "result": "defeat",
                        "reason": enemy_victory["message"]
                    },
                    "message": f"Turn {old_turn} complete - {enemy_victory['message']}",
                    "tactical_events": tactical_events,
                    "enemy_phase": enemy_phase_results,
                    "lapsed_offers": lapsed_offers or [],
                }
                self._clear_game_over_modal_state()
                return result

        # ════════════════════════════════════════════════════════════
        # AI DIPLOMATIC PHASE (Phase 8 Session 4)
        # Each AI nation evaluates whether to propose a treaty.
        # Runs AFTER enemy military turns, BEFORE advance_turn.
        # Max 1 proposal delivered per turn (rest queued).
        # ════════════════════════════════════════════════════════════
        ai_proposal_delivered = None
        if game_state and not self.world.game_over:
            ai_proposal_delivered = self._process_ai_diplomatic_phase()

        # ════════════════════════════════════════════════════════════
        # STRATEGIC ORDER EXECUTION (Phase 5.2-C)
        # Process player marshals' multi-turn strategic orders.
        # Must run BEFORE advance_turn() to see battles_this_turn
        # for cannon fire detection (advance_turn clears battles).
        # ════════════════════════════════════════════════════════════
        strategic_reports = []
        if game_state and hasattr(self, 'executor'):
            strategic_exec = StrategicOrderProcessor(self.executor)
            strategic_reports = strategic_exec.process_strategic_orders(
                self.world, game_state)

        # ════════════════════════════════════════════════════════════
        # JEALOUSY v3.2 — THE ONCE-PER-TURN PASS (spec §0.2 item 5)
        # After the enemy phase and strategic orders (every battle of the
        # cycle has processed its relationships; per-turn action flags are
        # still live), BEFORE advance_turn (so the Literal intel boost
        # lands in this advance's calculate_visibility). Covers ALL
        # nations — Building Blocks, spec §9b.
        # ════════════════════════════════════════════════════════════
        from backend.game_logic import jealousy as _jealousy_pass
        _jealousy_pass.process_turn(self.world)

        # ════════════════════════════════════════════════════════════
        # ADVANCE TURN (includes tactical state processing!)
        # WorldState._advance_turn_internal() now handles:
        # - Tactical states (drill/fortify/retreat) for ALL marshals
        # - Income application
        # - Action reset
        # ════════════════════════════════════════════════════════════
        if not _advanced:
            self.world.advance_turn()
            _advanced = True
        else:
            debug_print(f"[WARNING] Double advance_turn prevented in end_turn! current_turn={self.world.current_turn}")

        # ════════════════════════════════════════════════════════════
        # V2-89 → R12C: Promote from queue if current slot is empty
        # Priority: commitment_paradox > vassal_rebellion > sabotage > ai_proposal
        # ════════════════════════════════════════════════════════════
        self.world.dialogue_manager.promote_if_empty()

        # Get tactical events that were processed during advance
        tactical_events = self.world.get_last_tactical_events()
        debug_print(f"[TURN_MANAGER DEBUG] Retrieved {len(tactical_events)} tactical events")

        # ════════════════════════════════════════════════════════════
        # CAPITAL PROXIMITY ALERT: Warn when enemy enters capital-adjacent region
        # ════════════════════════════════════════════════════════════
        capital_alerts = self._check_capital_proximity()
        tactical_events.extend(capital_alerts)
        for i, evt in enumerate(tactical_events):
            debug_print(f"  Event {i}: type={evt.get('type')}, has_message={bool(evt.get('message'))}")

        # ════════════════════════════════════════════════════════════
        # AUTONOMOUS MARSHALS: Process at START of new turn (Phase 2.5)
        # Autonomous player marshals act BEFORE player can issue commands
        # Each gets 1 action using Enemy AI decision tree
        # ════════════════════════════════════════════════════════════
        autonomous_report = None
        if game_state:
            autonomous_report = self._process_autonomous_marshals(game_state)

        # Check victory/defeat conditions
        victory_check = self._check_victory_conditions()

        if victory_check["game_over"]:
            self.world.game_over = True
            self.world.victory = victory_check["result"]

        result = {
            "turn_ended": old_turn,
            "next_turn": self.world.current_turn,
            "victory_check": victory_check,
            "message": f"Turn {old_turn} complete",
            "lapsed_offers": lapsed_offers or [],
        }

        # Combine all events
        all_events = []
        if tactical_events:
            all_events.extend(tactical_events)
            result["tactical_events"] = tactical_events

        # Add enemy phase results
        if enemy_phase_results:
            result["enemy_phase"] = enemy_phase_results

        # Add autonomous marshal report (Phase 2.5)
        if autonomous_report:
            result["show_independent_command_report"] = autonomous_report.get("show_independent_command_report", False)
            result["independent_command_report"] = autonomous_report.get("independent_command_report", [])

        # Add AI diplomatic proposal if delivered (Phase 8 Session 4)
        if ai_proposal_delivered:
            result["ai_proposal"] = ai_proposal_delivered

        # Add strategic order reports (Phase 5.2-C)
        if strategic_reports:
            result["strategic_reports"] = strategic_reports
            # Surface cannon fire and other interrupts into main events list
            # so the frontend can display them alongside tactical events
            for report in strategic_reports:
                interrupt_type = report.get("interrupt_type") or report.get("interrupt")
                if interrupt_type == "cannon_fire":
                    all_events.append({
                        "type": "cannon_fire_redirect",
                        "marshal": report.get("marshal", "Unknown"),
                        "battle_location": report.get("battle_location", report.get("to", "")),
                        "action_taken": report.get("action_taken", "redirect"),
                        "message": report.get("message", ""),
                    })
                elif report.get("order_status") in ("active", "continues", "completed"):
                    all_events.append({
                        "type": "strategic_progress",
                        "marshal": report.get("marshal", "Unknown"),
                        "command": report.get("command", ""),
                        "order_status": report.get("order_status"),
                        "message": report.get("message", ""),
                    })

        # ════════════════════════════════════════════════════════════
        # PT-F1 — THE AUTONOMOUS ATTACK STOPS BEING A RUMOUR.
        #
        # `process_autonomous_attacks` returns the full executor result
        # for every battle it fires — message, `events[0]` of type
        # `battle` with `.diorama` nested, `battle_report`,
        # `reinforcement_messages` — and it was assigned to a local
        # NOTHING read. Measured turn 5->6: the player was told "Murat,
        # hungry for glory, has attacked Archduke John on his own
        # initiative." and nothing else. No battle event, no report, no
        # casualties, no diorama. Murat went 21,384 -> 17,997 men and
        # morale 100 -> 81 with no supply event to explain it. Reproduced
        # on ALL FOUR autonomous attacks of the campaign.
        #
        # This is the marquee payoff of the whole Jealousy system — a
        # marshal defying the Emperor — and it landed as hearsay.
        #
        # Threaded in the ENEMY-PHASE shape (Route B), because that is
        # the transport whose renderers already read `battle_report` and
        # `events[*].diorama`; the strategic-report renderer, the other
        # candidate, shows only `message` and would silently drop both.
        # `new_state` is stripped — the standing serialization rule.
        # ════════════════════════════════════════════════════════════
        if jealousy_attack_results:
            _autonomous = []
            for _res in jealousy_attack_results:
                if not isinstance(_res, dict):
                    continue
                _autonomous.append({
                    key: value for key, value in _res.items()
                    if key != "new_state"
                })
            if _autonomous:
                result["jealousy_attacks"] = _autonomous

        if all_events:
            result["events"] = all_events

        return result

    # R12C: _pop_dialogue_queue() replaced by world.dialogue_manager.promote_if_empty()
    # Priority dict consolidated into DialogueManager.DIALOGUE_PRIORITY

    def _clear_game_over_modal_state(self) -> None:
        """Clear choice-requiring modal state once game over is final.

        Session 6 cleanup: the old turn-manager popup flush was a response-shaping
        workaround. It also happened to clear stuck dialogues. Keep the state
        cleanup, but stop smuggling popup payloads through raw end_turn results.
        """
        while self.world.dialogue_manager.peek():
            self.world.dialogue_manager.pop()

        # Choice popups cannot be acted on after game_over because command
        # endpoints reject further input. Clear them instead of surfacing stale
        # modal state ahead of the game-over screen.
        self.world.incoming_proposal_popup = None
        self.world.diplomatic_objection_popup = None
        self.world.diplomatic_sabotage_popup = None
        self.world.vassal_rebellion_imminent_popup = None
        self.world.vassal_rebellion_imminent_popups = []
        self.world.coalition_popup = None
        self.world.commitment_paradox_popup = None
        self.world.pending_capture_choice = None

    def _process_ai_diplomatic_phase(self) -> Optional[Dict]:
        """Process AI diplomatic proposals for all enemy nations.

        Phase 8 Session 4: Each AI nation evaluates P1-P7 triggers.

        F8 fix: hegemony-pressure bandwagon proposals fire on a GLOBAL condition
        (the player crossing a bloc-share band), so every eligible minor would
        deliver an identical open-borders proposal in the same turn (7 at once
        observed). Those bandwagon proposals are capped per turn; the remainder
        simply re-evaluate on later turns. War/peace/armistice proposals (P1-P8)
        are uncapped — only the shared-trigger bandwagon flood is throttled.

        Returns the last delivered dialogue dict if any were created, None otherwise.
        """
        if self.world.game_over:
            return None

        from backend.game_logic.ai_diplomacy import (
            process_diplomatic_phase, deliver_ai_proposal,
        )

        world = self.world
        active = set(world.get_active_nations())  # DLF-11
        enemy_nations = [n for n in getattr(world, 'enemy_nations', []) if n in active]
        delivered = None

        # Evaluate each AI nation — all proposals go through deliver_ai_proposal
        # which calls dialogue_manager.push() (auto-queues when slot is occupied)
        MAX_BANDWAGON_PER_TURN = 2
        bandwagon_delivered = 0
        # AI-2 §4.2c: intent asks carry their OWN world-wide budget —
        # sized so the §4.2b marquee case (both belligerents courting
        # France the same turn) can never be starved by an unrelated
        # bandwagon flood. An intent ask NEVER counts against the
        # bandwagon cap (whatever its derived decision_reason), and
        # vice versa. Ultimatums stay exempt from both.
        from backend.game_logic.ai_diplomacy import (
            INTENT_ASK_BUDGET_PER_TURN,
        )
        intent_delivered = 0
        for nation in enemy_nations:
            proposal = process_diplomatic_phase(nation, world)
            if not proposal:
                continue
            # NA-1: agenda_pursuit outranks hegemony_pressure in the reason
            # ladder but is the same pressure-driven flood shape — both
            # count against the bandwagon throttle.
            # NA-5 §8: ultimatums are EXEMPT — the rung already caps them at
            # one live world-wide + a 15-turn per-nation cooldown SET AT
            # ISSUE, so a throttle deferral here would silently eat the
            # court's one ultimatum for 15 turns.
            if proposal.get("recipient") not in (None, world.player_nation):
                # A court-to-court envelope never touches the mailbox —
                # it must not consume either mailbox budget (review fix).
                pass
            elif proposal.get("intent_ask"):
                if intent_delivered >= INTENT_ASK_BUDGET_PER_TURN:
                    debug_print(f"[DIPLOMACY] {nation} intent ask deferred (§4.2c budget)")
                    continue
                intent_delivered += 1
            elif (proposal.get("decision_reason") in ("hegemony_pressure",
                                                      "agenda_pursuit")
                    and proposal.get("proposal_type") != "ultimatum"):
                if bandwagon_delivered >= MAX_BANDWAGON_PER_TURN:
                    debug_print(f"[DIPLOMACY] {nation} bandwagon proposal deferred (per-turn cap)")
                    continue
                bandwagon_delivered += 1
            result = deliver_ai_proposal(proposal, world)
            if delivered is None:
                delivered = result
            debug_print(f"[DIPLOMACY] {nation} delivered proposal: {proposal.get('proposal_type')}")

        # ════════════════════════════════════════════════════════════
        # VASSAL COURTING (Phase 8 Session 5)
        # AI nations attempt to court player's vassals
        # ════════════════════════════════════════════════════════════
        if world.vassals:
            from backend.game_logic.vassal import attempt_vassal_courting
            for nation in enemy_nations:
                courting_events = attempt_vassal_courting(world, nation)
                for event in courting_events:
                    debug_print(f"[VASSAL COURTING] {event.get('message', '')}")

        # ════════════════════════════════════════════════════════════
        # THE DEFECTION (VS-6, VASSAL_DEEPENING_SPEC §7)
        # A nation at war with a lord BRIBES a wavering satellite into
        # changing sides. Runs immediately after courting and resolves
        # IMMEDIATELY — the bribed vassal is transferred/freed before
        # advance_turn's cascade/rebellion chain ever sees it (structural
        # double-fire guard). Unlike courting's debug-print sink, defection
        # events ride notification + dispatch + campaign log inside the
        # domain function.
        # ════════════════════════════════════════════════════════════
        if world.vassals:
            from backend.game_logic.vassal import attempt_vassal_bribe
            for nation in enemy_nations:
                if not world.vassals:
                    break
                bribe_events = attempt_vassal_bribe(world, nation)
                for event in bribe_events:
                    debug_print(f"[VASSAL DEFECTION] {event.get('message', '')}")

        # ════════════════════════════════════════════════════════════
        # SETTLEMENT OFFER PRODUCER + UI PROMOTION
        # (SC-5 reversal / Slice G1 commit 2)
        # AI side-leaders produce incoming settlement offers for the
        # player on active multi-party wars. The producer writes into
        # `world.pending_settlement_dialogues`; `promote_pending_
        # settlement_offers` drains that into the dialogue_manager
        # mailbox so the Godot popup / `/pending_envoy` / `/mailbox`
        # routes can surface the offer. Notification + popup-queue
        # push happens here too so the first encounter auto-shows.
        # Cooldowns and one-active-offer-per-war guards are enforced
        # inside the producer.
        # ════════════════════════════════════════════════════════════
        from backend.game_logic.ai_diplomacy import (
            process_mediation_offers,
            process_settlement_offer_phase,
        )
        from backend.game_logic.settlement_offers import (
            promote_pending_settlement_offers,
        )
        from backend.notifications import (
            INCOMING_SETTLEMENT_OFFER,
            NotificationPriority,
            create_notification,
        )
        produced_offers = process_settlement_offer_phase(world)
        # AI-5c: the Arbiter's Offer rides the SAME pending store, so the
        # promotion / notification / popup plumbing below serves it
        # unchanged — a mediated offer is an incoming settlement offer
        # with a named third-court provenance.
        produced_offers = produced_offers + process_mediation_offers(world)
        promoted_offers = promote_pending_settlement_offers(world)
        for offer in produced_offers:
            debug_print(
                "[SETTLEMENT OFFER] "
                f"{offer.get('proposer_nation')} offered settlement on "
                f"{offer.get('war_id')} (offer_id={offer.get('offer_id')})"
            )
        for offer in promoted_offers:
            popup_payload = offer.get("popup_payload") or {}
            proposer = str(offer.get("proposer_nation") or "Unknown")
            war_label = str(
                popup_payload.get("war_label")
                or offer.get("war_id")
                or "settlement"
            )
            amount = int(popup_payload.get("amount") or 0)
            message = (
                f"{proposer} has offered terms to settle {war_label}."
                + (f" Asking {amount} gold." if amount else "")
            )
            world.notifications.add(
                create_notification(
                    notification_type=INCOMING_SETTLEMENT_OFFER,
                    priority=NotificationPriority.HIGH,
                    title=f"Settlement offer from {proposer}",
                    message=message,
                    turn_created=int(getattr(world, "current_turn", 0)),
                    details={
                        "war_id": str(offer.get("war_id") or ""),
                        "offer_id": str(offer.get("offer_id") or ""),
                        "proposer_nation": proposer,
                        "amount": amount,
                        "review_target": "incoming_settlement_offer_popup",
                    },
                )
            )
            # Push the popup payload to the popup queue so the very
            # first response cycle after producer fires auto-shows the
            # offer. The mailbox path remains available for queue
            # browsing / dismissed-popup recovery.
            popup_queue = getattr(world, "_popup_queue", None)
            if popup_queue is not None and popup_payload:
                popup_queue.push(
                    "incoming_settlement_offer_popup", dict(popup_payload)
                )
            # Settlement-offer arrival dispatch line — categorized as a
            # diplomacy event so the dispatch panel groups it with
            # other settlement family beats.
            dispatch_events = getattr(world, "pending_dispatch_events", None)
            if isinstance(dispatch_events, list):
                dispatch_events.append({
                    "type": "settlement_offer_arrival",
                    "war_id": str(offer.get("war_id") or ""),
                    "offer_id": str(offer.get("offer_id") or ""),
                    "proposer_nation": proposer,
                    "war_label": war_label,
                    "amount": amount,
                    "message": message,
                    "turn": int(getattr(world, "current_turn", 0)),
                    "event_family": "diplomatic",
                })

        return delivered

    def _process_autonomous_marshals(self, game_state: Dict) -> Dict:
        """
        Process autonomous player marshals at START of player's turn.

        Phase 2.5: Autonomous marshals use the Enemy AI decision tree
        but aligned with the player's nation (France). Each gets 1 action.

        For each autonomous marshal:
        1. Execute AI-decided action (1 action per marshal)
        2. Track performance (battles won/lost, regions captured)
        3. Decrement autonomy_turns
        4. If turns <= 0, evaluate performance and end autonomy

        Returns:
            Dict with independent_command_report for Godot popup
        """
        from backend.ai.enemy_ai import EnemyAI
        from backend.commands.executor import CommandExecutor

        # DEBUG: Log all marshals and their autonomy state
        debug_print("\n" + "=" * 70)
        debug_print("🔍 DEBUG: Checking for autonomous marshals")
        debug_print("=" * 70)
        for m in self.world.marshals.values():
            auto_status = "AUTONOMOUS" if getattr(m, 'autonomous', False) else "normal"
            debug_print(f"  {m.name} ({m.nation}): {auto_status}, turns={getattr(m, 'autonomy_turns', 0)}")

        autonomous_marshals = [
            m for m in self.world.marshals.values()
            if m.nation == self.world.player_nation and getattr(m, 'autonomous', False)
        ]

        debug_print(f"🔍 DEBUG: Found {len(autonomous_marshals)} autonomous player marshals")

        if not autonomous_marshals:
            debug_print("🔍 DEBUG: No autonomous marshals - skipping report")
            return {
                "show_independent_command_report": False,
                "independent_command_report": []
            }

        debug_print("\n" + "=" * 70)
        debug_print("INDEPENDENT COMMAND REPORT")
        debug_print("=" * 70)

        executor = CommandExecutor()
        ai = EnemyAI(executor)

        report = []

        for marshal in autonomous_marshals:
            debug_print(f"\n--- {marshal.name} (Autonomous, {marshal.autonomy_turns} turns remaining) ---")

            # V2-26: Wrap per-marshal body in try/except so one crash doesn't kill the turn
            try:
                # Execute AI action for this marshal (aligned with player's nation)
                action_result = ai.decide_single_action(
                    marshal=marshal,
                    nation=self.world.player_nation,  # France - only attacks enemies of France
                    world=self.world,
                    game_state=game_state
                )

                # Track performance based on result
                if action_result and action_result.get("result"):
                    result = action_result["result"]

                    # Check for battle outcomes
                    if result.get("battle_won"):
                        marshal.autonomous_battles_won += 1
                        debug_print(f"  Battle won! (Total: {marshal.autonomous_battles_won})")
                    elif result.get("battle_lost"):
                        marshal.autonomous_battles_lost += 1
                        debug_print(f"  Battle lost! (Total: {marshal.autonomous_battles_lost})")

                    # Check for region capture
                    if result.get("region_captured"):
                        marshal.autonomous_regions_captured += 1
                        debug_print(f"  Region captured! (Total: {marshal.autonomous_regions_captured})")

                # Decrement autonomy turns
                marshal.autonomy_turns -= 1

                # Build report entry
                report_entry = {
                    "marshal": marshal.name,
                    "action": action_result.get("action") if action_result else "wait",
                    "target": action_result.get("target") if action_result else None,
                    "result": action_result.get("result") if action_result else {"message": "No action taken"},
                    "turns_remaining": marshal.autonomy_turns,
                    "performance": {
                        "battles_won": marshal.autonomous_battles_won,
                        "battles_lost": marshal.autonomous_battles_lost,
                        "regions_captured": marshal.autonomous_regions_captured
                    }
                }

                # Check if autonomy is ending
                if marshal.autonomy_turns <= 0:
                    end_result = self._end_autonomy(marshal)
                    report_entry["autonomy_ended"] = True
                    report_entry["end_result"] = end_result
                    debug_print(f"\n  AUTONOMY ENDED: {end_result['message']}")

            except Exception:
                import traceback
                debug_print(f"[ERROR] Autonomous marshal {marshal.name} crashed: {traceback.format_exc()}")
                marshal.autonomy_turns -= 1
                report_entry = {
                    "marshal": marshal.name,
                    "action": "error",
                    "target": None,
                    "result": {"message": f"{marshal.name} encountered an error during independent command"},
                    "turns_remaining": marshal.autonomy_turns,
                    "performance": {
                        "battles_won": marshal.autonomous_battles_won,
                        "battles_lost": marshal.autonomous_battles_lost,
                        "regions_captured": marshal.autonomous_regions_captured
                    }
                }

            report.append(report_entry)

        return {
            "show_independent_command_report": True,
            "independent_command_report": report
        }

    def _end_autonomy(self, marshal) -> Dict:
        """
        Evaluate marshal performance and restore control.

        Performance tiers (RELATIVE gains from ~20 floor, prevents exploit):
        - Spectacular: 2+ battles won OR 1+ region captured → +40 trust, +10 authority
        - Success: positive score → +25 trust
        - Neutral: zero score → +15 trust
        - Failure: negative score → +5 trust

        Note: Vindication does NOT change during autonomy.
        Vindication tracks "marshal objected to player's order and was right/wrong."
        During autonomy there are no player orders - trust changes capture outcomes.

        Returns:
            Result dict with message, tier, and new trust
        """
        # Log trust before change
        old_trust = marshal.trust.value
        debug_print(f"\n[AUTONOMY END] {marshal.name}")
        debug_print(f"  Trust before: {old_trust}")
        debug_print(f"  Performance: {marshal.autonomous_battles_won}W / {marshal.autonomous_battles_lost}L / {marshal.autonomous_regions_captured} captured")

        marshal.autonomous = False

        # Calculate performance score
        score = (
            marshal.autonomous_battles_won * 2 +
            marshal.autonomous_regions_captured * 3 -
            marshal.autonomous_battles_lost * 2
        )

        spectacular = (
            marshal.autonomous_battles_won >= 2 or
            marshal.autonomous_regions_captured >= 1
        )

        # All RELATIVE gains (not flat values) to prevent exploit
        if spectacular:
            marshal.trust.modify(+40)  # 20 → 60 (Reliable, not fully Trusted)
            self.world.authority_tracker.modify_authority(+10)
            message = f"{marshal.name} has proven themselves spectacularly! Trust +40, Authority +10."
            tier = "spectacular"
        elif score > 0:
            marshal.trust.modify(+25)  # 20 → 45 (Recovering)
            message = f"{marshal.name} performed well independently. Trust +25."
            tier = "success"
        elif score == 0:
            marshal.trust.modify(+15)  # 20 → 35 (Still strained)
            message = f"{marshal.name} returns to your command. Trust +15."
            tier = "neutral"
        else:
            marshal.trust.modify(+5)   # 20 → 25 (Barely above floor)
            message = f"{marshal.name} struggled but shows humility. Trust +5."
            tier = "failure"

        new_trust = marshal.trust.value

        # Log trust after change
        debug_print(f"  Trust after: {new_trust} (score={score}, tier={tier})")

        # Reset tracking fields
        marshal.autonomous_battles_won = 0
        marshal.autonomous_battles_lost = 0
        marshal.autonomous_regions_captured = 0
        marshal.autonomy_turns = 0
        marshal.autonomy_reason = ""

        return {
            "message": message,
            "tier": tier,
            "new_trust": int(new_trust),
            "old_trust": int(old_trust),
            "score": score
        }

    def _process_enemy_turns(self, game_state: Dict) -> Dict:
        """
        Process all enemy nations' turns.

        Each enemy nation gets actions based on nation_actions config.
        Uses EnemyAI decision tree to select actions.
        Executes through same executor as player.

        Args:
            game_state: Game state dict for executor

        Returns:
            Dict with results for each nation
        """
        from backend.ai.enemy_ai import EnemyAI
        from backend.commands.executor import CommandExecutor

        debug_print("\n" + "=" * 70)
        debug_print("ENEMY PHASE")
        debug_print("=" * 70)

        # Create executor and AI
        executor = CommandExecutor()
        ai = EnemyAI(executor)

        results = {
            "nations": {},
            "total_actions": 0,
            "summary": []
        }

        # V2-20/21: Decrement cooldowns ONCE before processing all nations
        # (was inside per-nation loop → 4x tick bug)
        ai.decrement_all_cooldowns(self.world)

        # Process each enemy nation
        for nation in self.world.enemy_nations:
            # BUG #2 FIX: Check if victory already achieved before processing more nations
            existing_victory = self._check_enemy_victory()
            if existing_victory:
                debug_print(f"\n[ENEMY VICTORY] {existing_victory['message']} - stopping enemy phase")
                results["enemy_victory"] = existing_victory
                break

            # Check if nation has any marshals
            marshals = self.world.get_marshals_by_nation(nation)
            if not marshals:
                debug_print(f"\n{nation} has no marshals remaining - skipping")
                results["summary"].append(f"{nation}: No marshals (eliminated?)")

                # Trigger 7: Enemy nation eliminated notification (first detection only)
                if nation not in self.world.eliminated_nations_notified:
                    self.world.eliminated_nations_notified.add(nation)
                    from backend.notifications import (
                        create_notification, NotificationPriority, NATION_ELIMINATED,
                    )
                    self.world.notifications.add(create_notification(
                        notification_type=NATION_ELIMINATED,
                        priority=NotificationPriority.NORMAL,
                        title=f"{nation} eliminated",
                        message=f"{nation} has no marshals remaining. Their forces are spent.",
                        turn_created=int(self.world.current_turn),
                        details={"nation": nation},
                    ))

                continue

            # Process this nation's turn (wrapped for resilience)
            try:
                nation_results = ai.process_nation_turn(nation, self.world, game_state)

                # ════════════════════════════════════════════════════════════
                # AI ADMIN PHASE (Phase 6.2.G): Economic actions after military
                # ════════════════════════════════════════════════════════════
                admin_results = ai.execute_admin_phase(nation, self.world, game_state)
                if admin_results:
                    nation_results.extend(admin_results)
            except Exception:
                import traceback
                debug_print(f"[ERROR] {nation} turn crashed: {traceback.format_exc()}")
                # V2-19: Surface error to player instead of swallowing silently
                nation_results = [{
                    "action": "error",
                    "message": f"{nation} encountered an error during their turn",
                    "battle_message": ""
                }]
                admin_results = []

            results["nations"][nation] = {
                "actions": nation_results,
                "action_count": len(nation_results),
                "admin_actions": len(admin_results) if admin_results else 0
            }
            results["total_actions"] += len(nation_results)

            # Build summary for this nation (human-readable action names).
            # Internal action names must NEVER reach the frontend — translate before sending.
            action_display_names = {
                "attack": "attacks",
                "move": "moves",
                "defend": "defends",
                "fortify": "fortifies",
                "unfortify": "unfortifies",
                "drill": "drills",
                "stance_change": "changes stance",
                "retreat": "retreats",
                "wait": "holds position",
                "recruit": "recruits",
                "scout": "scouts",
                "build": "builds",
                "repair": "repairs",
            }
            nation_summary = f"{nation} ({len(nation_results)} actions)"
            if nation_results:
                action_types = []
                for r in nation_results:
                    ai_act = r.get("ai_action", {})
                    raw = ai_act.get("action", "unknown")
                    marshal = ai_act.get("marshal", "")
                    display = action_display_names.get(raw, raw.replace("_", " "))
                    action_types.append(f"{marshal} {display}" if marshal else display)
                nation_summary += f": {', '.join(action_types)}"
            results["summary"].append(nation_summary)

        # V2b: Resolve defensive vindication for player marshals attacked during enemy phase
        self._resolve_defensive_vindication()

        # Final check for enemy win condition (if not already found)
        if "enemy_victory" not in results:
            enemy_victory = self._check_enemy_victory()
            if enemy_victory:
                results["enemy_victory"] = enemy_victory

        debug_print("\n" + "=" * 70)
        debug_print("ENEMY PHASE COMPLETE")
        debug_print(f"Total actions: {results['total_actions']}")
        debug_print("=" * 70)

        return results

    def _resolve_defensive_vindication(self) -> None:
        """V2b: Resolve defensive vindication after enemy phase.

        If an enemy attacked a player marshal with pending defensive vindication:
        - Marshal held (not broken, not retreating) → vindication +1
        - Marshal lost (broken or retreating) → vindication -1
        - First battle only — entry cleared after resolution

        Uses battles_this_turn to detect which player marshals were attacked.
        """
        if not hasattr(self.world, 'vindication_tracker'):
            return
        pending = self.world.vindication_tracker.pending_defensive_vindication
        if not pending:
            return

        # Check which player marshals were involved in battles this turn
        resolved = []
        for marshal_name in list(pending.keys()):
            marshal = self.world.get_marshal(marshal_name)
            if marshal is None:
                # Marshal destroyed — clear entry
                resolved.append(marshal_name)
                continue

            # Check if this marshal was attacked (appeared as defender in any battle)
            was_attacked = False
            for battle in getattr(self.world, 'battles_this_turn', []):
                # battles_this_turn stores {"location", "attacker", "defender", "outcome"}
                if battle.get("defender") == marshal_name:
                    was_attacked = True
                    break

            if was_attacked:
                # Resolve: held = not broken and not retreating
                if getattr(marshal, 'broken', False) or getattr(marshal, 'retreating', False):
                    # Marshal lost — vindication -1
                    marshal.vindication_score = max(-5, marshal.vindication_score - 1)
                else:
                    # Marshal held — vindication +1
                    marshal.vindication_score = min(5, marshal.vindication_score + 1)
                # 6C-2: Reset vindication decay timer after defensive resolution
                self.world.vindication_tracker.last_change_turn[marshal_name] = self.world.current_turn
                resolved.append(marshal_name)

        for name in resolved:
            pending.pop(name, None)

    def _check_enemy_victory(self) -> Optional[Dict]:
        """
        Check if any enemy nation has achieved victory conditions.

        Enemy wins if they control 14+ regions (same as player threshold).

        Returns:
            Dict with victory info, or None if no enemy victory
        """
        # EC-6a sandbox: no enemy conquest victory on Europe worlds either
        # (called once per enemy nation inside the enemy phase + a final
        # sweep — cheap early out, keeps enforcement symmetric).
        if self.world.sandbox_mode:
            return None

        victory_threshold = max(1, int(len(self.world.regions) * VICTORY_REGION_FRACTION))
        active = set(self.world.get_active_nations())  # DLF-11
        for nation in self.world.enemy_nations:
            if nation not in active:
                continue
            regions = self.world.get_nation_regions(nation)
            if len(regions) >= victory_threshold:
                return {
                    "nation": nation,
                    "regions_controlled": len(regions),
                    "message": f"{nation} has conquered Europe! They control {len(regions)} regions."
                }
        return None

    def _check_capital_proximity(self) -> list:
        """
        Check if any enemy marshal is adjacent to the player's capital.
        Returns list of alert events.

        Dedup: Only alerts if the enemy marshal hasn't triggered an alert
        in the last 3 turns (prevents spam when enemy sits near capital).
        """
        alerts = []
        last_alerts = getattr(self.world, '_capital_proximity_last_alert', {})
        current_turn = self.world.current_turn

        # Golden Rule 8: iterate the player's cached region index and use the
        # per-region marshal index for the adjacency probe (Slice 8 audit).
        for region_name in self.world.get_player_regions():
            region = self.world.regions[region_name]
            if not region.is_capital:
                continue
            for adj_name in region.adjacent_regions:
                enemies_adj = [
                    m for m in self.world.get_marshals_in_region(adj_name)
                    if m.nation != self.world.player_nation
                    and self.world.is_at_war(self.world.player_nation, m.nation)
                    and m.strength > 0
                ]
                for enemy in enemies_adj:
                    key = f"{enemy.name}|{region.name}"
                    last_turn = last_alerts.get(key, -99)
                    if current_turn - last_turn < 3:
                        continue  # Suppress repeat within 3 turns
                    last_alerts[key] = current_turn
                    alerts.append({
                        "type": "capital_proximity_alert",
                        "capital": region.name,
                        "enemy": enemy.name,
                        "enemy_location": adj_name,
                        "enemy_strength": int(enemy.strength),
                        "message": (
                            f"Berthier: Enemy forces spotted near {region.name}! "
                            f"{enemy.name} ({enemy.strength:,} troops) at {adj_name}."
                        )
                    })

        self.world._capital_proximity_last_alert = last_alerts
        return alerts

    def _check_victory_conditions(self) -> Dict:
        """
        Check if game is over and determine result.

        EC-6a: Europe worlds are an open-ended SANDBOX — no hard win/lose
        at all (the early return below). Legacy-world conditions:

        Victory conditions:
        - Control all regions (total victory)
        - All enemy nations have 0 regions (total elimination)
        - Survive max_turns holding VICTORY_REGION_FRACTION (time victory)

        Defeat conditions:
        - All marshals destroyed
        - All territory lost (0 regions)
        - max_turns reached below the victory fraction (time defeat)
        """
        # EC-6a sandbox guard — MUST stay the first statement: it disables
        # every victory/defeat branch (incl. the max-turns time defeat) AND
        # kills the FINAL-11 full region-scan below, which this method would
        # otherwise run twice per end_turn on the 126-province map (GR8).
        # Real victory conditions → Pre-Ship Victory & Objectives Pass.
        if self.world.sandbox_mode:
            return {"game_over": False, "result": None, "reason": None}

        player_regions = self.world.get_player_regions()
        player_marshals = self.world.get_player_marshals()

        # Check defeat conditions first
        if not player_marshals or all(m.strength <= 0 for m in player_marshals):
            return {
                "game_over": True,
                "result": "defeat",
                "reason": "All armies destroyed!"
            }

        # FINAL-9: Defeat on 0 regions
        if len(player_regions) == 0:
            return {
                "game_over": True,
                "result": "defeat",
                "reason": "All territory lost!"
            }

        # PL-31: Capital-loss defeat removed. Capital can be lost via treaties
        # or conquest without ending the campaign. Defeat only on 0 armies or
        # 0 territory. If this rule is ever reinstated, reopen PL-31.

        # Check victory conditions — derived from total region count
        total = len(self.world.regions)
        if len(player_regions) >= total - 1:  # Total victory
            return {
                "game_over": True,
                "result": "victory",
                "reason": "Total conquest of Western Europe!"
            }

        # FINAL-11: Victory on total enemy elimination
        all_nations = set(r.controller for r in self.world.regions.values() if r.controller)
        enemy_nations_with_regions = all_nations - {self.world.player_nation}
        if not enemy_nations_with_regions and len(player_regions) > 0:
            return {
                "game_over": True,
                "result": "victory",
                "reason": "All enemies defeated!"
            }

        if self.world.current_turn >= self.world.max_turns:
            # Already handled in world.advance_turn(), but check here too
            if len(player_regions) >= int(total * VICTORY_REGION_FRACTION):  # Time victory
                return {
                    "game_over": True,
                    "result": "victory",
                    "reason": "Survived and control majority of Europe!"
                }
            else:
                return {
                    "game_over": True,
                    "result": "defeat",
                    "reason": "Time expired without achieving dominance"
                }

        # Game continues
        return {
            "game_over": False,
            "result": None,
            "reason": None
        }

    def get_turn_summary(self) -> Dict:
        """Get summary of current turn state.

        EC-6a: sandbox worlds OMIT the max_turns / turns_remaining countdown
        keys entirely — an open-ended campaign has no clock, and a gated
        enforcement seam with an ungated reader would render a stale
        "0 turns remaining".
        """
        summary = {
            "turn": self.world.current_turn,
            "gold": self.world.gold,
            "regions": len(self.world.get_player_regions()),
            "game_over": self.world.game_over,
            "victory": self.world.victory
        }
        if not self.world.sandbox_mode:
            summary["max_turns"] = self.world.max_turns
            summary["turns_remaining"] = self.world.max_turns - self.world.current_turn
        return summary


# Test code
if __name__ == "__main__":
    """Test turn manager."""
    debug_print("=" * 70)
    debug_print("TURN MANAGER TEST")
    debug_print("=" * 70)

    from backend.models.world_state import WorldState

    # Create world
    world = WorldState(player_nation="France")
    turn_manager = TurnManager(world)

    debug_print(f"\nStarting state: {world}")
    debug_print(f"Gold: {world.gold}")

    # Test Turn 1 — end turn directly (start_turn removed as dead code)
    debug_print("\n" + "=" * 70)
    debug_print("TURN 1")
    debug_print("=" * 70)

    end = turn_manager.end_turn()
    debug_print(f"\n{end['message']}")
    debug_print(f"Next turn: {end['next_turn']}")
    debug_print(f"Game over: {end['victory_check']['game_over']}")

    # Test Turn 2
    debug_print("\n" + "=" * 70)
    debug_print("TURN 2")
    debug_print("=" * 70)

    end = turn_manager.end_turn()
    debug_print(f"\n{end['message']}")
    debug_print(f"Gold: {world.gold}")

    # Test victory check by simulating loss of Paris
    debug_print("\n" + "=" * 70)
    debug_print("TEST: Defeat Condition (Lose Paris)")
    debug_print("=" * 70)

    paris = world.get_region("Paris")
    paris.controller = "Britain"  # Lose Paris!

    end = turn_manager.end_turn()
    debug_print(f"\nVictory check: {end['victory_check']}")

    if end['victory_check']['game_over']:
        debug_print(f"Game Over! Result: {end['victory_check']['result']}")
        debug_print(f"Reason: {end['victory_check']['reason']}")

    debug_print("\n" + "=" * 70)
    debug_print("TURN MANAGER TEST COMPLETE!")
    debug_print("=" * 70)
    debug_print("\n✓ Turn advancement working")
    debug_print("✓ Victory/defeat checking working")
