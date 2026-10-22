"""The enemy phase as the player SEES it — the fog filter over the actions
the enemy AI took (Fog of War, Session 34B), lifted out of `backend/main.py`
verbatim by RR6-X3 (Pre-Deploy S14b's head, October 21, 2026).

It lived in the response layer because only the client's dialog read it. Now
the end turn reads it too: what the dialog SHOWS is what the player saw, and
`intel_surfaces.record_shown_sightings` writes each shown actor's sighting
into the intel store before the morning dispatch and the autosave are built
(`meta_executor._execute_end_turn`). One predicate for both — the dialog and
the store can never disagree about what was shown. `backend/main.py` keeps
its old names as aliases (`_filter_enemy_phase_by_visibility`,
`_own_soil_event_types`), and its response builder still calls them.
"""
from backend.models.intel import FULL

# FA-23 (slice 11): an enemy assault on the player's own garrison is
# reported through the fog (the own-soil arm of the visibility filter).
# FA-N66 (slice 17, Sept 11 2026): `occupation_started` joins the arm below.
# Both producers (the post-garrison twin and the unopposed march inside
# `_execute_attack`) emit a `region` and no ownership key, and the province
# IS still the player's when it fires (the siege has not completed) — so an
# enemy beginning a siege on a French province at PARTIAL was dropped and the
# court read as 'beyond our sight'. Measured on the boot: 0 kept vs 1 for a
# `garrison_assault` on the same province.


def own_soil_event_types() -> tuple:
    """The event types whose `region` is read against the player's soil."""
    types = ("garrison_assault", "garrison_destroyed")
    types += ("occupation_started",)
    return types


def filter_enemy_phase_by_visibility(enemy_phase: dict, world_state) -> dict:
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

            # ── FA-23 (slice 11): an ASSAULT ON OUR OWN GARRISON ───────
            # The same shape one step further in. A garrison assault has no
            # marshal on the defending side, so the battle arm above never
            # matched it, and the region gate below keys on the ASSAULTER's
            # province — which for the ordinary P4.25 rung is enemy ground
            # at PARTIAL. Measured: a French detachment at Rhineland cut
            # from 8,000 to 4,000 by Mack, `total_actions` 1 before the
            # filter and 0 after. The assault itself lights the ASSAULTED
            # province FULL (`update_intel_from_battle`), so the province
            # France is being attacked in was fully visible while the
            # report of the attack was suppressed.
            #
            # It leaks nothing the payload does not already carry: the
            # garrison figure the player owns has changed, and the region
            # is his.
            if (not involves_player and isinstance(events, list)):
                for evt in events:
                    if not isinstance(evt, dict):
                        continue
                    if evt.get("type") not in own_soil_event_types():
                        continue
                    _assaulted = str(evt.get("region")
                                     or evt.get("defender_location") or "")
                    _region = world_state.regions.get(_assaulted)
                    if _region is not None and _region.controller == player_nation:
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


def shown_enemy_phase(enemy_phase, world_state):
    """The shown phase of a RAW enemy-phase result (the actions still carry
    `new_state`, which the filter never reads) — None when there was none."""
    if not enemy_phase or not enemy_phase.get("nations"):
        return None
    return filter_enemy_phase_by_visibility(enemy_phase, world_state)
