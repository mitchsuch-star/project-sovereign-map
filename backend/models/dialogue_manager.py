"""DialogueManager — centralized dialogue state management (R12).

Replaces scattered pending_diplomatic_dialogue/pending_dialogue_queue
field assignments with structured push/pop/peek operations.

Session 2 follow-up: Mailbox infrastructure added. DialogueManager is
now the SINGLE pending-diplomacy queue (diplomatic_queue eliminated).
"""

import copy
from typing import Dict, List, Optional, Callable


def _proposal_display(ptype: str) -> str:
    """PT-G5(b): the mailbox row read "Armistice Losing" while the popup
    for the SAME item read "Armistice".

    `display_names.PROPOSAL_TYPE_DISPLAY` already maps all four armistice
    variants and simply was not imported here; `.title()` on the raw key
    is what invented the second name. It reaches the player unmodified —
    `mailbox_panel.gd:125` renders `summary_text` verbatim.
    """
    from backend.display_names import PROPOSAL_TYPE_DISPLAY

    key = str(ptype or "")
    return PROPOSAL_TYPE_DISPLAY.get(key, key.replace("_", " ").title())


def _nation_display(source: str) -> str:
    """PT-G5(b), second leak in the same dict: `source` is a raw nation
    key and `mailbox_panel.gd:123` renders it with no repair."""
    from backend.display_names import display_nation

    return display_nation(str(source or ""))


# FA slice 10 flip levers.
# FA-17 / FA-N44: a counter-offer and a commitment paradox displace MAIL to
# reach the player. False restores the plain `push` (queue behind anything).
MOUNT_OVER_MAIL_ACTIVE = True
# FA-N44: the commitment paradox survives the stale sweep. False restores the
# pre-slice-10 behaviour (a crisis the player never saw is deleted silently).
PARADOX_SURVIVES_THE_STALE_SWEEP = True
PARADOX_DIALOGUE_TYPES = frozenset({"commitment_paradox", "alliance_paradox"})


