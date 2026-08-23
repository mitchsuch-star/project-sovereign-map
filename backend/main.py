"""
FastAPI server for Project Sovereign
Connects Godot frontend to Python game logic
"""

import os
import re  # soft-stop option token matching (playthrough fix, Aug 1 2026)
import asyncio  # noqa: E402 - 3A-1: state_lock (async middleware)
import weakref  # noqa: E402 - 3A-1: per-event-loop state locks
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load .env BEFORE any imports that might read env vars
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field  # noqa: F401

from backend.commands.parser import CommandParser
from backend.commands.executor import CommandExecutor
from backend.commands.dialogue_routing import (
    match_dialogue_answer,
    format_answer_words,
)
from backend.models.world_state import WorldState
from backend.nation_config import DEFAULT_PLAYER_NATION, get_player_nation
from backend.models.intel import FULL  # noqa: E402, F811 — used by _filter_enemy_phase_by_visibility
from backend.commands.meta_executor import _filter_tactical_events_by_fog
import backend.save_manager as save_manager
from backend.save_manager import autosave, save_game, load_game, list_saves, delete_save

# ════════════════════════════════════════════════════════════
# DEBUG MODE: Set to True to enable debug endpoints
# ════════════════════════════════════════════════════════════
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

# ════════════════════════════════════════════════════════════
# STARTUP: Show LLM configuration
# ════════════════════════════════════════════════════════════
print("=" * 60)
print("PROJECT SOVEREIGN - Server Starting")
print("=" * 60)
llm_mode = os.getenv("LLM_MODE", "mock")
api_key = os.getenv("ANTHROPIC_API_KEY", "")
print(f"LLM_MODE: {llm_mode}")
print(f"ANTHROPIC_API_KEY: {'SET (' + api_key[:10] + '...)' if api_key else 'NOT SET'}")
print("=" * 60)

# Initialize game
app = FastAPI(title="Project Sovereign API")
parser = CommandParser()  # Uses LLM_MODE from environment
executor = CommandExecutor()
world = None
game_state = {"world": None, "debug_mode": DEBUG_MODE}
# 3A-1: Protects state-mutating endpoints. asyncio, NOT threading (July 18,
# 2026): the middleware that takes it is `async def`, so a threading.Lock held
# across `await call_next` blocks the whole event loop for the request's
# duration — see serialize_state_mutations. The handlers themselves are sync
# (`def`), so FastAPI runs them in a threadpool; the ONLY acquisition site is
# that one middleware, on the loop thread.
#
# PER-LOOP, not module-level. An asyncio.Lock binds to the first event loop
# that awaits it and raises "bound to a different event loop" on any other —
# and each `TestClient` spins up a fresh loop, so a single module-level lock
# broke 21 endpoint tests the moment a second client was constructed. The same
# hazard exists in production for any loop restart. Keyed by the running loop,
# which is exactly the scope over which mutual exclusion is meaningful: two
# different loops cannot be concurrently serving the same in-process world.
# Keyed by the loop OBJECT in a WeakKeyDictionary, not by id(loop). CPython
# reuses memory addresses, so an id-keyed map hands a brand-new loop the lock
# belonging to a collected one — which then raises the very
# "bound to a different event loop" error this indirection exists to prevent.
# The weak keys also mean entries retire with their loop instead of leaking.
_state_locks: "weakref.WeakKeyDictionary" = weakref.WeakKeyDictionary()


def get_state_lock() -> asyncio.Lock:
    """The state lock for the CURRENT running event loop."""
    loop = asyncio.get_running_loop()
    lock = _state_locks.get(loop)
    if lock is None:
        lock = asyncio.Lock()
        _state_locks[loop] = lock
    return lock


def _resolve_sovereign_map() -> str:
    """Resolve the SOVEREIGN_MAP flag for the game bootstrap (Map Slice 5, G1).

    The game ships the 126-province Europe map: the default is "europe".
    Rollback is a flag flip, not a code change — set SOVEREIGN_MAP=legacy to
    restore the 19-region world. Read per-call (not cached at import) so a
    running process and the test suite can exercise both paths.
    """
    value = os.getenv("SOVEREIGN_MAP", "europe").strip().lower()
    if value not in ("europe", "legacy"):
        print(f"[WARN] Unknown SOVEREIGN_MAP={value!r} -- falling back to 'europe'")
        return "europe"
    return value


# Map Slice 7 default-boot flip: the shipped campaign IS the 1805 scenario.
# Absolute (repo-root-derived) so the boot works regardless of CWD.
_DEFAULT_SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
)
# Explicit opt-out sentinel: with a scenario as the default, tests/devs need an
# env value that means "no scenario — boot the bare flag-resolved world".
SCENARIO_NONE_SENTINEL = "none"

# POSITION 7: named scenarios a client may request over HTTP (/new_game).
# Names map to repo-root-derived paths (the _DEFAULT_SCENARIO_PATH idiom) —
# a raw path is NEVER accepted over the wire.
TUTORIAL_SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps" / "tutorial_1805.json"
)
SCENARIO_ALLOWLIST = {"tutorial": TUTORIAL_SCENARIO_PATH}


def _resolve_scenario_path() -> str:
    """Resolve the scenario for the game bootstrap (Slice 7 default-boot flip).

    Precedence (read per-call so tests can exercise every path):
    1. SOVEREIGN_SCENARIO=<path> — explicit scenario, fails loudly downstream.
    2. SOVEREIGN_SCENARIO=none — bare flag-resolved world (opt-out sentinel).
    3. SOVEREIGN_MAP=legacy — no scenario (the G1 rollback drill stays a pure
       flag flip: legacy world, legacy marshals, no code change).
    4. SOVEREIGN_SMOKE_START set — no scenario (presets seed their own wars in
       the WorldState constructor; combining them with a scenario is untested
       by design — the never-combine rule, STATUS §Diplomacy accommodations).
    5. Default: the authored 1805 opening (europe_1805.json).
    """
    explicit = os.getenv("SOVEREIGN_SCENARIO", "").strip()
    if explicit:
        if explicit.lower() == SCENARIO_NONE_SENTINEL:
            return ""
        return explicit
    if _resolve_sovereign_map() == "legacy":
        return ""
    if os.getenv("SOVEREIGN_SMOKE_START", "").strip():
        print("[WARN] SOVEREIGN_SMOKE_START set -- skipping the default 1805 scenario boot")
        return ""
    return str(_DEFAULT_SCENARIO_PATH)


def _build_new_world(
    player_nation: str = DEFAULT_PLAYER_NATION,
    scenario_override: str = "",
) -> WorldState:
    """Create a fresh campaign world with the default start-state.

    A configured SOVEREIGN_SCENARIO fails LOUDLY (missing file / invalid
    scenario raises) — silently falling back to the default world would run
    the wrong campaign and hide scenario-authoring errors.

    POSITION 7: `scenario_override` (an allowlist-resolved PATH, already
    validated by the caller) outranks the whole env precedence chain — an
    explicit player request beats process env, which is also what makes it
    reachable under the test suite's SOVEREIGN_SCENARIO=none pin. Empty
    override → byte-identical to the pre-override behavior.
    """
    scenario_path = str(scenario_override).strip() or _resolve_scenario_path()
    if scenario_path:
        if os.getenv("SOVEREIGN_SMOKE_START", "").strip():
            # An EXPLICIT scenario + a smoke preset is the documented
            # never-combine pair (the preset seeds wars in the constructor,
            # the scenario seeds its own) — fail loudly rather than boot an
            # untested hybrid. (The DEFAULT scenario already yields to the
            # preset in _resolve_scenario_path.)
            raise ValueError(
                "SOVEREIGN_SCENARIO and SOVEREIGN_SMOKE_START are both set — "
                "never combine them (unset one; see docs/STATUS.md "
                "'Diplomacy accommodations')."
            )
        print(f"SOVEREIGN_SCENARIO: loading scenario from {scenario_path!r}")
        return WorldState.from_scenario(scenario_path)
    return WorldState(player_nation=player_nation, sovereign_map=_resolve_sovereign_map())


def _set_active_world(new_world: WorldState) -> WorldState:
    """Install a world instance as the active campaign state."""
    global world
    world = new_world
    game_state["world"] = new_world
    return new_world


def _reset_world_state(
    player_nation: str = DEFAULT_PLAYER_NATION,
    scenario_override: str = "",
) -> WorldState:
    """Replace the active campaign with a fresh world."""
    return _set_active_world(
        _build_new_world(player_nation=player_nation, scenario_override=scenario_override)
    )


_reset_world_state()
print(f"SOVEREIGN_MAP: {world.sovereign_map} ({len(world.regions)} regions)")
# AI-0b boot banner: the seed is reported here but its default lives in
# WorldState.__init__ (SOVEREIGN_SEED env) — it is orthogonal to the
# scenario-path precedence chain above, not a rung in it (spec §3.8.1).
print(f"SOVEREIGN_SEED: campaign seed {world.campaign_seed!r}")


def get_llm_game_state() -> dict:
    """
    Build game state dict in the format expected by prompt_builder.

    The LLM prompt builder expects:
    - marshals: {name: {location, strength, morale}}
    - enemies: {name: {location, strength, nation}}
    - map_data: {region: {controller, marshals: [{name, personality}]}}

    This is separate from get_game_state_summary() which is for the frontend.
    """
    # Build marshals dict (player marshals)
    marshals = {}
    for m in world.get_player_marshals():
        if m.strength > 0:  # Only alive marshals
            marshals[m.name] = {
                "location": m.location,
                "strength": int(m.strength),
                "morale": int(m.morale),
            }

    # Build enemies dict — fog-filtered (V2-5)
    # Only include enemies in regions with PARTIAL+ visibility.
    # PARTIAL: show "unknown" strength. FULL: show exact.
    from backend.models.intel import FULL, PARTIAL, VISIBILITY_PRIORITY
    enemies = {}
    for m in world.get_enemy_marshals():
        if m.strength > 0:  # Only alive marshals
            region_intel = world.get_region_intel(m.location)
            vis = region_intel.visibility
            if VISIBILITY_PRIORITY.get(vis, 0) >= VISIBILITY_PRIORITY[PARTIAL]:
                enemies[m.name] = {
                    "location": m.location,
                    "strength": int(m.strength) if vis == FULL else "unknown",
                    "nation": m.nation,
                }

    # Build map_data dict — R5: fog-filter enemy marshals
    map_data = {}
    for region_name, region in world.regions.items():
        marshals_here = world.get_marshals_in_region(region_name)
        region_vis = world.get_region_intel(region_name).visibility_at_least(PARTIAL)
        visible_marshals = [
            {"name": m.name, "personality": getattr(m, 'personality', 'unknown')}
            for m in marshals_here
            if m.strength > 0
            and (m.nation == world.player_nation or region_vis)
        ]
        map_data[region_name] = {
            "controller": region.controller or "Neutral",
            "marshals": visible_marshals,
        }

    return {
        "turn": int(world.current_turn),
        "gold": int(world.gold),
        "marshals": marshals,
        "enemies": enemies,
        "map_data": map_data,
        # July 2026 AI audit: the live providers read game_state["world"]
        # for the command-history repetition guardrail (anti-spam on the
        # strategic-score bonuses) — without it they silently sent empty
        # history on every parse. Never serialized: this dict only feeds
        # prompt building.
        "world": world,
    }

def _player_coalition_brewing(w):
    """Stage D review fix [r1]: the top-bar alarm reads only a brewing that
    TARGETS the player — an eclipse brewing (target_nation != player) must
    not pulse France's coalition warning."""
    brewing = getattr(w, 'coalition_brewing', None)
    if not brewing:
        return None
    player = getattr(w, 'player_nation', 'France')
    if (brewing.get("target_nation") or player) != player:
        return None
    return brewing


def _dp_ceiling(w) -> int:
    """The DP denominator the top bar shows — the base clamp plus the Seat.

    NP promise audit: the Emperor holding court in his capital adds +1
    ABOVE `calculate_dp`'s 1-5 clamp (NP-5's deliberate choice), so the
    HUD read "DP: 6/5". Single source in `diplomacy.displayed_dp_ceiling`.
    """
    from backend.game_logic.diplomacy import displayed_dp_ceiling
    return int(displayed_dp_ceiling(w))


def _get_talleyrand_state_label(w) -> str:
    """Get Talleyrand state label for top bar (authority-based, PL-23)."""
    if not hasattr(w, 'authority_tracker'):
        return "UNKNOWN"
    return w.authority_tracker.get_authority_label()


_MISSION_TYPE_DISPLAY = {
    "IMPROVE_RELATIONS": "Improving Relations",
    "COURT_NATION": "Courting",
    "GATHER_INTEL": "Gathering Intel",
    "UNDERMINE_ALLIANCE": "Undermining Alliance",
    "REASSURE_ALLY": "Reassuring Ally",
    "CONTINENTAL_SYSTEM": "Continental System",
}


def _get_talleyrand_mission_summary(w) -> str:
    """Get Talleyrand mission summary for top bar."""
    mission = getattr(w, 'active_diplomatic_mission', None)
    if mission and not mission.get("completed"):
        raw_type = mission.get("type", "Unknown")
        m_type = _MISSION_TYPE_DISPLAY.get(raw_type, raw_type.replace("_", " ").title())
        m_target = mission.get("target", "Unknown")
        return f"{m_type} → {m_target}"
    return "None"


def _capture_popup_passthroughs(response: dict) -> dict:
    """Non-None PopupQueue keys already delivered into `response`.

    `_include_popup_passthroughs` POPS its winner off the queue and clears
    the world field, so a response that is later discarded takes the popup
    with it — irrecoverably, for any one-shot event.
    """
    from backend.models.cooldown_manager import PopupQueue
    return {
        key: response[key]
        for key in set(PopupQueue.RESPONSE_KEYS.values())
        if response.get(key) is not None
    }


def _restore_popup_passthroughs(response: dict, carried: dict) -> None:
    """Re-stamp carried popups onto a rebuilt response, never clobbering a
    popup the rebuild legitimately delivered."""
    for key, value in carried.items():
        if response.get(key) is None:
            response[key] = value


def _formations_history_names(world, text: str, event: dict) -> str:
    """Thin door onto formations.apply_formation_names_to_history."""
    from backend.game_logic.formations import apply_formation_names_to_history
    return apply_formation_names_to_history(world, text, event)


def _attach_nation_identity_overrides(response: dict, world) -> None:
    """NA-6 §11.10-3 — stamp the formed-nation display/flag overrides.

    Empty dicts at boot by construction (nothing can form at boot), so
    this is zero behavior change until the first proclamation.

    Deliberately applied to the hand-rolled GET payloads too, not just
    `build_base_response`: the ledgers, dispatch, campaign log, marshal
    overview and map topology all render nation names, and a player who
    LOADS a save with formations and opens a ledger before issuing any
    command would otherwise read the dead name (§11.8 stage 3: "no
    surface may show the dead name"). One helper, every door.
    """
    from backend.game_logic.formations import (
        build_nation_display_overrides, build_nation_flag_overrides,
    )
    response["nation_display_overrides"] = build_nation_display_overrides(world)
    response["nation_flag_overrides"] = build_nation_flag_overrides(world)


def build_base_response(world, success: bool = True, message: str = "",
                        events: list = None,
                        include_popup_passthroughs: bool = True,
                        queue_informational_notices: bool = True,
                        include_notifications: bool = True,
                        **extra) -> dict:
    """Standard response builder. ALL POST endpoints must use this.

    Structurally guarantees:
    - Standard gameplay envelope (impossible to forget)
    - Diplomatic top-bar fields (always present, never stale)
    - War-status payload (`active_wars`) in every gameplay response
    - Game state summary (always present)
    - Optional popup passthroughs / notice queuing / notification draining
      for endpoints that need to defer those surfaces temporarily

    Endpoint-specific fields passed as **extra.
    """
    from backend.game_logic.envoy_digest import build_envoy_digest
    from backend.game_logic.war_status import build_active_wars

    response = {
        "success": success,
        "message": message,
        "events": events if events is not None else [],
        "game_state": world.get_filtered_game_state_summary(),
        "action_summary": world.get_action_summary(),
        "active_wars": build_active_wars(world),
        # Diplomatic top-bar fields — present in EVERY gameplay response
        "diplomatic_points": int(getattr(world, 'diplomatic_points', 0)),
        "max_diplomatic_points": _dp_ceiling(world),
        "talleyrand_state": _get_talleyrand_state_label(world),
        "talleyrand_mission_summary": _get_talleyrand_mission_summary(world),
        "threat_level": int(getattr(world, 'threat_level', 0)),
        "coalition_brewing": _player_coalition_brewing(world) is not None,
        "coalition_brewing_turns": int(
            _player_coalition_brewing(world).get("turns_remaining", 0)
        ) if _player_coalition_brewing(world) else None,
        # Session 2 follow-up: Single source of truth for mailbox badge
        "pending_envoy_count": int(world.dialogue_manager.get_mailbox_count()),
        # IGR-F: the letter-book. Derived fresh from the dialogue manager on
        # every response so it can never go stale against the queue it
        # describes; None when no small court is waiting. It rides the base
        # envelope (not the popup queue) deliberately — a queue slot would
        # cost the 11-key pin AND a new arbitration against
        # incoming_proposal / incoming_settlement_offer, which is the exact
        # "two things in one slot, one gets swallowed" shape this review has
        # already logged twice.
        "envoy_digest": build_envoy_digest(world),
    }
    response.update(extra)
    # NA-6 §11.10-3: the identity override map rides EVERY response so the
    # Godot R7 chokepoints can resolve a formed nation's new name and flag
    # without N payload builders each adopting a helper. Set AFTER
    # `update(extra)` — `_build_result_response` forwards every executor
    # result key into **extra and could otherwise clobber it.
    _attach_nation_identity_overrides(response, world)
    if include_popup_passthroughs:
        _include_popup_passthroughs(response, world)
    if queue_informational_notices:
        _queue_informational_diplomacy_notices(response, world)
    notice_drain = getattr(world, "drain_settlement_draft_notices", None)
    if callable(notice_drain):
        draft_notices = notice_drain()
        if draft_notices:
            response["settlement_draft_notices"] = draft_notices
    # Notifications — persistent alerts for Godot notification bar.
    # Aug 23, 2026: the `has_pending()` guard meant that when the LAST row
    # cleared, the key was omitted entirely — and `main.gd` renders on
    # `if response.has("notifications")`, so the rail was never told to empty
    # and kept a ghost row on screen. Retiring a notification has to be
    # something the client can be told about, so an empty rail ships `[]`.
    if include_notifications:
        response["notifications"] = world.notifications.get_pending()
    return response


def _build_result_response(result: dict, world, drain_popups: bool = True) -> dict:
    """Build a standard response from an executor result dict.

    Strips new_state (circular refs), adds base fields via build_base_response().
    Used for /command early returns and endpoints that forward executor results.

    drain_popups=False (IGR-X7): the capture-choice routes' client handler
    (main.gd's capture route) reads only the capture keys — a popup POPPED
    into this response dies unread, exactly the IGR-F letter-book shape.
    Keys stay present (filled without draining) so the response contract
    holds; the queued popup rides the player's next ordinary /command.
    """
    extra = {k: v for k, v in result.items() if k != "new_state"}
    # Sweep-5 P0 (live 500): an early-return result that already ran the enemy
    # phase (e.g. a capture choice raised DURING end-turn strategic processing)
    # carried `enemy_phase` RAW — its per-action `new_state` WorldStates hold
    # tuple-keyed caches that crash jsonable_encoder AFTER the turn advanced
    # (the player loses the whole turn's report to a naked 500), and the
    # unfiltered actions leak fog besides. Route it through the same cleaner
    # the main /command path uses.
    if "enemy_phase" in extra:
        cleaned_phase = _build_visible_enemy_phase(extra.pop("enemy_phase"), world)
        if cleaned_phase is not None:
            extra["enemy_phase"] = cleaned_phase
    # PT-H1: the early-return paths reach the wire with `suggestion`
    # intact and no client reads it. Same seam, same treatment. Computed
    # BEFORE the pops, because it reads both keys.
    _message = _message_with_suggestion(extra)
    extra.pop("message", None)
    response = build_base_response(
        world,
        success=extra.pop("success", False),
        message=_message,
        events=extra.pop("events", []),
        include_popup_passthroughs=drain_popups,
        **extra
    )
    if not drain_popups:
        _fill_popup_keys_without_draining(response)
    return response


def _build_command_response(result: dict, world, feedback: dict | None = None) -> dict:
    """Build the main /command response from the shared base contract.

    /command still has one legitimate divergence from the default builder:
    when enemy_phase is present, choice-requiring popups are deferred so Godot
    can show the end-turn report first. Start from build_base_response() and
    layer only that specialized post-processing afterward.
    """
    response = build_base_response(
        world,
        success=result.get("success", False),
        message=_message_with_suggestion(result) or "Command executed",
        events=result.get("events", []),
        include_popup_passthroughs=False,
        queue_informational_notices=False,
        include_notifications=False,
        action_info=result.get("action_info", {}),
        # Turn the enemy phase actually happened on (before advance_turn increments).
        turn_ended=int(result["turn_ended"]) if "turn_ended" in result else None,
    )
    if feedback:
        response["feedback"] = feedback
    return response


def _message_with_suggestion(result: dict) -> str:
    """PT-H1 — the executor's recovery hint finally reaches the player.

    43 `"suggestion":` literals across nine backend files build a
    concrete next step — "Try 'move to Rhineland' to get closer first",
    "Targets in range: Mack, Charles" — and there is NO consumer, on
    either side. `main.py` contains the word exactly once, in a comment;
    `main.gd` contains it zero times. On the main path it does not even
    reach the wire: `_copy_truthy_result_fields` reads a fixed allowlist
    that omits it, so the key is discarded at the API boundary. One of
    108 responses in the campaign contained the word at all.

    Appended to the MESSAGE rather than wired as a new field, because
    that covers all 43 producers at one seam and needs no client change —
    and because PT-H1 is PT-H2's root cause: the refusal that told the
    player "Range: 1, Distance: 2" and nothing else was carrying the
    working synonym the whole time.
    """
    message = str(result.get("message", "") or "")
    suggestion = str(result.get("suggestion", "") or "").strip()
    if not suggestion or suggestion in message:
        return message
    return f"{message}\n{suggestion}" if message else suggestion


_COMMAND_RESULT_SIMPLE_FIELDS = (
    "show_load_dialog",
    "cavalry_terrain_message",
    "bombardment_advisory",
    "battle_report",
    # BD: the Battle Diorama tableau payload (display-only, fog-gated at
    # build time in battle_diorama.build_battle_diorama)
    "battle_diorama",
    # NV-7: the same tableau for a §4.4 fleet action. Built at the
    # resolver, so a naval battle can never reach the player without its
    # picture (the BD §14.1 lesson).
    "naval_diorama",
    "reinforcement_messages",
    "coordination_tutorial",
    "opening_attack_guidance",
    "mild_concerns",
    "morning_dispatch",
    # G4F-21: failed mounts (e.g. opening a settlement on an archived war)
    # name their refusal code and recovery surface; the /command response
    # dropped them while /respond_to_diplomatic_dialogue passed them through.
    "error",
    "error_display",
    "recovery_route",
)


def _copy_truthy_result_fields(
    response: dict, result: dict, field_names: tuple[str, ...]
) -> None:
    """Copy simple truthy executor fields into the API response."""
    for field_name in field_names:
        value = result.get(field_name)
        if value:
            response[field_name] = value


def _include_peace_ratification_summary(response: dict, result: dict) -> None:
    """Pass BPH-D ratification summaries through command response builders."""
    summary = result.get("peace_ratification_summary")
    proposal_result = response.get("proposal_result")
    if not summary and isinstance(proposal_result, dict):
        summary = proposal_result.get("peace_ratification_summary")
    if not summary:
        return

    response["peace_ratification_summary"] = summary
    if isinstance(proposal_result, dict):
        proposal_result["peace_ratification_summary"] = summary


def _include_command_bombardment_result(response: dict, result: dict) -> None:
    """Pass through bombardment payloads and keep the explicit action marker."""
    bombardment_result = result.get("bombardment_result")
    if bombardment_result:
        response["bombardment_result"] = bombardment_result
        response["action"] = "bombardment"


def _include_command_redemption_event(response: dict, result: dict, world) -> None:
    """Surface redemption choice state and persist it for the follow-up endpoint."""
    redemption_event = result.get("redemption_event")
    if redemption_event:
        response["state"] = "awaiting_redemption_choice"
        response["redemption_event"] = redemption_event
        world.pending_redemption = redemption_event
        print(f"[ALERT] REDEMPTION TRIGGERED for {redemption_event['marshal']}")


def _move_chain_event(action: dict) -> dict | None:
    """The move event a chain hop is stitched by — None if not a pure,
    successful move with a from/to record (anything else is a barrier)."""
    if not action.get("success"):
        return None
    ai_action = action.get("ai_action") or {}
    if ai_action.get("action") != "move":
        return None
    for evt in action.get("events") or []:
        if (isinstance(evt, dict) and evt.get("type") == "move"
                and evt.get("from") and evt.get("to")):
            return evt
    return None


def _forced_march_entry(chain: list[dict], world) -> dict:
    """One entry for a marshal's whole chain: hop DESTINATIONS named (the
    set today's separate bullets already disclose), attrition summed, all
    hop events preserved (a capture-on-move keeps its conquest event, so
    the fall of each province still renders under the one march line).
    The origin is named only when the player's own intel there is FULL —
    it is the one name the per-hop bullets never disclosed."""
    hops = [_move_chain_event(a) for a in chain]
    stages = [h["to"] for h in hops]
    origin = hops[0]["from"]
    losses = sum(int(h.get("march_losses", 0) or 0) for h in hops)
    marshal_name = (chain[0].get("ai_action") or {}).get("marshal", "")

    merged = {k: v for k, v in chain[-1].items() if k != "events"}
    events = []
    for a in chain:
        events.extend(a.get("events") or [])
    merged["events"] = events
    merged["ai_action"] = {
        "marshal": marshal_name,
        "action": "forced_march",
        "target": stages[-1],
    }
    forced = {
        "stages": stages,
        "to": stages[-1],
        "hops": len(stages),
        "march_losses": losses,
    }
    route = list(stages)
    try:
        if world.get_region_intel(origin).visibility == FULL:
            forced["from"] = origin
            route = [origin] + route
    except Exception:
        pass
    merged["forced_march"] = forced
    loss_note = f", {losses:,} lost on the march" if losses > 0 else ""
    merged["message"] = (
        f"{marshal_name} drives a forced march — "
        f"{' → '.join(route)} ({len(stages)} stages{loss_note})"
    )
    return merged


