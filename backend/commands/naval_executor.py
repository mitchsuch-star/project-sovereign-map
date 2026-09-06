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


# FA slice 7 (FA-N9 / FA-N24 — FA-11's optional half): the marshal-free
# naval verbs REFUSE an order addressed to a marshal in the field rather
# than discarding him — "Ney, lay down a ship" used to lay the keel and
# forget Ney. The posture verb already carried this arm; now all three do.
ADMIRALTY_REFUSES_AN_ADDRESSED_MARSHAL = True


def _admiralty_misaddressed(command: Dict, world, actor: str, example: str):
    if not ADMIRALTY_REFUSES_AN_ADDRESSED_MARSHAL:
        return None
    if actor != getattr(world, "player_nation", "France"):
        return None  # the AI's rungs never carry a marshal
    name = command.get("marshal")
    if not name:
        return None
    # Review round (R2-13): the posture verb refuses on ANY bound marshal;
    # so do these two now — one predicate, not two.
    marshal = (getattr(world, "marshals", {}) or {}).get(name)
    from backend.display_names import humanize_entity_name
    shown = humanize_entity_name(marshal.name if marshal is not None else str(name))
    return {"success": False, "variable_action_cost": 0, "message": (
        f"The Admiralty takes its orders from the Emperor, Sire, not from "
        f"Marshal {shown} in the field. Say '{example}'.")}


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
        misaddressed = _admiralty_misaddressed(
            command, world, actor, "lay down a ship of the line")
        if misaddressed:
            return misaddressed
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
        #
        # ⚠ FA-11, measured: the structured branch is production-DEAD.
        # `posture` is absent from `providers.PARSE_TOOL`, no mock, live, AI
        # or chip producer writes it, and the only writers in the repo are
        # tests — so the raw-text derivation below is not a fallback, it is
        # the whole implementation, and it used to be two bare substring
        # tests. The door stays open for the wizard and the AI; what changed
        # is that the English behind it goes through ONE pure rule
        # (`naval.derive_posture`) instead of `"blockade" in raw`.
        posture = (command.get("posture") or "").strip().lower()
        raw = (command.get("raw_input") or command.get("original_command")
               or command.get("raw_command") or "")
        derived_from_english = False
        # An EMPTY command carries no English to judge — it is the bare
        # `set_fleet_posture` the wizard and the Admiralty chips send when no
        # posture was named, and its answer is the prompt at the bottom of
        # this block, not a lecture about reports.
        if posture not in naval.POSTURES and raw.strip():
            derived_from_english = True
            # (a) THE ORDER MUST BE ADDRESSED TO THE ADMIRALTY. An addressed
            # marshal, or a target that names a province or a marshal, means
            # the player is investing a city, not putting the fleet to sea —
            # `Ney, blockade Vienna` and `Ney, blockade Mack` both stood the
            # fleet out on blockade and charged for it. MEMBERSHIP, never
            # truthiness: `blockade Britain` and `guard home waters` must
            # survive, and neither is a region or a marshal.
            target = command.get("target")
            regions = getattr(world, "regions", {}) or {}
            marshals = getattr(world, "marshals", {}) or {}
            misaddressed = command.get("marshal") or (
                isinstance(target, str)
                and (target in regions or target in marshals))
            # (b) A REPORT IS NOT AN ORDER. The only guard that catches the
            # class carrying neither a marshal nor a province.
            if misaddressed:
                return {"success": False, "message": (
                    "The Admiralty takes its orders from the Emperor, Sire, "
                    "not from a marshal in the field — and a fleet cannot "
                    "invest a city. Say 'blockade the enemy' or 'guard home "
                    "waters'; to invest a place, march on it.")}
            if not naval.sentence_is_an_order(raw):
                return {"success": False, "message": (
                    "I have noted it, Sire, but that is intelligence, not an "
                    "order — nothing has gone to the Admiralty. To move the "
                    "fleet, say 'blockade the enemy' or 'guard home "
                    "waters'.")}
            posture = naval.derive_posture(raw) or ""
        if posture not in naval.POSTURES:
            return {"success": False, "message": (
                "Give the Admiralty a posture, Sire: 'blockade the enemy' "
                "(close the ports of every at-war enemy our sail can "
                "outmatch) or 'guard home waters'.")}

        previous = rec.get("posture", "guard")
        # (c) IDEMPOTENCE, on the TYPED path. Without it the row's own
        # behaviour test cannot pass: `lift the blockade` from a fleet
        # already guarding used to prepend "The fleet already holds that
        # station." and still charge 1 AP — a paid no-op, and the inversion
        # fix would have created a second one.
        #
        # Scoped to English deliberately. The structured field is the
        # AI/wizard door, where a redundant posture is the caller's own
        # decision, made without a sentence to misread; refusing it there
        # would change AI behaviour this row did not measure, and it reds a
        # WO-slice-6 pin that drives guard->guard structurally to read the
        # order's copy.
        if derived_from_english and posture == previous:
            return {"success": False, "message": (
                f"The fleet already lies at {previous}, Sire — no signal is "
                f"needed and none has been sent.")}
        # ── Who is ACTUALLY released, measured across the flip ──────────
        # Release is a MEMBERSHIP question, not an ownership one: a court a
        # second power also pins stays pinned when we stand down. The first
        # cut asked `blockade_forecast` (what OUR blockade meets the ratio
        # against) and so announced releasing a Russia that Britain was
        # also closing — measured, with her trade loss and her readiness
        # rot both continuing.
        #
        # It also recorded a FALSE reason for reading before the write. The
        # forecast is invariant to our own posture — `combined_effective`
        # adds our own strength unconditionally and `match_posture` filters
        # partners only — so the `previous == "blockade"` test was the
        # entire safeguard. The before/after difference below needs the
        # pre-read for a real reason: it is a set difference.
        _pinned_before = set(naval.blockaded_nations(world))
        rec["posture"] = posture
        _was_closing = sorted(_pinned_before
                              - set(naval.blockaded_nations(world)))
        if posture == "blockade":
            # ── WO-14 (row WO slice 6): the order states what it DOES ────
            # It used to name every at-war court with a `navies` row and
            # promise all of them pinned. Measured on the 1805 boot it
            # named "Austria, Britain, Russia" and Britain is unpinnable by
            # anyone on that board — 125.0 needed against France's 31.5.
            # The set now comes from `naval.blockade_forecast`, the same
            # source the Admiralty chip reads, computed AFTER the posture
            # write above so it is a present fact and not a forecast.
            #
            # The drill claim is gone rather than reworded: it was inverted
            # three ways at once (see `blockade_forecast`) — the fleet that
            # rots at the boot is OURS.
            at_war = [n for n in world.get_nations_at_war_with(actor)
                      if naval.get_fleet(world, n) is not None]
            if not at_war:
                message = ("The fleet stands out to sea on blockade. There "
                           "is no enemy at sea to close — we are at peace. "
                           "Our own coasts go unguarded.")
            else:
                message = (
                    "The fleet stands out to sea on blockade. "
                    + naval.blockade_forecast_sentence(world, actor)
                    + " Our own coasts go unguarded.")
        else:
            # The mirror falsity: "pressure is lifted" was unconditional,
            # so a fleet that had pinned nobody announced relieving a siege
            # it never laid.
            message = (
                "The fleet returns to home waters on guard — every crossing "
                "touching our own coast is covered."
                + (" " + naval.release_clause(world, _was_closing)
                   if _was_closing else
                   " No blockade pressure is lifted; we were closing no "
                   "enemy port."))
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
            # WO slice 6: the refusal named a remedy the executor refuses
            # everywhere on the boot board. `naval.over_lift_refusal` owns
            # the honest sentence, and the region panel's sibling
            # (`expedition_blocked_reasons`) calls the SAME source for its
            # detachment clause — the review round caught that first claim
            # of a shared source being false while the panel still shipped
            # "detach 15,000 first" on 28 provinces.
            return {"success": False,
                    "message": naval.over_lift_refusal(world, marshal)}

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
                    f"{coverer_line}. A failed run costs "
                    f"~{int(naval.EXPEDITION_INTERCEPT_LOSS * 100)}% of the "
                    f"corps if intercepted, "
                    f"~{int(naval.EXPEDITION_TURNBACK_LOSS * 100)}% turned "
                    f"back — and the fleet's readiness "
                    f"−{naval.EXPEDITION_TURNBACK_READINESS} if she is "
                    f"turned back. Sail? (yes / no)"),
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
                # Aug 30, 2026 review: "the existing land game takes over" was
                # only half true — the land game asks TWO questions before it
                # captures, is there a marshal AND is there a garrison, and
                # this arm asked only the first. A capital's garrison is not a
                # marshal, so 14,000 men put ashore at London walked past
                # 25,000 defenders and took the city, which then flipped to
                # the conqueror. Same predicate as `_execute_attack`'s
                # garrison gate: a detachment always fights, a capital
                # garrison fights above the 5,000 collapse threshold.
                garrison_fights = False
                if (getattr(target_region, "garrison_strength", 0) > 0
                        and target_region.controller != marshal.nation):
                    if getattr(target_region, "garrison_detachment", False):
                        garrison_fights = True
                    elif target_region.garrison_strength >= 5000:
                        garrison_fights = True
                if not defenders and garrison_fights:
                    garrison_result = (
                        self._executor._combat._resolve_garrison_combat(
                            marshal, target_region, world, game_state))
                    message += " " + str(garrison_result.get("message") or "")
                    garrison_result["message"] = message
                    garrison_result["landed"] = True
                    garrison_result["odds"] = int(outcome["odds"])
                    return garrison_result
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
            # WO-34 (found while building slice 15): the landing mounts the
            # plunder/secure question in world state through the shared
            # pipeline above, but this result carried only the three keys
            # copied out of `capture` — never `pending_capture_choice` /
            # `capture_data`, which is what `main.gd` gates the modal on. So
            # an expedition that took a province asked a question the player
            # was never shown; they discovered it by having their next order
            # refused. Same two keys, same priced sentence, as every other
            # capture route (combat_executor's conquest attach).
            if (marshal.nation == world.player_nation
                    and world.pending_capture_choice):
                from backend.models.world_state import capture_choice_prompt
                result["message"] += capture_choice_prompt(
                    world.pending_capture_choice)
                result["pending_capture_choice"] = True
                result["capture_data"] = world.pending_capture_choice
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
        misaddressed = _admiralty_misaddressed(
            command, world, actor, "order the diversion")
        if misaddressed:
            return misaddressed
        # ── PC15-7: quote-then-confirm, the expedition's own idiom ──
        # The typed Grand Diversion resolved IRREVERSIBLY on one line
        # ("order the diversion" at readiness 53 → "caught coming home …
        # loses 46 sail") while its sibling naval_expedition quotes and
        # confirms. Same two-step now: the once-per-war 45% gamble states
        # its terms first. AI callers pass `_acting_nation` and confirm
        # implicitly (the rung already weighed it — GR5 unchanged).
        if actor == getattr(world, 'player_nation', 'France'):
            raw = (command.get("raw_input") or command.get("original_command")
                   or command.get("raw_command") or "").lower()
            confirmed = bool(command.get("confirmed")) or bool(
                re.search(r'\bconfirm(ed)?\b|\bset sail\b', raw))
            if not confirmed:
                rec = naval.get_fleet(world, actor)
                if not rec or int(rec.get("ships", 0) or 0) <= 0:
                    return {"success": False,
                            "message": "We have no fleet to sail, Sire."}
                if rec.get("diversion_used"):
                    return {"success": False, "message": (
                        "The fleet has already attempted its grand "
                        "diversion this war — the squadrons cannot repeat "
                        "the feint while the enemy watches for it.")}
                # Aug 30, 2026 review: shown = applied. The failure arm
                # docks readiness BEFORE the battle, so the quoted "current
                # readiness" was never the readiness she fought at. One
                # source, read here and by `resolve_diversion`.
                readiness = naval.diversion_failure_readiness(rec)
                # FA-31: state the thing being bought, not only the price.
                # ⚠ This arm is `awaiting_clarification` / `free_action` —
                # LOCAL_PLANNING, not a hard stop — so the player may end a
                # turn between the quote and the answer and the number goes
                # stale, exactly as the UX23-A reward price did (measured:
                # a quote of "readiness 60" resolving two turns later at
                # 50). The GUARANTEE is therefore the outcome sentence in
                # `resolve_diversion`, which is derived live after the
                # window is set; this clause is the advice.
                forecast_clause = naval.window_forecast_clause(world, actor)
                forecast_line = (f" And mark this, Sire: {forecast_clause}."
                                 if forecast_clause else "")
                return {
                    "success": True,
                    "free_action": True,
                    "state": "awaiting_clarification",
                    "type": "clarification",
                    "naval_confirm": True,
                    # WO slice 6: the modal had no subject, so it opened
                    # "MARSHAL ASKS:" — and the terminal line beside it
                    # read "Marshal requests clarification". The KEY must
                    # stay `marshal` (both client consumers read it and the
                    # slice touches no `.gd`), but a Grand Diversion has no
                    # marshal: `_execute_naval_diversion` never reads
                    # `world.marshals`, `resolve_diversion` is nation-keyed,
                    # and the parser refuses "Villeneuve, order the
                    # diversion". The admiral is NOT a safe subject either —
                    # 4 of the 10 authored fleets have no `admiral` row. So
                    # the subject is the standing institution, which reads
                    # correctly in BOTH renderings: the title upper-cases it
                    # ("THE ADMIRALTY ASKS:") and the terminal line does not
                    # ("The Admiralty requests clarification").
                    "marshal": "The Admiralty",
                    "original_command": command.get("raw_command", ""),
                    "message": (
                        f"The Grand Diversion is drawn up, Sire — once, "
                        f"and once only, this war. The fleet sails to draw "
                        f"the enemy squadrons off station: "
                        f"{naval.DIVERSION_SUCCESS_PCT} times in 100 the "
                        f"strait opens for {naval.WINDOW_TURNS} turns; "
                        f"otherwise she is caught coming home and fights "
                        f"at readiness {readiness}."
                        f"{forecast_line} "
                        f"Sail? (yes / no)"),
                    "options": [
                        {"label": "Order the diversion",
                         "command": "order the diversion confirmed",
                         "aliases": ["sail", "set sail", "yes", "go"]},
                        {"label": "Stand down", "command": "cancel",
                         "aliases": ["stand down", "no"]},
                    ],
                }
        outcome = naval.resolve_diversion(world, actor)
        result = dict(outcome)
        if outcome.get("success"):
            result["events"] = [{"type": "naval_diversion", "nation": actor,
                                 "window": bool(outcome.get("window"))}]
            result["new_state"] = game_state
        return result