class DialogueManager:
    """Manages the active dialogue slot and priority queue.

    API:
        push(dialogue)         — set current if empty, queue if occupied
        replace(dialogue)      — overwrite current (enrichment / clear-then-set)
        pop()                  — clear current, auto-promote from queue
        peek()                 — read current without side effects
        iter_queue()           — public read-only view of queued dialogues
        is_blocking()          — True if current dialogue blocks commands
        is_hard_stop()         — True if current dialogue blocks ALL commands
        is_soft_stop()         — True if current is mailbox/hybrid soft-stop
        clear_stale(turn)      — auto-dismiss expired dialogues
        promote_if_empty()     — promote from queue when current is None
        remove_matching(pred)  — filter queue + current by predicate
        get_mailbox_count()    — count of mailbox-eligible items (active + queued)
        get_mailbox_items()    — ordered list of mailbox items for inbox panel
        activate_mailbox_item(id) — swap a queued item into the active slot
    """

    QUEUE_CAP = 20
    BLOCKING_TIMEOUT_TURNS = 2  # turn_created + 2 < current → force-clear

    # ── PL-27: Dialogue type taxonomy (Session 2) ────────────────────
    # Hard-stop: blocks ALL commands until resolved.
    #
    # `alliance_paradox` is kept as a legacy alias for save replay.
    # Production emitters now use `commitment_paradox`, which owns the
    # dedicated `commitment_paradox_popup.{tscn,gd}` Godot surface.
    HARD_STOP_TYPES = frozenset({
        "force_declare_war_confirmation",
        "force_break_treaty_confirmation",
        "alliance_paradox",
        "commitment_paradox",
        "war_purpose_selection",
        "settlement_confirm",
        # PC15-3: the pair-substitute chooser was in NO taxonomy set — not
        # a hard stop, so typed commands passed through it silently while
        # its presence blocked proposals (the wedge). It is the same
        # family and same modal surface as settlement_confirm; it now
        # blocks with a NAMED subject and is answerable by typed word
        # ("confirm" / "keep") as well as by button.
        "settlement_pair_substitute_confirm",
    })
    # Current-turn offer types: AI-initiated offers that lapse at end of turn.
    # Visible via envoy badge. Do NOT block ordinary commands or end-turn.
    CURRENT_TURN_OFFER_TYPES = frozenset({
        "incoming_proposal",
        "counter_offer",
        "counter_offer_response",
        # NA-5 §8: AI ultimatums ride the same lapse-at-end-of-turn
        # transport. A lapse is NOT a rejection — no pressure marker; the
        # issue-time 15-turn cooldown keeps an ignored demand from
        # returning next season (pinned in test_nation_agendas_ultimatums).
        "incoming_ultimatum",
    })
    # Persistent mailbox types: AI-initiated offers that persist across turns
    # until accepted, rejected, or the producer cooldown / one-active-offer
    # guard removes them. Mailbox-eligible like current-turn offers but
    # `lapse_pending_offers()` and `has_current_turn_offers()` deliberately
    # exclude this set.
    #
    # SC-5 reversal commit 2 (Slice G1): `incoming_settlement_offer` is a
    # persistent mailbox type. The producer
    # (`ai_diplomacy.process_settlement_offer_phase`) writes offers into
    # `world.pending_settlement_dialogues`, the
    # `promote_pending_settlement_offers(...)` helper drains them into the
    # mailbox queue, and the player accepts / rejects / requests revision
    # via `handle_incoming_settlement_offer_action(...)`. The type also
    # stays in `SETTLEMENT_FAMILY_DIALOGUE_TYPES` so cross-war family
    # guards keep catching it.
    #
    # G2-Slice-G2b: `ally_settlement_petition` is also persistent and
    # mailbox-eligible, but it is advisory only: it never enters
    # HARD_STOP_TYPES and never blocks ordinary commands or settlement
    # ratification.
    PERSISTENT_MAILBOX_TYPES = frozenset({
        "incoming_settlement_offer",
        "ally_settlement_petition",
    })
    # Combined mailbox-eligible set: lapsing (current-turn) + persistent.
    # Downstream code references SOFT_STOP_MAILBOX_TYPES for mailbox
    # eligibility regardless of lapse semantics.
    SOFT_STOP_MAILBOX_TYPES = CURRENT_TURN_OFFER_TYPES | PERSISTENT_MAILBOX_TYPES
    # Hybrid soft-stop: does NOT block ordinary commands, but end_turn
    # should auto-default or warn if unresolved.
    HYBRID_SOFT_STOP_TYPES = frozenset({
        "sabotage_confrontation",
        "vassal_rebellion_imminent",
    })
    # Local planning flow: player-initiated, never a global blocker.
    LOCAL_PLANNING_TYPES = frozenset({
        "proposal_confirm",
        "advisory",
        "mission",
        "terms_guidance",
        "ultimatum_demand_wizard",
        "pushback_confirm",
        "proposal_execute",
        "proposal_options",
        "feasibility",
        "ultimatum_confirm",
        "conflict_alert",
        # CR-2: one-question command clarification ("Which marshal, Sire?").
        # (Also DISPOSABLE_ACTIVE_TYPES below — see that set's note.)
        # Registered ONLY from main.py's player-command path (never for AI
        # commands); any next typed input consumes it, and clear_stale
        # dismisses a lingering one at the next turn boundary.
        "command_clarification",
    })

    # ── Aug 23, 2026: what a mailbox answer may displace ────────────────
    # LOCAL_PLANNING is documented above as "never a global blocker", and for
    # ordinary commands that holds. It did NOT hold for the letter-book:
    # `activate_mailbox_item` refused outright for every LOCAL_PLANNING type,
    # so a Talleyrand `advisory` left in the active slot made every routine
    # envoy unanswerable, and the refusal ("Settle it before answering the
    # lesser courts") named nothing the player could see or act on. Measured
    # live on a turn-3 France campaign: advisory dialogue_id 6 holding the
    # slot with a Saxony letter queued behind it.
    #
    # These are the LOCAL_PLANNING types that are pure READ-OUTS — they carry
    # no staged authoring state and can be re-derived on demand, so making way
    # for a mailbox answer costs the player nothing. The wizard and confirm
    # types (`terms_guidance`, `ultimatum_demand_wizard`, `proposal_confirm`,
    # `proposal_execute`, `pushback_confirm`, `ultimatum_confirm`,
    # `proposal_options`, `mission`, `conflict_alert`) are deliberately ABSENT:
    # displacing a half-drafted set of terms would destroy the player's work
    # silently, which is a worse bug than the one being fixed. Those still
    # refuse — but by NAME now, via `active_blocker_type`.
    DISPOSABLE_ACTIVE_TYPES = frozenset({
        "advisory",
        "feasibility",
        "command_clarification",
    })

    # Single source of truth for dialogue priority (lower = higher priority).
    # Unlisted types (counter_offer_response, advisory, etc.) default to 99.
    DIALOGUE_PRIORITY: Dict[str, int] = {
        "alliance_paradox": 0,
        "commitment_paradox": 0,
        "settlement_confirm": 0,
        # PC15-3: same tier as its parent confirm.
        "settlement_pair_substitute_confirm": 0,
        "vassal_rebellion_imminent": 1,
        # SC-5 reversal commit 2: incoming settlement offers sit above
        # ordinary proposals because they touch entire wars and persist
        # across turns. Tested via mailbox ordering regressions.
        "incoming_settlement_offer": 2,
        "ally_settlement_petition": 4,
        "sabotage_confrontation": 2,
        # NA-5 §8: an ultimatum outranks routine proposals in the mailbox —
        # same tier as settlement offers (it touches war and peace).
        "incoming_ultimatum": 2,
        "incoming_proposal": 3,
        "counter_offer": 3,
        "counter_offer_response": 3,
    }
    MAILBOX_SUMMARY_LABELS: Dict[str, str] = {
        "incoming_proposal": "Incoming proposal",
        "counter_offer": "Counter-offer",
        "counter_offer_response": "Counter response",
        "incoming_settlement_offer": "Settlement offer",
        "ally_settlement_petition": "Ally settlement petition",
        "incoming_ultimatum": "Ultimatum",
    }

    def __init__(self):
        self._current: Optional[Dict] = None
        self._queue: List[Dict] = []
        self._next_mailbox_id: int = 1  # monotonic ID for mailbox items
        self._next_dialogue_id: int = 1  # W6-0: monotonic identity for EVERY dialogue

    # ── Core API ──────────────────────────────────────────────────────

    def _assign_mailbox_metadata(self, dialogue: dict) -> None:
        """Stamp mailbox_id and mailbox_order on mailbox-eligible dialogues."""
        dtype = dialogue.get("type", "")
        if dtype in self.SOFT_STOP_MAILBOX_TYPES and "mailbox_id" not in dialogue:
            dialogue["mailbox_id"] = self._next_mailbox_id
            dialogue["mailbox_order"] = self._next_mailbox_id
            dialogue["mailbox_priority"] = self.DIALOGUE_PRIORITY.get(dtype, 99)
            self._next_mailbox_id += 1

    def _assign_dialogue_id(self, dialogue: dict) -> None:
        """W6-0 (BUG-CA-7): stamp a monotonically increasing identity.

        A dialogue that already carries a ``dialogue_id`` keeps it — enrichment
        flows carry the same dict (or a copy of it) forward, so "the same
        matter" keeps the same identity while a freshly-built dict gets a new
        one. The id is mirrored onto ``popup_payload`` so every popup shape
        derived from it reaches Godot carrying the identity it must answer
        with.
        """
        if "dialogue_id" not in dialogue:
            dialogue["dialogue_id"] = self._next_dialogue_id
            self._next_dialogue_id += 1
        payload = dialogue.get("popup_payload")
        if isinstance(payload, dict):
            payload["dialogue_id"] = dialogue["dialogue_id"]

    def mint_dialogue_id(self) -> int:
        """W6-8: identity for question surfaces that do NOT route through the
        manager (the estate capture choice rides the bespoke capture_choice
        pipeline) — drawn from the same monotonic counter so ids stay
        globally unique and serialize with it."""
        did = self._next_dialogue_id
        self._next_dialogue_id += 1
        return int(did)

    def push(self, dialogue: dict) -> None:
        """Add dialogue. If current slot is empty, set it; otherwise queue."""
        self._assign_mailbox_metadata(dialogue)
        self._assign_dialogue_id(dialogue)
        if self._current is None:
            self._current = dialogue
        else:
            if len(self._queue) < self.QUEUE_CAP:
                self._queue.append(dialogue)

    def replace(self, dialogue: dict) -> None:
        """Overwrite current dialogue regardless of state.

        Use for enrichment (modify/expand an active dialogue) or
        clear-then-set patterns where the new dialogue must become current.
        """
        previous = self._current
        new_type = dialogue.get("type", "")
        if previous is not None:
            previous_type = previous.get("type", "")
            if (
                previous_type in self.SOFT_STOP_MAILBOX_TYPES
                and new_type in self.SOFT_STOP_MAILBOX_TYPES
            ):
                if "mailbox_id" not in dialogue and "mailbox_id" in previous:
                    dialogue["mailbox_id"] = previous["mailbox_id"]
                if "mailbox_order" not in dialogue and "mailbox_order" in previous:
                    dialogue["mailbox_order"] = previous["mailbox_order"]
                if "mailbox_priority" not in dialogue:
                    dialogue["mailbox_priority"] = self.DIALOGUE_PRIORITY.get(
                        new_type, previous.get("mailbox_priority", 99)
                    )
            elif new_type in self.SOFT_STOP_MAILBOX_TYPES and "mailbox_id" not in dialogue:
                self._assign_mailbox_metadata(dialogue)
        elif new_type in self.SOFT_STOP_MAILBOX_TYPES and "mailbox_id" not in dialogue:
            self._assign_mailbox_metadata(dialogue)

        self._assign_dialogue_id(dialogue)
        self._current = dialogue

    def open_flow(self, dialogue: dict) -> None:
        """Start a NEW player-initiated flow without destroying the player's mail.

        Aug 30, 2026 review. `replace()` overwrites `_current` and, unless BOTH
        the old and the new dialogue are mailbox types, the displaced one is
        gone — never re-queued. That is correct for a wizard advancing its OWN
        step (and for `_handle_accept_ai_proposal`, which replaces the letter it
        has just answered: re-queueing there would ask the player the same
        question twice). It is wrong for the FIRST step of a new flow, because
        soft-stop mailbox dialogues do not block ordinary commands — so while
        Saxony's open-borders letter or Austria's persistent settlement offer
        holds the slot, "propose an alliance with Prussia", "declare war on
        Austria", "break the treaty with Bavaria", or simply attacking a
        neutral province (which stages War Purpose) silently destroyed it.

        The Aug-23 fix converted three READ-OUT sites (advisory / mission /
        feasibility) to `preempt()` and its own comment claimed the remaining
        `replace()` calls only ever replace the wizard's own dialogue. That was
        false for the eight creation sites this method now serves.

        The rule stated once: a standing letter the player owns is preserved;
        a transient step of some other planning flow is still overwritten, so
        re-issuing a wizard verb does not pile up stale steps.
        """
        previous = self._current
        displaced_is_mail = (
            previous is not None
            and previous.get("type", "") in self.SOFT_STOP_MAILBOX_TYPES
            and dialogue.get("type", "") not in self.SOFT_STOP_MAILBOX_TYPES
        )
        if displaced_is_mail:
            self.preempt(dialogue)
        else:
            self.replace(dialogue)

    def mount_over_mail(self, dialogue: dict) -> bool:
        """Make ``dialogue`` current when only MAIL (or nothing) holds the slot.

        FA-17 / FA-N44 (slice 10). ``push`` sets the current slot only when it
        is EMPTY, and the slot is refilled by routine mail on most turns — the
        IGR-F drip runs about two letters a turn. So two dialogues that exist
        to interrupt the player never did:

        * the COUNTER to France's own 3-DP overture (``counter_offer_response``,
          priority 3) was pushed behind whatever letter had arrived that same
          turn — ``_process_ai_diplomatic_phase`` delivers the mail BEFORE
          ``advance_turn`` resolves the proposal in transit, so the answer to
          the player's own question was always last in the queue;
        * the COMMITMENT PARADOX (priority 0, a HARD stop) was pushed behind a
          persistent settlement offer that never vacates, sat invisible for
          two turns, and was then destroyed by ``clear_stale`` with no event —
          France stayed allied to both belligerents having chosen nothing.

        Mail is not a decision in progress: a letter yields the slot and
        returns to the queue, exactly as it already does when a wizard step
        preempts it (``open_flow``). A HARD stop, a staged planning surface,
        or anything else the player is mid-answer on KEEPS the slot and the
        new dialogue queues behind it as before.

        Returns True when the dialogue became current.
        """
        current = self._current
        if current is None or current.get("type", "") in self.SOFT_STOP_MAILBOX_TYPES:
            self.preempt(dialogue)
            return True
        self.push(dialogue)
        return False

    def preempt(self, dialogue: dict) -> None:
        """Make a dialogue current while preserving the displaced one.

        Use when a newly-created dialogue must surface immediately while an
        existing one should not be dropped — either a hard-stop that must
        interrupt, OR the Sweep-5 typed-answer clarification that preempts a
        non-hard-stop soft dialogue so the player can answer inline (the
        docstring formerly claimed hard-stop-only; that is no longer true).
        The displaced dialogue returns through normal queue promotion once the
        preempting dialogue is resolved.

        S5-4 known limitation (owner: Pre-EA Dialogue Robustness row in
        DESIGN_REFINEMENT.md §8.EVAL Dispositions): if the queue is already at
        QUEUE_CAP the displaced dialogue is DROPPED rather than overflowed to
        the mailbox. Requires a pathological 20-deep queue; push() has the
        identical pre-existing drop. The overflow-to-mailbox fix is deferred;
        only this contract refresh rides Batch Q.
        """
        self._assign_mailbox_metadata(dialogue)
        self._assign_dialogue_id(dialogue)
        previous = self._current
        if previous is not None and len(self._queue) < self.QUEUE_CAP:
            self._queue.append(previous)
        self._current = dialogue

    def pop(self) -> Optional[Dict]:
        """Remove and return current dialogue. Auto-promotes highest-priority
        item from queue if available."""
        result = self._current
        self._current = None
        self._promote()
        return result

    def peek(self) -> Optional[Dict]:
        """Read current dialogue without removing it."""
        return self._current

    def iter_queue(self) -> List[Dict]:
        """Public read-only view of queued (non-current) dialogues.

        Returned as a shallow list copy so callers can iterate or filter
        without mutating internal queue state. Use this in preference
        to reaching into `_queue` directly so the dialogue-manager
        public API stays the only allowed seam.
        """
        return list(self._queue)

    def is_blocking(self) -> bool:
        """True if current dialogue has blocking=True."""
        return (self._current is not None
                and self._current.get("blocking", False))

    def is_hard_stop(self) -> bool:
        """True if current dialogue is a hard-stop type that blocks ALL commands.

        PL-27: Only hard-stop dialogues should prevent ordinary command execution.

        Re-front Slice 1 §10: a ``settlement_confirm`` in ``dialogue_mode ==
        "PROPOSE"`` is an AUTHORING surface (the conversational Tier-1/2 front),
        not a staged decision. Like EDIT, it must not block ordinary commands or
        end-turn — the unsubmitted draft simply discards at turn end. Only the
        staged-decision settlement surfaces (REVIEW / BLOCKED_TERMINAL) remain
        hard stops.
        """
        if self._current is None:
            return False
        dtype = self._current.get("type", "")
        if dtype not in self.HARD_STOP_TYPES:
            return False
        if (
            dtype == "settlement_confirm"
            and str(self._current.get("dialogue_mode", "")).upper() == "PROPOSE"
        ):
            return False
        return True

    def is_soft_stop(self) -> bool:
        """True if current dialogue is a soft-stop type (mailbox or hybrid).

        PL-27: Soft-stop dialogues do NOT block ordinary commands.
        """
        if self._current is None:
            return False
        dtype = self._current.get("type", "")
        return dtype in self.SOFT_STOP_MAILBOX_TYPES or dtype in self.HYBRID_SOFT_STOP_TYPES

    def is_local_planning(self) -> bool:
        """True if current dialogue is a player-initiated local planning flow."""
        if self._current is None:
            return False
        dtype = self._current.get("type", "")
        return dtype in self.LOCAL_PLANNING_TYPES

    def get_soft_stop_count(self) -> int:
        """Count of active soft-stop dialogue (0 or 1) plus queued items.

        PL-27: Authoritative envoy count for the top-bar badge.
        Retained for backward compatibility — prefer get_mailbox_count().
        """
        count = len(self._queue)
        if self.is_soft_stop():
            count += 1
        return count

    def get_mailbox_count(self) -> int:
        """Count of mailbox-eligible items (active + queued).

        Session 2 follow-up: Single source of truth for the mailbox badge.
        Counts SOFT_STOP_MAILBOX_TYPES only — excludes hybrid soft-stops.
        """
        count = 0
        if self._current and self._current.get("type", "") in self.SOFT_STOP_MAILBOX_TYPES:
            count += 1
        for item in self._queue:
            if item.get("type", "") in self.SOFT_STOP_MAILBOX_TYPES:
                count += 1
        return count

    def get_lapsing_count(self) -> int:
        """Count of items that will actually LAPSE if the turn ends now.

        Aug 30, 2026 review. The client's end-turn warning ("N unanswered
        envoy(s) that will lapse if you end the turn now") was fed from
        `get_mailbox_count`, which counts SOFT_STOP_MAILBOX_TYPES — the
        current-turn offers that DO lapse plus the PERSISTENT ones that
        explicitly do not (`lapse_pending_offers` excludes them by design, so
        a standing settlement offer survives every end turn). The player was
        stopped, and told he was about to lose something he could not lose;
        worse, a turn whose only "envoy" was persistent produced a warning
        that could never be satisfied by answering anything.

        The badge keeps `get_mailbox_count` — the letter-book really does
        hold both. Only the LAPSE claim narrows.
        """
        count = 0
        if self._current and self._current.get("type", "") in self.CURRENT_TURN_OFFER_TYPES:
            count += 1
        for item in self._queue:
            if item.get("type", "") in self.CURRENT_TURN_OFFER_TYPES:
                count += 1
        return count

    def get_mailbox_items(self) -> List[Dict]:
        """Return ordered list of mailbox items for the inbox panel.

        Returns dicts with: mailbox_id, state (ACTIVE/WAITING), source_nation,
        item_type, arrival_turn, summary. Active item first, then by
        mailbox_priority asc, mailbox_order asc.
        """
        items = []

        def _make_summary(d: dict) -> dict:
            ctx = d.get("context", {})
            dtype = d.get("type", "unknown")
            turn = d.get("turn_created", 0)
            # Settlement offers store the proposer at top level (not in
            # `context.source`) because they are produced outside the
            # ordinary AI-proposal pipeline.
            if dtype == "incoming_settlement_offer":
                source = d.get("proposer_nation", "Unknown")
                ptype = "settlement_offer"
                # Gate-4 1805 smoke (E-5): the row is player-facing — use the
                # humanized war label, never the raw internal war id (R7).
                war_label = d.get("war_label", "") or d.get("war_id", "")
                summary = (
                    f"{self.MAILBOX_SUMMARY_LABELS.get(dtype, 'Settlement offer')}"
                    + (f": {war_label}" if war_label else "")
                )
            elif dtype == "ally_settlement_petition":
                source = d.get("ally_nation", "Unknown")
                ptype = str(d.get("petition_type", "ally_petition"))
                war_id = d.get("war_id", "")
                summary = str(
                    d.get("summary_text", "")
                    or (
                        f"{self.MAILBOX_SUMMARY_LABELS.get(dtype, 'Ally petition')}"
                        + (f": {war_id}" if war_id else "")
                    )
                ).strip()
            else:
                source = d.get("target_nation", ctx.get("source", "Unknown"))
                terms = ctx.get("counter_terms") or ctx.get("proposal") or ctx.get("terms") or {}
                ptype = terms.get("type", dtype)
                summary = str(
                    d.get("proposal_terms_summary", "")
                    or ctx.get("proposal_terms_summary", "")
                    or (
                        f"{self.MAILBOX_SUMMARY_LABELS.get(dtype, 'Diplomatic item')}: "
                        f"{_proposal_display(ptype)}"
                    )
                ).strip()
            summary = summary.splitlines()[0]
            if len(summary) > 72:
                summary = summary[:69].rstrip() + "..."
            return {
                "mailbox_id": d.get("mailbox_id", 0),
                "state": "ACTIVE" if d is self._current else "WAITING",
                "source_nation": source,
                "item_type": dtype,
                "proposal_type": ptype,
                "arrival_turn": int(turn),
                "summary_text": summary,
                "summary": f"{_nation_display(source)} — {_proposal_display(ptype)}",
            }

        # Active mailbox item first
        if self._current and self._current.get("type", "") in self.SOFT_STOP_MAILBOX_TYPES:
            items.append(_make_summary(self._current))

        # Queued mailbox items sorted by priority then order
        queued = [
            q for q in self._queue
            if q.get("type", "") in self.SOFT_STOP_MAILBOX_TYPES
        ]
        queued.sort(key=lambda d: (
            d.get("mailbox_priority", 99),
            d.get("mailbox_order", 999999),
        ))
        for q in queued:
            items.append(_make_summary(q))

        return items

    def has_current_turn_offers(self) -> bool:
        """True if any current-turn offer items exist (active or queued).

        Used by diplomacy gating to block new diplomacy initiation while
        unanswered offers are pending.
        """
        if self._current and self._current.get("type", "") in self.CURRENT_TURN_OFFER_TYPES:
            return True
        return any(
            item.get("type", "") in self.CURRENT_TURN_OFFER_TYPES
            for item in self._queue
        )

    def lapse_pending_offers(self) -> list:
        """Remove all current-turn offer items. Returns lapse info for logging.

        Called at start of TurnManager.end_turn() BEFORE enemy phase / AI
        diplomacy. Each returned dict has: nation, offer_type, proposal_type.
        """
        lapsed = []

        # Check current slot
        if self._current and self._current.get("type", "") in self.CURRENT_TURN_OFFER_TYPES:
            lapsed.append(self._extract_lapse_info(self._current))
            self._current = None

        # Check queue
        remaining = []
        for item in self._queue:
            if item.get("type", "") in self.CURRENT_TURN_OFFER_TYPES:
                lapsed.append(self._extract_lapse_info(item))
            else:
                remaining.append(item)
        self._queue = remaining

        # Promote from queue if current was cleared
        if self._current is None and self._queue:
            self._promote()

        return lapsed

    def _extract_lapse_info(self, dialogue: dict) -> dict:
        """Pull structured lapse info from a dialogue dict.

        W6-10: `proposal_type` prefers the STABLE P-rule label the dialogue
        context carries — `terms["type"]` is rewritten by
        `_build_proposal_terms` (harsh_peace → "peace"), and keying the
        lapse type-cooldown on the rewritten value is the documented
        cooldown trap (the P-rule checks would never read it)."""
        ctx = dialogue.get("context", {})
        nation = dialogue.get("target_nation", ctx.get("source", "Unknown"))
        terms = ctx.get("counter_terms") or ctx.get("proposal") or ctx.get("terms") or {}
        return {
            "nation": nation,
            "offer_type": dialogue.get("type", "unknown"),
            "proposal_type": (ctx.get("proposal_type")
                              or terms.get("type", "unknown")),
        }

    def active_blocker_type(self) -> str:
        """The type of the dialogue that would refuse `activate_mailbox_item`.

        Empty string when the slot is free, holds a mailbox item, or holds
        something a mailbox answer may displace. Exists so the refusal can
        NAME the obstacle: the old copy said "Settle it before answering the
        lesser courts" about a dialogue the player frequently cannot see, and
        an unactionable instruction is worse than no instruction.
        """
        if self._current is None:
            return ""
        current_type = self._current.get("type", "")
        if current_type in self.DISPOSABLE_ACTIVE_TYPES:
            return ""
        if current_type in self.SOFT_STOP_MAILBOX_TYPES:
            return ""
        # Everything else blocks — INCLUDING a type in no taxonomy set.
        # `activate_mailbox_item` denies those (they used to fall through and
        # be silently overwritten), so reporting "" for them made the deny
        # path anonymous: the client got `activation_blocked: false`, left the
        # letter-book open over the modal, and told the player the letter did
        # not exist. The two functions must agree, and this is the side that
        # was wrong. Measured production case:
        # `settlement_scope_replace_confirm`.
        return current_type

    def activate_mailbox_item(self, mailbox_id: int) -> Optional[Dict]:
        """Swap a queued mailbox item into the active slot.

        The previously active soft-stop item returns to the queue without
        data loss. Returns the newly activated dialogue, or None if the
        mailbox_id was not found or activation is blocked.
        """
        # Guard: only swap when the active slot is empty, holds a mailbox
        # item, or holds a read-out we are allowed to discard.
        #
        # NOTE the ordering below is load-bearing: the DISCARD happens AFTER
        # the queue lookup, never before it. A first cut dropped the read-out
        # up here and then failed the lookup on a stale/expired mailbox_id —
        # which destroyed the player's advisory for nothing and broke the
        # standing rule that a stale id must "leave the current active item
        # untouched" (docs/BUG_FIXES.md, the IGR-F refusal contract).
        if self._current is not None:
            current_type = self._current.get("type", "")
            if current_type in self.DISPOSABLE_ACTIVE_TYPES:
                pass          # discardable — decided below, once we can swap
            elif current_type in self.SOFT_STOP_MAILBOX_TYPES:
                pass          # a mailbox item; it is re-queued below
            else:
                # HARD_STOP, HYBRID, staged LOCAL_PLANNING — and anything not
                # in ANY taxonomy set. The default used to be fall-through,
                # which silently OVERWROTE an unclassified dialogue
                # (`clarification`, `settlement_scope_replace_confirm`,
                # `diplomatic_treaty_failed`, `proposal_result` are all
                # reachable and all unclassified). Deny is the safe default:
                # a refusal the player can read beats a dialogue that
                # vanishes.
                return None

        # Find the target in queue
        target_idx = None
        for i, item in enumerate(self._queue):
            if item.get("mailbox_id") == mailbox_id:
                target_idx = i
                break

        if target_idx is None:
            # Also check if the active item already has this id
            if self._current and self._current.get("mailbox_id") == mailbox_id:
                return self._current
            return None

        target = self._queue.pop(target_idx)

        if self._current is not None:
            current_type = self._current.get("type", "")
            if current_type in self.SOFT_STOP_MAILBOX_TYPES:
                # Preserve original turn_created — no refresh
                self._queue.append(self._current)
            # else: a DISPOSABLE_ACTIVE_TYPES read-out, dropped here — the
            # swap is certain now, so nothing is lost for nothing.

        self._current = target
        return target

    # ── Lifecycle ─────────────────────────────────────────────────────

    def clear_stale(self, current_turn: int) -> Optional[Dict]:
        """Auto-dismiss expired dialogues. Returns cleared dialogue if any.

        Current-turn offers are exempt — their lifecycle is managed by
        lapse_pending_offers() at the start of TurnManager.end_turn().
        AI proposals arrive during end_turn BEFORE advance_turn increments
        the turn counter, so they have turn_created = old_turn and would be
        falsely cleared without this exemption.
        - Non-blocking non-offer: dismiss if turn_created < current_turn
        - Blocking: force-clear if turn_created + BLOCKING_TIMEOUT_TURNS < current_turn
        """
        # PC15-3: the QUEUE is swept by the same rules. A stale dialogue
        # displaced into the queue was immortal — clear_stale only ever
        # inspected the active slot — and was promoted turns later, where
        # its confirm vocabulary consumed every subsequent "confirm" (the
        # settlement pair-substitute wedge). Mailbox types keep their own
        # lifecycle, exactly as in the active-slot arms below.
        if self._queue:
            kept = []
            for queued in self._queue:
                q_type = queued.get("type", "")
                if q_type in self.SOFT_STOP_MAILBOX_TYPES:
                    kept.append(queued)
                    continue
                # FA-N44 (slice 10): the COMMITMENT PARADOX is never swept
                # from the queue.
                #
                # PC15-3 added this sweep for a good reason — a stale
                # `settlement_pair_substitute_confirm` displaced into the
                # queue was immortal, and its confirm vocabulary ate every
                # later "confirm" when it was finally promoted. That cure
                # stays for every type it was written for.
                #
                # The paradox is the opposite shape. It has no vocabulary to
                # eat (it is answered by option index), and deleting it is
                # not a cleanup but a DECISION: France keeps both alliances,
                # having chosen nothing, and no event records that the crisis
                # ever existed. Measured: queued behind a persistent
                # settlement offer, the paradox was gone two turns later with
                # France still allied to both belligerents. With
                # `mount_over_mail` it now reaches the slot on arrival, so
                # this is defence in depth — the only way to queue is behind
                # ANOTHER hard stop, which blocks play until answered.
                if (PARADOX_SURVIVES_THE_STALE_SWEEP
                        and q_type in PARADOX_DIALOGUE_TYPES):
                    kept.append(queued)
                    continue
                q_created = queued.get("turn_created", 0)
                q_blocking = queued.get("blocking", False)
                if not q_blocking and q_created < current_turn:
                    continue
                if (q_blocking
                        and q_created + self.BLOCKING_TIMEOUT_TURNS
                        < current_turn):
                    continue
                kept.append(queued)
            self._queue = kept

        if not self._current:
            return None

        # Current-turn offers are lapsed explicitly, not by generic stale clearing.
        # Persistent mailbox items remain until the player resolves them.
        dtype = self._current.get("type", "")
        if dtype in self.SOFT_STOP_MAILBOX_TYPES:
            return None

        turn_created = self._current.get("turn_created", 0)
        is_blocking = self._current.get("blocking", False)

        # Non-blocking: dismiss if older than current turn
        if not is_blocking and turn_created < current_turn:
            return self.pop()

        # Blocking: safety valve
        if is_blocking and turn_created + self.BLOCKING_TIMEOUT_TURNS < current_turn:
            return self.pop()

        return None

    def promote_if_empty(self) -> bool:
        """If current is None and queue has items, promote highest-priority.

        Returns True if promotion occurred. Use at turn-start to drain
        queue items from prior turns.
        """
        if self._current is not None or not self._queue:
            return False
        self._promote()
        return True

    def remove_matching(self, predicate: Callable[[Dict], bool]) -> int:
        """Remove queue items (and current if matched) by predicate.

        Returns count of items removed. Auto-promotes from queue if
        current was removed.
        """
        removed = 0
        # Filter queue
        before = len(self._queue)
        self._queue = [d for d in self._queue if not predicate(d)]
        removed += before - len(self._queue)
        # Check current
        if self._current and predicate(self._current):
            self._current = None
            removed += 1
            self._promote()
        return removed

    # ── Internals ─────────────────────────────────────────────────────

    def _promote(self) -> None:
        """Promote highest-priority queue item to current slot.

        Mailbox types use (mailbox_priority, mailbox_order) for stable sort.
        Non-mailbox types use DIALOGUE_PRIORITY as before.
        """
        if not self._queue:
            return
        self._queue.sort(
            key=lambda d: (
                d.get("mailbox_priority", self.DIALOGUE_PRIORITY.get(d.get("type", ""), 99)),
                d.get("mailbox_order", 999999),
            )
        )
        self._current = self._queue.pop(0)

    @property
    def queue_size(self) -> int:
        return len(self._queue)

    # ── Serialization ─────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "current": copy.deepcopy(self._current) if self._current else None,
            "queue": [copy.deepcopy(d) for d in self._queue],
            "next_mailbox_id": self._next_mailbox_id,
            "next_dialogue_id": self._next_dialogue_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DialogueManager":
        dm = cls()
        dm._current = copy.deepcopy(data.get("current")) if data.get("current") else None
        dm._queue = [copy.deepcopy(d) for d in data.get("queue", [])]
        dm._next_mailbox_id = data.get("next_mailbox_id", 1)
        dm._next_dialogue_id = data.get("next_dialogue_id", 1)
        # Legacy migration: stamp mailbox_id on any mailbox items missing it
        for item in ([dm._current] if dm._current else []) + dm._queue:
            if item and item.get("type", "") in cls.SOFT_STOP_MAILBOX_TYPES and "mailbox_id" not in item:
                item["mailbox_id"] = dm._next_mailbox_id
                item["mailbox_order"] = dm._next_mailbox_id
                item["mailbox_priority"] = cls.DIALOGUE_PRIORITY.get(item.get("type", ""), 99)
                dm._next_mailbox_id += 1
        # W6-0 migration: stamp dialogue_id on any pre-identity dialogues
        for item in ([dm._current] if dm._current else []) + dm._queue:
            if item and "dialogue_id" not in item:
                dm._assign_dialogue_id(item)
        return dm