# ════════════════════════════════════════════════════════════════════════
# PC-0 (quiet-France played campaign, Aug 3 2026): the pending-interrupt
# router is a keyword matcher that runs ABOVE the parser and returns before
# it, so none of PARSE-NEG's clause guards were reaching it. Two defects,
# both reproduced live:
#
#   1. Raw `in` matching had no word boundaries, and "flee" is a substring
#      of "fleet" — so EVERY naval order in the game answered a cornered
#      marshal's last stand as "attempt breakout". Typing
#      "set the fleet to raid commerce" with Massena cornered rolled the
#      escape at -10% and lost him ("raise a fleet" is a golden-corpus row).
#   2. No negation guard: `"attack" in cmd_lower` fires on every negated
#      form, and the attack branch is tested BEFORE the hold branch. So
#      PARSE-NEG's own headline sentence — "hold your position, do not
#      attack" — resolves to HOLD at the parser and to ATTACK here.
#
# The corpus eval calls `CommandParser.parse` directly and never traverses
# this router, which is why 514 green rows could not see either one.
#
# Extracted to a pure function so the mapping is one testable source.
# ════════════════════════════════════════════════════════════════════════
_INTERRUPT_KEYWORDS = (
    # (option that must be offered, keywords, resolved choice preference)
    ("fight_to_the_last", ("fight", "last stand", "to the last", "die"),
     ("fight_to_the_last",)),
    ("attempt_breakout", ("breakout", "break out", "escape", "cut out", "flee"),
     ("attempt_breakout",)),
    (None, ("investigate", "march to", "guns", "attack", "charge", "join",
            "commit", "proceed"),
     ("investigate", "attack", "attack_anyway")),
    (None, ("continue", "ignore", "keep going", "carry on", "press on",
            "push on", "push through"),
     ("continue_order", "attack_anyway")),
    (None, ("hold", "stay", "stop", "wait", "halt"), ("hold_position",)),
    (None, ("go around", "reroute", "avoid"), ("go_around",)),
    (None, ("cancel", "abort", "belay"), ("cancel_order",)),
)


def _mentions_whole(text: str, keyword: str) -> bool:
    """Whole-word (or whole-phrase) containment. `flee` must not match
    `fleet`; `cut` must not match `executed`."""
    return re.search(r"(?<![a-z])" + re.escape(keyword) + r"(?![a-z])",
                     text) is not None


def _interrupt_choice_from_text(cmd_lower: str, options) -> Optional[str]:
    """Map a typed reply to one of a pending interrupt's `options`.

    Returns None when nothing matches, which lets the command fall through
    to the normal parse pipeline — where PARSE-NEG's guards apply and a
    genuinely negated order is refused rather than executed affirmatively.
    """
    from backend.ai.clause_guards import mentions_stand_down, strip_negated_clauses

    options = options or []

    # PARSE-NEG: read what SURVIVES the negation, exactly as the parser does.
    # "hold your position, do not attack" -> "hold your position" -> hold.
    # "do not attack" -> nothing survives -> no route, parser refuses.
    effective, _negated = strip_negated_clauses(cmd_lower)
    effective = effective.lower()

    # "stop attacking" / "attack no more" is a STAND-DOWN, never an assault.
    # Without this the attack branch (tested first) wins on the bare verb.
    if mentions_stand_down(effective):
        for candidate in ("cancel_order", "hold_position"):
            if candidate in options:
                return candidate
        return None

    for required, keywords, preferences in _INTERRUPT_KEYWORDS:
        if required is not None and required not in options:
            continue
        # "avoid" is a PARSE-NEG negation marker ("avoid attacking") AND the
        # affirmative label of this very option ("avoid them" = go around).
        # Answering an offered option is not negating an order, and both
        # readings land on go_around here, so this one branch reads the raw
        # text — otherwise the guard blanks the answer to the game's own
        # question and the reply falls through to the parser unanswered.
        haystack = cmd_lower if "go_around" in preferences else effective
        if not any(_mentions_whole(haystack, kw) for kw in keywords):
            continue
        for candidate in preferences:
            if candidate in options:
                return candidate
        return None
    return None


def _addressed_fresh_order_elsewhere(command_text: str, cmd_lower: str,
                                     pending: dict, world) -> bool:
    """PC15-2(b): the typed line explicitly addresses the interrupt's OWN
    marshal but names ground the interrupt is not about — a fresh ORDER,
    not an answer.

    Live case: 'Davout, march to London' while Davout held a cannon_fire
    interrupt resolved as "investigate" and the order to London was eaten.
    An explicitly-addressed command naming a region or enemy outside the
    interrupt's own context (its location / enemy / blocked destination)
    falls through to the parser; the executor's override-cancel then clears
    an order-bound interrupt with the order it replaces (TUT-F4a).

    Un-addressed answers ("press on", "hold", "investigate the guns") keep
    the current keyword behaviour by construction — no leading address
    token, no fresh-order reading.
    """
    from backend.ai.llm_client import name_match_patterns, unique_name_tokens
    from backend.commands.parser import _leading_addressed_token

    if not _leading_addressed_token(command_text):
        return False

    # ── The interrupt's OWN ground ────────────────────────────────────────
    # NPC-20: this was a hand-kept three-key literal (location / enemy /
    # destination) while each builder names its ground independently —
    # cannon_fire stores `battle_location`, muster_confirm stores `target`,
    # last_stand stores only `enemy`. So `own_ground` was EMPTY for every
    # cannon-fire interrupt, and the guard read the marshal's own battle as
    # "somewhere else". Derived from the payload's own string values now, so
    # a new interrupt type inherits the right behaviour without editing this
    # seam again. Non-strings (requires_input, muster_preview) drop out;
    # membership below is exact equality, so a stray value like
    # enemy_nation="Austria" is inert.
    # `battle_location` is deliberately NOT ground. Review round, August 16
    # 2026: including it silently un-did PC15-2(b) for cannon_fire — with the
    # battle province in the set, an addressed "Ney, march to Swabia" during
    # a "cannon fire at Swabia" interrupt stopped reading as the MARCH the
    # player typed and was consumed as `investigate`, which launches an
    # AP-free, objection-free ATTACK. Naming the guns is ambiguous between
    # "yes, go" and "march there", and a line that says march must not become
    # an assault. The other builders' ground keys are unambiguous and stay.
    _NON_GROUND_KEYS = {
        "marshal", "interrupt", "interrupt_type", "message", "options",
        "command", "order_status", "action_taken", "battle_location",
    }
    own_ground = set()
    for _k, _v in (pending or {}).items():
        if _k in _NON_GROUND_KEYS or not isinstance(_v, str) or not _v:
            continue
        # Both registers of the own-ground name, for the same reason the
        # needles below carry both — otherwise fixing NPC-1 INVERTS it: the
        # needle would be "archduke charles" while own_ground held only
        # "archdukecharles", so an answer naming the interrupt's own enemy
        # would newly read as a fresh order.
        own_ground.update(name_match_patterns(_v))
    own_ground.discard("")

    for region_name in world.regions.keys():
        rl = region_name.lower()
        if rl in own_ground:
            continue
        if _mentions_whole(cmd_lower, rl):
            return True

    # ── Enemies named in the line ─────────────────────────────────────────
    # NPC-1: this loop used to match `em.name.lower()` — the internal scenario
    # KEY ("archdukecharles") — against text the player writes in the register
    # the game PRINTS ("Archduke Charles", via display_names.humanize_entity_name).
    # For every enemy whose two registers differ the guard answered "nothing
    # foreign named", and its False branch does not merely fail to help: it
    # routes the line into the pending interrupt as an ANSWER. Measured, at
    # the 1805 boot with Ney holding a stale contact_bad_odds about Mack:
    # "Ney, attack Archduke Charles" -> "Ney attacks MACK and wins", 21,974
    # Austrian casualties, Charles untouched — while "Ney, attack
    # ArchdukeCharles" refused honestly. The player was punished for copying
    # the game's own spelling.
    # The roster the player can NAME is wider than the roster that is
    # standing. Review round, August 16 2026 — the first cut of this fix
    # corrected the register and left the MEMBERSHIP premise alone, so the
    # P1 survived one step over: `destroy_marshal` removes the fallen from
    # `world.marshals`, so a player who had just read "Marshal Kutuzov's
    # corps has been DESTROYED" in his own dispatch and typed "Ney, attack
    # Kutuzov" was still routed into the interrupt — measured, **Mack
    # 52,000 -> 0, Austria's army annihilated by an order naming a dead
    # Russian.** Bench names in the authored `marshal_pool` (Bagration,
    # Wellesley) were invisible the same way. Any name the game has shown
    # the player must be heard here; the parser's own tombstone refusal
    # (PC15-4) then answers honestly instead of a battle happening.
    player_nation = world.player_nation
    enemy_names = [em.name for em in world.marshals.values()
                   if em.nation != player_nation]
    enemy_names += [n for n, rec in getattr(world, "fallen_marshals", {}).items()
                    if (rec or {}).get("nation") != player_nation]
    for _nation, _pool in (getattr(world, "marshal_pool", {}) or {}).items():
        if _nation == player_nation:
            continue
        for _entry in (_pool or []):
            _n = _entry.get("name") if isinstance(_entry, dict) else _entry
            if _n:
                enemy_names.append(str(_n))
    for name in enemy_names:
        for needle in name_match_patterns(name):
            if needle in own_ground:
                continue
            if _mentions_whole(cmd_lower, needle):
                return True
    # ...and by surname, the way people actually address a general. The
    # uniqueness gate is computed over the whole candidate SET (never per
    # name), which is the entire safety argument: "charles" and "john" each
    # identify exactly one Archduke and are admitted; "archduke" belongs to
    # both and is dropped, so a shared token can never silently pick one of
    # two real armies. Single source with the parser — llm_client.unique_name_tokens.
    for token, owner in unique_name_tokens(enemy_names).items():
        if token in own_ground or owner.lower() in own_ground:
            continue
        if _mentions_whole(cmd_lower, token):
            return True
    return False


def _addressed_lost_marshal_refusal(command_text: str, world):
    """PC15-4: an order addressed to a FALLEN or CAPTURED marshal refuses
    by name — never roster-nearest substitution.

    Live case: 'Ney, attack Archduke Charles' with Ney destroyed → the LLM
    parse failed validation ("Unknown marshal: Ney"), fell back to the
    fast parser's bare `attack`, and Soult's muster/battle ran. The roster
    of the dead IS knowable (world.fallen_marshals, PC15-1) — the address
    seam now reads it. Never-existed names keep the CR-2 unknown-name
    clarify; living names keep the normal path.

    Returns the refusal sentence, or None to proceed.
    """
    from backend.ai.validation import _marshal_mentioned
    from backend.commands.parser import _leading_addressed_token
    from backend.game_logic.formations import formed_display_name

    token = _leading_addressed_token(command_text)
    if not token:
        return None
    # A living player marshal owns the normal path — unless he is a
    # PRISONER: captured marshals stay on the roster at strength 0 by
    # design (W6-7), so an addressed order used to bind to a 0-strength
    # corps in a foreign capital and fail with a generic strength message.
    for m in world.get_player_marshals():
        if _marshal_mentioned(token, m.name):
            captor = getattr(m, "captured_by", "")
            if captor:
                return (f"Marshal {m.name} is a prisoner of "
                        f"{formed_display_name(world, captor)}, Sire — no "
                        f"order can reach him until his release.")
            return None
    fallen = getattr(world, "fallen_marshals", None) or {}
    for name, tomb in fallen.items():
        if (tomb or {}).get("nation") != world.player_nation:
            continue
        if _marshal_mentioned(token, name):
            location = (tomb or {}).get("location") or "the field"
            line = (f"Marshal {name} is lost to us, Sire — his corps was "
                    f"destroyed at {location}. His name cannot lead the "
                    f"army again.")
            # PT-J4 discipline: the recovery path is named only when the
            # executor's own commission gate would grant it RIGHT NOW.
            try:
                from backend.game_logic.recruitment import (
                    first_affordable_commission,
                )
                bench = first_affordable_commission(
                    world, world.player_nation)
            except Exception:
                bench = None
            if bench is not None:
                line += (f" The Marshalate holds men yet — "
                         f"{bench.get('name', '?')} awaits a commission "
                         f"at {int(bench.get('cost', 0)):,}g.")
            return line
    return None


def _collapse_enemy_phase_composition(cleaned_phase: dict) -> dict:
    """PC-3/PC-7 composition collapse, plus CA8-15's empty-nation prune.

    Extracted from `_collapse_enemy_move_chains` by CA8-15 (creative audit,
    Aug 4 2026) so the prune is directly testable — the defect it fixes is
    invisible from the endpoint unless a nation's whole visible phase
    happens to collapse to nothing.
    """
    for nation_data in cleaned_phase.get("nations", {}).values():
        actions = nation_data.get("actions", [])

        def _verb(entry):
            return (entry.get("ai_action") or {}).get("action")

        def _who(entry):
            return (entry.get("ai_action") or {}).get("marshal")

        def _undone_fortify(index, actions=actions) -> int:
            """Index of the unfortify that cancels actions[index], else -1.
            Only the marshal's OWN next action counts — other marshals'
            entries interleave freely and break nothing."""
            name = _who(actions[index])
            if not name:
                return -1
            for ahead in range(index + 1, len(actions)):
                if _who(actions[ahead]) != name:
                    continue
                return ahead if _verb(actions[ahead]) == "unfortify" else -1
            return -1

        dropped, seen_waits, kept = set(), set(), []
        for index, action in enumerate(actions):
            if index in dropped:
                continue
            if _verb(action) == "wait":
                key = (_who(action), (action.get("message") or "").strip())
                if key in seen_waits:
                    continue
                seen_waits.add(key)
            if _verb(action) == "fortify":
                cancels = _undone_fortify(index)
                if cancels != -1:
                    dropped.add(cancels)
                    continue
            kept.append(action)
        nation_data["actions"] = kept

    # ────────────────────────────────────────────────────────────────────
    # CA8-15: PRUNE A NATION THIS PASS EMPTIED.
    #
    # The fog filter is innocent — `_filter_enemy_phase_by_visibility`'s
    # `if filtered_actions:` already drops nations that filter to nothing.
    # The collapse above runs AFTER it and had no such guard, and PC-3's
    # fortify->unfortify arm removes BOTH entries, so a nation whose whole
    # visible phase was one cancelled fortify kept its heading and lost its
    # body. Godot prints the header before it touches the list
    # (enemy_phase_dialog.gd:75-89), so a great power was announced by name
    # in the enemy phase and then said nothing — on the one screen whose
    # entire job is to report what Europe did.
    #
    # Self-inflicted by the composition slice, and fixed at the same layer.
    # ────────────────────────────────────────────────────────────────────
    nations = cleaned_phase.get("nations", {})
    for nation in [n for n, d in nations.items() if not d.get("actions")]:
        del nations[nation]
    return cleaned_phase


def _collapse_enemy_move_chains(cleaned_phase: dict, world) -> dict:
    """PT-D4 (Aug-1 played-world re-measure): a corps legally chains 3-4
    moves per enemy phase (symmetric AP), but 3-4 separate "moves to X"
    bullets read as teleportation — the loudest contributor to the
    addendum's "enemy phase as theater: 5.5". Chains of 3+ hops render as
    ONE forced-march line. Presentation only: runs AFTER the fog filter,
    merges only entries that survived it, and never touches the moves
    themselves. A marshal's own non-move action (or a hop discontinuity)
    breaks his chain; other marshals' interleaved entries do not.
    """
    for nation, nation_data in cleaned_phase.get("nations", {}).items():
        actions = nation_data.get("actions", [])
        if len(actions) < 3:
            continue

        # Per-marshal open segments: name -> list of action indices.
        segments: dict[str, list[int]] = {}
        closed: list[list[int]] = []

        def _flush(name: str):
            seg = segments.pop(name, None)
            if seg and len(seg) >= 3:
                closed.append(seg)

        for idx, action in enumerate(actions):
            ai_action = action.get("ai_action") or {}
            name = ai_action.get("marshal", "")
            if not name:
                continue
            evt = _move_chain_event(action)
            if evt is None:
                _flush(name)
                continue
            seg = segments.get(name)
            if seg:
                prev_evt = _move_chain_event(actions[seg[-1]])
                if prev_evt and prev_evt.get("to") == evt.get("from"):
                    seg.append(idx)
                    continue
                _flush(name)
            segments[name] = [idx]
        for name in list(segments):
            _flush(name)

        if not closed:
            continue

        replace_at = {seg[-1]: seg for seg in closed}
        drop = {i for seg in closed for i in seg[:-1]}
        rebuilt = []
        for idx, action in enumerate(actions):
            if idx in drop:
                continue
            if idx in replace_at:
                chain = [actions[i] for i in replace_at[idx]]
                rebuilt.append(_forced_march_entry(chain, world))
            else:
                rebuilt.append(action)
        nation_data["actions"] = rebuilt
        nation_data["action_count"] = len(rebuilt)

    # Keep the fog filter's invariants: totals and summary reflect the
    # ── PC-2: drop a marshal's REPEATED no-op within one phase ──────────
    # `wait` costs 0 AP, so the AI loop re-selects the same marshal and
    # `_evaluate_marshal` — being stateless about "I already waited" —
    # returns the identical dict. The only brake is a `_consecutive_waits
    # >= 2` latch, whose own comment reads "2 waits = nothing useful to do":
    # the design REQUIRES a second wasted no-op to detect idleness, and that
    # second no-op is appended to the results and shipped. Measured: 30
    # verbatim duplicate lines across 41 phases, 23 of them one Bavarian
    # marshal holding position (he is authored `literal`, and P8's literal
    # arm is one of five `wait` producers with no `None` sibling).
    #
    # Fixed at the VIEW layer beside PT-D4's move-chain collapse, by the same
    # precedent and for the same reason: the producer's `action_count` and
    # `max_total_actions` break are computed before the append, so pruning
    # inside the loop would desynchronise the budget and reach BASELINE_SERIES.
    # Here nothing but the rendering changes, and it covers all five
    # producers rather than the one that happened to be loudest.
    #
    # ── PC-3: and drop a fortify he undoes in the same breath ───────────
    # P5 fortifies (the marshal is not yet dug in, so P3.5 declined and fell
    # through); the executor sets `fortified` at once; the next loop
    # iteration re-runs the ladder from the top, P3.5 now applies, and its
    # CHECK 2 unfortifies him. The existing guards are one-directional —
    # `_unfortified_this_turn` and `ai_refortify_cooldown` block
    # unfortify → re-fortify and nothing blocks fortify → unfortify — which
    # is why that is the only shape ever observed (41 thrash occurrences in
    # 41 phases; Brunswick on turns 14/16/18, the arithmetic of the 2-turn
    # cooldown). PT-F6 is square-scoped and does not reach it.
    #
    # Collapsed here rather than latched in the producer, DELIBERATELY: the
    # producer fix was built and measured, and it diverges BASELINE_SERIES
    # at index 2 AND collapses the AI-V §4.7 variance signature (two seeds
    # then agree on war count, war turns and fight-rung courts). Attribution
    # was verified by experiment — disabling the latch reproduces both pins
    # byte-identically. Weakening a behaviour guarantee to fix a narration
    # complaint is the wrong trade, so the 2 wasted AP and the defeated
    # stagnation counter stay OPEN as a balance row with the experiment
    # already done; what the player READS is fixed here, at the layer
    # PT-D4 established for exactly this.
    _collapse_enemy_phase_composition(cleaned_phase)

    # entries actually shown.
    total = 0
    rebuilt_summary = []
    for nation, nation_data in cleaned_phase.get("nations", {}).items():
        entries = nation_data.get("actions", [])
        total += len(entries)
        for action in entries:
            ai_action = action.get("ai_action") or {}
            if ai_action:
                entry = f"{ai_action.get('marshal', 'Unknown')}: {ai_action.get('action', 'unknown')}"
                if ai_action.get("target"):
                    entry += f" → {ai_action.get('target')}"
                rebuilt_summary.append(entry)
    cleaned_phase["total_actions"] = total
    cleaned_phase["summary"] = rebuilt_summary
    return cleaned_phase


def _join_courts(names: list, capitalize: bool = False) -> str:
    """PT-E4: "A", "A and B", "A, B and C", "A, B and four others".

    Bounded like IGR-B's `COLLAPSE_NAMED_LIMIT`: a short list loses no
    names, a long one stops being a wall. The 1805 boot can hide nine
    courts at once.
    """
    _NAMED_LIMIT = 3
    names = [str(n) for n in names if str(n).strip()]
    if not names:
        return ""
    if len(names) > _NAMED_LIMIT:
        rest = len(names) - _NAMED_LIMIT
        head = ", ".join(names[:_NAMED_LIMIT])
        joined = f"{head} and {rest} other court{'s' if rest != 1 else ''}"
    elif len(names) == 1:
        joined = names[0]
    else:
        joined = ", ".join(names[:-1]) + " and " + names[-1]
    if capitalize and joined:
        joined = joined[0].upper() + joined[1:]
    return joined


def _build_visible_enemy_phase(enemy_phase: dict, world) -> dict | None:
    """Serialize enemy-phase data and apply fog filtering for Godot."""
    from backend.display_names import with_definite_article
    from backend.game_logic.formations import formed_display_name

    cleaned_phase = {
        "nations": {},
        "total_actions": enemy_phase.get("total_actions", 0),
        "summary": [],
    }

    for nation, nation_data in enemy_phase.get("nations", {}).items():
        cleaned_actions = []
        for action in nation_data.get("actions", []):
            cleaned_action = {k: v for k, v in action.items() if k != "new_state"}
            if DEBUG_MODE:
                if "events" in cleaned_action:
                    print(
                        f"[ENEMY_PHASE_DEBUG] {nation} action has events: "
                        f"{len(cleaned_action.get('events', []))} events"
                    )
                    for evt in cleaned_action.get("events", []):
                        print(f"  - Event type: {evt.get('type')}, keys: {list(evt.keys())}")
                else:
                    print(
                        f"[ENEMY_PHASE_DEBUG] {nation} action has NO events! "
                        f"Keys: {list(cleaned_action.keys())}"
                    )
            cleaned_actions.append(cleaned_action)
        cleaned_phase["nations"][nation] = {
            "actions": cleaned_actions,
            "action_count": nation_data.get("action_count", 0),
        }

    if enemy_phase.get("enemy_victory"):
        cleaned_phase["enemy_victory"] = enemy_phase["enemy_victory"]

    raw_total = cleaned_phase.get("total_actions", 0)
    raw_nations = list(cleaned_phase.get("nations", {}).keys())
    cleaned_phase = _filter_enemy_phase_by_visibility(cleaned_phase, world)
    cleaned_phase = _collapse_enemy_move_chains(cleaned_phase, world)

    # ── CA9-N40: `action_count` is what the CLIENT prints, and it was the
    # PRODUCER's number. Three passes rewrite `actions` after it is
    # copied — the fog filter, the wait-spam collapse and the move-chain
    # collapse (which sets it, alone among the three) — so the header said
    # "4 actions" over two lines. Measured wrong on 8 nation-turns.
    # Recomputed once, at the END of the pipeline, so a fourth pass
    # inherits it. Must run BEFORE the F7 line below, which quotes it.
    for _nd in cleaned_phase.get("nations", {}).values():
        _nd["action_count"] = len(_nd.get("actions", []))

    if cleaned_phase.get("total_actions", 0) > 0 or cleaned_phase.get("enemy_victory"):
        # ── CA9-F7 / CA8-15 §2a: the fog fallback was WHOLE-PHASE ────────
        # It fired only when EVERY court's actions were hidden — once in
        # fifteen phases, and it then named all nine courts at once. The
        # ordinary case is the one that went unreported: some courts
        # visible, others entirely fogged, and the fogged ones simply
        # vanished from the screen with no sign they had acted.
        #
        # Under a NEW key, deliberately. `enemy_phase_dialog.gd` branches
        # on `fog_hidden_summary` INSTEAD OF the nations loop, so reusing
        # it here would delete every visible action — which is the exact
        # shape of the defect it is meant to close.
        #
        # PT-E4: ONE sentence, naming the courts. The list comprehension
        # here emitted a full sentence per hidden court and
        # `enemy_phase_dialog.gd:96-100` printed every one with no cap, no
        # dedupe and no collapse — measured 7-10 near-identical lines on
        # 16 of 18 phases, all ending in the same seven words. It is the
        # single largest contributor to the ~149 fog sentences the
        # campaign produced against 63 real enemy actions, and it is why
        # narration is held under 7 by VOLUME rather than quality.
        #
        # Still a list, because that is the shape the client's loop
        # consumes — one entry, so no `.gd` change and no new key.
        _visible = set(cleaned_phase.get("nations", {}).keys())
        _hidden = [n for n in raw_nations if n not in _visible]
        if _hidden:
            _names = [with_definite_article(formed_display_name(world, n))
                      for n in _hidden]
            cleaned_phase["fog_hidden_nations"] = [
                f"{_join_courts(_names, capitalize=True)} stirred as well, "
                f"but their formations remain beyond our sight."
            ]
        return cleaned_phase
    if raw_total > 0:
        # N28 (CA9): the raw tag reached the player — "within Ottoman's
        # borders". `display_nation` is the chokepoint (Ottoman -> Ottoman
        # Empire); `humanize_entity_name` is a NO-OP on it, being the
        # camelCase MARSHAL repair. `formed_display_name` wraps
        # `display_nation` and adds the NA-6 dead-name repair for free.
        # `with_definite_article` also kills the unfiled sibling: the
        # possessive rendered "Papal States's borders", and PapalStates is
        # in the boot roster.
        cleaned_phase["fog_hidden_summary"] = [
            f"Our scouts report activity within the borders of "
            f"{with_definite_article(formed_display_name(world, nation))}, "
            f"but their formations remain beyond our sight."
            for nation in raw_nations
        ]
        return cleaned_phase
    return None


def _include_command_enemy_phase(response: dict, result: dict, world) -> None:
    """Attach enemy-phase payloads without leaking hidden actions."""
    enemy_phase = result.get("enemy_phase")
    if not enemy_phase:
        return

    cleaned_phase = _build_visible_enemy_phase(enemy_phase, world)
    if cleaned_phase is not None:
        response["enemy_phase"] = cleaned_phase

    if DEBUG_MODE and cleaned_phase is not None:
        print("[ENEMY_PHASE_FINAL] Sending to Godot:")
        for nation, data in cleaned_phase.get("nations", {}).items():
            print(f"  {nation}: {len(data.get('actions', []))} actions")
            for i, act in enumerate(data.get("actions", [])):
                has_events = "events" in act and len(act.get("events", [])) > 0
                print(
                    f"    [{i}] {act.get('ai_action', {}).get('action', '?')} "
                    f"- has_events: {has_events}"
                )


