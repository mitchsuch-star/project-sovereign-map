"""
Naval Executor — the Wooden Wall's four verbs (DEF-5, docs/NAVAL_SPEC.md §9)

build_fleet · set_fleet_posture · naval_expedition · naval_diversion.
Thin adapters over backend/game_logic/naval.py (the vassal_executor idiom):
resolve args, validate through the SAME functions every surface quotes
(shown = applied), charge gold in-executor, return result dicts. The AI
rides the same verbs with `_acting_nation` (GR5).
"""
import re
from typing import Dict, Optional

from backend.game_logic import naval


class NavalExecutor:
    """Handles the four naval commands."""

    def __init__(self, parent_executor):
        self._executor = parent_executor

    # ──────────────────────────────────────────────────────────────────
    # build_fleet — 1 admin AP + SHIP_COST gold lays down ONE ship
    # ──────────────────────────────────────────────────────────────────

    def _execute_build_fleet(self, command: Dict, game_state: Dict) -> Dict:
        """Lay down one ship of the line (N2: 400g + 1 admin AP; national
        rate cap 2/turn, 1 under blockade — the §3.5 three brakes)."""
        world = game_state.get("world")
        if not world:
            return {"success": False, "message": "No active game."}
        actor = command.get("_acting_nation") or getattr(world, 'player_nation', 'France')

        if not naval.has_naval_layer(world):
            return {"success": False, "message": (
                "This campaign has no naval theatre — the fleets of Europe "
                "are not in play on this map.")}
        refusal = naval.check_build_fleet(world, actor)
        if refusal:
            return {"success": False, "message": refusal}
        treasury = int(world.nation_gold.get(actor, 0))
        if treasury < naval.SHIP_COST:
            return {"success": False, "message": (
                f"A ship of the line costs {naval.SHIP_COST}g — the treasury "
                f"holds {treasury}g.")}

        world.nation_gold[actor] = int(treasury - naval.SHIP_COST)
        outcome = naval.lay_down_ship(world, actor)
        rec = naval.get_fleet(world, actor) or {}
        yards = naval.controlled_dockyards(world, actor)
        rate = naval.build_rate(world, actor)
        laid = int(rec.get("built_this_turn", 0) or 0)
        world.log_event({
            "type": "fleet_laid_down", "turn": int(world.current_turn),
            "nation": actor, "ships": int(outcome["ships"]),
            "readiness": int(outcome["readiness"]),
        })
        result = {
            "success": True,
            "message": (
                f"A keel is laid at {yards[0]} ({naval.SHIP_COST}g). The fleet "
                f"stands at {outcome['ships']} sail — readiness "
                f"{outcome['readiness']} (new crews come aboard green at "
                f"{naval.NEW_SHIP_READINESS}; only sea-time makes a navy). "
                f"{rate - laid} more keel{'s' if rate - laid != 1 else ''} "
                f"possible this turn."),
            "ships": int(outcome["ships"]),
            "readiness": int(outcome["readiness"]),
            "events": [{"type": "fleet_laid_down", "nation": actor}],
        }
        result["new_state"] = game_state
        return result

    # ──────────────────────────────────────────────────────────────────
    # set_fleet_posture — guard | blockade (untargeted, v1.0.3)
    # ──────────────────────────────────────────────────────────────────

    def _execute_set_fleet_posture(self, command: Dict, game_state: Dict) -> Dict:
        world = game_state.get("world")
        if not world:
            return {"success": False, "message": "No active game."}
        actor = command.get("_acting_nation") or getattr(world, 'player_nation', 'France')

        rec = naval.get_fleet(world, actor)
        if not rec or int(rec.get("ships", 0) or 0) <= 0:
            return {"success": False,
                    "message": "We have no fleet to give orders to, Sire."}

        # Structured field first (GR5 — the AI/wizard never synthesizes
        # English), then the raw text.
        posture = (command.get("posture") or "").strip().lower()
        if posture not in naval.POSTURES:
            raw = (command.get("raw_input") or command.get("original_command")
                   or command.get("raw_command") or "").lower()
            if "blockade" in raw or "close the ports" in raw:
                posture = "blockade"
            elif ("guard" in raw or "home waters" in raw or "recall" in raw
                  or "defend" in raw):
                posture = "guard"
        if posture not in naval.POSTURES:
            return {"success": False, "message": (
                "Give the Admiralty a posture, Sire: 'blockade the enemy' "
                "(close every at-war enemy's ports) or 'guard home waters'.")}

        previous = rec.get("posture", "guard")
        rec["posture"] = posture
        at_war = [n for n in world.get_nations_at_war_with(actor)
                  if naval.get_fleet(world, n) is not None]
        if posture == "blockade":
            covered = ", ".join(sorted(at_war)) if at_war else "no one — we are at peace"
            message = (
                f"The fleet stands out to sea on blockade. Every port of every "
                f"enemy is watched at once (currently: {covered}) — their "
                f"crews rot at anchor while ours drill. Our own coasts go "
                f"unguarded.")
        else:
            message = (
                "The fleet returns to home waters on guard — every crossing "
                "touching our own coast is covered. Blockade pressure on the "
                "enemy is lifted, and their crews will begin to recover.")
        if previous == posture:
            message = f"The fleet already holds that station. {message}"
        world.log_event({
            "type": "fleet_posture", "turn": int(world.current_turn),
            "nation": actor, "posture": posture,
        })
        result = {"success": True, "message": message, "posture": posture,
                  "events": [{"type": "fleet_posture", "nation": actor,
                              "posture": posture}]}
        result["new_state"] = game_state
        return result

    # ──────────────────────────────────────────────────────────────────
    # naval_expedition — the H4 gamble (§4.3), odds quoted then confirmed
    # ──────────────────────────────────────────────────────────────────

    def _execute_naval_expedition(self, command: Dict, game_state: Dict) -> Dict:
        world = game_state.get("world")
        if not world:
            return {"success": False, "message": "No active game."}

        marshal_name = (command.get("marshal") or "").strip()
        marshal = world.get_marshal(marshal_name) if marshal_name else None
        if not marshal or marshal.nation != (
                command.get("_acting_nation")
                or getattr(world, 'player_nation', 'France')):
            return {"success": False, "message": (
                "Name the marshal who is to embark, Sire — 'land Soult in "
                "Munster'.")}
        if not naval.has_naval_layer(world):
            return {"success": False, "message": (
                "This campaign has no naval theatre — there are no "
                "transports to be had.")}

        target = self._resolve_expedition_target(command, world, marshal)
        if isinstance(target, dict):
            return target  # refusal dict from the resolver
        target_region = world.regions.get(target)

        # Embarkation: from home soil the expedition assembles at a yard we
        # control; from ABROAD (the beachhead return — §4.3 "the same verb
        # from the beachhead") any coastal shore serves, the transports
        # taking the corps off the beach.
        location = marshal.location
        loc_region = world.regions.get(location)
        loc_controller = getattr(loc_region, "controller", None)
        yards = naval.controlled_dockyards(world, marshal.nation)
        if loc_controller == marshal.nation and location not in yards:
            if yards:
                return {"success": False, "message": (
                    f"An expedition assembles at a dockyard, Sire — "
                    f"{marshal.name} must stand at one of our yards: "
                    f"{', '.join(yards)}.")}
            return {"success": False, "message": (
                "We control no dockyard from which to embark an expedition.")}
        if (loc_controller != marshal.nation
                and not getattr(loc_region, "is_coastal", False)):
            return {"success": False, "message": (
                f"{marshal.name} stands inland at {location} — the boats "
                "cannot reach him. March to the coast first.")}

        troops = int(marshal.strength)
        if troops <= 0:
            return {"success": False,
                    "message": f"{marshal.name} commands no troops."}
        if troops > naval.EXPEDITION_MAX_TROOPS:
            return {"success": False, "message": (
                f"The transports can lift {naval.EXPEDITION_MAX_TROOPS:,} "
                f"men; {marshal.name} commands {troops:,}. Detach the excess "
                f"first ('{marshal.name}, garrison "
                f"{troops - naval.EXPEDITION_MAX_TROOPS:,} men here') — small "
                "expeditions slip past, armies do not.")}

        quote = naval.expedition_slip_odds(world, marshal.nation, target, troops)

        raw = (command.get("raw_input") or command.get("original_command")
               or command.get("raw_command") or "").lower()
        confirmed = bool(command.get("confirmed")) or bool(
            re.search(r'\bconfirm(ed)?\b|\bset sail\b', raw))
        if not confirmed:
            # Two-step confirm on the EXISTING command_clarification channel
            # (no new dialogue type — §8): the option reissues a full
            # deterministic command string.
            reissue = f"land {marshal.name} in {target} confirmed"
            odds_line = (
                f"The transports slip past unseen {quote['odds']} times in "
                f"100" if quote["coverer"] else
                "No hostile fleet patrols these waters — the passage is "
                "unopposed")
            coverer_line = ""
            if quote["coverer"]:
                coverer_line = (
                    f" ({quote['coverer']} watches at {quote['coverage']:.0f} "
                    f"effective against our escort"
                    f"{' — the Strait window is open' if quote['window'] else ''})")
            return {
                "success": True,
                "free_action": True,
                "state": "awaiting_clarification",
                "type": "clarification",
                "naval_confirm": True,
                "marshal": marshal.name,
                "original_command": command.get("raw_command", ""),
                "message": (
                    f"The expedition is drawn up, Sire: {marshal.name} with "
                    f"{troops:,} men, {location} to {target}. {odds_line}"
                    f"{coverer_line}. On a failed run the corps is turned "
                    f"back with losses — or brought to battle at sea. "
                    f"Sail? (yes / no)"),
                "interpreted_target": target,
                "options": [
                    {"label": f"Sail for {target}", "command": reissue,
                     "target": target,
                     "aliases": ["sail", "set sail", "embark", "go"]},
                    {"label": "Stand down", "command": "cancel",
                     "aliases": ["stand down", "no"]},
                ],
                "action_summary": world.get_action_summary(),
                "game_state": world.get_filtered_game_state_summary(),
            }

        # Confirmed: resolve now (shown = applied — same quote function).
        outcome = naval.resolve_expedition(world, marshal, target)
        if outcome["landed"]:
            message = (
                f"THE LANDING: {marshal.name} slips past "
                f"{'the ' + outcome['coverer'] + ' patrols' if outcome['coverer'] else 'the empty sea'}"
                f" and puts {troops:,} men ashore at {target} "
                f"(odds were {outcome['odds']} in 100).")
            capture = None
            controller = getattr(target_region, "controller", None)
            if controller and controller != marshal.nation and world.is_at_war(
                    marshal.nation, controller):
                defenders = [m for m in world.get_marshals_in_region(target)
                             if m.nation != marshal.nation and m.strength > 0]
                if not defenders:
                    # The existing land game takes over (§4.3): undefended
                    # soil falls through the SAME capture pipeline every
                    # march uses (capture-choice, estates, EC-W1 — all free).
                    capture = self._executor._combat._attempt_region_capture(
                        marshal, target, world, game_state)
                else:
                    message += (
                        f" Enemy forces under {defenders[0].name} hold the "
                        f"country — the beachhead is contested.")
            result = {"success": True, "message": message,
                      "landed": True, "odds": int(outcome["odds"]),
                      "events": [{"type": "expedition_landed",
                                  "marshal": marshal.name, "target": target}]}
            if isinstance(capture, dict):
                for key in ("capture_choice", "capture_message", "region_captured"):
                    if capture.get(key) is not None:
                        result[key] = capture[key]
                if capture.get("message"):
                    result["message"] = message + " " + str(capture["message"])
        elif outcome["intercepted"]:
            action = outcome.get("fleet_action")
            sea_line = ""
            if action:
                sea_line = (
                    f" The escorting fleet is brought to action and "
                    f"{'beaten decisively' if action['loser'] == marshal.nation and action['decisive'] else 'engaged'}"
                    f" — {int(sum(action['losses'].get(marshal.nation, {}).values()))} sail lost.")
            result = {
                "success": True, "landed": False, "odds": int(outcome["odds"]),
                "message": (
                    f"INTERCEPTED AT SEA: the {outcome['coverer']} squadrons "
                    f"catch the transports off {target}. {marshal.name} loses "
                    f"{outcome['troops_lost']:,} men to the guns and the water "
                    f"before the convoy scatters home.{sea_line}"),
                "events": [{"type": "expedition_intercepted",
                            "marshal": marshal.name, "target": target}]}
            # NV-7: the escort was brought to action — the player watches it.
            if action and action.get("naval_diorama"):
                result["naval_diorama"] = action["naval_diorama"]
        else:
            result = {
                "success": True, "landed": False, "odds": int(outcome["odds"]),
                "message": (
                    f"TURNED BACK: the weather and the patrols close the "
                    f"passage to {target}. {marshal.name} returns to "
                    f"{marshal.location} minus {outcome['troops_lost']:,} "
                    f"men; the fleet's readiness suffers for the scramble."),
                "events": [{"type": "expedition_turned_back",
                            "marshal": marshal.name, "target": target}]}
        result["new_state"] = game_state
        return result

    def _resolve_expedition_target(self, command: Dict, world, marshal):
        """Resolve the landing target from the structured field or raw text
        (the vassal_executor region-scan idiom). Returns the region NAME or
        a refusal dict."""
        target = (command.get("region") or command.get("target") or "").strip()
        if target and target in world.regions:
            name = target
        else:
            raw = (command.get("raw_input") or command.get("original_command")
                   or command.get("raw_command") or "").lower()
            best = ""
            for region_name in world.regions:
                pattern = rf'(?<![a-z]){re.escape(region_name.lower())}(?![a-z])'
                if re.search(pattern, raw) and len(region_name) > len(best):
                    best = region_name
            if not best and target:
                # Fuzzy fall-through: the executor's matcher for typo'd names
                match = self._executor.fuzzy_matcher.match(
                    target, list(world.regions.keys()))
                if match:
                    best = match[0]
            name = best
        if not name:
            return {"success": False, "message": (
                "Name the landing, Sire — 'land Soult in Munster with the "
                "transports'.")}
        if name == marshal.location:
            return {"success": False, "message":
                    f"{marshal.name} already stands at {name}."}
        region = world.regions.get(name)
        if not getattr(region, "is_coastal", False):
            return {"success": False, "message": (
                f"{name} has no shore to land on — the expedition must make "
                "for a coastal province.")}
        adjacent = name in (world.regions.get(marshal.location).adjacent_regions
                            if world.regions.get(marshal.location) else [])
        if adjacent and not naval.is_sea_link(world, marshal.location, name):
            return {"success": False, "message": (
                f"{name} lies adjacent by land — march there; the fleet is "
                "for crossings the army cannot make.")}
        # NV-4 review (Aug 2, 2026) — THE CONSENT GATE. The land game asks
        # a neutral's leave before an army enters; the sea game did not,
        # so an expedition could put a corps on ANY neutral's coast with
        # no diplomacy at all — the neutrality-bypass hole. The rule is
        # the SAME predicate the AI's own targeting already used (GR5,
        # single source): our own soil is a sealift, an at-war shore is
        # the verb's whole point, and anyone else must actually RECEIVE
        # us — an ally, a vassal, or a court at
        # AI_EXPEDITION_HOST_RELATION or better (Portugal, 1808).
        holder = getattr(region, "controller", None)
        if (holder and holder != marshal.nation
                and not world.is_at_war(marshal.nation, holder)
                and not naval.is_expedition_host(world, marshal.nation, holder)):
            from backend.display_names import display_nation
            return {"success": False, "message": (
                f"{display_nation(holder)} has not opened her ports to our "
                f"army, Sire — a court receives an expedition only as a "
                f"friend (relation {naval.AI_EXPEDITION_HOST_RELATION} or "
                f"better), an ally, or a vassal. Court them first, or make "
                f"it war.")}
        return name

    # ──────────────────────────────────────────────────────────────────
    # naval_diversion — the Grand Diversion (§5.3.3a), once per war
    # ──────────────────────────────────────────────────────────────────

    def _execute_naval_diversion(self, command: Dict, game_state: Dict) -> Dict:
        world = game_state.get("world")
        if not world:
            return {"success": False, "message": "No active game."}
        actor = command.get("_acting_nation") or getattr(world, 'player_nation', 'France')
        if not naval.has_naval_layer(world):
            return {"success": False, "message": (
                "This campaign has no naval theatre, Sire.")}
        outcome = naval.resolve_diversion(world, actor)
        result = dict(outcome)
        if outcome.get("success"):
            result["events"] = [{"type": "naval_diversion", "nation": actor,
                                 "window": bool(outcome.get("window"))}]
            result["new_state"] = game_state
        return result