def _include_command_strategic_reports(response: dict, result: dict) -> None:
    """Pass through strategic reports and preserve debug visibility."""
    strategic_reports = result.get("strategic_reports")
    if strategic_reports:
        response["strategic_reports"] = strategic_reports
        # NPC-16 / WIN-H1: an interrupt raised during END-TURN processing
        # rides ONLY strategic_reports[i].requires_input. The Godot client
        # derives it from that list (main.gd:4218), but every OTHER
        # consumer — the playtest driver, any headless or scripted client
        # — saw nothing to answer, so step 0a returned "awaiting_response"
        # forever and the marshal, then the turn loop, froze. Promote the
        # first report awaiting input to the key the synchronous interrupt
        # path already uses, so ONE contract serves both routes.
        #
        # This is only safe BECAUSE main.gd's `_response_has_interrupt_route`
        # now DEFERS whenever the response also carries a report awaiting
        # input. Without that guard the client's route table — consulted at
        # main.gd:1909, before the strategic-reports branch at :2000, in the
        # same function, and returning — would fire the interrupt popup and
        # skip the summary narrating the turn. The two changes are a PAIR;
        # neither ships alone, and a test pins the client half.
        #
        # Never overwrite a live pending_interrupt: that one is the
        # immediate, more specific surface.
        if not response.get("pending_interrupt"):
            awaiting = next((r for r in strategic_reports
                             if isinstance(r, dict) and r.get("requires_input")),
                            None)
            if awaiting:
                response["pending_interrupt"] = awaiting
                response["requires_input"] = True
        if DEBUG_MODE:
            print(f"[STRATEGIC_REPORTS] Sending {len(strategic_reports)} reports to Godot:")
            for i, sr in enumerate(strategic_reports):
                print(
                    f"  [{i}] {sr.get('marshal')}: {sr.get('command')} -> "
                    f"{sr.get('action', 'N/A')}, status={sr.get('order_status')}, "
                    f"has_battle={bool(sr.get('battle_details'))}"
                )
    elif DEBUG_MODE:
        print(f"[STRATEGIC_REPORTS] No strategic reports in result (keys: {[k for k in result.keys() if 'strat' in k.lower()]})")


def _include_command_tactical_events(response: dict, result: dict, world) -> None:
    """Pass through fog-filtered tactical events for the turn log."""
    tactical_events = result.get("tactical_events")
    if tactical_events:
        response["tactical_events"] = _filter_tactical_events_by_visibility(
            tactical_events, world
        )


def _include_command_independent_report(response: dict, result: dict) -> None:
    """Pass through independent command report payloads when present."""
    if result.get("show_independent_command_report"):
        response["show_independent_command_report"] = True
        response["independent_command_report"] = result.get(
            "independent_command_report", []
        )


def _apply_command_popup_contract(response: dict, result: dict, world) -> None:
    """Apply the one /command-specific popup deferral rule after base response build."""
    if not response.get("enemy_phase"):
        if result.get("ai_proposal"):
            response["ai_proposal"] = result["ai_proposal"]
            if world.pending_diplomatic_dialogue:
                response["diplomatic_dialogue"] = world.pending_diplomatic_dialogue
        _include_popup_passthroughs(response, world)
        return

    # IGR-F: the letter-book is a CHOICE surface, so it follows the same
    # deferral as every other choice popup — the end-turn report is read
    # first. It is derived, not queued, so deferring is just blanking the
    # key: the next response rebuilds it from the same dialogues. This puts
    # the digest in exactly the slot the modal storm used to occupy (the
    # first response of the new turn), which is what "interrupts a command
    # in flight" described.
    response["envoy_digest"] = None

    # PL-5A + PL-30: proposal results are informational-only and safe to show
    # alongside enemy_phase; other choice popups stay deferred on world.
    proposal_result = world.proposal_result_popup
    if proposal_result is not None:
        from backend.display_names import diplomatic_decision_reason_display

        proposal_result = dict(proposal_result)
        if (
            proposal_result.get("decision_reason")
            and not proposal_result.get("decision_reason_display")
        ):
            proposal_result["decision_reason_display"] = diplomatic_decision_reason_display(
                str(proposal_result.get("decision_reason", ""))
            )
            world.proposal_result_popup = proposal_result
        response["proposal_result"] = proposal_result
        world.proposal_result_popup = None

    # NA-6 §11.8 stage 2 — the SAME carve-out, for the same reason. A
    # formation almost always fires during the turn tick, which is exactly
    # the response carrying `enemy_phase`; deferred, the Proclamation would
    # surface a full command later, long after the dispatch already
    # announced it. The card is choice-less and informational, so it is
    # safe beside enemy_phase on the PL-5A/PL-30 rationale.
    proclamation = world.nation_proclamation_popup
    if proclamation is not None:
        response["nation_proclamation"] = proclamation
        world.nation_proclamation_popup = None
        # Refill the slot from the overflow so a second formation on the
        # same tick is delivered on the very next response rather than
        # stranded behind an empty slot.
        if getattr(world, "nation_proclamation_popups", None):
            world.nation_proclamation_popup = world.nation_proclamation_popups.pop(0)


def _finalize_command_notifications(response: dict, world) -> None:
    """Drain informational notices into the persistent notification rail."""
    _queue_informational_diplomacy_notices(response, world)
    # Always emit the key — see the note in `build_base_response`. An omitted
    # key reads to the client as "no change", not "nothing left".
    response["notifications"] = world.notifications.get_pending()


def _apply_command_result_layers(response: dict, result: dict, world) -> None:
    """Keep /command post-processing centralized instead of hand-layered inline."""
    _copy_truthy_result_fields(response, result, _COMMAND_RESULT_SIMPLE_FIELDS)
    _include_command_bombardment_result(response, result)
    _include_command_redemption_event(response, result, world)
    _include_command_enemy_phase(response, result, world)
    _include_command_strategic_reports(response, result)
    # PT-F1: the autonomous glory attacks, carried whole (minus
    # `new_state`, stripped at the producer) so the client's existing
    # battle renderers can show the battle the player was only TOLD
    # about.
    if result.get("jealousy_attacks"):
        response["jealousy_attacks"] = result["jealousy_attacks"]
    _include_command_tactical_events(response, result, world)
    _include_command_independent_report(response, result)
    _apply_command_popup_contract(response, result, world)
    _include_peace_ratification_summary(response, result)
    _finalize_command_notifications(response, world)


def _derive_proposal_result_outcome(result: dict) -> str:
    """Best-effort ACCEPT/REJECT normalization for fallback proposal popups."""
    raw_outcome = result.get("outcome", result.get("result", ""))
    if raw_outcome is not None:
        normalized = str(raw_outcome).strip().upper()
        if "REJECT" in normalized or "DECLIN" in normalized or "COUNTER" in normalized:
            return "REJECT"
        if "ACCEPT" in normalized or "APPROV" in normalized or "SUCCESS" in normalized:
            return "ACCEPT"

    if "accepted" in result:
        return "ACCEPT" if bool(result.get("accepted")) else "REJECT"

    message = str(result.get("message", "")).lower()
    if ("reject" in message or "declin" in message or "empty-handed" in message
            or "not agree" in message or "unacceptable" in message):
        return "REJECT"
    if "accept" in message or "agreed" in message or "excellent news" in message:
        return "ACCEPT"
    # Gate-4 1805 smoke (E-4): a successful in-transit dispatch ("Talleyrand
    # departs for the Saxony court... Expect a response by next turn.") is
    # neither accepted nor rejected — the hard REJECT default titled every
    # such send "Diplomatic Action Rejected" on the notice rail.
    if ("departs for" in message or "expect a response" in message
            or "expect an answer" in message or "en route" in message):
        return "PENDING"

    return "REJECT"


def _queue_informational_diplomacy_notices(response: dict, world) -> None:
    """Mirror informational diplomacy outcomes into the persistent notice rail."""
    proposal_result = response.get("proposal_result")
    if not isinstance(proposal_result, dict) or not proposal_result:
        return

    from backend.notifications import (
        create_notification,
        DIPLOMATIC_PROPOSAL_RESULT,
        NotificationPriority,
    )

    outcome = _derive_proposal_result_outcome(proposal_result)
    target_nation = str(proposal_result.get("target_nation", "Unknown"))
    proposal_type = str(proposal_result.get("proposal_type", "Diplomatic Action"))
    message = str(proposal_result.get("message", "")).strip()
    feedback = str(proposal_result.get("feedback", "")).strip()

    outcome_word = {
        "ACCEPT": "Accepted",
        "PENDING": "Dispatched",
    }.get(outcome, "Rejected")
    # PF-5: at most one proposal-result notice per counterparty on the rail —
    # each diplomatic command otherwise appended a fresh "Action Accepted/
    # Rejected/Dispatched" that re-rendered every turn (the main pile-up source).
    world.notifications.dismiss_by_type(
        DIPLOMATIC_PROPOSAL_RESULT,
        filter_fn=lambda n, t=target_nation: (
            n.get("details", {}).get("target_nation") == t))
    world.notifications.add(create_notification(
        DIPLOMATIC_PROPOSAL_RESULT,
        NotificationPriority.NORMAL,
        f"{proposal_type} {outcome_word}",
        message or f"{target_nation} has responded to our {proposal_type.lower()}.",
        int(world.current_turn),
        details={
            "target_nation": target_nation,
            "proposal_type": proposal_type,
            "outcome": outcome,
            "feedback": feedback,
        },
    ))


def _fill_popup_keys_without_draining(response: dict) -> None:
    """Present-but-None popup keys, WITHOUT popping the queue.

    IGR-F review [1]: `build_base_response` drains the PopupQueue by default,
    and `pop_highest` REMOVES the entry — so a response whose client handler
    ignores popups destroys whatever was queued. That is exactly the shape of
    `POST /mailbox/respond`: `_on_mailbox_row_action_result` reads only
    `success`, `message` and the top-bar fields, so the first Accept in the
    letter-book was eating a deferred `diplomatic_sabotage_popup` (one-shot,
    PERMANENTLY lost) or a Proclamation overflow card. It is reachable on the
    ordinary path — the enemy-phase response defers every choice popup, and
    the letter-book opens over them.

    Keys stay present so the Godot contract (`tests/test_response_pipeline.py`)
    still holds; the popup itself rides the player's next `/command`, which is
    what the client handler's own docstring already promises.
    """
    from backend.models.cooldown_manager import PopupQueue

    for response_key in PopupQueue.RESPONSE_KEYS.values():
        response.setdefault(response_key, None)


_CAPTURE_ANSWER_TOKENS = ("plunder", "secure", "confiscate", "respect")
_CAPTURE_ANSWER_FILLERS = ("the", "in", "at", "of", "province", "region")


def _typed_capture_answer(world, text: str):
    """WO-29 — a typed capture-pipeline answer, and the province it names.

    Returns None when `text` is not a capture answer at all (the command
    then falls through to the ordinary pipeline exactly as before this
    slice). Otherwise returns ``(token, named_region_or_None)``.

    The filed fix was to thread ``dialogue_id`` onto this route so the W6-0
    stale guard would stop being inert here. There is nothing to thread:
    ``CommandRequest`` has no such field, the terminal's request body is
    ``{"command": ...}``, and the client's only capture id is written when
    the MODAL renders — which disables the command line, so the two states
    are mutually exclusive. Server-side the sole candidate is the pending
    question's own id, which would make the guard compare a value with
    itself. So this route binds identity by CONTENT, the way the typed
    diplomatic route already binds by the court's name: name a province and
    the answer is bound to it; name the wrong one and it is refused with
    the real question restated, never applied to a different province.

    Only a REAL province name qualifies an answer. Trailing words that name
    no province ("plunder it") do not reach the handler at all — they fall
    through to the ordinary pipeline and are restated by the executor's
    pending-choice block, exactly as before this slice. The W6-0 router's
    exact-token contract is therefore widened by one shape and no keyword
    ownership moves.
    """
    pending = getattr(world, "pending_capture_choice", None)
    if not pending:
        return None
    parts = (text or "").strip().split()
    if not parts or parts[0] not in _CAPTURE_ANSWER_TOKENS:
        return None
    token = parts[0]
    rest = [w.strip(".,!'\"") for w in parts[1:]]
    while rest and rest[0].lower() in _CAPTURE_ANSWER_FILLERS:
        rest.pop(0)
    if not rest:
        return (token, None)
    named = " ".join(rest)
    for region_name in getattr(world, "regions", {}) or {}:
        if region_name.lower() == named.lower():
            return (token, region_name)
    return None


def _digest_owns(dialogue, world) -> bool:
    """IGR-F: is this dialogue a routine small-court letter?

    The safety valve below re-derives a blocking modal from the ACTIVE
    dialogue on every single response cycle until it is answered — that
    valve, not the popup queue, is what turns a queue of small-court letters
    into N sequential modals. A letter the digest owns must never reach it.
    """
    from backend.game_logic.envoy_digest import is_routine_small_court

    return is_routine_small_court(dialogue, world)


def _include_popup_passthroughs(response: dict, world) -> None:
    """Read the HIGHEST-PRIORITY popup from world, include in response, clear from world.

    R4: Called internally by build_base_response() — do NOT call directly.
    Use build_base_response() or _build_result_response() instead, which
    structurally guarantee popup inclusion. The only exception is the
    /command main response path (enemy_phase popup deferral).

    R6+R76: Uses PopupQueue for priority resolution. Only one popup per response
    cycle. Lower-priority popups remain queued for subsequent cycles.

    Keys are ALWAYS included (None if not set) so Godot can rely on their presence.
    """
    from backend.models.cooldown_manager import PopupQueue
    # V2-90: Auto-pop rebellion popup from list if single field is empty
    if (world.vassal_rebellion_imminent_popup is None
            and getattr(world, 'vassal_rebellion_imminent_popups', None)):
        world.vassal_rebellion_imminent_popup = world.vassal_rebellion_imminent_popups.pop(0)

    # NA-6: same auto-pop for the Proclamation overflow — two nations can
    # form on one tick and the queue slot holds one.
    if (world.nation_proclamation_popup is None
            and getattr(world, 'nation_proclamation_popups', None)):
        world.nation_proclamation_popup = world.nation_proclamation_popups.pop(0)

    # R6: Pop highest-priority popup from queue (clears from world automatically)
    winner_attr, winner_key, winner_value = world._popup_queue.pop_highest()

    # Include the winner in response. Golden Rule 4 (cleared by pop) holds
    # for the queue-backed property slots; NOT for marshal_petition, whose
    # durable state is the plain world field `pending_marshal_petition` —
    # the pop clears only the delivery entry, and the per-turn re-push
    # (jealousy.process_turn) re-queues it until it is ANSWERED
    # (PC15-10 B0, F5-S9 comment correction).
    if winner_key is not None:
        if winner_key == "incoming_proposal" and isinstance(winner_value, dict):
            from backend.display_names import (
                diplomatic_decision_reason_display,
                proposal_display_name,
            )

            popup = winner_value.copy()
            if "proposal_type" in popup and "proposal_type_display" not in popup:
                popup["proposal_type_display"] = proposal_display_name(popup.get("proposal_type"))
            if popup.get("decision_reason") and "decision_reason_display" not in popup:
                popup["decision_reason_display"] = diplomatic_decision_reason_display(
                    str(popup.get("decision_reason", ""))
                )
            response[winner_key] = popup
        elif winner_key == "proposal_result" and isinstance(winner_value, dict):
            from backend.display_names import diplomatic_decision_reason_display

            popup = winner_value.copy()
            if popup.get("decision_reason") and "decision_reason_display" not in popup:
                popup["decision_reason_display"] = diplomatic_decision_reason_display(
                    str(popup.get("decision_reason", ""))
                )
            response[winner_key] = popup
        elif winner_key == "marshal_petition" and isinstance(winner_value, dict):
            # In-game review July 25, 2026: petitions are built inside the turn
            # pass (before advance_turn refills AP), so their priced arms must
            # have affordability re-derived HERE, against the AP the player
            # actually holds when the dialog opens.
            from backend.game_logic.jealousy import refresh_petition_affordability

            response[winner_key] = refresh_petition_affordability(winner_value, world)
        else:
            response[winner_key] = winner_value

    # Set all non-winner response keys to None so Godot can rely on key presence
    for response_key in PopupQueue.RESPONSE_KEYS.values():
        if response_key not in response:
            # Special case: incoming_proposal safety valve from pending dialogue
            if (response_key == "incoming_proposal"
                    and world.pending_diplomatic_dialogue
                    and world.pending_diplomatic_dialogue.get("type")
                    in ("incoming_proposal", "incoming_ultimatum")
                    and winner_attr is not None):
                # A higher-priority popup won — don't derive incoming_proposal from dialogue
                response[response_key] = None
            elif (response_key == "incoming_proposal"
                    and winner_attr is None
                    and world.pending_diplomatic_dialogue
                    and world.pending_diplomatic_dialogue.get("type")
                    in ("incoming_proposal", "incoming_ultimatum")
                    and not _digest_owns(world.pending_diplomatic_dialogue,
                                         world)):
                # BUGFIX: Safety valve — derive clauses from dialogue context
                # instead of hardcoding []. Empty clauses cause blank popup
                # in Godot. See BUGFIX_PLAN_PROPOSAL_FLOW.md.
                # W6-0 (BUG-CA-8): the old inline rebuild here was an
                # impoverished builder — a failed response re-mounted the
                # proposal as "Unknown diplomat" while the prose still named
                # Hardenberg. Route through the same recovery builder the
                # mailbox activation uses: it prefers the dialogue's own rich
                # popup_payload and falls back to the full envoy builder
                # (which resolves the diplomat from world.diplomats).
                dialogue = world.pending_diplomatic_dialogue
                response["incoming_proposal"] = (
                    _build_pending_envoy_popup_from_dialogue(world, dialogue))
            else:
                response[response_key] = None

    # V2-89 → R12C: Auto-promote from queue handled by dialogue_manager.pop() auto-promote.
    # Explicit promote_if_empty() covers the case where current is already None.
    world.dialogue_manager.promote_if_empty()

def _filter_enemy_phase_by_visibility(enemy_phase: dict, world_state) -> dict:
    """
    Fog of War (Session 34B): Filter enemy phase actions by player visibility.

    Fog filters information, not mechanics. The enemy AI ran omnisciently;
    this function redacts the DISPLAY of those actions based on what the
    player can see.

    Rules:
    - Battle involving a player marshal -> ALWAYS SHOW (player was in the battle)
    - Action in FULL visibility region -> show as-is
    - Action below FULL -> suppress (safe default)
    - Missing/unrecognized fields -> suppress (never show more than intended)
    """
    if not enemy_phase or not enemy_phase.get("nations"):
        return enemy_phase

    player_nation = world_state.player_nation
    filtered_phase = {
        "nations": {},
        "total_actions": 0,
        "summary": []
    }

    for nation, nation_data in enemy_phase.get("nations", {}).items():
        filtered_actions = []
        for action in nation_data.get("actions", []):
            # Check 1: Does this action involve a player marshal? (battle)
            involves_player = False

            # NV-9: A FLEET ACTION the player fought. The battle arm below
            # recognises only "battle"/"bombardment" event types, and a
            # §4.4 action emits none of those — an intercepted AI
            # expedition leaves the AI marshal at its home yard (never
            # FULL for the player) and a caught diversion carries no
            # marshal at all, so BOTH fell to the region check and were
            # suppressed. The player's own fleet could lose thirty sail in
            # the enemy phase and hear nothing. The diorama builder has
            # already answered "is the player in this" — read it.
            _sea = action.get("naval_diorama")
            if isinstance(_sea, dict) and _sea.get("player_side") is not None:
                involves_player = True

            events = action.get("events", [])
            if not involves_player and isinstance(events, list):
                for evt in events:
                    if isinstance(evt, dict):
                        # Battle events with player involvement
                        if evt.get("type") in ("battle", "bombardment"):
                            attacker = evt.get("attacker", "")
                            defender = evt.get("defender", "")
                            # attacker/defender can be dicts ({"name": ..., "casualties": ...})
                            # or strings — extract name safely for comparison
                            attacker_name = attacker.get("name", "") if isinstance(attacker, dict) else attacker
                            defender_name = defender.get("name", "") if isinstance(defender, dict) else defender
                            attacker_nation = evt.get("attacker_nation", "")
                            defender_nation = evt.get("defender_nation", "")
                            if (attacker_nation == player_nation or
                                    defender_nation == player_nation):
                                involves_player = True
                                break
                            # Also check marshal names against player marshals
                            for pm in world_state.get_player_marshals():
                                if pm.name in (attacker_name, defender_name):
                                    involves_player = True
                                    break

            # Also check ai_action target against player marshals
            ai_action = action.get("ai_action", {})
            if ai_action and isinstance(ai_action, dict):
                target = ai_action.get("target", "")
                if target:
                    for pm in world_state.get_player_marshals():
                        if pm.name == target:
                            involves_player = True
                            break

            # ── PT-E5: a bloodless capture of OUR OWN SOIL ──────────────
            # Own soil is PARTIAL by construction, so an enemy marching
            # UNOPPOSED into a French province failed both arms above and
            # was suppressed by the FULL gate below — measured three
            # times in three turns (Provence, Languedoc, Rhineland).
            #
            # This is the one screen whose job is reporting what Europe
            # did, and it silently dropped Europe taking our provinces.
            # It leaks nothing: the same payload already flips the
            # province on the map, names the marshal in `fogged_forces`,
            # and leads the briefing with an own-soil wound headline
            # (`home_captured` 99, or `capital_lost` 100 when the province
            # is our own capital — WO slice 4 split the class and demoted
            # the homeland one; this comment said "weight 100" and named
            # only `home_captured`). Precisely the reasoning behind the
            # NV-9 and CA8-15 carve-outs in this same function.
            if not involves_player and isinstance(events, list):
                for evt in events:
                    if not isinstance(evt, dict):
                        continue
                    if evt.get("captured_from") == player_nation:
                        involves_player = True
                        break

            if involves_player:
                filtered_actions.append(action)
                continue

            # Check 2: Determine action region and check visibility
            action_region = None

            # Try to get region from ai_action
            if ai_action and isinstance(ai_action, dict):
                ai_marshal_name = ai_action.get("marshal", "")
                if ai_marshal_name:
                    ai_marshal = world_state.get_marshal(ai_marshal_name)
                    if ai_marshal:
                        action_region = ai_marshal.location

            # If we have a region, check visibility
            if action_region:
                intel = world_state.get_region_intel(action_region)
                if intel.visibility == FULL:
                    # PT-E5, the other direction: keying on the marshal's
                    # location alone OVER-shows. `ai_marshal.location` is
                    # where he finished, so a whole three-hop route through
                    # provinces the player cannot see renders in full
                    # because the traveller happened to end on a lit
                    # square. Show it only if the march BEGAN somewhere we
                    # could see, or ended there having started nowhere we
                    # can name.
                    _origin = ""
                    if isinstance(events, list):
                        for evt in events:
                            if isinstance(evt, dict) and evt.get("from"):
                                _origin = str(evt["from"])
                                break
                    if _origin:
                        _from_intel = world_state.get_region_intel(_origin)
                        if _from_intel.visibility != FULL:
                            # We saw him arrive, not where he came from —
                            # so report the arrival and DROP the road.
                            #
                            # The first cut set a `route_fogged` flag and
                            # showed the action unchanged; the review fleet
                            # proved the flag had no reader anywhere, which
                            # is the same dead field this row is about.
                            # Blanking the origin is what actually stops the
                            # over-show: the renderer builds "X moves from
                            # A to B" from these keys.
                            action = dict(action)
                            _events = [dict(e) if isinstance(e, dict) else e
                                       for e in (action.get("events") or [])]
                            for _e in _events:
                                if isinstance(_e, dict) and _e.get("from"):
                                    _e.pop("from", None)
                            if _events:
                                action["events"] = _events
                            _ai = action.get("ai_action")
                            if isinstance(_ai, dict) and _ai.get("from"):
                                _ai = dict(_ai)
                                _ai.pop("from", None)
                                action["ai_action"] = _ai
                    filtered_actions.append(action)
                    continue
            # Missing region or below FULL -> suppress (safe default)

        if filtered_actions:
            filtered_phase["nations"][nation] = {
                "actions": filtered_actions,
                "action_count": len(filtered_actions)
            }
            filtered_phase["total_actions"] += len(filtered_actions)

    # 2A-1: Rebuild summary from filtered (visible) actions only
    rebuilt_summary = []
    for nation, nation_data in filtered_phase["nations"].items():
        for action in nation_data.get("actions", []):
            ai_action = action.get("ai_action", {})
            if ai_action:
                marshal_name = ai_action.get("marshal", "Unknown")
                action_type = ai_action.get("action", "unknown")
                target = ai_action.get("target", "")
                entry = f"{marshal_name}: {action_type}"
                if target:
                    entry += f" → {target}"
                rebuilt_summary.append(entry)
    filtered_phase["summary"] = rebuilt_summary

    # Preserve enemy_victory if present
    if enemy_phase.get("enemy_victory"):
        filtered_phase["enemy_victory"] = enemy_phase["enemy_victory"]

    return filtered_phase


_filter_tactical_events_by_visibility = _filter_tactical_events_by_fog  # P3-2: consolidated alias


# Allow Godot to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# 3A-1: Serialize state-mutating requests to prevent concurrent corruption
@app.middleware("http")
async def serialize_state_mutations(request: Request, call_next):
    """Serialize all POST requests (state-mutating) behind one lock.

    July 18, 2026 — this used a `threading.Lock` acquired with a plain `with`
    inside an `async def`. That blocks the EVENT LOOP, not just the request:
    the lock is taken on the loop thread and held across `await call_next`, so
    while one POST is in flight nothing else on the server can make progress —
    not another endpoint, not a health check, not the response of the request
    that already finished.

    Ordinarily that is invisible, because the handlers are fast and declared
    with plain `def` (so FastAPI runs them in a threadpool). It stops being
    invisible when a POST blocks on the live LLM parse: a stalled Anthropic
    call could freeze the entire server for the whole timeout, and the client
    double-send pattern the UI-6 chip latch exists to defend against is
    exactly the input that produces a second POST during that window.

    `asyncio.Lock` gives the same mutual exclusion — one POST mutates world
    state at a time — while yielding the loop to other tasks. The lock still
    wraps the whole request rather than a narrower critical section: the
    protection covers ~14 mutating endpoints, and narrowing it to the command
    path alone would leave the rest racing the world object.
    """
    if request.method == "POST":
        async with get_state_lock():
            return await call_next(request)
    return await call_next(request)


class CommandRequest(BaseModel):
    command: str = Field(max_length=500)
    action: str | None = None
    target_nation: str | None = None
    war_id: str | None = None
    # VS-3: the diplomacy wizard's land-grant sub-picker sends the chosen
    # province; without this field pydantic silently DROPS it (pre-build
    # seam verification, July 16, 2026).
    region: str | None = None
    # GT-Slice-4: the SC-5R editor's structured Submit-for-Review fields
    # (`settlement_terms` / `selected_target_nation` /
    # `covered_enemy_participants`) are removed with the freeform editor
    # after a verify-dead pass — no non-editor producer ever sent them.
    # `target_nation` + `war_id` predate them and stay: the War Detail
    # reopen (PF-2) and the diplomacy wizard both send them.


class ObjectionResponse(BaseModel):
    """Request model for responding to marshal objections."""
    choice: str  # 'trust', 'insist', or 'compromise'


class DiplomaticObjectionResponse(BaseModel):
    """Request model for typed Talleyrand objection popup responses."""
    choice: str  # 'proceed', 'modify', or 'cancel'
    action: str | None = None
    target_nation: str | None = None


class RedemptionResponse(BaseModel):
    """Request model for responding to redemption events."""
    choice: str  # 'grant_autonomy', 'dismiss', or 'demand_obedience'


class MarshalPetitionResponse(BaseModel):
    """Request model for the Jealousy v3.2 marshal-petition channel —
    jealousy confrontations, rivalry confrontations, the Fontainebleau
    petition, and war-weary counsel all answer through this one shape."""
    choice: str  # option id from the petition's options list


class GloriousChargeResponse(BaseModel):
    """Request model for responding to Glorious Charge popup."""
    choice: str  # 'charge' or 'restrain'


class CaptureChoiceResponse(BaseModel):
    """Request model for responding to plunder/secure choice (Phase 6.2.E).

    W6-8: also answers the estate stage ('confiscate'/'respect');
    dialogue_id is the optional W6-0 identity of the question the popup
    rendered — a mismatched id is refused instead of misapplied.
    """
    choice: str  # 'plunder' or 'secure' — or 'confiscate' or 'respect'
    dialogue_id: Optional[int] = None


class StrategicInterruptResponse(BaseModel):
    """Request model for responding to strategic command interrupts (Phase D)."""
    marshal_name: str
    response_type: str  # 'cannon_fire', 'blocked_path', 'ally_moving'
    choice: str  # varies by response_type


class LLMConfigRequest(BaseModel):
    api_key: str = ""


class SaveRequest(BaseModel):
    """Request model for saving game state."""
    save_name: str = "Quicksave"


class LoadRequest(BaseModel):
    """Request model for loading a saved game."""
    filename: str


class DeleteSaveRequest(BaseModel):
    """Request model for deleting a save file."""
    filename: str


class NewGameRequest(BaseModel):
    """Request model for /new_game (POSITION 7).

    `scenario` is an ALLOWLIST NAME (see SCENARIO_ALLOWLIST), never a path;
    empty/absent keeps today's boot byte-identical.
    """
    scenario: str = ""


@app.get("/test")
def test_connection():
    """Test endpoint for Godot connection."""
    from backend.game_logic.war_status import build_active_wars
    response = {
        "success": True,
        "status": "ok",
        "message": "Backend is running",
        "turn": int(world.current_turn),
        "gold": int(world.gold),
        "manpower_pools": {
            "infantry": int(world.manpower_pools.get(world.player_nation, {}).get("infantry", 0)),
            "cavalry": int(world.manpower_pools.get(world.player_nation, {}).get("cavalry", 0)),
            "artillery": int(world.manpower_pools.get(world.player_nation, {}).get("artillery", 0)),
        },
        "action_summary": world.get_action_summary(),
        "game_state": world.get_filtered_game_state_summary(),
        # Diplomatic top-bar fields (Session 8A)
        "diplomatic_points": int(getattr(world, 'diplomatic_points', 0)),
        "max_diplomatic_points": _dp_ceiling(world),
        "talleyrand_state": _get_talleyrand_state_label(world),
        "talleyrand_mission_summary": _get_talleyrand_mission_summary(world),
        "threat_level": int(getattr(world, 'threat_level', 0)),
        "coalition_brewing": _player_coalition_brewing(world) is not None,
        "coalition_brewing_turns": int(_player_coalition_brewing(world).get("turns_remaining", 0)) if _player_coalition_brewing(world) else None,
        # Session 2 follow-up: Single source of truth for mailbox badge
        "pending_envoy_count": int(world.dialogue_manager.get_mailbox_count()),
    }
    # War status panel data (N4f) — for HUD initialization on page load
    response["active_wars"] = build_active_wars(world)
    return response


@app.get("/map_topology")
def get_map_topology():
    """Static map topology (adjacency, terrain, grid) for frontend rendering.

    Source of truth for region adjacency shared between backend and Godot.
    Per-turn state (controller, marshals, fog) still lives in
    `game_state.map_data`; this endpoint exposes only authored scenario data.

    Map Slice 5: serves the ACTIVE world's map — the 126-province Europe
    graph on the default bootstrap, the 19-region set under
    SOVEREIGN_MAP=legacy — so backend and renderer can never drift.
    """
    from backend.models.region import get_starting_controllers

    starting_controllers = (
        getattr(world, "_starting_controllers", None) or get_starting_controllers()
    )
    regions = {}
    for name, region in world.regions.items():
        grid = region.grid_position or (0, 0)
        regions[name] = {
            "adjacent": list(region.adjacent_regions),
            "terrain": region.terrain,
            "region_type": region.region_type,
            "is_capital": bool(region.is_capital),
            "starting_controller": starting_controllers.get(name),
            "grid_position": [int(grid[0]), int(grid[1])],
        }
    payload = {
        "success": True,
        "regions": regions,
        "nation_capitals": dict(world.nation_capitals),
    }
    _attach_nation_identity_overrides(payload, world)   # NA-6 §11.8 stage 3
    return payload


@app.post("/command")
def execute_command(request: CommandRequest):
    """Execute a game command and return result."""
    # print(f"\n{'=' * 60}")
    # print(f"📨 COMMAND RECEIVED: '{request.command}'")
    # print(f"   Current turn: {world.current_turn}")
    # print(f"   Actions before: {world.actions_remaining}/{world.max_actions_per_turn}")
    # print(f"{'=' * 60}")

    try:
        # ════════════════════════════════════════════════════════════
        # GAME-OVER GUARD — No actions after the war ends
        # ════════════════════════════════════════════════════════════
        if world.game_over:
            return build_base_response(
                world, success=False, message="The war is over.",
                game_over=True, victory=world.victory)

        # ════════════════════════════════════════════════════════════
        # EMPTY COMMAND CHECK — Reject blank input
        # ════════════════════════════════════════════════════════════
        if not request.command or not request.command.strip():
            return build_base_response(
                world, success=False, message="No command given, Sire.",
                action_info={"remaining": int(world.actions_remaining)})

        # ════════════════════════════════════════════════════════════
        # CR-2: PENDING COMMAND CLARIFICATION — one question, one answer.
        # Typed answers ("Davout", "2", "yes", "cancel") resolve against
        # the stored options into a full deterministic reissue command;
        # anything else clears the question and parses normally
        # (LOCAL_PLANNING never blocks). Consumed either way — the player
        # gets exactly one question per command, never a dialogue loop.
        # Adversarial-review fix: this MUST run before the strategic
        # interrupt loop — the clarification is the most recent question
        # asked, and the interrupt keyword matcher would otherwise hijack
        # answers like "cancel" and leave the dialogue lingering.
        # ════════════════════════════════════════════════════════════
        from backend.commands.clarification import (
            CLARIFICATION_DIALOGUE_TYPE,
            build_marshal_choice_clarification,
            build_unknown_name_clarification,
            interpret_clarification_answer,
            register_pending_clarification,
        )
        from backend.commands.delegation import (
            build_delegation_clarification,
            describe_cautious_delegation,
            detect_delegation,
            maybe_delegation_hint,
            parse_resolved_to_action,
            resolve_delegation_flavor,
            resolve_live_cautious_prefix,
            route_arm,
        )

        command_text = request.command
        pending_clarification = world.dialogue_manager.peek()
        if (pending_clarification is not None
                and pending_clarification.get("type") == CLARIFICATION_DIALOGUE_TYPE
                and not command_text.lower().strip().startswith("cheat ")):
            resolution = interpret_clarification_answer(
                pending_clarification, command_text)
            world.dialogue_manager.pop()
            if resolution["kind"] == "cancel":
                return build_base_response(
                    world, success=True,
                    message="Berthier nods. \"Very well, Sire — the order is withdrawn.\"",
                    action_info={
                        "cost": 0,
                        "remaining": int(world.actions_remaining),
                        "turn_advanced": False,
                        "new_turn": None,
                    })
            if resolution["kind"] == "command":
                print(f"[CLARIFICATION] Resolved answer '{request.command}' "
                      f"-> '{resolution['command']}'")
                command_text = resolution["command"]

        # ════════════════════════════════════════════════════════════
        # PENDING STRATEGIC INTERRUPT CHECK (Phase 5.2-D)
        # If a marshal has a pending interrupt (cannon fire, blocked path),
        # try to map the player's text input to a response choice.
        # This prevents the command from being parsed as a new order.
        # ════════════════════════════════════════════════════════════
        for m in world.get_player_marshals():
            pending = getattr(m, 'pending_interrupt', None)
            if pending:
                cmd_lower = command_text.strip().lower()

                # ── Guard: if command addresses a DIFFERENT marshal, skip ──
                # "grouchy march to brittany" should NOT be routed as
                # Davout's interrupt response just because "march to" matches.
                #
                # PC15-2: the check was ROSTER-BOUND, so a command
                # addressing a name no longer on the roster ('Murat, attack
                # Buxhowden' with Murat destroyed) read as un-addressed and
                # was consumed as Soult's destination_blocked answer. The
                # leading address token is now honoured whether or not the
                # name still lives — any explicit address that is not THIS
                # marshal falls through to the parser (where the CR-2 /
                # PC15-4 guards own the unknown/fallen-name reply).
                known_marshal_names = [
                    pm.name.lower() for pm in world.get_player_marshals()
                ]
                addressed_other = any(
                    name in cmd_lower
                    for name in known_marshal_names
                    if name != m.name.lower()
                )
                if not addressed_other:
                    from backend.ai.validation import _marshal_mentioned
                    from backend.commands.parser import (
                        _leading_addressed_token,
                    )
                    _addr_token = _leading_addressed_token(command_text)
                    if _addr_token and not _marshal_mentioned(
                            _addr_token, m.name):
                        addressed_other = True
                # PC15-2(b): the command explicitly addresses the
                # interrupt's OWN marshal but names ground the interrupt is
                # not about — a fresh ORDER, not an answer ('Davout, march
                # to London' was consumed as a cannon-fire "investigate").
                # Bare un-addressed answers ("press on") keep the current
                # behaviour.
                if not addressed_other and _addressed_fresh_order_elsewhere(
                        command_text, cmd_lower, pending, world):
                    addressed_other = True
                if addressed_other:
                    # Command is for a different marshal — let it parse
                    # normally. Clear a STALE informational interrupt, but
                    # never silently discard a real pending DECISION the player
                    # hasn't answered: a cornered marshal's last stand or an
                    # unconfirmed muster. Dropping those would strand the
                    # marshal (un-retreated forever / attack abandoned).
                    #
                    # Creative audit July 19 2026: the exemption list was an
                    # allow-list of two, so EVERY contact/blocked-path decision
                    # was silently discarded the moment the player addressed a
                    # different marshal — ordering "Davout, support Ney" threw
                    # away the question Ney had just asked. Those are decisions
                    # by the comment's own definition. The rule is now derived
                    # rather than a hand-kept name list (which is what drifted):
                    # an interrupt that OFFERS THE PLAYER OPTIONS is a pending
                    # decision and is preserved; one with no options is pure
                    # information and may be dropped. New interrupt types get
                    # the right behaviour without touching this seam.
                    if not pending.get("options"):
                        m.pending_interrupt = None
                    continue

                options = pending.get("options", [])
                interrupt_type = pending.get("interrupt_type", "")

                choice = _interrupt_choice_from_text(cmd_lower, options)

                if choice:
                    print(f"[INTERRUPT ROUTE] Routing '{request.command}' -> "
                          f"{m.name} {interrupt_type} response: {choice}")
                    from backend.commands.strategic import StrategicOrderProcessor
                    strategic_exec = StrategicOrderProcessor(executor)
                    result = strategic_exec.handle_response(
                        m.name, interrupt_type, choice, world, game_state)
                    return _build_result_response(result, world)

        # ════════════════════════════════════════════════════════════
        # W6-0 (BUG-CA-1): PENDING-QUESTION ROUTER — when the game itself
        # just asked a question, the exact answer tokens IT offered must
        # resolve that question instead of falling into the parser (live
        # audit: with an objection pending, typed "trust" reached the LLM
        # parser bewildered and "insist" hit the diplomatic handler).
        # Deterministic (Golden Rule 6), exact-token only, and each token
        # reroutes ONLY while its matching state is pending — anything else
        # falls through to the normal pipeline untouched (no keyword
        # ownership changes; the fast-parser contract and golden corpus are
        # unaffected). Runs after the clarification/interrupt steps (the
        # most recent questions win) and before CR-4 carryover/parsing.
        # ════════════════════════════════════════════════════════════
        _pending_answer_token = command_text.strip().lower()
        _objection_pending = (
            world.pending_objection is not None
            or getattr(world, "pending_strategic_objection", None) is not None)
        if _pending_answer_token in ("trust", "insist", "compromise") \
                and _objection_pending:
            print(f"[PENDING-QUESTION] Routing '{_pending_answer_token}' "
                  f"-> objection response")
            return _respond_to_objection_sync(_pending_answer_token)
        # CA9-N5: the exact-token gate above rejected plain English meaning
        # one of its own words — "I trust him", "insist on it", "trust
        # Davout" all fell through to the parser and then died on the
        # objection block, which (before this row) did not name the words
        # either. Nothing else can execute while an objection stands, so a
        # line naming exactly ONE answer word as a whole word is
        # unambiguous; two words is ambiguous and gets the question back.
        if _objection_pending and _pending_answer_token:
            # CA9 review round: this sits BEFORE the parser, which is where
            # PARSE-NEG's `strip_negated_clauses` lives — so "I don't trust
            # him", "do not insist" and "no compromise" each matched
            # exactly one word and executed its OPPOSITE. Blank the negated
            # clauses first, with the same guard the parser uses; if the
            # answer word only survives inside the negation, nothing routes
            # and the block re-prompts.
            from backend.ai.clause_guards import strip_negated_clauses
            _answer_text, _ = strip_negated_clauses(_pending_answer_token)
            # `strip_negated_clauses` owns "not"/"don't"/"never" and is the
            # single source for them. It does not treat a BARE "no" as a
            # marker — widening it would move the whole parser — so this
            # router adds the one shape it needs: a refusal immediately
            # before the answer word ("no compromise").
            _answer_text = re.sub(
                r"(?<![a-z])no\s+(trust|insist|compromise)(?![a-z])",
                " ", _answer_text)
            _spoken = [
                w for w in ("trust", "insist", "compromise")
                if re.search(rf"(?<![a-z]){w}(?![a-z])", _answer_text)
            ]
            if len(_spoken) == 1:
                print(f"[PENDING-QUESTION] Plain-English objection answer "
                      f"'{command_text}' -> {_spoken[0]}")
                return _respond_to_objection_sync(_spoken[0])
        _capture_answer = _typed_capture_answer(world, _pending_answer_token)
        if _capture_answer is not None:
            # W6-8: all four capture-pipeline tokens route here; the handler
            # itself is stage-aware (a wrong-stage token is refused with the
            # question restated, never misapplied).
            _cap_token, _cap_region = _capture_answer
            print(f"[PENDING-QUESTION] Routing '{_pending_answer_token}' "
                  f"-> capture choice")
            result = executor.handle_capture_choice(
                _cap_token, game_state, region=_cap_region)
            # IGR-X7: the capture route must not eat a queued popup.
            return _build_result_response(result, world, drain_popups=False)
        if world.pending_diplomatic_dialogue is not None:
            _pending_dlg = world.pending_diplomatic_dialogue
            _dlg_options = _pending_dlg.get("options", []) or []
            if not _dlg_options and isinstance(
                    _pending_dlg.get("popup_payload"), dict):
                _dlg_options = _pending_dlg["popup_payload"].get("options") or []
            _dlg_action_ids = {
                str(opt.get("action") or "").strip().lower()
                for opt in _dlg_options if opt.get("action")
            }
            _is_option_digit = (
                _pending_answer_token.isdigit()
                and 1 <= int(_pending_answer_token) <= len(_dlg_options))
            if _is_option_digit or (
                    _pending_answer_token
                    and _pending_answer_token in _dlg_action_ids):
                _dlg_choice = (int(_pending_answer_token) if _is_option_digit
                               else _pending_answer_token)
                print(f"[PENDING-QUESTION] Routing '{_pending_answer_token}' "
                      f"-> diplomatic dialogue response")
                return _respond_to_dialogue_sync(_dlg_choice)

        # ════════════════════════════════════════════════════════════
        # CR-4: CONTEXT CARRYOVER — resolve shorthand references ("again",
        # "same target", "him"/"there", "not you, Davout") against the
        # command history BEFORE the parser sees them (Golden Rule 6: the
        # rewrite is fully deterministic). A reference with nothing to
        # resolve against gets a helpful in-character reply rather than a
        # confusing parse failure. Runs after the clarification-answer and
        # interrupt steps so those terse answers are never treated as
        # references.
        # ════════════════════════════════════════════════════════════
        from backend.commands.context_carryover import (
            resolve_context_references,
            try_focus_reissue,
        )
        # Safe during a pending diplomatic dialogue too: a terse decline
        # ("no"/"nope"/"not you") with no resolvable marshal falls through as
        # a pass, so it still reaches the dialogue routing; only an explicit
        # reference ("again", "not you, Davout") rewrites — and the resolved
        # military command is then blocked by any hard-stop just as the raw
        # input would be. (Objection answers use /respond_to_objection.)
        carryover = resolve_context_references(command_text, world)
        if carryover["kind"] == "error":
            return build_base_response(
                world, success=False, message=carryover["message"],
                action_info={
                    "cost": 0,
                    "remaining": int(world.actions_remaining),
                    "turn_advanced": False,
                    "new_turn": None,
                })
        if carryover["kind"] == "rewrite":
            print(f"[CARRYOVER] '{command_text}' -> '{carryover['command']}'")
            command_text = carryover["command"]

        # ════════════════════════════════════════════════════════════
        # PC15-4: FALLEN/CAPTURED NAME GUARD — an order addressed to a
        # marshal who is dead or a prisoner refuses BY NAME before any
        # parser can substitute the nearest living man. Runs on the FINAL
        # command text (after carryover rewrites), before the parse.
        # ════════════════════════════════════════════════════════════
        _lost_refusal = _addressed_lost_marshal_refusal(command_text, world)
        if _lost_refusal:
            print(f"[LOST-MARSHAL GUARD] refused: {command_text!r}")
            return build_base_response(
                world, success=False, message=_lost_refusal,
                action_info={
                    "cost": 0,
                    "remaining": int(world.actions_remaining),
                    "turn_advanced": False,
                    "new_turn": None,
                })

        # Parse command
        # Build LLM-compatible game state for command parsing
        llm_game_state = get_llm_game_state()
        parsed = parser.parse(command_text, llm_game_state, world=world)
        if parsed.get("success") and isinstance(parsed.get("command"), dict):
            if request.action:
                parsed["command"]["action"] = request.action
            if request.target_nation:
                parsed["command"]["target_nation"] = request.target_nation
            if request.war_id:
                parsed["command"]["war_id"] = request.war_id
            if request.region:
                parsed["command"]["region"] = request.region
        print(f"[OK] Parsed: {parsed.get('command', {}).get('action', 'unknown')}")

        # ════════════════════════════════════════════════════════════
        # COMMAND HISTORY: Track parsed commands for LLM repetition detection
        # (live-mode prompt) AND CR-4 context carryover ("again"/"same
        # target"/"him"/"there"/"not you, X"). CR-4 decision: record in BOTH
        # mock and live modes — carryover must resolve with the fast/mock
        # parser too, and the live-only repetition prompt is unaffected.
        # ``target`` is recorded (CR-4) so "same target"/"him"/"there" and
        # "not you, X" reconstruction have an objective to reference. Recorded
        # only when the command will execute as a REAL field order — NOT when
        # it is consumed as a dialogue answer (a response that happens to
        # parse as a valid action must not be recorded as a phantom order).
        # A soft-stop mailbox dialogue (incoming proposal / settlement offer)
        # does not block ordinary orders, so an order typed while one is
        # pending still executes (soft-stop pass-through) and MUST be recorded;
        # only inputs matching the dialogue's own options are answers.
        # ════════════════════════════════════════════════════════════
        _consumed_as_dialogue_answer = False
        if world.pending_diplomatic_dialogue is not None:
            if world.dialogue_manager.is_hard_stop():
                _consumed_as_dialogue_answer = True
            else:
                # CA9: the third copy of the option-match rule, now the
                # same call the routing gate below makes.
                _consumed_as_dialogue_answer = bool(match_dialogue_answer(
                    world.pending_diplomatic_dialogue, command_text.lower()))
        if parsed.get("success") and not _consumed_as_dialogue_answer:
            _parsed_command = parsed.get("command", {})
            world.add_to_command_history({
                "raw_input": command_text,
                "marshal": _parsed_command.get("marshal"),
                "action": _parsed_command.get("action"),
                "target": _parsed_command.get("target"),
                "turn": int(world.current_turn),
            })

        # ════════════════════════════════════════════════════════════
        # CR-5: PERSONALITY-BIASED DISAMBIGUATION (COMMAND_ROBUSTNESS_SPEC §6).
        # A delegation verb ("Soult, deal with Mack") cedes the method to the
        # marshal; the concrete action is inferred from his CHARACTER, and the
        # routing here is DETERMINISTIC (Golden Rule 6 — the executor is never
        # LLM-driven):
        #   - literal / neutral / mock  -> ASK the Emperor (attack or observe?),
        #     overriding whatever the live LLM guessed for a literal marshal.
        #   - cautious                  -> observe first; a battle action the
        #     live LLM produced is CLAMPED to scout (he never assaults on a
        #     vague order, §6.3c) + a soft note that names his character.
        #   - aggressive                -> ENABLED (Phase 4). Re-issue a
        #     delegation-INFERRED strategic PURSUE; every auto-attack seam it can
        #     reach is covered by the Phase-3/4 fortification-aware bad-odds gate,
        #     so a dug-in superior force still routes through the one-modal
        #     confirm. Only reached on a genuine LIVE resolution (guardrail e —
        #     a mock/unresolved parse degrades to ASK via route_arm).
        # Guarded by _consumed_as_dialogue_answer so a hard-stop dialogue answer
        # is never hijacked; runs AFTER CR-4 carryover + history recording.
        # ════════════════════════════════════════════════════════════
        _cautious_note = None
        _delegation_arm_ran = False
        # CR-5b Flavor Echoing (§6.4): the marshal's spoken reaction at the
        # RESPONSE seam. _aggressive_flavor rides the pursue-order response;
        # _cautious_flavor_prefix rides IN FRONT of the cautious deed-note.
        _aggressive_flavor = None
        _cautious_flavor_prefix = None
        if not _consumed_as_dialogue_answer:
            _deleg = detect_delegation(world, command_text,
                                       parsed.get("command"))
            if _deleg is not None:
                # CR-5 audit fix (F2): in LIVE mode the delegation was already
                # recorded to command_history (main.py above) with the LLM's
                # DISTRUSTED target. The arms below re-parse against the
                # authoritative deterministic target, so after they run we
                # overwrite that history entry's marshal/target with the values
                # the marshal actually acted on — otherwise a later "same
                # target"/"him"/"again" carryover reissues against the wrong
                # place. No-op in mock mode (no entry was recorded there); the
                # raw_input guard prevents clobbering a prior command's entry.
                _orig_delegation_text = command_text
                # CR-5b: capture the LIVE flavor line NOW — both executed arms
                # re-parse the explicit reissue below, which returns flavor=null
                # and CLOBBERS `parsed`. Read it off the ORIGINAL delegation
                # parse (the only parse the player's raw words rode on).
                _delegation_flavor = (parsed.get("command") or {}).get("flavor")

                def _correct_delegation_carryover_target():
                    hist = getattr(world, "command_history", None)
                    if hist and hist[-1].get("raw_input") == _orig_delegation_text:
                        hist[-1]["marshal"] = _deleg.marshal
                        hist[-1]["target"] = _deleg.target

                _arm = route_arm(_deleg.personality,
                                 parse_resolved_to_action(parsed))
                if _arm == "cautious":
                    # Deterministic: a cautious marshal observes first (§6.2).
                    # Re-issue an explicit scout at the OBSERVE target (the
                    # enemy's location) — a plain re-parse, no LLM (Golden Rule
                    # 6). This also corrects the live LLM's unreliable target
                    # resolution (playtest: "deal with Kutuzov" mis-scouted
                    # Algarve); the detector's target is authoritative.
                    _reissue = f"{_deleg.marshal} scout {_deleg.scout_target}"
                    parsed = parser.parse(_reissue, llm_game_state, world=world)
                    command_text = _reissue
                    _cautious_note = describe_cautious_delegation(
                        _deleg, "scout")
                    # CR-5b: a live-only, register-gated spoken PREFIX in front
                    # of the note (None when the live line is absent/violating —
                    # then only the shipped note shows, no double-narration).
                    _cautious_flavor_prefix = resolve_live_cautious_prefix(
                        _deleg, _delegation_flavor)
                    _delegation_arm_ran = True
                    _correct_delegation_carryover_target()
                    print(f"[CR-5] Delegation CAUTIOUS ({_deleg.marshal}) "
                          f"-> scout {_deleg.scout_target}")
                elif _arm == "aggressive":
                    # Deterministic (Golden Rule 6 — the live LLM proved too
                    # flaky for delegation, so mirror the cautious re-parse
                    # pattern): an aggressive marshal gives battle. Re-issue a
                    # strategic PURSUE ("pursue <enemy>" — the strategic parser
                    # upgrades it to a tracking order that engages on contact)
                    # and TAG it delegation_inferred so the Phase-3 fortification-
                    # aware bad-odds gate fires at every auto-attack seam: the
                    # marshal never NAMED the attack, his CHARACTER inferred it.
                    # A bare one-shot "attack" would be ungated AND could not
                    # march him to a non-adjacent enemy. The player's verbatim
                    # words become the order record (rider d, §6.4). Only reached
                    # in live mode — a mock/unresolved parse degrades to ASK
                    # above via route_arm (guardrail e).
                    _delegation_phrase = command_text
                    _reissue = f"{_deleg.marshal} pursue {_deleg.target}"
                    parsed = parser.parse(_reissue, llm_game_state, world=world)
                    parsed["delegation_inferred"] = True
                    parsed["delegation_phrase"] = _delegation_phrase
                    command_text = _reissue
                    # CR-5b: the register-passing live line, else the
                    # deterministic aggressive floor (attached only on the
                    # non-modal success path in the attach block below).
                    _aggressive_flavor = resolve_delegation_flavor(
                        _deleg, "aggressive", _delegation_flavor)
                    _delegation_arm_ran = True
                    _correct_delegation_carryover_target()
                    print(f"[CR-5] Delegation AGGRESSIVE ({_deleg.marshal}) "
                          f"-> pursue {_deleg.target} (inferred, gated)")
                elif _arm == "ask":
                    _deleg_clar = build_delegation_clarification(
                        world, _deleg, command_text)
                    # §6.7 first-use hint — the ASK always surfaces, so latch it
                    # here (maybe_delegation_hint sets the flag only when it hands
                    # back the copy, once per campaign).
                    _ask_hint = maybe_delegation_hint(world)
                    if _ask_hint:
                        _deleg_clar["message"] = (
                            f"{_deleg_clar['message']}\n\n{_ask_hint}")
                    _deleg_clar["clarification_registered"] = (
                        register_pending_clarification(
                            world, _deleg_clar, command_text))
                    print(f"[CR-5] Delegation ASK "
                          f"({_deleg.marshal}/{_deleg.personality or 'unset'}) "
                          f"-> frontend")
                    return _build_result_response(_deleg_clar, world)

        # ════════════════════════════════════════════════════════════
        # DIPLOMATIC DIALOGUE RESPONSE ROUTING (Audit fix)
        # Must run BEFORE Berthier parse recovery — dialogue keywords
        # like "accept"/"reject" fail parsing and would trigger
        # Berthier recovery early return, preventing dialogue routing.
        # ════════════════════════════════════════════════════════════
        # Cheat commands bypass dialogue guard
        is_cheat = parsed.get("success") and parsed.get("command", {}).get("action") == "cheat"

        if world.pending_diplomatic_dialogue is not None and not is_cheat:
            raw_lower = command_text.lower()
            is_hard_stop = world.dialogue_manager.is_hard_stop()

            # CA9: ONE matcher for both stop kinds — only a dialogue's own
            # options may claim a typed line (`dialogue_routing`).
            #
            # The hard-stop arm used to scan a fixed keyword list for BARE
            # SUBSTRINGS, and that list held ordinary game words: "no",
            # "send", "garrison", "start", "more", "side", "continue". So
            # `Ney, move north` answered "no" (→ back_out / reconsider) and
            # `send Ney to Bavaria` answered "send" (→ send_override) on
            # whatever hard stop happened to be staged — and the answer was
            # applied to that dialogue regardless of what the sentence was
            # about. The list is gone; a verb now has to resolve onto an
            # action the live dialogue actually offers, as a whole word.
            matched_keyword = match_dialogue_answer(
                world.pending_diplomatic_dialogue, raw_lower)

            if matched_keyword:
                print(f"[DIPLOMATIC] Routing dialogue response: {matched_keyword}")
                result = executor.handle_diplomatic_dialogue_response(
                    matched_keyword, game_state, raw_text=command_text)
            elif is_hard_stop:
                # ══════════════════════════════════════════════════════
                # PT-A3 — A HARD STOP MUST NOT SWALLOW AN UNRELATED ORDER.
                #
                # This arm used to hand the player's WHOLE SENTENCE to the
                # choice resolver as if it were an answer. Measured live:
                # `Davout, march to Munich and relieve the Bavarians` came
                # back "I don't understand that choice, Sire." — the game
                # claiming it misunderstood a sentence that was never
                # about the dialogue, and never saying what was blocking.
                #
                # The escape hatch below it was DEAD. It gated on the
                # literal "Please choose an option", which
                # `_enumerated_choice_prompt` emits only for a non-str or
                # out-of-range-int choice; `main.py` always passes a `str`
                # here, and an unresolved `str` returns "I don't
                # understand that choice" instead. So no typed string
                # could ever reach `executor.execute`. CA9-N5 rewrote that
                # failure string and killed the fall-through with it.
                #
                # Answer the way the OBJECTION block answers (`executor.py
                # :531-562`): never feed the sentence to a resolver, name
                # the blocker, say nothing was relayed, and quote the exact
                # words that clear it — read off the live dialogue, so
                # shown == accepted.
                # ══════════════════════════════════════════════════════
                print(f"[DIPLOMATIC] Hard-stop refusal (unrelated): {raw_lower}")
                from backend.commands.dialogue_routing import (
                    format_numbered_options, hard_stop_subject)
                _dlg = world.pending_diplomatic_dialogue
                _numbered = format_numbered_options(_dlg)
                _waiting = hard_stop_subject(_dlg)
                _msg = f"{_waiting} awaits your answer, Sire"
                if _numbered:
                    _msg += (f" — nothing was relayed. Answer with one of: "
                             f"{_numbered}.")
                else:
                    _msg += " — nothing was relayed."
                result = {
                    "success": False,
                    "message": _msg,
                    "awaiting_response": True,
                    "diplomatic_dialogue": _dlg,
                }
            else:
                # PL-27: Soft-stop — no dialogue keyword match, execute normally
                print(f"[DIPLOMATIC] Soft-stop pass-through: {raw_lower}")
                result = executor.execute(parsed, game_state)
        else:
            # m1: Dialogue keywords typed with no active dialogue — clear message
            raw_lower_check = command_text.lower().strip()
            # Only keywords that are NEVER valid game commands.
            # Excludes: cancel (strategic order cancel), garrison, more, execute, start, yes, no
            _DIALOGUE_ONLY_KEYWORDS = [
                "accept", "reject", "decline", "counter",
                "proceed", "confront", "overlook",
                "apologize", "replace", "reconsider", "modify",
                "honor", "side", "dismiss",
                "harsh", "generous", "adjust",
                "nudge", "insist",  # PL-23: Drafting pushback
                "elaborate", "review", "consider",
                "begin",
                "agree", "never mind",
            ]
            if raw_lower_check in _DIALOGUE_ONLY_KEYWORDS:
                # Live playthrough: with Massena's tactical OBJECTION pending,
                # "proceed" fell through here and Berthier denied any pending
                # matter — while every real order stayed blocked on the
                # objection ("settle the objection before issuing new
                # orders"). A dialogue-ish word typed while an objection
                # waits must reprompt THAT objection's own choices, not
                # gaslight the player about the diplomatic channel.
                if world.pending_objection is not None:
                    _objecting = world.pending_objection.get(
                        "marshal", "A marshal")
                    # CA9 review round: same missing key as the
                    # executor block — see `OBJECTION_FREE_READS`'s
                    # neighbour there. Read the validator's own predicate.
                    _obj_choices = ["trust", "insist"]
                    if (world.pending_objection.get("suggested_alternative")
                            or world.pending_objection.get("compromise")
                            or world.pending_objection.get("alternative")):
                        _obj_choices.append("compromise")
                    return build_base_response(
                        world, success=False,
                        message=(
                            f"{_objecting} awaits your answer, Sire — reply "
                            f"{format_answer_words(_obj_choices)}."),
                        objection=world.pending_objection,
                        choices=_obj_choices,
                        action_info={
                            "cost": 0,
                            "remaining": int(world.actions_remaining),
                            "turn_advanced": False,
                            "new_turn": None,
                        })
                return build_base_response(
                    world, success=False,
                    message="Berthier: \"There is no pending diplomatic matter to respond to, Sire.\"",
                    action_info={
                        "cost": 0,
                        "remaining": int(world.actions_remaining),
                        "turn_advanced": False,
                        "new_turn": None,
                    })

            # ════════════════════════════════════════════════════════════
            # WO-1: THE ENEMY ADDRESSEE. The parser refused by name and in
            # voice ("Marshal Kutuzov commands for Russia, Sire — he does
            # not answer to us"); the refusal must reach the player
            # VERBATIM. Without this arm it carried candidates=[] so the
            # CR-2 clarification below skipped it and it fell through to
            # the generic Berthier recovery — the by-name refusal was
            # production-dead on the wire (review finding, Aug 21 2026).
            # ════════════════════════════════════════════════════════════
            if (not parsed.get("success")
                    and parsed.get("kind") == "enemy_addressee"):
                refusal_message = parsed.get("error") or (
                    "That commander serves the enemy, Sire — he does not "
                    "answer to us.")
                if parsed.get("suggestion"):
                    refusal_message += f" {parsed['suggestion']}"
                return build_base_response(
                    world, success=False, message=refusal_message,
                    action_info={
                        "cost": 0,
                        "remaining": int(world.actions_remaining),
                        "turn_advanced": False,
                        "new_turn": None,
                    })

            # ════════════════════════════════════════════════════════════
            # CR-2: UNKNOWN-NAME CLARIFICATION — a parse failure that
            # carries structured candidates ("Murat, charge" on a world
            # without Murat; "Davut, attack") becomes a one-question
            # did-you-mean instead of a dead-end error. Before CR-2 these
            # errors fell through the executor into the generic Berthier
            # shrug and the computed suggestions were dropped entirely.
            # ════════════════════════════════════════════════════════════
            if not parsed.get("success") and parsed.get("candidates"):
                name_clarification = build_unknown_name_clarification(
                    world,
                    parsed.get("unknown_name") or "",
                    parsed["candidates"],
                    command_text,
                    parsed.get("kind") or "marshal_not_found",
                    partial_action=parsed.get("partial_action"),
                )
                if name_clarification is not None:
                    name_clarification["clarification_registered"] = (
                        register_pending_clarification(
                            world, name_clarification, command_text))
                    print("[CLARIFICATION] Unknown-name question -> frontend")
                    return _build_result_response(name_clarification, world)

            # ════════════════════════════════════════════════════════════
            # PARSE-NEG: A DELIBERATE NO-ORDER. The parser understood the
            # sentence perfectly — "Ney, never attack Mack" is an instruction
            # NOT to act, and "if Mack advances, fall back" is a condition the
            # engine cannot hold open. Both used to execute the affirmative at
            # confidence 0.9+. Answering with the generic "I cannot interpret
            # that order" would be a second, smaller lie: Berthier says what he
            # read and what he did about it.
            # ════════════════════════════════════════════════════════════
            if not parsed.get("success") and parsed.get("refusal"):
                if parsed["refusal"] == "conditional":
                    refusal_msg = (
                        "Berthier sets down his pen. \"Sire, that is a "
                        "contingency, not an order — I have no way to hold a "
                        "dispatch until the enemy moves. Nothing has been "
                        "relayed. Give me the order for THIS turn and I shall "
                        "carry it at once; a standing order I can hold is "
                        "'hold until Davout arrives'.\"")
                else:
                    refusal_msg = (
                        "Berthier lowers the dispatch. \"Then no order goes "
                        "out, Sire — I have relayed nothing. If a standing "
                        "order is to be stood down, say 'cancel his order'; "
                        "otherwise tell me what the marshal IS to do.\"")
                # ══════════════════════════════════════════════════════
                # PT-H5: this path bypassed CA9-N5's option-naming helper.
                #
                # It returns BEFORE `executor.execute`, so the block at
                # `executor.py:531-562` — the one that names the objecting
                # marshal and quotes "'trust', 'insist' or 'compromise'" —
                # is never reached. With an objection pending, a
                # clause-guard-refused sentence got "Then no order goes
                # out, Sire…" while every real order stayed blocked, and
                # the words that clear the block were stated nowhere in
                # the response. Same shape as the bug the `:2175` comment
                # calls gaslighting, one branch over.
                # ══════════════════════════════════════════════════════
                _pending_obj = getattr(world, "pending_objection", None)
                if _pending_obj:
                    # ALIASED deliberately: a bare local import here binds
                    # the name for the WHOLE function, and the objection
                    # re-prompt at `:2347` already uses the module-level
                    # `format_answer_words` — which a local import turns
                    # into an UnboundLocalError at a line that had not
                    # changed.
                    from backend.commands.dialogue_routing import (
                        format_answer_words as _answer_words,
                    )
                    _choices = ["trust", "insist"]
                    if (_pending_obj.get("suggested_alternative")
                            or _pending_obj.get("compromise")
                            or _pending_obj.get("alternative")):
                        _choices.append("compromise")
                    _objector = _pending_obj.get("marshal", "A marshal")
                    refusal_msg += (
                        f"\n\n{_objector} still awaits your answer, Sire. "
                        f"Reply {_answer_words(_choices)}.")
                return build_base_response(
                    world, success=False, message=refusal_msg,
                    objection=_pending_obj if _pending_obj else None,
                    action_info={
                        "cost": 0,
                        "remaining": int(world.actions_remaining),
                        "turn_advanced": False,
                        "new_turn": None,
                    })

            # ════════════════════════════════════════════════════════════
            # BERTHIER PARSE RECOVERY: Replace generic "Unknown action"
            # with in-character Berthier clarification. Only fires for
            # type-1 parse failures; marshal typos & validation errors
            # pass through unchanged.
            # ════════════════════════════════════════════════════════════
            if not parsed.get("success") and (parsed.get("error") or "").startswith("Unknown action"):
                berthier_msg = parser.llm.generate_berthier_recovery(
                    raw_command=command_text,
                    game_state=llm_game_state,
                    partial_parse={
                        "recognized_marshal": parsed.get("partial_marshal"),
                        "recognized_target": parsed.get("partial_target"),
                        "raw_input": parsed.get("raw_input", command_text),
                    },
                    # CR-3(c): the parse-stage LLM call already failed —
                    # don't stack a second blocking call on this request
                    skip_llm=bool(parsed.get("llm_error")),
                )
                return build_base_response(
                    world, success=False, message=berthier_msg,
                    action_info={
                        "cost": 0,
                        "remaining": int(world.actions_remaining),
                        "turn_advanced": False,
                        "new_turn": None,
                    })

            # Execute command
            result = executor.execute(parsed, game_state)

        # ════════════════════════════════════════════════════════════
        # CR-2: parser warnings (sequential-order drop note, non-standard
        # marshal note) were computed and then never surfaced — append them
        # to the player-visible message ("every input gets a response").
        # Sits BEFORE the early-return checks so diplomatic dialogues and
        # popup paths carry the note too; objection popups (success=False)
        # deliberately skip it — the objection dominates, and the sequel
        # note re-surfaces if the reissued/proceeded command re-parses.
        # ════════════════════════════════════════════════════════════
        if result.get("success") and parsed.get("warning"):
            result["message"] = (
                f"{result.get('message') or ''}\n\n"
                f"Berthier: \"{parsed['warning']}\""
            ).strip()

        # CR-5: a cautious delegation executed as an observe-first order —
        # append the character-naming soft note (§6.3c legibility) so the
        # player sees WHY the marshal scouted and can press the assault. Note
        # only on a SUCCESSFUL scout (a failed reissue makes "will reconnoiter"
        # false).
        if _cautious_note and isinstance(result, dict) and result.get("success"):
            # CR-5b: a live-only, register-passed spoken flavor PREFIX leads the
            # deed-note ("the game heard me" -> then WHY he scouted). When the
            # prefix is None (mock / absent / register-dropped) only the shipped
            # note shows — no double-narration (delegation.resolve_live_cautious_
            # prefix owns that decision; there is no deterministic cautious floor).
            _cautious_tail = (
                f"{_cautious_flavor_prefix}\n\n{_cautious_note}"
                if _cautious_flavor_prefix else _cautious_note)
            result["message"] = (
                f"{(result.get('message') or '').strip()}\n\n{_cautious_tail}"
            ).strip()

        # CR-5b: the AGGRESSIVE arm's spoken flavor (register-passed live line
        # or the deterministic floor) rides the pursue-order response. Attach
        # ONLY on the non-modal success path: SKIP every modal shape the reissued
        # PURSUE can raise — the bad-odds confirm (requires_input /
        # pending_interrupt) AND a strategic/tactical objection (pending_objection
        # / awaiting_response, e.g. a fog-driven MILD->MODERATE on the PURSUE) —
        # so guardrail (c)'s ONE-modal legibility surface stays uncluttered
        # (§6.3), and skip failures. Purely cosmetic — never touches the resolved
        # order (Golden Rule 6).
        if (_aggressive_flavor and isinstance(result, dict)
                and result.get("success")
                and not result.get("requires_input")
                and not result.get("pending_interrupt")
                and not result.get("pending_objection")
                and not result.get("awaiting_response")):
            result["message"] = (
                f"{(result.get('message') or '').strip()}\n\n{_aggressive_flavor}"
            ).strip()

        # CR-5 §6.7 first-use hint — surfaced (and latched) at the point it
        # actually rides a response, for BOTH the cautious and aggressive arms,
        # on success OR failure. LATCH-ON-SURFACE (audit fix): maybe_delegation_
        # hint() sets the once-per-campaign flag only here where it hands back the
        # copy, so a first-ever delegation whose reissued order is REJECTED (not
        # at war / no AP / marshal broken) still teaches the affordance instead of
        # silently consuming the flag. The ASK arm surfaced its own hint and
        # returned early, so it never reaches here.
        if _delegation_arm_ran and isinstance(result, dict):
            _tail_hint = maybe_delegation_hint(world)
            if _tail_hint:
                result["message"] = (
                    f"{(result.get('message') or '').strip()}\n\n{_tail_hint}"
                ).strip()

        # ════════════════════════════════════════════════════════════
        # BERTHIER EXECUTOR RECOVERY: Catch "Marshal 'None' not found"
        # This happens when a valid action is parsed but no marshal was
        # identified (e.g., "move to Belgium" without naming a marshal).
        # CR-2: upgraded to the one-question marshal-choice clarification
        # ("Which marshal shall march to Belgium, Sire?") with reissue
        # options; Berthier prose remains the no-candidate fallback.
        # ════════════════════════════════════════════════════════════
        if not result.get("success") and "Marshal 'None' not found" in (result.get("message") or ""):
            # CR-4: PERSISTENT COMMAND FOCUS — a bare specific order ("hold",
            # "move to Vienna") defaults to the marshal the player is already
            # commanding instead of re-asking. Only fires at this seam (the
            # missing-executor case), so it never overrides an explicitly-
            # addressed marshal or a general/auto-assign order; falls through
            # to the CR-2 clarification when no eligible focus exists.
            focus_handled = False
            if parsed.get("success"):
                focus_outcome = try_focus_reissue(
                    world, parser, executor, parsed, command_text,
                    game_state, llm_game_state)
                if focus_outcome is not None:
                    parsed, command_text, result = focus_outcome
                    print(f"[FOCUS] Reissued bare order to "
                          f"{parsed.get('command', {}).get('marshal')}")
                    focus_handled = True
                    # CR-4 (audit): the parser-warning surfacing block ran
                    # above on the OLD (failed) result, so the reissued
                    # command's own warning (e.g. the sequential-clause drop
                    # note) would be lost — re-surface it here so a focus
                    # reissue matches an explicitly-addressed order.
                    if result.get("success") and parsed.get("warning"):
                        result["message"] = (
                            f"{result.get('message') or ''}\n\n"
                            f"Berthier: \"{parsed['warning']}\""
                        ).strip()

            if not focus_handled:
                if parsed.get("success"):
                    marshal_clarification = build_marshal_choice_clarification(
                        world, parsed, command_text)
                    if marshal_clarification is not None:
                        marshal_clarification["clarification_registered"] = (
                            register_pending_clarification(
                                world, marshal_clarification, command_text))
                        print("[CLARIFICATION] Marshal-choice question -> frontend")
                        return _build_result_response(marshal_clarification, world)
                berthier_msg = parser.llm.generate_berthier_recovery(
                    raw_command=command_text,
                    game_state=llm_game_state,
                    partial_parse={
                        "recognized_marshal": None,
                        "recognized_target": parsed.get("command", {}).get("target"),
                        "raw_input": command_text,
                    },
                    skip_llm=bool(parsed.get("llm_error")),  # CR-3(c)
                )
                return build_base_response(
                    world, success=False, message=berthier_msg,
                    action_info={
                        "cost": 0,
                        "remaining": int(world.actions_remaining),
                        "turn_advanced": False,
                        "new_turn": None,
                    })

        # ════════════════════════════════════════════════════════════
        # CHECK FOR OBJECTION: If awaiting player choice, return full result
        # Tactical objections: state == "awaiting_player_choice"
        # Strategic objections (Phase M): pending_objection == True
        # ════════════════════════════════════════════════════════════
        if result.get("state") == "awaiting_player_choice":
            print("[OBJECTION] TACTICAL OBJECTION - Returning full result to frontend")
            return _build_result_response(result, world)

        if result.get("pending_objection"):
            print("[OBJECTION] STRATEGIC OBJECTION (Phase M) - Returning full result to frontend")
            return _build_result_response(result, world)

        # ════════════════════════════════════════════════════════════
        # CHECK FOR CLARIFICATION: If awaiting clarification, return full result
        # CR-2: also register the question on the DialogueManager so the
        # player's next typed input can answer it (player path only — AI
        # commands never flow through this endpoint).
        # ════════════════════════════════════════════════════════════
        if result.get("state") == "awaiting_clarification":
            result["clarification_registered"] = (
                register_pending_clarification(world, result, command_text))
            print("[CLARIFICATION] Returning clarification popup to frontend")
            return _build_result_response(result, world)

        # ════════════════════════════════════════════════════════════
        # CHECK FOR GLORIOUS CHARGE: If pending, return full result for popup
        # ════════════════════════════════════════════════════════════
        if result.get("pending_glorious_charge"):
            print("GLORIOUS CHARGE PENDING - Returning full result to frontend")
            return _build_result_response(result, world)

        # ════════════════════════════════════════════════════════════
        # CHECK FOR STRATEGIC INTERRUPT: Blocked path, cannon fire popup
        # (Session 39: was missing — pending_interrupt dropped at response build)
        # ════════════════════════════════════════════════════════════
        if result.get("pending_interrupt"):
            print("[INTERRUPT] STRATEGIC INTERRUPT - Returning full result to frontend")
            return _build_result_response(result, world)

        # ════════════════════════════════════════════════════════════
        # CHECK FOR CAPTURE CHOICE (Phase 6.2.E): Plunder or Secure popup
        # ════════════════════════════════════════════════════════════
        if result.get("pending_capture_choice"):
            print("[CAPTURE] PLUNDER/SECURE CHOICE PENDING - Returning full result to frontend")
            # IGR-X7: this early-return's client route reads only the capture
            # keys — popping a queued popup here would discard it.
            return _build_result_response(result, world, drain_popups=False)

        # ════════════════════════════════════════════════════════════
        # CHECK FOR DIPLOMATIC DIALOGUE (Phase 8 Session 3)
        # ════════════════════════════════════════════════════════════
        if result.get("diplomatic_dialogue") or result.get("awaiting_diplomatic_response"):
            print("[DIPLOMATIC] Diplomatic dialogue - Returning full result to frontend")
            return _build_result_response(result, world)


        # ════════════════════════════════════════════════════════════
        # FEEDBACK GENERATION (Phase 5): Generate immersive feedback
        # Only for non-mock mode, successful player commands
        #
        # REQUIRED FIELDS FROM parser.parse() - see parser.py docstring:
        #   - parsed["mode"]: "mock" or "live"
        #   - parsed["strategic_score"]: 0-100 (controls morale/trust bonus)
        #   - parsed["ambiguity"]: 0-100 (controls clarity feedback)
        #
        # If these are missing, check parser.py return dict construction!
        # ════════════════════════════════════════════════════════════
        feedback = {}
        mode = parsed.get("mode", "mock")

        if mode != "mock" and result.get("success", False):
            from backend.ai.feedback import get_strategic_feedback, get_ambiguity_feedback

            # Get scores from parsed command
            strategic_score = parsed.get("strategic_score", 0)
            ambiguity_score = parsed.get("ambiguity", 0)
            print(f"[FEEDBACK DEBUG] mode={mode}, strategic_score={strategic_score}, ambiguity={ambiguity_score}")

            # Get marshal info - try result first, then parsed command
            marshal_name = result.get("marshal") or parsed.get("command", {}).get("marshal")
            if marshal_name:
                marshal = world.get_marshal(marshal_name)
                if marshal and marshal.nation == world.player_nation:
                    personality = getattr(marshal, 'personality', 'balanced')

                    # Generate feedback strings
                    strategic_text = get_strategic_feedback(strategic_score, marshal_name)
                    ambiguity_text = get_ambiguity_feedback(ambiguity_score, marshal_name, personality)

                    if strategic_text:
                        feedback["strategic"] = strategic_text
                    if ambiguity_text:
                        feedback["ambiguity"] = ambiguity_text

        response = _build_command_response(result, world, feedback)
        _apply_command_result_layers(response, result, world)
        return response
    except Exception as e:
        print(f"[ERROR]: {e}")
        import traceback
        traceback.print_exc()
        return build_base_response(
            world, success=False, message=f"Error: {str(e)}",
            action_info={"remaining": int(world.actions_remaining)})


@app.get("/status")
def get_status():
    """Get current game status — Berthier's Intelligence Report (Session 34A)."""
    from backend.intel_report import generate_intel_report
    from backend.game_logic.war_status import build_active_wars
    report = generate_intel_report(world)
    report["game_state"] = world.get_filtered_game_state_summary()
    report["active_wars"] = build_active_wars(world)
    _attach_nation_identity_overrides(report, world)   # NA-6 §11.8 stage 3
    return report


# ============================================================
# DISOBEDIENCE SYSTEM API ENDPOINTS (Phase 2)
# ============================================================

@app.get("/pending_objection")
def get_pending_objection():
    """
    Get the current pending objection if any.

    Returns objection details including:
    - marshal: Name of objecting marshal
    - message: The objection message
    - severity: How serious the objection is
    - choices: Available responses (trust, insist, compromise)
    - alternative: Marshal's suggested alternative (if any)
    """
    if world.pending_objection is None:
        return {
            "has_pending": False,
            "message": "No pending objection"
        }

    objection = world.pending_objection
    from backend.display_names import ACTION_DISPLAY
    trigger = objection.get("trigger")
    return {
        "has_pending": True,
        "marshal": objection.get("marshal"),
        "message": objection.get("message"),
        "severity": int(objection.get("severity", 0.5) * 100),  # int % for Godot — no raw floats
        "type": objection.get("type", "major"),
        "trigger": trigger,
        "trigger_display": ACTION_DISPLAY.get(trigger, (trigger or "").replace("_", " ")) if trigger else "",
        "choices": ["trust", "insist", "compromise"] if objection.get("alternative") else ["trust", "insist"],
        "alternative": objection.get("alternative"),
        "original_order": objection.get("original_order")
    }


@app.post("/marshal_petition_response")
def marshal_petition_response(request: MarshalPetitionResponse):
    """Answer the pending marshal petition (Jealousy v3.2 §0.2 item 10).

    One endpoint for all four petition kinds: jealousy_confrontation,
    rivalry_confrontation, fontainebleau, war_weary. The petition's
    options list defines the valid choice ids; effects are applied by
    jealousy.handle_petition_response (war_weary may re-execute the
    stored declare-war command through the standard executor).
    """
    try:
        if world.game_over:
            return build_base_response(
                world, success=False, message="The war is over.",
                game_over=True, victory=world.victory)
        from backend.game_logic.jealousy import handle_petition_response
        result = handle_petition_response(
            world, request.choice, executor=executor, game_state=game_state)
        # Forward the WHOLE result: a war_weary "we march" re-runs declare-war
        # through the executor, which can raise a follow-on diplomatic_dialogue
        # / ally_entry_preview / awaiting_diplomatic_response. The old
        # hand-forward kept only battle_report + marshal_petition and dropped
        # those, stranding the ally-entry decision. build_base_response runs
        # popup passthroughs; marshal_petition + battle_report ride `extra`.
        response = _build_result_response(result, world)
        return response
    except Exception as e:
        print(f"[ERROR] handling marshal petition response: {e}")
        import traceback
        traceback.print_exc()
        return build_base_response(
            world, success=False, message=f"Error: {str(e)}")


@app.post("/respond_to_objection")
def respond_to_objection(request: ObjectionResponse):
    """
    Respond to a marshal's objection.

    Args:
        request: ObjectionResponse with 'choice' field
            - 'trust': Accept marshal's judgment/alternative
            - 'insist': Override marshal and execute original order
            - 'compromise': Find middle ground (if available)

    Returns execution result after choice is processed.
    """
    try:
        if world.game_over:
            return build_base_response(
                world, success=False, message="The war is over.",
                game_over=True, victory=world.victory)
        return _respond_to_objection_sync(request.choice)
    except Exception as e:
        print(f"[ERROR] handling objection response: {e}")
        import traceback
        traceback.print_exc()
        return build_base_response(
            world, success=False, message=f"Error: {str(e)}")


def _respond_to_objection_sync(choice: str):
    """Shared objection-response assembly for the endpoint AND the W6-0 typed
    pending-question router — a typed "trust" must behave byte-identically to
    the objection popup's Trust button."""
    try:
        # Handle the objection response through executor
        result = executor.handle_objection_response(choice, game_state)

        # Non-draining (verify-fleet correction, Aug 2026): this response can
        # now carry pending_capture_choice via the combat allowlist below,
        # and the capture route pre-empts every popup route in
        # _route_response_ui — a drained one-shot popup riding the same
        # response would be destroyed unread. Same convention as the
        # /command capture early-return (drain_popups=False).
        response = build_base_response(
            world,
            success=result.get("success", False),
            message=result.get("message", "Response processed"),
            events=result.get("events", []),
            objection_resolved=result.get("objection_resolved", True),
            choice=result.get("choice"),
            trust_change=result.get("trust_change", 0),
            authority_change=result.get("authority_change", 0),
            disobeyed=result.get("disobeyed", False),
            action_info=result.get("action_info", {}),
            strategic_reports=result.get("strategic_reports", []),
            include_popup_passthroughs=False,
        )
        _fill_popup_keys_without_draining(response)
        if result.get("battle_report"):
            response["battle_report"] = result["battle_report"]

        # CA8-25 sibling (Aug 2026 health-check audit): the insist path
        # re-enters _execute_attack, which can produce a diorama and a
        # capture choice — this second hand-enumerated allowlist dropped
        # both. Carry the same combat allowlist the interrupt route uses.
        from backend.commands.strategic import _carry_combat_fields
        _carry_combat_fields(response, result)

        # V2b: Defiance passthrough
        if result.get("defiance"):
            response["defiance"] = True
            response["defiance_action"] = result.get("defiance_action")
            response["defiance_outcome"] = result.get("defiance_outcome")
            # R7: Display-friendly versions for UI
            from backend.display_names import DEFIANCE_DISPLAY, DEFIANCE_OUTCOME_DISPLAY
            da = result.get("defiance_action", "")
            response["defiance_action_display"] = DEFIANCE_DISPLAY.get(da, da.replace("_", " ")) if da else ""
            do = result.get("defiance_outcome", "")
            response["defiance_outcome_display"] = DEFIANCE_OUTCOME_DISPLAY.get(do, do.replace("_", " ").title()) if do else ""
            response["berthier_text"] = result.get("berthier_text", "")
        # V2b: Authority event passthrough
        if result.get("authority_event"):
            response["authority_event"] = result["authority_event"]

        # Strategic interrupt: post-objection command may hit blocked path
        if result.get("pending_interrupt"):
            response["pending_interrupt"] = result["pending_interrupt"]
            response["requires_input"] = True

        # Redemption event: trust dropped to critical level
        if result.get("redemption_event"):
            response["state"] = "awaiting_redemption_choice"
            response["redemption_event"] = result["redemption_event"]
            world.pending_redemption = result["redemption_event"]
            print(f"[ALERT] REDEMPTION TRIGGERED for {result['redemption_event']['marshal']}")

        return response
    except Exception as e:
        print(f"[ERROR] handling objection response: {e}")
        import traceback
        traceback.print_exc()
        return build_base_response(
            world, success=False, message=f"Error: {str(e)}")


@app.post("/respond_to_diplomatic_dialogue")
async def respond_to_diplomatic_dialogue(request: dict):
    """Respond to a diplomatic dialogue from Talleyrand (Phase 8 Session 3).

    Args:
        request: dict with 'choice' field (int 1-based index or str keyword),
            optional 'action_params' (settlement Tier-2 affordances) and
            optional 'dialogue_id' (W6-0: the identity of the dialogue the
            popup rendered — a mismatch with the current top is refused).
    """
    try:
        if world.game_over:
            return build_base_response(
                world, success=False, message="The war is over.",
                game_over=True, victory=world.victory)
        return _respond_to_dialogue_sync(
            request.get("choice"),
            action_params=request.get("action_params"),
            dialogue_id=request.get("dialogue_id"),
        )
    except Exception as e:
        print(f"[ERROR] handling diplomatic dialogue response: {e}")
        import traceback
        traceback.print_exc()
        return build_base_response(
            world, success=False, message=f"Error: {str(e)}")


def _respond_to_dialogue_sync(choice, action_params=None, dialogue_id=None,
                              suppress_result_popup=False):
    """Shared dialogue-response assembly for the endpoint AND the W6-0 typed
    pending-question router — a typed "2" must behave byte-identically to the
    popup's option-2 button.

    ``suppress_result_popup`` is IGR-F's only divergence and is set by exactly
    one caller, ``POST /mailbox/respond``. Answering three letters in the
    letter-book would otherwise raise three ``proposal_result`` modals — the
    same storm this slice exists to kill, moved one surface downstream. The
    outcome still reaches the player in full on ``message``, which the
    letter-book's client handler prints to the terminal transcript.

    It ALSO suppresses the popup-queue drain (review finding [1]): this
    response's client handler discards popups, so draining would destroy them.
    Anything queued rides the player's next ``/command`` instead.
    """
    try:
        dialogue_before = world.pending_diplomatic_dialogue or {}
        # Re-front Slice 2: structured settlement Tier-2 affordances (dials /
        # coverage edits / focus) ride on per-court rows + rail buttons and
        # carry `scope` / `nation` params the keyword path cannot express.
        result = executor.handle_diplomatic_dialogue_response(
            choice, game_state, action_params=action_params,
            dialogue_id=dialogue_id,
        )

        # PF-1 / D2: pass the handler's own text through instead of swallowing
        # it behind a literal "Response processed". Settlement failure arms
        # speak through `talleyrand_text` (in character) and `error_display`
        # (humanized reason) and may omit `message`; the old `.get` default
        # printed "Response processed" in red with no explanation.
        response = build_base_response(
            world,
            success=result.get("success", False),
            message=(
                result.get("message")
                or result.get("talleyrand_text")
                or result.get("error_display")
                or "Response processed"
            ),
            # IGR-F review [1]: a letter-book row answer must not DRAIN the
            # popup queue — its client handler throws popups away.
            include_popup_passthroughs=not suppress_result_popup,
        )
        if suppress_result_popup:
            _fill_popup_keys_without_draining(response)
        # PF-1 / D3: surface the failure fields so the client can render the
        # reason on a re-mounted dialogue instead of a silent no-op.
        # W6-0: `stale_dialogue` rides along so the client knows its rendered
        # dialogue was superseded (the current one is re-attached below).
        for failure_key in ("error", "error_display", "validation_error",
                            "validation_detail", "validation_error_index",
                            "stale_dialogue"):
            if result.get(failure_key) is not None:
                response[failure_key] = result[failure_key]

        # Pass through diplomatic dialogue if a new one was generated
        if result.get("diplomatic_dialogue"):
            response["diplomatic_dialogue"] = result["diplomatic_dialogue"]
        elif (result.get("success")
              and world.proposal_result_popup is None
              and not result.get("suppress_proposal_result_popup")
              and not suppress_result_popup):
            # PL-14 safety net: If dialogue concluded (no new dialogue pushed)
            # and handler forgot to set proposal_result_popup, create one from
            # the result message so it shows as a Godot popup, not terminal text.
            msg = result.get("message", "")
            if msg and not result.get("awaiting_diplomatic_response"):
                proposal_result = {
                    "target_nation": result.get(
                        "target_nation", dialogue_before.get("target_nation", "")
                    ),
                    "proposal_type": "Diplomatic Action",
                    "outcome": _derive_proposal_result_outcome(result),
                    "message": msg,
                    "feedback": "",
                    "decision_reason": result.get("decision_reason", ""),
                }
                if result.get("peace_ratification_summary"):
                    proposal_result["peace_ratification_summary"] = result[
                        "peace_ratification_summary"
                    ]
                world.proposal_result_popup = proposal_result
                # Rebuild response to pick up the newly-set popup.
                # The first build already ran _include_popup_passthroughs,
                # which POPS the winning popup off the queue and clears it
                # from the world — so anything it delivered is destroyed by
                # a naive rebind. Carry those keys across.
                #
                # Found on the NA-6 settlement-ratify path, where it made
                # the Proclamation 100% undeliverable: the card was popped
                # into `response`, the response was thrown away, and the
                # formation latch guarantees it can never fire again. The
                # bug is not NA-6-specific — it hits every popup type — so
                # the carry is generic.
                carried = _capture_popup_passthroughs(response)
                response = build_base_response(
                    world,
                    success=result.get("success", False),
                    message=result.get("message", "Response processed"),
                    include_popup_passthroughs=not suppress_result_popup,
                )
                if suppress_result_popup:
                    _fill_popup_keys_without_draining(response)
                _restore_popup_passthroughs(response, carried)

        _include_peace_ratification_summary(response, result)
        if result.get("settlement_result_feedback"):
            response["settlement_result_feedback"] = result["settlement_result_feedback"]
        if result.get("reopen_target"):
            response["reopen_target"] = result["reopen_target"]
        if result.get("must_reopen"):
            response["must_reopen"] = result["must_reopen"]
        if result.get("recovery_route"):
            response["recovery_route"] = result["recovery_route"]
        if result.get("war_detail_actionability"):
            response["war_detail_actionability"] = result["war_detail_actionability"]
        if result.get("terminal_recovery_copy"):
            response["terminal_recovery_copy"] = result["terminal_recovery_copy"]
        if result.get("error_display"):
            response["error_display"] = result["error_display"]
        return response
    except Exception as e:
        print(f"[ERROR] handling diplomatic dialogue response: {e}")
        import traceback
        traceback.print_exc()
        return build_base_response(
            world, success=False, message=f"Error: {str(e)}")


@app.post("/respond_to_diplomatic_objection")
def respond_to_diplomatic_objection(request: DiplomaticObjectionResponse):
    """Respond to a Talleyrand objection popup without synthesizing a command string."""
    try:
        if world.game_over:
            return build_base_response(
                world, success=False, message="The war is over.",
                game_over=True, victory=world.victory)

        result = executor.handle_diplomatic_objection_response(
            request.choice,
            game_state,
            action=request.action,
            target_nation=request.target_nation,
        )

        response = build_base_response(
            world,
            success=result.get("success", False),
            message=result.get("message", "Response processed"),
            events=result.get("events", []),
        )
        if result.get("diplomatic_dialogue"):
            response["diplomatic_dialogue"] = result["diplomatic_dialogue"]
        if result.get("awaiting_diplomatic_response"):
            response["awaiting_diplomatic_response"] = True
        return response
    except Exception as e:
        print(f"[ERROR] handling diplomatic objection response: {e}")
        import traceback
        traceback.print_exc()
        return build_base_response(
            world, success=False, message=f"Error: {str(e)}")


@app.post("/capture_choice")
def capture_choice(request: CaptureChoiceResponse):
    """Respond to the plunder/secure choice after capturing a region (Phase 6.2.E).

    Args:
        request: CaptureChoiceResponse with 'choice' field ('plunder' or 'secure')
    """
    try:
        if world.game_over:
            return build_base_response(
                world, success=False, message="The war is over.",
                game_over=True, victory=world.victory)
        result = executor.handle_capture_choice(
            request.choice, game_state, dialogue_id=request.dialogue_id)

        extra = {}
        # W6-8: the estate stage (or a refused answer) re-attaches the
        # pending question so Godot can chain the second popup.
        if result.get("pending_capture_choice"):
            extra["pending_capture_choice"] = True
            extra["capture_data"] = result.get("capture_data")
        if result.get("stale_dialogue"):
            extra["stale_dialogue"] = True
        # IGR-X7: the capture dialog's client handler reads only the capture
        # keys — draining the PopupQueue into this response destroys whatever
        # was queued (one-shot popups permanently). Fill without draining;
        # the popup rides the player's next /command.
        response = build_base_response(
            world,
            success=result.get("success", False),
            message=result.get("message", "Choice processed"),
            events=result.get("events", []),
            capture_choice=result.get("capture_choice"),
            include_popup_passthroughs=False,
            **extra,
        )
        _fill_popup_keys_without_draining(response)
        return response
    except Exception as e:
        print(f"ERROR handling capture choice: {e}")
        import traceback
        traceback.print_exc()
        return build_base_response(
            world, success=False, message=f"Error: {str(e)}")


@app.post("/respond_to_redemption")
def respond_to_redemption(request: RedemptionResponse):
    """
    Respond to a redemption event (trust at critical low).

    Args:
        request: RedemptionResponse with 'choice' field
            - 'grant_autonomy': Marshal acts independently for 3 turns
            - 'dismiss': Remove marshal, transfer troops
            - 'demand_obedience': Keep marshal but high disobey chance

    Returns result of the redemption choice.
    """
    try:
        if world.game_over:
            return build_base_response(
                world, success=False, message="The war is over.",
                game_over=True, victory=world.victory)
        # Check for pending redemption
        if not hasattr(world, 'pending_redemption') or world.pending_redemption is None:
            return build_base_response(
                world, success=False, message="No redemption event pending.")

        redemption_event = world.pending_redemption

        # Validate choice (Phase 3: administrative_role replaces demand_obedience)
        valid_choices = ['grant_autonomy', 'administrative_role', 'dismiss']
        if request.choice not in valid_choices:
            return build_base_response(
                world, success=False,
                message=f"Invalid choice: '{request.choice}'. Valid: {', '.join(valid_choices)}")

        # Process the redemption response
        result = world.disobedience_system.handle_redemption_response(
            redemption_event=redemption_event,
            choice=request.choice,
            game_state=game_state
        )

        # Clear pending redemption
        world.pending_redemption = None

        # Non-draining (Aug 2026 health-check audit): main.gd's
        # _on_redemption_response never routes popup keys, so a draining
        # build here destroyed any queued choice popup.
        response = build_base_response(
            world,
            success=result.get("success", False),
            message=result.get("message", "Redemption processed"),
            choice=request.choice,
            autonomous=result.get("autonomous", False),
            autonomy_turns=result.get("autonomy_turns", 0),
            dismissed=result.get("dismissed", False),
            administrative=result.get("administrative", False),
            new_max_actions=result.get("new_max_actions", 0),
            troops_frozen=result.get("troops_frozen", 0),
            authority_bonus=result.get("authority_bonus", 0),
            include_popup_passthroughs=False,
        )
        _fill_popup_keys_without_draining(response)
        return response
    except Exception as e:
        print(f"[ERROR] handling redemption response: {e}")
        import traceback
        traceback.print_exc()
        return build_base_response(
            world, success=False, message=f"Error: {str(e)}")


@app.get("/pending_redemption")
def get_pending_redemption():
    """
    Get the current pending redemption event if any.

    Returns redemption details including:
    - marshal: Name of marshal with broken trust
    - trust: Current trust level
    - options: Available choices
    """
    if not hasattr(world, 'pending_redemption') or world.pending_redemption is None:
        return {
            "has_pending": False,
            "message": "No pending redemption event"
        }

    redemption = world.pending_redemption
    return {
        "has_pending": True,
        "marshal": redemption.get("marshal"),
        "trust": redemption.get("trust"),
        "message": redemption.get("message"),
        "options": redemption.get("options", [])
    }


@app.post("/respond_to_glorious_charge")
def respond_to_glorious_charge(request: GloriousChargeResponse):
    """
    Respond to a Glorious Charge popup (Phase 3 Cavalry Recklessness).

    Args:
        request: GloriousChargeResponse with 'choice' field
            - 'charge': Execute Glorious Charge (2x damage dealt AND taken)
            - 'restrain': Normal attack (recklessness continues to build)

    Returns result of the charge/restrain choice.
    """
    try:
        if world.game_over:
            return build_base_response(
                world, success=False, message="The war is over.",
                game_over=True, victory=world.victory)
        # Validate choice
        valid_choices = ['charge', 'restrain']
        if request.choice not in valid_choices:
            return build_base_response(
                world, success=False,
                message=f"Invalid choice: '{request.choice}'. Valid: {', '.join(valid_choices)}")

        # Process the response through executor
        result = executor.respond_to_glorious_charge(request.choice, world)

        # Non-draining (Aug 2026 health-check audit): main.gd's
        # _on_glorious_charge_response never routes popup keys, so a
        # draining build here destroyed any queued choice popup.
        response = build_base_response(
            world,
            success=result.get("success", False),
            message=result.get("message", "Charge processed"),
            events=result.get("events", []),
            choice=request.choice,
            include_popup_passthroughs=False,
        )
        _fill_popup_keys_without_draining(response)
        if result.get("battle_report"):
            response["battle_report"] = result["battle_report"]
        # Verify-fleet correction (Aug 2026): BOTH charge arms can conquer —
        # the hand-enumerated build dropped pending_capture_choice /
        # capture_data (and the restrain arm's reinforcement messages), so a
        # conquering charge's capture question was invisible until the next
        # command was eaten by the executor's capture block.
        from backend.commands.strategic import _carry_combat_fields
        _carry_combat_fields(response, result)
        return response
    except Exception as e:
        print(f"[ERROR] handling Glorious Charge response: {e}")
        import traceback
        traceback.print_exc()
        return build_base_response(
            world, success=False, message=f"Error: {str(e)}")


@app.post("/strategic_response")
def handle_strategic_response(request: StrategicInterruptResponse):
    """
    Respond to a strategic command interrupt (Phase D).

    Called when a marshal's strategic order hits an interrupt that requires
    player input (cannon fire, blocked path, ally moving).

    Args:
        request: StrategicInterruptResponse with marshal_name, response_type, choice

    Returns execution result after choice is processed.
    """
    try:
        if world.game_over:
            return build_base_response(
                world, success=False, message="The war is over.",
                game_over=True, victory=world.victory)
        from backend.commands.strategic import StrategicOrderProcessor
        strategic_exec = StrategicOrderProcessor(executor)
        result = strategic_exec.handle_response(
            request.marshal_name, request.response_type,
            request.choice, world, game_state
        )

        # Forward the WHOLE executor result — same builder the typed interrupt
        # path uses (main.py /command interrupt route) — so a muster-confirmed
        # "Attack Anyway" that RESOLVES a battle surfaces its follow-on popups
        # (plunder/secure capture choice, glorious charge, battle report,
        # reinforcement narration) instead of dropping them and then blocking
        # the next command with "you must decide how to handle the captured
        # region first!".
        #
        # PC15-10 B0 (F7-2): NON-draining. Those follow-on surfaces all ride
        # the EXECUTOR RESULT's own keys (pending_capture_choice,
        # pending_glorious_charge, battle_report, …) through **extra — the
        # client's _post_hud_response_routes matchers read exactly those keys,
        # so they are untouched by the queue. What the default drain ALSO
        # popped was the highest-priority QUEUE popup — and the interrupt
        # route renders only its 12-family table, so a queued Proclamation
        # (formation-latched: it never re-fires) delivered here was lost
        # FOREVER. Held in the queue instead; it rides the next /command.
        response = _build_result_response(result, world, drain_popups=False)
        # Redemption event from strategic trust penalty
        if result.get("redemption_event"):
            response["state"] = "awaiting_redemption_choice"
            response["redemption_event"] = result["redemption_event"]
            world.pending_redemption = result["redemption_event"]
            print(f"[ALERT] REDEMPTION TRIGGERED for {result['redemption_event']['marshal']}")
        return response
    except Exception as e:
        print(f"[ERROR] handling strategic response: {e}")
        import traceback
        traceback.print_exc()
        return build_base_response(
            world, success=False, message=f"Error: {str(e)}")


@app.get("/authority_status")
def get_authority_status():
    """
    Get the current authority tracker status.

    Returns:
    - authority: Current authority level (0-100)
    - label: Authority status label (e.g., "Divine Right", "Questionable")
    - trust_modifier: Modifier affecting trust gains
    - obedience_modifier: Modifier affecting marshal obedience
    - recent_responses: Last few player responses to objections
    """
    authority = world.authority_tracker
    return {
        "authority": int(authority.authority),
        "label": authority.get_authority_label(),
        "trust_modifier": int(authority.get_trust_gain_modifier() * 100),  # As percentage (e.g., 80 = 0.8x)
        "obedience_modifier": int(authority.get_obedience_modifier() * 100),  # As percentage
        "recent_responses": list(authority.recent_responses[-5:])  # Last 5 responses
    }


@app.get("/marshal_trust/{marshal_name}")
def get_marshal_trust(marshal_name: str):
    """
    Get trust and disobedience info for a specific marshal.

    Returns:
    - name: Marshal name
    - trust: Current trust value (0-100)
    - trust_label: Trust status label (e.g., "Loyal", "Strained")
    - vindication_score: How often marshal has been proven right (-5 to +5)
    - recent_battles: Last 3 battle results
    - recent_overrides: Recent times player overrode marshal
    """
    marshal = world.get_marshal(marshal_name)
    if not marshal:
        return {
            "success": False,
            "message": f"Marshal '{marshal_name}' not found"
        }

    # Fog guard: only return data for player marshals
    if marshal.nation != world.player_nation:
        return {
            "success": False,
            "message": f"No intelligence available on {marshal_name}"
        }

    return {
        "success": True,
        "name": marshal.name,
        "trust": int(marshal.trust.value) if hasattr(marshal, 'trust') else 70,
        "trust_label": marshal.trust.get_label() if hasattr(marshal, 'trust') else "Unknown",
        "vindication_score": int(getattr(marshal, 'vindication_score', 0)),
        "recent_battles": list(getattr(marshal, 'recent_battles', [])),
        "recent_overrides": list(getattr(marshal, 'recent_overrides', [])),
        "personality": marshal.personality
    }


@app.get("/debug_marshal/{marshal_name}")
def debug_marshal(marshal_name: str):
    """
    DEBUG ENDPOINT: Get comprehensive marshal data for debugging disobedience system.

    Returns:
    - All trust/vindication/authority data
    - Personality details
    - Recent decision history
    - Last objection severity
    """
    if not DEBUG_MODE:
        return {"success": False, "message": "Debug endpoints disabled"}
    marshal = world.get_marshal(marshal_name)
    if not marshal:
        return {
            "success": False,
            "message": f"Marshal '{marshal_name}' not found",
            "available_marshals": [m.name for m in world.get_player_marshals()]
        }

    # Get vindication tracker data
    vindication_data = world.vindication_tracker.get_vindication_data(marshal_name)

    return {
        "success": True,
        "marshal": marshal.name,
        "personality": {
            "type": marshal.personality,
            "description": {
                "aggressive": "Favors bold attacks, objects to caution",
                "cautious": "Prefers defensive positions, objects to risky moves",
                "literal": "Follows orders precisely, objects to vague commands"
            }.get(marshal.personality, "Unknown")
        },
        "trust": {
            "value": int(marshal.trust.value) if hasattr(marshal, 'trust') else 70,
            "label": marshal.trust.get_label() if hasattr(marshal, 'trust') else "Unknown",
            "threshold_for_objection": "Trust affects objection likelihood"
        },
        "vindication": {
            "score": vindication_data.get("score", 0),
            "recent_overrides": vindication_data.get("recent_overrides", []),
            "recent_battles": vindication_data.get("recent_battles", []),
            "has_pending": world.vindication_tracker.has_pending(marshal_name)
        },
        "authority_context": {
            "player_authority": int(world.authority_tracker.authority),
            "authority_label": world.authority_tracker.get_authority_label(),
            "affects_trust_gains": int(world.authority_tracker.get_trust_gain_modifier() * 100)  # int % for Godot
        },
        "location": marshal.location,
        "strength": int(marshal.strength),
        "morale": int(marshal.morale)
    }


def _get_fortify_state_safe(marshal) -> dict:
    """Safe wrapper for _get_fortify_state with error handling."""
    try:
        return _get_fortify_state(marshal)
    except Exception as e:
        print(f"[FORTIFY_STATE_ERROR] Exception for {getattr(marshal, 'name', 'unknown')}: {e}")
        return {
            "direction": "error",
            "floor": 0,
            "turns_until_decay": -1,
            "turns_fortified": 0,
            "error": str(e)
        }


def _get_fortify_state(marshal) -> dict:
    """
    Get fortification state for display (Phase 3 - Fortify Decay).

    Returns:
        Dict with direction, floor, turns_until_decay for frontend display.
    """
    if not getattr(marshal, 'fortified', False):
        return {
            "direction": "none",
            "floor": 0,
            "turns_until_decay": -1,
            "turns_fortified": 0
        }

    # DEBUG: Print fortify state calculation
    print(f"[FORTIFY_STATE_DEBUG] {marshal.name}: fortified=True, defense_bonus={getattr(marshal, 'defense_bonus', 0)}, turns_fortified={getattr(marshal, 'turns_fortified', 0)}")

    from backend.models.personality_modifiers import get_max_fortify_bonus

    personality = getattr(marshal, 'personality', 'unknown')
    is_cavalry = getattr(marshal, 'cavalry', False)
    current_bonus = getattr(marshal, 'defense_bonus', 0)
    turns_fortified = getattr(marshal, 'turns_fortified', 0)
    max_bonus = get_max_fortify_bonus(personality)

    # Decay configuration by personality
    decay_config = {
        "aggressive": {"start": 4, "rate": 0.02, "floor": 0.0},
        "balanced": {"start": 6, "rate": 0.01, "floor": 0.0},
        "cautious": {"start": 8, "rate": 0.01, "floor": 0.05},
        "literal": {"start": 8, "rate": 0.01, "floor": 0.05},
    }
    default_decay = {"start": 6, "rate": 0.01, "floor": 0.0}
    decay_settings = decay_config.get(personality, default_decay)

    floor_percent = int(decay_settings["floor"] * 100)

    # Cavalry uses different system (auto-unfortify at turn 3)
    if is_cavalry:
        turns_until_unfortify = max(0, 3 - turns_fortified)
        return {
            "direction": "cavalry_limit",
            "floor": 0,
            "turns_until_decay": turns_until_unfortify,
            "turns_fortified": turns_fortified
        }

    # Determine direction
    decay_starts = decay_settings["start"]
    turns_until_decay = max(0, decay_starts - turns_fortified)

    if turns_fortified >= decay_starts:
        if current_bonus <= decay_settings["floor"]:
            direction = "at_floor"
        else:
            direction = "decaying"
    elif current_bonus >= max_bonus:
        # At max, waiting for decay to start
        direction = "stable"
    else:
        direction = "growing"

    result = {
        "direction": direction,
        "floor": floor_percent,
        "turns_until_decay": turns_until_decay,
        "turns_fortified": turns_fortified
    }
    print(f"[FORTIFY_STATE_DEBUG]   -> direction={direction}, floor={floor_percent}%, turns_until_decay={turns_until_decay}")
    return result


# ════════════════════════════════════════════════════════════
# SAVE/LOAD ENDPOINTS (Phase 6: Save/Load System)
# ════════════════════════════════════════════════════════════

def _validate_save_filename(filename: str) -> bool:
    """Reject filenames with path traversal characters."""
    if ".." in filename or "/" in filename or "\\" in filename:
        return False
    # Verify resolved path stays within saves dir
    resolved = (save_manager.SAVE_DIR / filename).resolve()
    return str(resolved).startswith(str(save_manager.SAVE_DIR.resolve()))


@app.post("/save")
async def save_endpoint(request: SaveRequest):
    """Save current game state."""
    global world
    # 3D-2: Validate save filename before passing to save_game
    if request.save_name and not _validate_save_filename(request.save_name):
        return build_base_response(world, success=False, message="Invalid save name")
    try:
        result = save_game(world, save_name=request.save_name)
        # Non-draining (Aug 2026 health-check audit): the pause-menu save
        # callback reads only success/message — a draining build here
        # destroyed any queued choice popup from the LIVE session (the save
        # file kept it; the running game lost it).
        response = build_base_response(
            world,
            include_popup_passthroughs=False,
            **{k: v for k, v in result.items() if k != "new_state"})
        _fill_popup_keys_without_draining(response)
        return response
    except Exception as e:
        print(f"[ERROR] handling save: {e}")
        import traceback
        traceback.print_exc()
        return build_base_response(world, success=False, message=f"Save failed: {str(e)}")


@app.post("/new_game")
async def new_game_endpoint(request: Optional[NewGameRequest] = None):
    """Start a fresh campaign without restarting the backend process.

    POSITION 7: an optional `scenario` allowlist NAME boots a named authored
    scenario ("tutorial" → The Danube Lesson). Unknown names fail loudly and
    the running world is NOT swapped. Absent/empty → today's default boot.
    """
    try:
        requested = (request.scenario or "").strip() if request else ""
        scenario_override = ""
        if requested:
            if requested not in SCENARIO_ALLOWLIST:
                return build_base_response(
                    world,
                    success=False,
                    message=(
                        f"Unknown scenario {requested!r}. "
                        f"Available: {sorted(SCENARIO_ALLOWLIST)}"
                    ),
                )
            scenario_override = str(SCENARIO_ALLOWLIST[requested])
        player_nation = get_player_nation(world)
        new_world = _reset_world_state(
            player_nation=player_nation, scenario_override=scenario_override
        )
        autosave_result = autosave(new_world)
        autosave_ok = bool(autosave_result.get("success", False))
        message = "New campaign started."
        if autosave_result.get("skipped") == "tutorial":
            # The lesson never writes the campaign's autosave slot — shown,
            # not silent, so nobody reads "refreshed" over a skip.
            message += " Your campaign autosave is untouched."
        elif autosave_ok:
            message += " Autosave refreshed."
        else:
            message += " Warning: autosave refresh failed."
        return build_base_response(
            new_world,
            message=message,
            new_game=True,
            autosave_success=autosave_ok,
            autosave_message=autosave_result.get("message", ""),
        )
    except Exception as e:
        print(f"[ERROR] handling new_game: {e}")
        import traceback
        traceback.print_exc()
        return build_base_response(world, success=False, message=f"New game failed: {str(e)}")


@app.post("/load")
async def load_endpoint(request: LoadRequest):
    """Load a saved game. Replaces current game state.

    PC15-10 B0 (F7-1): NON-draining. The client handler
    (`_apply_world_swap_response`) reads no popup keys, so the default
    drain destroyed the highest-priority popup `from_dict` had just
    RESTORED — one popup lost per load, silently. Keys stay present
    (filled without draining); the restored popup rides the player's
    first `/command`.
    """
    if not _validate_save_filename(request.filename):
        return {"success": False, "message": "Invalid save filename"}
    filepath = save_manager.SAVE_DIR / request.filename
    result = load_game(filepath)
    if result["success"]:
        _set_active_world(result["world"])
        response = build_base_response(world, message=result["message"],
                                       include_popup_passthroughs=False)
    else:
        response = build_base_response(world, success=False,
                                       message=result["message"],
                                       include_popup_passthroughs=False)
    _fill_popup_keys_without_draining(response)
    # WO-30: `pending_capture_choice` is a plain world attribute, not a
    # PopupQueue member, so the fill above cannot deliver it — it only
    # setdefaults queue keys to None. A save carrying an unanswered
    # plunder/secure question therefore loaded with the question standing
    # in world state (it round-trips at world_state.py to_dict/from_dict)
    # and NOTHING on screen: the player's next order was refused by the
    # executor's pending-choice block, which is how they found out.
    # Two keys, the same shape `/capture_choice` returns, and the client's
    # world-swap handler raises the modal from them.
    if world.pending_capture_choice:
        response["pending_capture_choice"] = True
        response["capture_data"] = world.pending_capture_choice
    # WO-35 (the pending_interrupt half): a marshal-level interrupt
    # round-trips the save (marshal.py to_dict/from_dict) and used to raise
    # nothing at load. ORDER-BOUND interrupts self-heal at the next end turn
    # (strategic.py re-emits requires_input), but ORDER-FREE ones
    # (last_stand, muster_confirm — raised from tactical combat on marshals
    # with no strategic order) never re-surface, and worse: the typed
    # pending-question router CONSUMES the next matching unaddressed command
    # as the answer to a question the player was never shown. One key; the
    # client raises it through the same predicate/route pair the command
    # path uses (`_response_has_interrupt_route`). `/load` carries no
    # strategic_reports, so the WIN-H1 defer in that predicate is vacuously
    # satisfied. First marshal wins — only one interrupt popup can be up at
    # a time and there is no drain; a second marshal's interrupt surfaces
    # the way it always has (order-bound at end turn, order-free by typed
    # answer), which this attach makes strictly better, not worse.
    #
    # `pending_objection` is deliberately NOT attached here: the saved dict
    # records no tactical/strategic discriminator the modal needs, and the
    # strategic arm would render a modal with no buttons and no ESC exit
    # (a soft-lock). Its block names the answer words, so the state is
    # answerable — declared as a P3 legibility gap, owner = row WO slice 12.
    for _lm in world.get_player_marshals():
        # Hazard-4 idiom (PC15-4): a marshal who no longer STANDS —
        # captured (strength 0 at the captor's capital) or destroyed —
        # must not attach a question nobody can act on.
        if (_lm.strength > 0 and not getattr(_lm, "captured_by", "")
                and getattr(_lm, "pending_interrupt", None)):
            response["pending_interrupt"] = _lm.pending_interrupt
            break
    return response


@app.get("/saves")
async def list_saves_endpoint():
    """List all available save files."""
    saves = list_saves()
    return {"saves": saves}


# ════════════════════════════════════════════════════════════
# LLM CONFIG (Main Menu pass, position 6 — the in-client API key)
# ════════════════════════════════════════════════════════════

def _llm_config_payload() -> dict:
    llm = parser.llm
    return {
        "success": True,
        "provider": llm.provider_name,
        "key_source": llm.key_source,
        "live": llm.use_real_api,
    }


@app.get("/config/llm")
async def get_llm_config():
    """Effective parser configuration — the Settings panel's honesty line."""
    return _llm_config_payload()


@app.post("/config/llm")
async def set_llm_config(request: LLMConfigRequest):
    """BYOK from the client Settings panel (Main Menu / pause).

    A non-empty key swaps the parser's LLM client to a BYOK Anthropic client
    (LLMClient.create forces live mode, so a key works even when .env says
    mock); an empty key reverts to the .env configuration. The key is held in
    MEMORY only — nothing server-side persists it (the client keeps its copy
    in user://ui_settings.cfg and re-pushes at each campaign start).
    """
    from backend.ai.llm_client import LLMClient
    key = (request.api_key or "").strip()
    try:
        parser.llm = LLMClient.create(key if key else None)
        return _llm_config_payload()
    except Exception as e:  # a bad key string must never take the server down
        print(f"[ERROR] /config/llm: {e}")
        return {"success": False, "message": f"Could not configure parser: {e}"}


@app.post("/delete_save")
async def delete_save_endpoint(request: DeleteSaveRequest):
    """Delete a save file."""
    if not _validate_save_filename(request.filename):
        return {"success": False, "message": "Invalid save filename"}
    filepath = save_manager.SAVE_DIR / request.filename
    result = delete_save(filepath)
    return build_base_response(world, **{k: v for k, v in result.items() if k != "new_state"})


# ════════════════════════════════════════════════════════════
# CAMPAIGN LOG ENDPOINT (Phase 6.5)
# ════════════════════════════════════════════════════════════

@app.get("/campaign_log")
def get_campaign_log():
    """Get fog-filtered campaign event log grouped by turn (descending)."""
    if not game_state.get("world"):
        return {"success": False, "message": "No active game"}
    from backend.campaign_log import (filter_campaign_log, format_event_oneliner,
                                      CATEGORY_MAP, collapse_refusal_family)

    # IGR-B: aggregate the O(n^2) court-to-court refusal bursts for DISPLAY
    # only — the producer's record is AI-3's ladder-gate substrate.
    filtered = collapse_refusal_family(filter_campaign_log(world.event_log, world))

    # Group by turn descending
    turns = {}
    for event in filtered:
        t = event.get("turn", 0)
        if t not in turns:
            turns[t] = []
        turns[t].append({
            **{k: (int(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v)
               for k, v in event.items() if k != "battle_report"},
            # NA-6 §11.8 stage 3: the log re-derives names from the stored
            # raw tag via the STATIC display_nation, so a POST-formation
            # entry would read under the dead name. History before the
            # proclamation is left alone (see the helper's docstring).
            "display": _formations_history_names(
                world, format_event_oneliner(event), event),
            "category": CATEGORY_MAP.get(event.get("type", ""), "unknown"),
        })

    # Hide empty turns (0 visible events after fog filtering)
    sorted_turns = [{"turn": int(t), "events": evts}
                    for t, evts in sorted(turns.items(), reverse=True)
                    if evts]
    payload = {"success": True, "turns": sorted_turns,
               "current_turn": int(world.current_turn)}
    _attach_nation_identity_overrides(payload, world)   # NA-6 §11.8 stage 3
    return payload


# ════════════════════════════════════════════════════════════
# DISPATCH RE-READ ENDPOINT (Session A)
# ════════════════════════════════════════════════════════════

@app.get("/dispatch")
def get_dispatch():
    """Get the last morning dispatch for re-read screen."""
    if not game_state.get("world"):
        return {"success": False, "message": "No active game"}
    dispatch = world.last_morning_dispatch
    payload = {"success": True, "dispatch": dispatch or {}}
    _attach_nation_identity_overrides(payload, world)   # NA-6 §11.8 stage 3
    return payload


@app.get("/gazette")
def get_gazette():
    """HC-G "Le Moniteur": the stored back-issue archive (newest last).
    Issues were composed fog-honest at publish time — this is a pure
    read of the serialized store, never a recomposition."""
    if not game_state.get("world"):
        return {"success": False, "message": "No active game"}
    payload = {
        "success": True,
        "issues": [dict(i) for i in getattr(world, "gazette_issues", [])],
        "calendar_label": world.get_calendar_label(),
    }
    _attach_nation_identity_overrides(payload, world)   # NA-6 §11.8 stage 3
    return payload


# ════════════════════════════════════════════════════════════
# STRATEGIC LEDGER ENDPOINT (Session B)
# ════════════════════════════════════════════════════════════

@app.get("/ledger")
def get_ledger():
    """Get the strategic ledger for the ledger screen."""
    if not game_state.get("world"):
        return {"success": False, "message": "No active game"}
    from backend.game_logic.ledger import build_strategic_ledger
    ledger = build_strategic_ledger(world)
    payload = {"success": True, "ledger": ledger}
    _attach_nation_identity_overrides(payload, world)   # NA-6 §11.8 stage 3
    return payload


# ════════════════════════════════════════════════════════════
# PENDING ENVOY RECOVERY (PL-27 Session 2)
# ════════════════════════════════════════════════════════════

def _build_proposal_popup_clauses(terms, *, include_base=True):
    """Build incoming_proposal_popup.gd-compatible clause strings."""
    from backend.game_logic.mailbox_payloads import build_proposal_popup_clauses

    return build_proposal_popup_clauses(terms, include_base=include_base)


def _build_acceptance_hints(acceptance):
    """Translate acceptance components into Godot-friendly hint strings."""
    from backend.game_logic.mailbox_payloads import build_acceptance_hints

    return build_acceptance_hints(acceptance)


def _build_pending_envoy_popup_from_terms(
    world,
    *,
    nation,
    terms,
    assessment="",
    is_counter_offer=False,
    acceptance=None,
    acceptance_score=None,
    decision_reason="",
):
    """Build the popup payload shape incoming_proposal_popup.gd expects."""
    from backend.game_logic.mailbox_payloads import build_pending_envoy_popup_from_terms

    return build_pending_envoy_popup_from_terms(
        world,
        nation=nation,
        terms=terms,
        assessment=assessment,
        is_counter_offer=is_counter_offer,
        acceptance=acceptance,
        acceptance_score=acceptance_score,
        decision_reason=decision_reason,
    )


def _build_pending_envoy_popup_from_dialogue(world, dialogue):
    """Recover popup payload for an active soft-stop dialogue."""
    from backend.display_names import proposal_display_name

    def _stamp_dialogue_id(popup: dict) -> dict:
        # W6-0 (BUG-CA-7): every popup shape derived from a dialogue carries
        # the identity the client must answer with.
        if dialogue.get("dialogue_id") is not None:
            popup["dialogue_id"] = dialogue["dialogue_id"]
        return popup

    context = dialogue.get("context", {})
    terms = context.get("counter_terms") or context.get("proposal") or {}
    popup_payload = dialogue.get("popup_payload") or context.get("popup_payload")
    if isinstance(popup_payload, dict) and popup_payload:
        popup = popup_payload.copy()
        popup["is_counter_offer"] = dialogue.get("type", "") in (
            "counter_offer", "counter_offer_response"
        )
        if "proposal_type_display" not in popup:
            proposal_type = popup.get("proposal_type", terms.get("type"))
            if proposal_type is not None:
                popup["proposal_type_display"] = proposal_display_name(proposal_type)
        return _stamp_dialogue_id(popup)

    existing_popup = getattr(world, "incoming_proposal_popup", None)
    expected_nation = dialogue.get("target_nation", context.get("source_nation", "Unknown"))
    expected_type = terms.get("type")
    if isinstance(existing_popup, dict) and existing_popup:
        if (
            existing_popup.get("from_nation") == expected_nation
            and (not expected_type or existing_popup.get("proposal_type") == expected_type)
        ):
            popup = existing_popup.copy()
            popup["is_counter_offer"] = dialogue.get("type", "") in (
                "counter_offer", "counter_offer_response"
            )
            if "proposal_type_display" not in popup:
                proposal_type = popup.get("proposal_type", expected_type)
                if proposal_type is not None:
                    popup["proposal_type_display"] = proposal_display_name(proposal_type)
            return _stamp_dialogue_id(popup)

    return _stamp_dialogue_id(_build_pending_envoy_popup_from_terms(
        world,
        nation=expected_nation,
        terms=terms,
        assessment=dialogue.get("talleyrand_text", ""),
        is_counter_offer=dialogue.get("type", "") in ("counter_offer", "counter_offer_response"),
        acceptance_score=context.get("acceptance_score"),
        decision_reason=context.get("decision_reason", ""),
    ))


@app.get("/pending_envoy")
def get_pending_envoy():
    """Return the current active mailbox item for envoy recovery.

    Session 2 follow-up: Active-item-only. If no active mailbox item
    (queued-only or non-mailbox active), returns has_pending=false with
    accurate count. GET /mailbox is the authoritative browse surface.

    SC-5 reversal commit 2 (Slice G1): incoming settlement offers are
    now first-class mailbox items. Save-loaded saves that carry
    pending settlement offers get promoted into the mailbox queue on
    every read so the badge / pending_envoy / mailbox surfaces stay
    consistent.
    """
    from backend.game_logic.settlement_offers import (
        build_ally_settlement_petition_popup,
        build_incoming_settlement_offer_popup,
        promote_pending_settlement_offers,
    )

    world = game_state["world"]
    promote_pending_settlement_offers(world)
    dm = world.dialogue_manager

    result = {
        "success": True,
        "has_pending": False,
        "pending_envoy_count": int(dm.get_mailbox_count()),
    }

    current = dm.peek()
    if current and current.get("type", "") in dm.SOFT_STOP_MAILBOX_TYPES:
        dtype = current.get("type", "")
        if dtype == "incoming_settlement_offer":
            result["has_pending"] = True
            result["dialogue_type"] = dtype
            # REBUILD every read, exactly like /mailbox/activate's arm: the
            # offer's status-quo clause is DERIVED from current controllers,
            # so serving the payload cached at creation described the map of
            # the turn the offer was DRAFTED (live: a turn-3 offer read at
            # turn 7 still claimed Britain held Flanders and Orleanais —
            # Spain had retaken both).
            popup = build_incoming_settlement_offer_popup(world, current)
            current["popup_payload"] = popup
            result["incoming_settlement_offer"] = popup
        elif dtype == "ally_settlement_petition":
            result["has_pending"] = True
            result["dialogue_type"] = dtype
            popup = current.get("popup_payload")
            if not isinstance(popup, dict) or not popup:
                popup = build_ally_settlement_petition_popup(current)
                current["popup_payload"] = popup
            result["diplomatic_dialogue"] = popup
        elif dtype in ("incoming_proposal", "counter_offer",
                       "counter_offer_response", "incoming_ultimatum"):
            # NA-5: ultimatums recover through the same popup transport —
            # the payload carries is_ultimatum so the popup renders the
            # ultimatum register.
            result["has_pending"] = True
            result["dialogue_type"] = dtype
            result["incoming_proposal"] = _build_pending_envoy_popup_from_dialogue(
                world, current
            )

    return result


@app.get("/mailbox")
def get_mailbox():
    """Return ordered list of mailbox items for the inbox panel.

    Session 2 follow-up: Authoritative browse surface for pending diplomacy.

    SC-5 reversal commit 2 (Slice G1): incoming settlement offers are
    first-class mailbox rows. Save-loaded saves get promoted on first
    read so badge counts stay accurate across game sessions.
    """
    from backend.game_logic.envoy_digest import build_envoy_digest
    from backend.game_logic.settlement_offers import (
        promote_pending_settlement_offers,
    )

    world = game_state["world"]
    promote_pending_settlement_offers(world)
    dm = world.dialogue_manager

    items = list(dm.get_mailbox_items())
    return {
        "success": True,
        "items": items,
        "count": len(items),
        # IGR-F: the letter-book rides the browse surface too, so the panel
        # gets rows AND their inline-answerable subset from one call. Same
        # derived builder as build_base_response — one source, no drift.
        "envoy_digest": build_envoy_digest(world),
    }


class MailboxActivateRequest(BaseModel):
    mailbox_id: int


@app.post("/mailbox/activate")
def activate_mailbox_item(request: MailboxActivateRequest):
    """Swap a queued mailbox item into the active slot.

    Session 2 follow-up: Returns the popup-safe payload for the newly
    active item. The previously active item returns to queue.

    SC-5 reversal commit 2 (Slice G1): incoming settlement offers
    activate into the popup the same way ordinary proposals do.
    Save-loaded saves get promoted into the mailbox queue first so the
    selected `mailbox_id` resolves to a real dialogue.
    """
    from backend.game_logic.settlement_offers import (
        build_ally_settlement_petition_popup,
        build_incoming_settlement_offer_popup,
        promote_pending_settlement_offers,
    )

    world = game_state["world"]
    promote_pending_settlement_offers(world)
    dm = world.dialogue_manager

    # Read the blocker BEFORE activating — a successful activation clears it.
    blocker = dm.active_blocker_type()
    dialogue = dm.activate_mailbox_item(request.mailbox_id)

    if dialogue is None:
        # Aug 23, 2026: this used to answer "Item not found or activation
        # blocked by current dialogue" — one string for two unrelated causes,
        # naming neither. This is also the route the mailbox panel's own row
        # click takes AFTER the panel has hidden itself, so the player is left
        # looking at an empty screen being told something they cannot see is
        # in the way. Two causes, two sentences, and the blocker by name.
        if blocker:
            from backend.display_names import dialogue_display_name
            named = dialogue_display_name(blocker)
            # Number-neutral — see the note at the sibling refusal.
            message = (f"{named[:1].upper()}{named[1:]} still stands before "
                       f"you, Sire — settle that first.")
        else:
            message = "That letter is no longer in the mailbox, Sire."
        return {
            "success": False,
            "message": message,
            # The client hides the panel on a BLOCKED refusal so the matter it
            # names is actually visible (the panel is CanvasLayer 119; the
            # dialogue modals it points at are 110).
            "activation_blocked": bool(blocker),
            "items": list(dm.get_mailbox_items()),
            "count": int(dm.get_mailbox_count()),
        }

    dtype = dialogue.get("type", "")
    result = {
        "success": True,
        "dialogue_type": dtype,
        "items": list(dm.get_mailbox_items()),
        "count": int(dm.get_mailbox_count()),
    }

    if dtype in ("incoming_proposal", "counter_offer",
                 "counter_offer_response", "incoming_ultimatum"):
        popup = _build_pending_envoy_popup_from_dialogue(world, dialogue)
        dialogue["popup_payload"] = popup.copy()
        # PC15-10 B0 (F7-3): return-only — the client shows THIS payload
        # immediately, so writing `world.incoming_proposal_popup` as well
        # queued a second copy that the next /command delivered AGAIN
        # (double-delivery of the same envoy). The PL-14 safety valve reads
        # `pending_diplomatic_dialogue`, not this field, so answerability
        # is untouched.
        result["incoming_proposal"] = popup
    elif dtype == "incoming_settlement_offer":
        # REBUILD every activation, exactly like the proposal arm above. The
        # offer's territorial clause is DERIVED from current controllers
        # (`_derive_status_quo_lines`), so re-showing a cached payload told
        # the player who held what on the turn the offer ARRIVED: a turn-3
        # offer re-opened on turn 8 still read "Austria retains Swabia"
        # after France had retaken it — false facts on the surface where
        # peace is accepted or refused.
        popup = build_incoming_settlement_offer_popup(world, dialogue)
        dialogue["popup_payload"] = popup
        result["incoming_settlement_offer"] = popup
    elif dtype == "ally_settlement_petition":
        popup = dialogue.get("popup_payload")
        if not isinstance(popup, dict) or not popup:
            popup = build_ally_settlement_petition_popup(dialogue)
            dialogue["popup_payload"] = popup
        result["diplomatic_dialogue"] = popup

    return result


class MailboxRespondRequest(BaseModel):
    mailbox_id: int
    choice: str


@app.post("/mailbox/respond")
def respond_to_mailbox_item(request: MailboxRespondRequest):
    """IGR-F: answer ONE letter-book row without opening it as a modal.

    `handle_diplomatic_dialogue_response` reads only the ACTIVE dialogue and
    refuses a `dialogue_id` that is not the current top (the W6-0 identity
    binding, which exists because answering Britain's settlement offer once
    rejected Saxony's never-seen proposal). So a per-row answer is only legal
    as activate-then-respond, and doing that in two client calls would
    re-open exactly the race the binding forbids: the id can go stale between
    them. Resolving the id server-side from the `mailbox_id` the player
    actually clicked preserves the binding by construction.

    Scoped deliberately: only a row the letter-book OWNS may be answered
    here. Anything else — a great power's ask, an ultimatum, a settlement
    offer, a peace or an alliance from a minor — must be opened in full, so
    this endpoint can never become a way to accept a consequential treaty
    with one unconsidered click.
    """
    from backend.game_logic.envoy_digest import is_routine_small_court
    from backend.game_logic.settlement_offers import (
        promote_pending_settlement_offers,
    )

    world = game_state["world"]
    if world.game_over:
        return build_base_response(
            world, success=False, message="The war is over.",
            game_over=True, victory=world.victory)

    promote_pending_settlement_offers(world)
    dm = world.dialogue_manager

    target = None
    for candidate in ([dm.peek()] if dm.peek() else []) + list(dm.iter_queue()):
        if int(candidate.get("mailbox_id", 0)) == int(request.mailbox_id):
            target = candidate
            break

    def _refuse(message: str) -> dict:
        # IGR-F review [1]: a refused click must not eat a queued popup either.
        response = build_base_response(
            world, success=False, message=message,
            include_popup_passthroughs=False,
            digest_row_failed=int(request.mailbox_id))
        _fill_popup_keys_without_draining(response)
        return response

    if target is None:
        return _refuse(
            "That letter is no longer among the pending envoys, Sire.")

    if not is_routine_small_court(target, world):
        return _refuse("That matter is too weighty to answer from the "
                       "letter-book, Sire. Open it in full.")

    # Read the blocker BEFORE activating — a successful activation clears it.
    blocker = dm.active_blocker_type()
    activated = dm.activate_mailbox_item(int(request.mailbox_id))
    if activated is None:
        # activate_mailbox_item refuses while a hard-stop / hybrid / STAGED
        # local-planning dialogue holds the active slot. Say so rather than
        # firing an answer that would land somewhere else — but NAME it.
        # The old copy ("Another matter holds your attention, Sire. Settle it
        # before answering the lesser courts.") was measured live against a
        # Talleyrand advisory the player had no way to see, making it an
        # instruction with no action behind it. Read-outs no longer reach here
        # at all (DialogueManager.DISPOSABLE_ACTIVE_TYPES); what does reach
        # here is real, staged, and has a surface the player can be sent to.
        if blocker:
            from backend.display_names import dialogue_display_name
            named = dialogue_display_name(blocker)
            response = _refuse(
                # Number-neutral: several display strings are plural noun
                # phrases ("the terms you are drafting"), and "…is still
                # before you" read as a grammar bug to the player.
                f"{named[:1].upper()}{named[1:]} still awaits your word, "
                f"Sire. Settle that before answering the lesser courts.")
            response["activation_blocked"] = True
            return response
        return _refuse("That letter cannot be answered from the letter-book "
                       "just now, Sire. Open it in full.")

    response = _respond_to_dialogue_sync(
        request.choice,
        dialogue_id=activated.get("dialogue_id"),
        suppress_result_popup=True,
    )
    response["digest_row_answered"] = int(request.mailbox_id)
    return response


# ════════════════════════════════════════════════════════════
# DIPLOMATIC LEDGER ENDPOINT (Session 8A)
# ════════════════════════════════════════════════════════════

@app.get("/diplomatic_preview")
def get_diplomatic_preview_endpoint(
    nation: str = "",
    mode: str = "",
    war_id: str = "",
    proposer_side: str = "",
    density: str = "medium",
):
    """Get diplomatic preview for the diplomacy wizard (§3c).

    Without ?nation: returns categorized nation list for Step 1.
    With ?nation=X: returns full preview for Step 2.
    """
    if not game_state.get("world"):
        return {"success": False, "message": "No active game"}
    if mode == "settlement":
        try:
            from backend.game_logic.settlement_staging import build_settlement_preview
            return build_settlement_preview(
                world,
                war_id=war_id,
                proposer_side=proposer_side or None,
                settlement_terms=[],
                actor_nation=getattr(world, "player_nation", "France"),
                density=density,
            )
        except Exception as e:
            return {"success": False, "error": str(e), "mode": "settlement", "war_id": war_id}
    if not nation or not nation.strip():
        # Step 1: Return categorized nation list for the wizard
        try:
            from backend.display_names import STATE_DISPLAY as _STATE_DISPLAY_NAMES
            player = world.player_nation
            enemy_nations = list(getattr(world, 'enemy_nations', []))
            vassals = getattr(world, 'vassals', {})
            dp = int(getattr(world, 'diplomatic_points', 0))
            dm = world.dialogue_manager
            dialogue_pending = dm.is_hard_stop() or dm.has_current_turn_offers() or dm.is_local_planning()
            # PL-30: Distinguish blocking dialogue from deferred proposal result
            has_deferred_result = world.proposal_result_popup is not None

            categories = {"at_war": [], "treaties": [], "vassals": [], "neutral": []}
            treaty_states = {"ARMISTICE", "OPEN_BORDERS", "NON_AGGRESSION",
                             "DEFENSIVE_ALLIANCE", "ALLIANCE"}

            from backend.game_logic.diplomacy import get_relation_descriptor

            # W2: Check for active mission target
            active_mission = getattr(world, 'active_diplomatic_mission', None)
            mission_target = None
            if active_mission and isinstance(active_mission, dict) and not active_mission.get("completed"):
                mission_target = active_mission.get("target")

            for n in enemy_nations:
                # Skip eliminated nations (no marshals with strength, no regions)
                has_forces = any(
                    m.strength > 0 for m in world.marshals.values() if m.nation == n
                )
                has_regions = any(
                    r.controller == n for r in world.regions.values()
                )
                if not has_forces and not has_regions:
                    continue

                diplo_key = world._make_diplo_key(player, n)
                state = world.diplomatic_states.get(diplo_key, "PEACE")
                is_vassal = n in vassals

                # W1: Relation score and descriptor
                relation = int(world.nation_relations.get(diplo_key, 0) or 0)
                relation_desc = get_relation_descriptor(relation)

                entry = {
                    "name": n,
                    "state": state,
                    "state_display": _STATE_DISPLAY_NAMES.get(state, state),
                    "is_vassal": is_vassal,
                    "relation": relation,
                    "relation_descriptor": relation_desc,
                    "has_active_mission": (mission_target == n),
                }

                if is_vassal:
                    entry["state_display"] = "Vassal"
                    categories["vassals"].append(entry)
                elif state == "WAR":
                    categories["at_war"].append(entry)
                elif state in treaty_states:
                    categories["treaties"].append(entry)
                else:
                    categories["neutral"].append(entry)

            return {
                "success": True,
                "mode": "nations",
                "dp_available": int(dp),
                "dialogue_pending": dialogue_pending,
                "pending_envoy_count": int(dm.get_mailbox_count()),
                "has_deferred_result": has_deferred_result,
                "categories": categories,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    try:
        from backend.game_logic.diplomacy import get_diplomatic_preview
        nation = nation.strip()
        # Reject self-proposal
        if nation == world.player_nation:
            return {"success": False, "error": "We cannot conduct diplomacy with ourselves, Your Excellency."}
        # Reject eliminated nations
        if nation in list(getattr(world, 'enemy_nations', [])):
            has_forces = any(m.strength > 0 for m in world.marshals.values() if m.nation == nation)
            has_regions = any(r.controller == nation for r in world.regions.values())
            if not has_forces and not has_regions:
                return {"success": False, "error": f"{nation} has been eliminated from the war."}
        preview = get_diplomatic_preview(world, nation)
        return {
            "success": True,
            "dialogue_pending": (
                world.dialogue_manager.is_hard_stop()
                or world.dialogue_manager.has_current_turn_offers()
                or world.dialogue_manager.is_local_planning()
            ),
            "pending_envoy_count": int(world.dialogue_manager.get_mailbox_count()),
            **preview,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/diplomatic_preview")
def post_diplomatic_preview_endpoint(request: dict):
    """Preview draft diplomatic payloads.

    Slice C2 currently supports `{"mode": "settlement"}` only. This endpoint
    is preview-only and must not stage settlement_confirm or mutate world state.
    """
    if not game_state.get("world"):
        return {"success": False, "message": "No active game"}
    if request.get("mode") != "settlement":
        return {"success": False, "error": "unsupported_preview_mode"}
    try:
        from backend.game_logic.settlement_staging import (
            build_settlement_preview,
        )
        from backend.game_logic.settlement_validation import (
            validate_settlement_terms,
        )
        actor = request.get("actor_nation") or getattr(world, "player_nation", "France")
        terms = request.get("settlement_terms", [])
        war_id_str = str(request.get("war_id") or "")
        # SC-1: validate authored terms before building preview.
        war_instance = (getattr(world, "war_instances", {}) or {}).get(war_id_str) or {}
        actor_side = None
        for side in ("attackers", "defenders"):
            if actor in (war_instance.get(side) or []):
                actor_side = side
                break
        validation = validate_settlement_terms(
            terms,
            actor_nation=actor,
            player_nation=getattr(world, "player_nation", "France"),
            proposer_side=request.get("proposer_side"),
            actor_side_in_war=actor_side,
            covered_enemy_participants=request.get("covered_enemy_participants"),
            world=world,
            war_instance=war_instance,
        )
        if not validation.get("valid"):
            return {
                "success": False,
                "mode": "settlement",
                "war_id": war_id_str,
                "error": validation.get("error"),
                "error_index": validation.get("error_index"),
                "disabled_reason_display": validation.get("disabled_reason_display"),
                "mutated": False,
            }
        return build_settlement_preview(
            world,
            war_id=war_id_str,
            proposer_side=request.get("proposer_side"),
            settlement_terms=terms,
            covered_enemy_participants=request.get("covered_enemy_participants"),
            actor_nation=actor,
            density=str(request.get("density") or "medium"),
        )
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "mode": "settlement",
            "war_id": request.get("war_id"),
        }


@app.get("/diplomatic_ledger")
def get_diplomatic_ledger():
    """Get the diplomatic ledger for the diplomatic ledger screen."""
    if not game_state.get("world"):
        return {"success": False, "message": "No active game"}
    try:
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        ledger = build_diplomatic_ledger(world)
        payload = {"success": True, "ledger": ledger}
        _attach_nation_identity_overrides(payload, world)   # NA-6 §11.8 stage 3
        return payload
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/cancel_order")
async def cancel_order(request: Request):
    """Cancel a marshal's strategic order from the Orders tab."""
    try:
        if world.game_over:
            return build_base_response(
                world, success=False, message="The war is over.",
                game_over=True, victory=world.victory)
        data = await request.json()
        marshal_name = data.get("marshal")
        if not marshal_name:
            return build_base_response(
                world, success=False, message="No marshal specified.")

        if not game_state.get("world"):
            return build_base_response(
                world, success=False, message="No active game")

        # AP pre-check (matches typed cancel command flow)
        if world.actions_remaining <= 0:
            return build_base_response(
                world, success=False,
                message="No actions remaining this turn.")

        # 2A-4: Dialogue guard — block cancel during active diplomatic dialogue
        if world.pending_diplomatic_dialogue is not None:
            return build_base_response(
                world, success=False,
                message="Talleyrand awaits your response to a diplomatic matter.")

        command = {"action": "cancel", "marshal": marshal_name}
        result = executor._execute_cancel(command, game_state)

        # Deduct 1 AP for successful cancels (matches typed "cancel" command flow)
        if result.get("success") and not result.get("no_action_cost"):
            world.use_action("cancel")

        # Non-draining (Aug 2026 health-check audit): the ledger's cancel
        # callback ignores the response body and just refreshes the ledger,
        # so a draining build here destroyed any queued choice popup.
        return _build_result_response(result, world, drain_popups=False)
    except Exception as e:
        print(f"[ERROR] handling cancel_order: {e}")
        import traceback
        traceback.print_exc()
        return build_base_response(
            world, success=False, message=f"Error: {str(e)}")


@app.get("/marshal_overview")
def get_marshal_overview():
    """Get the marshal overview for the Marshal Management screen."""
    if not game_state.get("world"):
        return {"success": False, "message": "No active game"}
    from backend.game_logic.marshal_overview import build_marshal_overview
    from backend.game_logic.jealousy import (
        GLORY_WINDOW,
        build_glory_ladder_payload,
    )
    from backend.game_logic.recruitment import build_recruitment_payload
    overview = build_marshal_overview(world)
    payload = {
        "success": True,
        "marshals": overview,
        # Jealousy v3.2: the player's glory ladder (Generals screen header)
        "glory_ladder": build_glory_ladder_payload(world),
        # A11 (CA9 row 3): the ladder header states its own window, and the
        # client INTERPOLATES this rather than re-hardcoding a number. The
        # caption said "last 5 turns" against a live GLORY_WINDOW of 8 —
        # stale since DR-2 lengthened it, and the only sentence in the
        # product that states the causal rule at all.
        "glory_window": int(GLORY_WINDOW),
        # Marshal recruitment: the commissionable candidate pool
        "recruitment": build_recruitment_payload(world),
    }
    _attach_nation_identity_overrides(payload, world)   # NA-6 §11.8 stage 3
    return payload


@app.get("/formables")
def get_formables():
    """NA-6d §11.6-8 — the Formables button payload: every Class C template
    and Class T watcher with honest gate terms (never hidden, never dead).
    Rendered by the F1 diplomacy wizard's "Formable Nations" entry."""
    if not game_state.get("world"):
        return {"success": False, "message": "No active game"}
    from backend.game_logic.formations import build_formables_payload
    active_world = game_state["world"]
    payload = build_formables_payload(active_world)
    payload["success"] = True
    _attach_nation_identity_overrides(payload, active_world)
    return payload


# ════════════════════════════════════════════════════════════
# NOTIFICATION ENDPOINTS (Phase 6.5)
# ════════════════════════════════════════════════════════════

@app.post("/notifications/dismiss")
async def dismiss_notification(request: Request):
    """Dismiss a notification by ID, or dismiss all if id='all'."""
    data = await request.json()
    notification_id = data.get("id")
    if not notification_id:
        return {"success": False, "message": "Missing notification id"}
    # Non-draining (Aug 2026 health-check audit — the IGR-X7 family): the
    # client's dismiss callback is a discard lambda, so a default
    # build_base_response here POPPED the queued choice popup and destroyed
    # it. Dismissing a notification must never consume an unrelated popup.
    if notification_id == "all":
        count = world.notifications.dismiss_all()
        response = build_base_response(
            world, dismissed=int(count), include_popup_passthroughs=False)
        _fill_popup_keys_without_draining(response)
        return response
    dismissed = world.notifications.dismiss(notification_id)
    response = build_base_response(
        world, success=dismissed, dismissed=1 if dismissed else 0,
        include_popup_passthroughs=False)
    _fill_popup_keys_without_draining(response)
    return response


@app.get("/notifications")
def get_notifications():
    """Get all pending notifications."""
    if not game_state.get("world"):
        return {"success": False, "notifications": []}
    return {"notifications": world.notifications.get_pending()}


# ════════════════════════════════════════════════════════════
# DEBUG ENDPOINTS (Only available when DEBUG_MODE = True)
# ════════════════════════════════════════════════════════════

@app.post("/debug/set_trust")
async def debug_set_trust(request: Request):
    """
    DEBUG: Set marshal trust to specific value.

    Usage:
        POST /debug/set_trust
        Body: {"marshal": "Ney", "trust": 25}
    """
    if not DEBUG_MODE:
        return {"success": False, "message": "Debug mode is disabled"}

    data = await request.json()
    marshal_name = data.get("marshal")
    trust_value = data.get("trust")

    if marshal_name is None or trust_value is None:
        return {"success": False, "message": "Required: marshal, trust"}

    marshal = world.get_marshal(marshal_name)
    if not marshal:
        return {"success": False, "message": f"Unknown marshal: {marshal_name}"}

    old_trust = int(marshal.trust.value)
    marshal.trust.set(int(trust_value))

    print(f"[DEBUG] Set {marshal_name} trust: {old_trust} -> {marshal.trust.value}")

    return build_base_response(world,
        marshal=marshal_name,
        old_trust=old_trust,
        new_trust=int(marshal.trust.value),
        trust_label=marshal.trust.get_label())


@app.get("/debug/marshal_status/{marshal_name}")
def debug_marshal_status(marshal_name: str):
    """
    DEBUG: Get full marshal status including autonomy state.

    Usage:
        GET /debug/marshal_status/Ney
    """
    if not DEBUG_MODE:
        return {"success": False, "message": "Debug mode is disabled"}

    marshal = world.get_marshal(marshal_name)
    if not marshal:
        available = [m.name for m in world.get_player_marshals()]
        return {
            "success": False,
            "message": f"Unknown marshal: {marshal_name}",
            "available_marshals": available
        }

    return {
        "success": True,
        "name": marshal.name,
        "nation": marshal.nation,
        "location": marshal.location,
        "strength": int(marshal.strength),
        "morale": int(marshal.morale),
        "trust": int(marshal.trust.value) if hasattr(marshal, 'trust') else 70,
        "trust_label": marshal.trust.get_label() if hasattr(marshal, 'trust') else "Unknown",
        "vindication": int(getattr(marshal, 'vindication_score', 0)),
        "autonomous": getattr(marshal, 'autonomous', False),
        "autonomy_turns": getattr(marshal, 'autonomy_turns', 0),
        "personality": marshal.personality,
        "recent_overrides": list(getattr(marshal, 'recent_overrides', [])),
    }


@app.get("/debug/status")
def debug_status():
    """
    DEBUG: Get overall debug status and available commands.

    Usage:
        GET /debug/status
    """
    return {
        "debug_mode": DEBUG_MODE,
        "message": "Debug mode is " + ("ENABLED" if DEBUG_MODE else "DISABLED"),
        "available_endpoints": [
            "POST /debug/set_trust - Set marshal trust value",
            "GET /debug/marshal_status/{name} - Get full marshal status",
            "GET /debug/status - This endpoint",
            "GET /debug/trigger_redemption/{name} - Force redemption event",
            "POST /debug/set_authority - Set player authority level",
        ] if DEBUG_MODE else []
    }


@app.get("/debug/trigger_redemption/{marshal_name}")
def debug_trigger_redemption(marshal_name: str):
    """
    DEBUG: Force a redemption event by setting trust to critical.

    Usage:
        GET /debug/trigger_redemption/Ney
    """
    if not DEBUG_MODE:
        return {"success": False, "message": "Debug mode is disabled"}

    marshal = world.get_marshal(marshal_name)
    if not marshal:
        return {"success": False, "message": f"Unknown marshal: {marshal_name}"}

    old_trust = int(marshal.trust.value)
    marshal.trust.set(15)  # Set to critical level

    # Create redemption event
    redemption_event = world.disobedience_system._create_redemption_event(marshal)
    world.pending_redemption = redemption_event

    print(f"[DEBUG] Triggered redemption for {marshal_name} (trust: {old_trust} -> 15)")

    return {
        "success": True,
        "marshal": marshal_name,
        "old_trust": old_trust,
        "new_trust": 15,
        "redemption_event": redemption_event,
        "message": f"Redemption event triggered for {marshal_name}. Use /respond_to_redemption to resolve."
    }


@app.post("/debug/set_authority")
async def debug_set_authority(request: Request):
    """
    DEBUG: Set player authority level.

    Usage:
        POST /debug/set_authority
        Body: {"authority": 50}
    """
    if not DEBUG_MODE:
        return {"success": False, "message": "Debug mode is disabled"}

    data = await request.json()
    authority_value = data.get("authority")

    if authority_value is None:
        return {"success": False, "message": "Required: authority"}

    old_authority = int(world.authority_tracker.authority)
    world.authority_tracker.authority = max(0, min(100, int(authority_value)))

    print(f"[DEBUG] Set authority: {old_authority} -> {world.authority_tracker.authority}")

    return build_base_response(world,
        old_authority=old_authority,
        new_authority=int(world.authority_tracker.authority),
        authority_label=world.authority_tracker.get_authority_label())


# ════════════════════════════════════════════════════════════
# DIPLOMATIC DEBUG ENDPOINTS (Session 8A)
# ════════════════════════════════════════════════════════════

@app.get("/debug/diplomatic_status")
def debug_diplomatic_status():
    """DEBUG: Full diplomatic snapshot — states, relations, treaties, vassals, DP, Talleyrand."""
    if not DEBUG_MODE:
        return {"success": False, "message": "Debug mode is disabled"}

    # Serialize tuple-keyed dicts as "A_B" strings
    diplomatic_states = {k: v for k, v in world.diplomatic_states.items()}
    nation_relations = {k: int(v) for k, v in world.nation_relations.items()}
    active_treaties = {}
    for k, v in getattr(world, 'active_treaties', {}).items():
        active_treaties[k] = v.copy() if isinstance(v, dict) else v

    vassals = {}
    for k, v in getattr(world, 'vassals', {}).items():
        vassals[k] = v.copy() if isinstance(v, dict) else v

    diplomats_data = {}
    for k, v in getattr(world, 'diplomats', {}).items():
        diplomats_data[k] = v.to_dict() if hasattr(v, 'to_dict') else str(v)

    # R7: Add display-friendly state names
    from backend.display_names import STATE_DISPLAY
    diplomatic_states_display = {k: STATE_DISPLAY.get(v, v) for k, v in diplomatic_states.items()}

    return {
        "success": True,
        "diplomatic_states": diplomatic_states,
        "diplomatic_states_display": diplomatic_states_display,
        "nation_relations": nation_relations,
        "active_treaties": active_treaties,
        "vassals": vassals,
        "diplomatic_points": int(getattr(world, 'diplomatic_points', 0)),
        "max_diplomatic_points": _dp_ceiling(world),
        "talleyrand": diplomats_data.get(get_player_nation(world), {}),
    }


@app.get("/debug/war_scores")
def debug_war_scores():
    """DEBUG: Per nation-pair war score with component breakdown."""
    if not DEBUG_MODE:
        return {"success": False, "message": "Debug mode is disabled"}

    from backend.game_logic.diplomacy import calculate_war_score
    scores = []
    for diplo_key, state in world.diplomatic_states.items():
        if state == "WAR":
            parts = diplo_key.split("|")
            if len(parts) == 2:
                components = calculate_war_score(parts[0], parts[1], world, return_components=True)
                scores.append({
                    "nation_a": parts[0],
                    "nation_b": parts[1],
                    "components": components,
                    "total": components["total"],
                })

    return {"success": True, "war_scores": scores}


@app.post("/debug/acceptance_preview")
async def debug_acceptance_preview(request: Request):
    """DEBUG: Run acceptance formula on a proposal body."""
    if not DEBUG_MODE:
        return {"success": False, "message": "Debug mode is disabled"}

    data = await request.json()
    proposal = data.get("proposal", {})
    if not proposal:
        return {"success": False, "message": "No proposal provided."}

    from backend.game_logic.diplomacy import calculate_acceptance
    result = calculate_acceptance(proposal, world)
    return {"success": True, "acceptance": result}


@app.get("/debug/coalition_status")
def debug_coalition_status():
    """DEBUG: Coalition threat, brewing, active coalition snapshot."""
    if not DEBUG_MODE:
        return {"success": False, "message": "Debug mode is disabled"}

    from backend.game_logic.coalition import get_qualifying_nations
    qualifying = get_qualifying_nations(world)

    threat = int(getattr(world, 'threat_level', 0))
    if threat >= 80:
        tier = "CRITICAL"
    elif threat >= 60:
        tier = "HIGH"
    elif threat >= 30:
        tier = "MODERATE"
    else:
        tier = "LOW"

    brewing = getattr(world, 'coalition_brewing', None)
    coalition = getattr(world, 'active_coalition', None)

    return {
        "success": True,
        "threat_level": threat,
        "threat_tier": tier,
        "brewing": brewing is not None,
        "brewing_turns": int(brewing.get("turns_remaining", 0)) if brewing else None,
        "qualifying_nations": qualifying,
        "active_coalition": coalition.copy() if coalition else None,
    }


@app.get("/debug/threat_sources")
def debug_threat_sources():
    """DEBUG: Threat sources this turn."""
    if not DEBUG_MODE:
        return {"success": False, "message": "Debug mode is disabled"}

    return {
        "success": True,
        "threat_sources_this_turn": list(getattr(world, 'threat_sources_this_turn', [])),
    }


@app.get("/debug/proposal_cooldowns")
def debug_proposal_cooldowns():
    """DEBUG: AI and player proposal cooldowns."""
    if not DEBUG_MODE:
        return {"success": False, "message": "Debug mode is disabled"}

    return {
        "success": True,
        "ai_proposal_cooldowns": dict(getattr(world, 'ai_proposal_cooldowns', {})),
        "player_proposal_cooldowns": dict(getattr(world, 'player_proposal_cooldowns', {})),
    }


@app.get("/debug/vassal_loyalty/{nation}")
def debug_vassal_loyalty(nation: str):
    """DEBUG: Vassal loyalty value + per-modifier breakdown."""
    if not DEBUG_MODE:
        return {"success": False, "message": "Debug mode is disabled"}

    if nation not in getattr(world, 'vassals', {}):
        return {"success": False, "message": f"{nation} is not a vassal."}

    state = world.vassals[nation]
    lord = state["lord"]
    loyalty = int(state["loyalty"])

    # Compute modifiers to match vassal.py process_vassal_loyalty. F7
    # (playtest): the old breakdown reported only 4 of the ~7 contributors —
    # it dropped both the lord's battle-results term AND the VS-R imperial-grip
    # term, so the displayed mods never summed to the real per-turn delta.
    from backend.game_logic.vassal import AUTONOMY_DRIFT
    from backend.models.authority import get_imperial_grip, authority_vassal_drift

    autonomy = state.get("autonomy", 1)
    drift = AUTONOMY_DRIFT.get(autonomy, 0)

    # Garrison term (VP-D1 wired July 16, 2026): presence-based flat +2 via
    # the SAME single-source predicate the loyalty pipeline uses (F7 lesson).
    from backend.game_logic.vassal import GARRISON_LOYALTY_BONUS, lord_garrison_present
    garrison_bonus = 0
    vassal_capital = world.get_nation_capital(nation)
    if vassal_capital and lord_garrison_present(world, lord, vassal_capital):
        garrison_bonus = GARRISON_LOYALTY_BONUS

    shared_enemy_bonus = 0
    all_nations = set(getattr(world, "enemy_nations", []))
    all_nations.update(world.get_active_nations())
    all_nations.update({lord, nation})
    for other_nation in sorted(all_nations):
        if other_nation == lord or other_nation == nation:
            continue
        lord_state = world.get_diplomatic_state(lord, other_nation)
        vassal_state_diplo = world.get_diplomatic_state(nation, other_nation)
        if lord_state == "WAR" and vassal_state_diplo == "WAR":
            shared_enemy_bonus += 2

    # Lord's battle results this turn (process_vassal_loyalty step 5).
    wins = losses = 0
    for battle in getattr(world, 'battles_this_turn', []):
        result = (battle.get("result", "") or "").lower()
        atk = world.get_marshal(battle.get("attacker", ""))
        dfn = world.get_marshal(battle.get("defender", ""))
        atk_nation = getattr(atk, 'nation', '') if atk else ''
        def_nation = getattr(dfn, 'nation', '') if dfn else ''
        if atk_nation != lord and def_nation != lord:
            continue
        if "attacker" in result and "victory" in result:
            winner = atk_nation
        elif "defender" in result and "victory" in result:
            winner = def_nation
        else:
            continue
        if winner == lord:
            wins += 1
        else:
            losses += 1
    lord_battle_modifier = min(wins, 3) - min(losses, 3) * 2

    diplo_key = world._make_diplo_key(nation, lord)
    relation = world.nation_relations.get(diplo_key, 0)
    relation_modifier = relation // 20

    grip = get_imperial_grip(world, lord)
    grip_drift = authority_vassal_drift(grip)

    return {
        "success": True,
        "nation": nation,
        "loyalty": loyalty,
        "lord": lord,
        "imperial_grip": int(grip),
        # NOTE: excludes the rare gold-investment-treaty term (step 3), 0 unless
        # an active treaty clause funds the vassal.
        "modifiers": {
            "autonomy_drift": drift,
            "garrison_bonus": garrison_bonus,
            "shared_enemy_bonus": shared_enemy_bonus,
            "lord_battle_modifier": lord_battle_modifier,
            "relation_modifier": relation_modifier,
            "imperial_grip_drift": grip_drift,
        },
    }


@app.get("/debug/proposal_queue")
def debug_proposal_queue():
    """DEBUG: Mailbox items (replaces old diplomatic_queue debug)."""
    if not DEBUG_MODE:
        return {"success": False, "message": "Debug mode is disabled"}

    world = game_state["world"]
    dm = world.dialogue_manager
    return {
        "success": True,
        "mailbox_items": dm.get_mailbox_items(),
        "mailbox_count": int(dm.get_mailbox_count()),
        "dialogue_manager": dm.to_dict(),
    }


if __name__ == "__main__":
    import uvicorn

    # SOVEREIGN_PORT (Aug 2026 test-harness pass): lets a SECOND backend run
    # beside the player's live session on 8005 — the CA9 audit had to skip
    # its visual half because the client and the driver fought over one
    # port. Default stays 8005 (Golden Rule 7); the Godot side reads the
    # same env var through Utils.backend_url().
    _port = int(os.getenv("SOVEREIGN_PORT", "8005"))

    print("=" * 60)
    print("[*] GAME INITIALIZED")
    print(f"[*] DEBUG MODE: {'ENABLED' if DEBUG_MODE else 'DISABLED'}")
    print("=" * 60)
    print(f"Turn: {world.current_turn}")
    print(f"Actions: {world.actions_remaining}/{world.max_actions_per_turn}")
    print(f"Gold: {world.gold}")
    print(f"Regions: {len(world.get_player_regions())}")
    print("=" * 60)
    print(f"[*] Server: http://127.0.0.1:{_port}")
    print(f"[*] API Docs: http://127.0.0.1:{_port}/docs")
    print("=" * 60)

    uvicorn.run(app, host="127.0.0.1", port=_port)
