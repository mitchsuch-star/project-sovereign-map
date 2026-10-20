"""War Status Panel data builder. Produces active_wars dict for HUD + detail popup."""

from typing import Any, Dict, List, Optional, Tuple

from backend.display_names import display_nation
from backend.game_logic.formations import format_progress, formed_display_name
from backend.errors import report

ARMISTICE_DURATION = 5  # Must match diplomacy.py
ARMISTICE_AUTO_PEACE_RELATION = -60  # Must match diplomacy.py (G4F-17)

# IQ-2 (Sept 14, 2026) flip lever. `get_settlement_tier` reads |score|, so
# the war row printed "Harsh Peace" in the popup's prize gold on a war France
# was losing with one province left — the tier never said WHOSE table it
# was. Each player war row now carries `settlement_tier_side` ("theirs" /
# "ours" / "" at 0) off the same score the tier was computed from, and the
# war HUD and detail popup colour and label by it. False = no key, the row
# byte-for-byte.

# IQ-2 (Sept 14, 2026) flip lever. The FA-D4 hint told a France holding no
# province of her homeland "A defensive purpose only (hold the homeland)"
# and invited her to name a purpose of her own — measured on the collapsed
# campaign, beside a war score the enemy was cashing. Keyed on the homeland
# (authority._homeland_held_fraction, the grip's own reader), not on the
# collapse: a France holding foreign conquests but none of her own soil is
# in the same position. False = the FA-D4 hint byte-for-byte.

# LV-8 (row EP F1, Sept 23, 2026) flip lever: a war purpose's targets are ONE
# sentence. FA-D4 gave every boot war the declaration's defensive purpose, and
# a defence purpose's target list IS the homeland — twenty-eight province names
# printed every turn on the morning dispatch, the war panel, the war-detail
# popup and the envoy's War Summary (FA-N71 was verified while the boot list
# was still empty). Europe-scoped (N1): the legacy fixture keeps its list.
# False = every surface prints the raw list, as before.
# Any other target list names at most this many provinces, then ", and N
# more" — the cap `nation_names.nation_not_a_province_message` already uses.
PURPOSE_TARGETS_NAMED = 8


def objective_is_the_homeland(world, owner: str, objective) -> bool:
    """True when `objective` is a DEFENSE purpose whose targets cover the
    owner's whole homeland — FA-D4's shape (`_auto_assign_defense_objective`
    copies `nation_starting_regions`). False on a board with no recorded
    homeland (a bare test world) and for every other purpose."""
    if not isinstance(objective, dict):
        return False
    if str(objective.get("type") or "") != "defense":
        return False
    home = list((getattr(world, "nation_starting_regions", None) or {}).get(owner, []) or [])
    targets = set(str(t) for t in (objective.get("target_regions") or []))
    return bool(home) and set(home) <= targets


def objective_target_summary(world, owner: str, objective) -> str:
    """The ONE sentence every surface prints for a war purpose's targets.

    * a defence purpose over the owner's homeland → "the homeland — 28 of 28
      provinces held" (`formations.format_progress`), or "the homeland is
      lost" when none of it is held (IQ-2's phrase, which the dispatch and
      the war-detail hint already speak);
    * any other list → its names, at most eight, then ", and N more";
    * "" when the lever is down, off the Europe board, or with no targets —
      each surface keeps its own fallback copy for that case.
    """
    if world is None:
        return ""
    if not bool(getattr(world, "sandbox_mode", False)):
        return ""
    if not isinstance(objective, dict):
        return ""
    targets = [str(t) for t in (objective.get("target_regions") or []) if str(t)]
    if not targets:
        return ""
    if objective_is_the_homeland(world, owner, objective):
        held = 0
        for name in targets:
            region = world.regions.get(name)
            if region is not None and getattr(region, "controller", None) == owner:
                held += 1
        if held == 0:
            return "the homeland is lost"
        return f"the homeland — {format_progress(held, len(targets))}"
    shown = ", ".join(targets[:PURPOSE_TARGETS_NAMED])
    rest = len(targets) - PURPOSE_TARGETS_NAMED
    return shown if rest <= 0 else f"{shown}, and {rest} more"


def _tier_side(score: int) -> str:
    """Whose table the settlement tier is: the enemy's below 0, ours above,
    nobody's at a level score (`get_settlement_tier` is direction-blind).

    IQ-2 review round: nobody's at a WHITE PEACE either — the HUD and the
    war-detail popup called a −10 white peace "theirs to impose" while the
    dispatch's copy of this rule excluded it. One rule now: the dispatch
    reads this function."""
    from backend.game_logic.diplomacy import get_settlement_tier
    if get_settlement_tier(score) == "white_peace":
        return ""
    if score < 0:
        return "theirs"
    if score > 0:
        return "ours"
    return ""


def _stored_and_live_pressure(world, france: str, opponents: List[str],
                              war_id: str) -> Tuple[Optional[int], Optional[int]]:
    """PC-F3: the side pressure the settlement scorer reads — the power-
    weighted average of the STORED pair scores (`settlement_scoring.
    compute_side_pressure_score`, its own selection of each court's best
    pair) — and the same pressure on the LIVE pair scores. (None, None) when
    the row has nothing to score."""
    from backend.game_logic import settlement_scoring as SC
    from backend.game_logic.diplomacy import get_war_score_for, live_war_score_for
    opponents = [o for o in opponents if o and o != france]
    if not opponents:
        return None, None
    instance = (getattr(world, "war_instances", None) or {}).get(war_id or "")
    side = ((instance or {}).get("side_by_nation") or {}).get(france) if isinstance(
        instance, dict) else None
    if side in ("attackers", "defenders"):
        stored = SC.compute_direct_scores_by_enemy(
            world, instance, proposer_side=side, covered_enemy_participants=opponents)
        live = {enemy: {member: live_war_score_for(world, member, enemy)
                        for member in per_member}
                for enemy, per_member in stored.items()}
        reading = SC.compute_side_pressure_score(
            world, instance, proposer_side=side,
            covered_enemy_participants=opponents, direct_scores=stored).get("score")
        field = SC.compute_side_pressure_score(
            world, instance, proposer_side=side,
            covered_enemy_participants=opponents, direct_scores=live).get("score")
        if reading is not None and field is not None:
            return int(reading), int(field)
    if len(opponents) == 1:
        # No war instance (a synthetic or legacy pair): the bilateral seams
        # read the stored pair score itself.
        return (int(get_war_score_for(world, france, opponents[0])),
                int(live_war_score_for(world, france, opponents[0])))
    return None, None


def _peace_table(world, france: str, row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """PC-F3 (the Peace Conundrum F3, October 15, 2026): what the peace math
    reads for this war, beside the war score the row shows.

    The row's `war_score` is the war's LIVE aggregate (71 in the user's 1805
    game); the settlement scorer reads the side pressure on the STORED
    scores (17) and judges every court against 50. The row said "Harsh
    Peace" where the table filed a white peace and charged its −10
    legitimacy. So `settlement_tier` now names the scorer's tier; `courts`
    carries each court's total for a settlement as it stands (no terms);
    `lag_note` says when this turn's fighting has moved the field but not
    yet the table (the stored scores are recomputed once a turn, at the
    advance); `lines` is the sentence the war HUD's tooltip and the detail
    popup print. None when the row has nothing to score."""
    from backend.game_logic.diplomacy import SETTLEMENT_TIER_DISPLAY, get_settlement_tier
    opponents = [str(o) for o in (row.get("opponents") or [row.get("opponent")]) if o]
    war_id = str(row.get("war_instance_id", "") or "")
    pressure, field = _stored_and_live_pressure(world, france, opponents, war_id)
    if pressure is None:
        return None
    tier = get_settlement_tier(int(pressure))
    out: Dict[str, Any] = {
        "pressure": int(pressure),
        "pressure_live": int(field),
        "tier": tier,
        "tier_display": SETTLEMENT_TIER_DISPLAY.get(tier, tier),
        "courts": [],
        "carries": False,
        "lag_note": "",
        "lines": [],
    }
    if war_id:
        # The settlement preview's own per-court verdict (no terms) — the
        # very table Open Settlement shows; it refuses (success False) where
        # a settlement cannot be opened (a one-on-one war, not the side
        # leader), and the row then carries no tally.
        try:
            from backend.game_logic.settlement_staging import build_settlement_preview
            preview = build_settlement_preview(
                world, war_id=war_id, settlement_terms=[], actor_nation=france,
                ignore_active_dialogue=True)
        except Exception as exc:
            report(exc, "war_status._peace_table: build_settlement_preview")
            preview = {}
        body = preview.get("settlement_preview") if preview.get("success") else None
        if isinstance(body, dict):
            from backend.game_logic.ai_diplomacy import court_own_readiness
            from backend.game_logic.diplomacy import live_war_score_for
            for court in body.get("per_court_acceptance") or []:
                total = court.get("total")
                threshold = int(court.get("threshold", 50) or 50)
                nation = str(court.get("nation", ""))
                # PC-F37 / PC-F88 (S13e part 1): each court's OWN pair score
                # from France's chair, and what the court itself would do
                # (its threshold, its break-ranks reason, the letter it sends).
                own = court_own_readiness(world, nation, france) if nation else {}
                out["courts"].append({
                    "nation": nation,
                    "total": None if total is None else int(total),
                    "threshold": threshold,
                    "ready": total is not None and int(total) >= threshold,
                    # PC-R4: the court's own pressure and whether it is consulted.
                    "court_pressure": court.get("court_pressure_score"),
                    "consulted": court.get("consulted", True),
                    "pair_score": int(live_war_score_for(world, france, nation)) if nation else 0,
                    "own_score": int(own.get("score", 0)),
                    "own_threshold": int(own.get("threshold", 0)),
                    "sues": bool(own.get("sues")),
                    "break_ranks": str(own.get("break_ranks") or ""),
                    "letter": str(own.get("letter") or ""),
                })
            out["carries"] = bool((body.get("overall_acceptance") or {}).get("carries"))
    line = f"The peace table reads the war at {int(pressure)} — {out['tier_display']}"
    if out["courts"]:
        tally = " · ".join(
            f"{formed_display_name(world, c['nation'])} "
            + ("ready" if c["ready"] else
               ("no score" if c["total"] is None else f"{c['total']}/{c['threshold']}"))
            for c in out["courts"])
        line += (f". A settlement carries only when every court reaches "
                 f"{out['courts'][0]['threshold']} — with no terms: {tally}")
    out["lines"].append(line + ".")
    if len(out["courts"]) > 1:
        # PC-F37: the averaging, shown — each court's own score; PC-R4: each
        # court is now scored on its OWN pair — the mean is the table's label.
        pairs = " · ".join(f"{formed_display_name(world, c['nation'])} {c['pair_score']:+d}"
                           for c in out["courts"])
        out["lines"].append(f"Court by court: {pairs}; the table reads their mean ({int(pressure)}) "
                            f"for its tier, and scores each court on its own pair.")
    for c in out["courts"]:
        # PC-F88: what the beaten court itself would do.
        if c["sues"]:
            letter = {"peace": "her peace letter comes", "truce": "her letter asks a truce"}.get(
                c["letter"], "her letter comes")
            why = {"score": "beaten", "exhaustion": "spent", "long_war": "worn down",
                   "pressburg": "satisfied"}.get(c["break_ranks"], "")
            out["lines"].append(
                f"{formed_display_name(world, c['nation'])}'s own court would sue at "
                f"{c['own_threshold']} (she reads {c['own_score']}"
                f"{', ' + why if why else ''}): {letter}.")
    # PC-R4 (ruling E item 3): the courts under the stake floor, said.
    _not_consulted = [c for c in out["courts"] if c.get("consulted") is False]
    if _not_consulted:
        _names = " and ".join(formed_display_name(world, c["nation"]) for c in _not_consulted)
        out["lines"].append(
            f"{_names} {'is' if len(_not_consulted) == 1 else 'are'} covered, not consulted "
            f"— under the 10 % stake floor; the side's peace binds "
            f"{'her' if len(_not_consulted) == 1 else 'them'}.")
    if int(field) != int(pressure):
        out["lag_note"] = (
            f"This turn's battles and captures count from next turn: the table "
            f"reads {int(pressure)} until the turn ends; the field stands at {int(field)}.")
        out["lines"].append(out["lag_note"])
    return out


def _exhaustion_block(world, opponent: str) -> Tuple[int, Dict[str, Any]]:
    """PC-F42 (S13e part 3): DIPLOMACY CARRIES NO FOG. The war row fog-gated
    the opponent's exhaustion on its map visibility while the same popup's
    Request Terms button stated it ("exhaustion 45 of 80"); the figure is
    public, as every diplomatic read is. PC-R5: the clock's components ride
    beside it (`coalition.war_exhaustion_terms`, `war_exhaustion_lines`) —
    every number an int (Golden Rule 2)."""
    from backend.game_logic.coalition import war_exhaustion_lines, war_exhaustion_terms
    terms = war_exhaustion_terms(world, opponent)
    block = {
        "current": int(terms["current"]), "base": int(terms["base"]),
        "occupation": int(terms["occupation"]), "subsidy": int(terms["subsidy"]),
        "finance": int(terms["finance"]), "total": int(terms["total"]),
        "at_war": bool(terms["at_war"]), "in_truce": bool(terms["in_truce"]),
        "subsidy_role": str(terms["subsidy_role"] or ""),
        "held": list(terms["held"]),
        "forecast_turns": (None if terms["forecast_turns"] is None
                           else int(terms["forecast_turns"])),
        "lines": war_exhaustion_lines(world, opponent),
    }
    return int(world.war_exhaustion.get(opponent, 0) or 0), block


def _objective_block(world, france: str, opponent: str, coalition_members,
                     diplo_key: str) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """The war row's objective blocks (ours, theirs) — extracted from
    `build_active_wars` in S13e part 4 (the ratchet's 500-line cap; the
    row's keys are byte-identical)."""
    from backend.game_logic.diplomacy import TICKING_RATES, OBJECTIVE_TYPE_DISPLAY
    war_obj_data = getattr(world, 'war_objectives', {}).get(diplo_key, {})
    france_obj = war_obj_data.get(france, {})
    enemy_obj = war_obj_data.get(opponent, {})
    # FA-D2 (slice 17, Phase 2): a purpose set against a coalition MEMBER
    # ticks into the score (which sums every pair) but the row resolved
    # its objective through the LEADER pair only, so "set war purpose
    # against Austria" rendered nothing while the score moved. Walk the
    # war's opponents (leader first) and take the first live objective,
    # labelling the court it targets; single-opponent rows are unchanged.
    # FA-D4 (Phase 2b) on top: every boot pair now carries the
    # declaration's default `defense`, so "the first live objective"
    # was always the leader pair's default and a purpose the player
    # NAMED against a member never rendered again. A named purpose
    # outranks a default one; the leader still wins among equals.
    france_obj, objective_against = _pick_war_objective(
        world, france, opponent, coalition_members, france_obj, side="france")
    enemy_obj, enemy_objective_by = _pick_war_objective(
        world, france, opponent, coalition_members, enemy_obj, side="enemy")

    objective_info = None
    if france_obj and france_obj.get("concluded_turn") is None:
        obj_type = france_obj.get("type", "")
        objective_info = {
            "type": obj_type,
            "against": objective_against,
            "type_display": OBJECTIVE_TYPE_DISPLAY.get(obj_type, obj_type),
            "target_regions": france_obj.get("target_regions", []),
            "accumulated_ticking": int(france_obj.get("accumulated_ticking", 0)),
            "ticking_active": bool(france_obj.get("ticking_active", False)),
            "ticking_rate": int(TICKING_RATES.get(obj_type, 0)),
        }
        # LV-8: the ONE sentence the war panel and the war-detail popup
        # print. Absent (not "") off the Europe board or with the lever
        # down, so those payloads stay byte-identical and each client
        # surface keeps its own list fallback.
        _summary = objective_target_summary(world, france, france_obj)
        # PC-R7 (ii) part 2: the war's declared articles ride the one sentence
        from backend.game_logic.declared_goals import declared_line as _declared_line
        _declared = _declared_line(world, france, str(objective_against or opponent))
        if _declared:
            objective_info["declared_display"] = _declared
            if _summary:
                _summary = f"{_summary} — {_declared}"
        if _summary:
            objective_info["target_summary"] = _summary

    enemy_objective_info = None
    if enemy_obj and enemy_obj.get("concluded_turn") is None:
        eo_type = enemy_obj.get("type", "")
        enemy_objective_info = {
            "by": enemy_objective_by,
            "type": eo_type,
            "type_display": OBJECTIVE_TYPE_DISPLAY.get(eo_type, eo_type),
        }
        # PC-R7 (ii) part 2: what the enemy declared against us, on its purpose
        from backend.game_logic.declared_goals import theirs_line as _theirs_line
        _theirs = _theirs_line(world, france, str(enemy_objective_by or opponent))
        if _theirs:
            enemy_objective_info["declared_display"] = _theirs
            enemy_objective_info["type_display"] = (
                f"{enemy_objective_info['type_display']} — declared: {_theirs}")
    return objective_info, enemy_objective_info


def _held_line(world, france: str, opponents: List[str]) -> str:
    """PC-F33 (S13e part 4): the coalition's "white peace" is uti possidetis
    — it confirms every province each side holds — and the tier, the war
    panel and the letter called it a white peace and nothing more. The
    ONE rule the ratifier runs (`game_end.status_quo_forecast_lines`, the
    retention pass read before the signature) says what a peace signed now
    would title, from the player's chair: "Bohemia, Tyrol and Vienna stay
    ours by the treaty". One sentence per court, joined; '' when a peace
    would move nothing."""
    from backend.game_logic.game_end import status_quo_forecast_lines
    lines: List[str] = []
    for opponent in opponents:
        if world.get_diplomatic_state(france, opponent) not in ("WAR", "ARMISTICE"):
            continue
        try:
            words = status_quo_forecast_lines(world, france, opponent, france, ())
        except Exception as exc:
            report(exc, "war_status._held_line: status_quo_forecast_lines")
            continue
        for line in list(words.get("warnings") or []) + list(words.get("lines") or []):
            # the ratifier's sentence, read as a FORECAST on the war card:
            # "Status quo: X stay ours by the treaty — titled." names what a
            # peace signed now would title, not what is titled already
            text = str(line or "")
            if text.startswith("Status quo: "):
                text = text[len("Status quo: "):]
            if text.endswith(" — titled."):
                text = text[:-len(" — titled.")] + "."
            if text and text not in lines:
                lines.append(text)
    if not lines:
        return ""
    return "A peace signed now is on the held line: " + " ".join(lines)


def _title_block(world, war_id: str, court: str = "") -> Dict[str, Any]:
    """PC-R7 (i) — ruling J: the row's title by the war's STAKE ("War for
    Bohemia"), the one builder (`war_title.war_title`) every surface reads;
    `war_roster_display` keeps WHO beside it. A pair with no instance (a
    bare fixture) is titled by the court."""
    from backend.game_logic.war_title import war_title
    try:
        rec = war_title(world, war_id, court=court or None) if (war_id or court) else {}
    except Exception as exc:  # a title is display substrate; never a crash
        report(exc, "war_status._title_block: war_title")
        rec = {}
    return {
        "war_title": str(rec.get("title") or ""),
        "war_title_source": str(rec.get("source") or ""),
        "war_title_line": str(rec.get("line") or ""),
        "war_title_display": str(rec.get("display") or ""),
        "war_roster_display": str(rec.get("roster_display") or ""),
        "war_stake": list(rec.get("stake") or []),
    }


def build_active_wars(world) -> Dict[str, Any]:
    """Build active wars data for the war status panel.

    Returns {wars: [...], coalition: {...} | None}.
    Each war entry includes HUD-level data (score, trend) AND
    detail-popup data (breakdown, battles, WE).
    All numbers int()-wrapped per Golden Rule #2.
    """
    from backend.game_logic.diplomacy import (
        armistice_projected_relation,
        calculate_war_score,
        war_score_fill,
        war_score_fill_lines,
    )
    from backend.game_logic.diplomatic_ledger import (
        _get_nation_visibility, _format_army_strength,
    )

    france = world.player_nation
    wars = []
    coalition = getattr(world, 'active_coalition', None)
    coalition_members = set(
        coalition.get("members", [])
    ) if coalition else set()
    prev_scores = getattr(world, 'previous_war_scores', {})

    # ── Active wars ──
    for key, state in world.diplomatic_states.items():
        if state != "WAR":
            continue
        nations = key.split("|")
        if france not in nations:
            continue
        opponent = nations[0] if nations[1] == france else nations[1]

        # Skip eliminated nations (0 regions + 0 living marshals).
        # Golden Rule 8: this builder runs on EVERY HTTP response — use the
        # cached region index, never a raw O(R) scan (Slice 8 audit).
        opp_regions = len(world.get_nation_regions(opponent))
        opp_marshals = sum(
            1 for m in world.marshals.values()
            if m.nation == opponent and m.strength > 0
        )
        if opp_regions == 0 and opp_marshals == 0:
            continue

        diplo_key = world._make_diplo_key(france, opponent)

        # War score + components (always live-calculate, not cached war_scores)
        components = calculate_war_score(
            france, opponent, world, return_components=True
        )
        score = int(components["total"])
        breakdown = {
            "territory": int(components["territory"]),
            "battles": int(components["battles"]),
            "decisive": int(components["decisive"]),
            "capital": int(components["capital"]),
            # PT-J2: the war's memory rides the same breakdown the popup
            # renders — shown = applied.
            "campaign": int(components.get("campaign", 0)),
            "blood": int(components.get("blood", 0)),
            # HC-1: sustained naval denial (shown = applied).
            "blockade": int(components.get("blockade", 0)),
            # NP-4: the Captive Eagle (shown = applied).
            "captive": int(components.get("captive", 0)),
            "ticking": int(components.get("ticking", 0)),
        }

        # Duration
        started = int(getattr(world, 'war_start_turns', {}).get(diplo_key, 0))
        duration = int(world.current_turn) - started

        # Trend (compare to previous turn)
        prev = prev_scores.get(diplo_key, 0)
        if france != diplo_key.split("|")[0]:
            prev = -prev
        if score > prev + 2:
            trend = "rising"
        elif score < prev - 2:
            trend = "falling"
        else:
            trend = "stable"

        # Battle history (for detail popup)
        all_records = getattr(world, 'battle_records', {})
        records = all_records.get(diplo_key, [])
        battles_fought = int(len(records))
        # Recent battles (last 5, newest first)
        recent_battles = []
        sorted_records = sorted(
            records, key=lambda r: r.get("turn", 0), reverse=True
        )[:5]
        decisive_set = set()
        d_records = getattr(
            world, 'decisive_battles', {}
        ).get(diplo_key, [])
        # PC-F6 (the Peace Conundrum F6, October 15, 2026): a battle row
        # recorded since the fix carries its own `decisive` flag (set by
        # `record_battle` when the bonus is booked), and its decisive record
        # names the battle's `location`. A record no flagged row accounts
        # for matches on (turn, winner, location); only a LEGACY record (no
        # `location`) still matches on (turn, winner) — the match that
        # starred every battle of the turn the winner fought: both repulsed
        # assaults on Vienna wore the star.
        flagged = {(r.get("turn", 0), r.get("winner", ""), r.get("location"))
                   for r in records if r.get("decisive")}
        decisive_at = set()
        for d in d_records:
            turn_winner = (d.get("turn", 0), d.get("winner", ""))
            if d.get("location") is None:
                decisive_set.add(turn_winner)
            elif turn_winner + (d.get("location"),) not in flagged:
                decisive_at.add(turn_winner + (d.get("location"),))
        decisive_won = int(sum(
            1 for d in d_records if d.get("winner") == france
        ))
        for rec in sorted_records:
            turn = int(rec.get("turn", 0))
            winner = rec.get("winner", "")
            location = rec.get("location", "unknown")
            is_decisive = (bool(rec.get("decisive"))
                           or (turn, winner) in decisive_set
                           or (turn, winner, rec.get("location")) in decisive_at)
            won = winner == france
            recent_battles.append({
                "turn": turn,
                "location": location,
                # W6-2: the composed dynamic name; legacy records without
                # one fall back to the classic form.
                "name": rec.get("battle_name") or f"Battle of {location}",
                "won": won,
                "decisive": is_decisive,
            })

        # War exhaustion — PC-F42 / PC-R5 (S13e part 3): no fog, the clock's
        # components beside it (`_exhaustion_block`).
        vis = _get_nation_visibility(opponent, world)
        war_exhaustion, exhaustion_terms = _exhaustion_block(world, opponent)

        opp_strength = sum(
            m.strength for m in world.marshals.values()
            if m.nation == opponent and m.strength > 0
        )
        army_strength = _format_army_strength(opp_strength, vis)

        # Coalition tagging
        in_coalition = opponent in coalition_members
        is_coalition_leader = bool(
            coalition and coalition.get("leader") == opponent
        )

        # WPS-A: War objective + settlement tier
        from backend.game_logic.diplomacy import (
            SETTLEMENT_TIER_DISPLAY, get_settlement_tier,
        )
        objective_info, enemy_objective_info = _objective_block(
            world, france, opponent, coalition_members, diplo_key)

        tier = get_settlement_tier(score)

        # Slice E §16.2 line 1629 — contribution share rows for the war
        # status detail panel. Resolved via the active war_instance for
        # the bilateral pair when one exists; falls back to an empty
        # block when no war_instance is wired (early game / synthetic).
        contribution = _resolve_contribution_share(world, france, opponent)

        # AI-6c (§4.6): a war's reason is carried and shown wherever the
        # war appears — the Stage D stamp, read off the instance when one
        # covers this pair (an AI-declared war names its design; player
        # wars keep their objective block below).
        stated_instance = (getattr(world, "war_instances", None) or {}).get(
            contribution.get("war_id") or "")
        stated_reason = ""
        if isinstance(stated_instance, dict):
            stated_reason = str(stated_instance.get("stated_reason") or "")

        settlement_eligibility = _evaluate_settlement_eligibility(
            world, contribution.get("war_id", ""),
        )
        settlement_available = bool(settlement_eligibility.get("available"))
        war_detail_actionability = _evaluate_war_detail_actionability(
            world,
            contribution.get("war_id", ""),
            opponent,
            settlement_eligibility.get("coverable_enemy_participants", []),
        )
        # PF-2 / D4 + UX-1: "Draft kept" badge — true iff a same-turn scoped
        # settlement draft exists for this war (drafts are cleared at turn
        # end, so existence == same-turn), making the Back Out promise
        # visible AND true on the reopen surface.
        settlement_draft_kept = _war_has_kept_settlement_draft(
            world, contribution.get("war_id", ""),
        )

        # PC-R3 (ruling I item 4): the war panel shows the tier the court's
        # NEXT letter would dictate, and the refused peace that stands.
        from backend.game_logic.ai_diplomacy import (
            next_dictated_letter as _next_letter, refused_peace_clause as _refused_clause,
        )
        row = {
            "next_letter": _next_letter(world, opponent, france),
            "refused_peace": _refused_clause(world, france),
            # PC-R7 (i): the war's title by its stake, and who.
            **_title_block(world, contribution.get("war_id", ""), opponent),
            # PC-F33: what a peace on the held line would title.
            "held_line": _held_line(world, france, [opponent]),
            "opponent": opponent,
            "war_score": score,
            "breakdown": breakdown,
            "duration": duration,
            "started_turn": started,
            "trend": trend,
            "stated_reason": stated_reason,
            "battles_fought": battles_fought,
            "decisive_won": decisive_won,
            "recent_battles": recent_battles,
            "war_exhaustion": war_exhaustion,
            # PC-R5 / F42: the clock's named components, in words too.
            "exhaustion_terms": exhaustion_terms,
            "exhaustion_line": exhaustion_terms["lines"][0] if exhaustion_terms["lines"] else "",
            # PC-R6 (ruling G): each component's fill against its cap.
            "breakdown_fill": war_score_fill(components),
            "breakdown_fill_lines": war_score_fill_lines(components),
            # PC-F84: the trend's glyph, drawn by the card and the popup.
            "trend_glyph": {"rising": "↑", "falling": "↓"}.get(trend, "→"),
            "army_strength": army_strength,
            # DEF-5 naval §9: one naval line per belligerent with a fleet.
            # PUBLIC data (the recorded fog ruling — period newspapers
            # printed orders of battle); empty string when fleet-less.
            "naval_line": _naval_line(world, opponent),
            "status": "war",
            "in_coalition": in_coalition,
            "is_coalition_leader": is_coalition_leader,
            "objective": objective_info,
            "enemy_objective": enemy_objective_info,
            # FA-D4 (slice 17, Phase 2): the verb that sets a purpose had no
            # UI home — the popup says it where the objective block stands.
            "objective_hint": _objective_hint(objective_info, opponent, world),
            "settlement_tier": tier,
            "settlement_tier_display": SETTLEMENT_TIER_DISPLAY.get(tier, tier),
            "contribution_share": contribution.get("rows", []),
            "contribution_overflow_count": int(
                contribution.get("overflow_count", 0) or 0
            ),
            "standing_status": contribution.get("standing_status", ""),
            "standing_status_display": contribution.get(
                "standing_status_display", ""
            ),
            "war_instance_id": contribution.get("war_id", ""),
            "settlement_available": settlement_available,
            "settlement_draft_kept": settlement_draft_kept,
            "settlement_eligibility": settlement_eligibility,
            "war_detail_actionability": war_detail_actionability,
            # SC-30 / Slice G1: the Request Terms affordance + lifecycle
            # state for the War Detail popup.
            "request_terms_state": _evaluate_request_terms_state(
                world, contribution.get("war_id", ""),
            ),
            "settlement_disabled_reason": settlement_eligibility.get(
                "display_reason", ""
            ) if not settlement_available else "",
            "settlement_disabled_reason_display": settlement_eligibility.get(
                "disabled_reason_display", ""
            ) if not settlement_available else "",
        }
        row["settlement_tier_side"] = _tier_side(score)
        wars.append(row)

    wars = _collapse_shared_war_instance_rows(world, france, wars)

    # PC-F3 (the Peace Conundrum F3, October 15, 2026): each war row says
    # what the peace math reads — the scorer's tier (the side pressure on
    # the stored scores) replaces the live aggregate's, the side follows the
    # same number (IQ-2's rule), and the peace table rides the row for the
    # HUD tooltip and the detail popup. Read after the collapse, so a shared
    # war is scored once, over the courts actually at war.
    for row in wars:
        if row.get("status") != "war":
            continue
        table = _peace_table(world, france, row)
        if table is None:
            continue
        row["peace_table"] = table
        row["settlement_tier"] = table["tier"]
        row["settlement_tier_display"] = table["tier_display"]
        row["settlement_tier_side"] = _tier_side(int(table["pressure"]))

    # Sort: coalition leader first, then coalition members, then bilateral
    wars.sort(key=lambda w: (
        not w.get("is_coalition_leader", False),
        not w.get("in_coalition", False),
        w["opponent"],
    ))

    # ── Coalition metadata ──
    coalition_info = None
    if coalition and any(w["in_coalition"] for w in wars):
        # Coordination quality between members (for detail popup)
        from backend.game_logic.coalition import get_coalition_friction
        # FA-N75: read the FOLDED pair rows where the CA8-D2 collapse left
        # them, not the one row that survived it. Before this, `members` was
        # `['Britain']` on the 1805 boot and the coordination loop had
        # nothing to pair — so the card showed no coordination and no weak
        # link, and `diplomatic_advisory._build_situation_recommendation`'s
        # "court the weak link" counsel was dead on every multi-participant
        # war. The block is left BELOW the leader-first sort deliberately:
        # hoisting it above would re-order `members` by `diplomatic_states`
        # insertion and flip `test_coordination_quality_labels`.
        members = [w["opponent"] for w in _coalition_rows(wars)
                   if w["in_coalition"]]
        coordination = []
        for i, m1 in enumerate(members):
            for m2 in members[i + 1:]:
                friction = get_coalition_friction(m1, m2, world)
                if friction >= 0.75:
                    quality = "Good"
                elif friction >= 0.5:
                    quality = "Strained"
                else:
                    quality = "Poor"
                coordination.append({
                    "nation_a": m1,
                    "nation_b": m2,
                    "quality": quality,
                })

        # Weak link: highest WE among members with known WE
        weak_link = None
        max_we = -1
        # FA-N75: same reader as `members` above — the collapsed row's
        # own `war_exhaustion` is the LEADER's, so this loop could only
        # ever nominate the leader or nobody.
        for w in _coalition_rows(wars):
            if w["in_coalition"] and w["war_exhaustion"] is not None:
                if w["war_exhaustion"] > max_we:
                    max_we = w["war_exhaustion"]
                    weak_link = w["opponent"]

        coalition_info = {
            "name": coalition.get("name", "Unknown Coalition"),
            "leader": coalition.get("leader", ""),
            "posture": coalition.get("strategic_posture", "defensive"),
            "coordination": coordination,
            "weak_link": weak_link,
        }

    # ── Armistice nations ──
    armistice_turns_dict = getattr(world, 'armistice_turns', {})
    for key, state in world.diplomatic_states.items():
        if state != "ARMISTICE":
            continue
        nations_in_key = key.split("|")
        if france not in nations_in_key:
            continue
        opponent = (
            nations_in_key[0]
            if nations_in_key[1] == france
            else nations_in_key[1]
        )
        diplo_key = world._make_diplo_key(france, opponent)
        elapsed = int(armistice_turns_dict.get(diplo_key, 0))
        remaining = int(max(0, ARMISTICE_DURATION - elapsed))

        # Relation + trend for armistice detail popup
        relation = int(
            world.nation_relations.get(diplo_key, 0) or 0
        )
        from backend.game_logic.diplomacy import get_relation_descriptor
        relation_desc = get_relation_descriptor(relation)
        relation_history = getattr(
            world, 'relation_history', {}
        ).get(diplo_key, [])
        if len(relation_history) >= 2:
            delta = relation - relation_history[-1]
            rel_trend = (
                "rising" if delta > 2
                else "falling" if delta < -2
                else "stable"
            )
        else:
            rel_trend = "stable"

        # PC-R2 / PC-F44 (S13e part 2): the truce KEEPS the ledger, and the
        # card says so — the kept score, the war's age, the exit it heads
        # for (dictated / peace / war) with the hope terms, and the cure
        # priced. One wording (`diplomacy.truce_words`), read here, on the
        # popup, the wizard row, the counsel and the dispatch.
        from backend.game_logic.diplomacy import get_war_score_for, truce_words
        _words = truce_words(world, france, opponent)
        _kept_score = int(get_war_score_for(world, france, opponent))
        _war_start = int((getattr(world, "war_start_turns", {}) or {}).get(diplo_key, world.current_turn))
        wars.append({
            "opponent": opponent,
            # PT-B2 drive-by, same screen: the war row renders the backend's
            # `formed_display_name` while the armistice card ran the raw key
            # through the client's own map — so a nation that formed under
            # NA-6 appeared under its NEW name two rows above its DEAD one.
            # One producer for both.
            "opponent_display": formed_display_name(world, opponent),
            # PC-R7 (i): a truce keeps the war's title (the pair's instance).
            **_title_block(world, "", opponent),
            "war_score": _kept_score,
            "breakdown": None,
            "duration": int(max(0, int(world.current_turn) - _war_start)),
            "started_turn": _war_start,
            "trend": "stable",
            "battles_fought": int(_words["keeps"]["battles"]),
            "decisive_won": int(_words["keeps"]["decisives"]),
            "recent_battles": [],
            "war_exhaustion": None,
            "army_strength": None,
            "status": "armistice",
            "armistice_remaining": remaining,
            # G4F-17: project the expiry fork (relations vs the -60 line)
            # so the HUD/detail can say where the truce is heading, not
            # just how long it has left.
            # FA-D18 (slice 17, Phase 2): the HUD's fork counts the thaw over the
            # turns REMAINING, the same arithmetic the war-context snapshot uses.
            # PC-R2: the two signed exits both read "peace" to the card's
            # fork; `armistice_exit` carries which.
            "armistice_projected_outcome": (
                "peace" if _words["exit"] in ("peace", "dictated") else "war"
            ),
            "armistice_exit": str(_words["exit"]),
            "armistice_keeps_line": str(_words["keeps_line"]),
            "armistice_heading_line": str(_words["heading_line"]),
            "armistice_hope_line": str(_words["hope_line"]),
            "armistice_cure_line": str(_words["cure_line"]),
            "armistice_sureties_line": str(_words["sureties_line"]),
            "armistice_lines": list(_words["display_lines"]),
            "armistice_projected_relation": int(armistice_projected_relation(relation, remaining)),
            "armistice_auto_peace_threshold": int(ARMISTICE_AUTO_PEACE_RELATION),
            "relation": relation,
            "relation_descriptor": relation_desc,
            "relation_trend": rel_trend,
            "in_coalition": False,
            "is_coalition_leader": False,
        })

    return {
        "wars": wars,
        "coalition": coalition_info,
        # AI-6c (Stage F, §4.6b): the wars France is NOT in — the panel
        # previously dropped every one of them, so "let them bleed while
        # France rearms" was unreadable on the HUD.
        "foreign_wars": _build_foreign_wars(world),
    }


def _naval_line(world, nation: str) -> str:
    """DEF-5 naval §9: the belligerent's fleet in one line — ships, readiness,
    posture, blockade state. Empty for fleet-less nations / worlds."""
    from backend.game_logic.naval import get_fleet, posture_phrase
    rec = get_fleet(world, nation)
    if not rec or int(rec.get("ships", 0) or 0) <= 0:
        return ""
    # DDB-61: ONE phrase for the station, honest about a blockade on her —
    # "on blockade (UNDER BLOCKADE — pinned in port)" said both at once.
    return (f"{int(rec['ships'])} sail of the line — readiness "
            f"{int(rec.get('readiness', 0))}, {posture_phrase(world, nation)}")


def _build_foreign_wars(world) -> List[Dict[str, Any]]:
    """AI-6c (§4.6b): compact rows for live third-party wars. The war's
    EXISTENCE, sides and STATED REASON are court knowledge across Europe
    (DPF-1 — beat 6 already reports their endings town-crier-wide); the
    exhaustion NUMBERS stay military intel, fogged to PARTIAL+ exactly
    like the France-war rows above. Bounded by live war instances —
    never a region scan (GR8)."""
    from backend.game_logic.diplomatic_ledger import _get_nation_visibility
    from backend.models.intel import PARTIAL, VISIBILITY_PRIORITY

    france = world.player_nation
    exhaustion = getattr(world, "war_exhaustion", {}) or {}
    partial_priority = VISIBILITY_PRIORITY.get(PARTIAL, 3)

    def _fogged_we(nation: str) -> Optional[int]:
        vis = _get_nation_visibility(nation, world)
        if VISIBILITY_PRIORITY.get(vis, 0) >= partial_priority:
            return int(exhaustion.get(nation, 0) or 0)
        return None

    rows: List[Dict[str, Any]] = []
    for war_id in sorted((getattr(world, "war_instances", None) or {})):
        instance = world.war_instances[war_id]
        if not isinstance(instance, dict):
            continue
        if instance.get("ended_turn") is not None:
            continue
        side_by_nation = instance.get("side_by_nation") or {}
        participants = list(instance.get("active_participants")
                            or side_by_nation.keys())
        if france in participants:
            continue
        attackers = [n for n in participants
                     if side_by_nation.get(n) == "attackers"]
        defenders = [n for n in participants
                     if side_by_nation.get(n) == "defenders"]
        if not attackers or not defenders:
            continue
        attacker_leader = str(instance.get("attacker_leader") or "")
        defender_leader = str(instance.get("defender_leader") or "")
        attackers = _leader_first(attackers, attacker_leader)
        defenders = _leader_first(defenders, defender_leader)
        lead_attacker = attackers[0]
        lead_defender = defenders[0]
        started = int(instance.get("created_turn") or 0)
        # PC-X25 (S13e part 4, PC-R7 (i)'s sibling): a war between other
        # courts is titled by its stake too — read from the aggressor's chair
        # (its design, else the ground in play) — never "Austria vs Bavaria"
        # as its name; the sides stay on the row as who.
        from backend.game_logic.war_title import war_title as _wt
        try:
            _title = _wt(world, str(war_id), chair=lead_attacker)
        except Exception as exc:  # a title is display substrate
            report(exc, "war_status._build_foreign_wars: war_title")
            _title = {}
        rows.append({
            "war_id": str(war_id),
            "war_title": str(_title.get("title") or ""),
            "war_title_line": str(_title.get("line") or ""),
            "attackers": attackers,
            "defenders": defenders,
            # NA-6 §11.8-3: never a dead name on an always-on surface.
            "attackers_display": " + ".join(
                formed_display_name(world, n) for n in attackers),
            "defenders_display": " + ".join(
                formed_display_name(world, n) for n in defenders),
            "duration": int(world.current_turn) - started,
            "attacker_exhaustion": _fogged_we(lead_attacker),
            "defender_exhaustion": _fogged_we(lead_defender),
            # The Stage D stamps: a war's reason is carried and shown
            # wherever the war appears (§4.6's fifth deliverable).
            "stated_reason": str(instance.get("stated_reason") or ""),
            "ai_initiated": bool(instance.get("ai_initiated")),
        })
    return rows


# FA-N75 (slice 11) flip lever: False restores the post-collapse blindness
# (one bar, one member line, no Targets, no coordination, no weak link).

# The keys the coalition card actually reads off a member row: the bar loop
# (opponent, war_score), the member-line loop (opponent, war_exhaustion,
# army_strength) and the Target loop (opponent, in_coalition,
# is_coalition_leader). `opponent_display` rides along so a formed nation is
# never shown under its dead name (NA-6 §11.8-3).
COALITION_MEMBER_ROW_KEYS = (
    "opponent",
    "opponent_display",
    "war_score",
    "war_exhaustion",
    "exhaustion_line",      # PC-R5 / F42: each member's clock, in words
    "army_strength",
    "in_coalition",
    "is_coalition_leader",
)


def _coalition_rows(wars: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """The per-member rows behind the coalition card (FA-N75).

    A collapsed row carries the pair rows it folded; every other row IS its
    own member. One reader, so the backend metadata and the client card can
    never again disagree about who is in the coalition.
    """
    out: List[Dict[str, Any]] = []
    for row in wars:
        folded = row.get("coalition_member_rows")
        if isinstance(folded, list) and folded:
            out.extend(folded)
        else:
            out.append(row)
    return out


def _leader_first_rows(
    rows: List[Dict[str, Any]],
    leader: str,
) -> List[Dict[str, Any]]:
    """The folded pair rows, the coalition's leader first (FA-N75)."""
    lead = [row for row in rows if str(row.get("opponent", "")) == str(leader)]
    rest = [row for row in rows if str(row.get("opponent", "")) != str(leader)]
    return lead + rest


def _collapse_shared_war_instance_rows(
    world,
    france: str,
    wars: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Collapse bilateral HUD rows that are fronts of one shared war_instance."""
    instances = getattr(world, "war_instances", None) or {}
    if not instances:
        return wars

    passthrough: List[Dict[str, Any]] = []
    by_war_id: Dict[str, List[Dict[str, Any]]] = {}
    for row in wars:
        war_id = str(row.get("war_instance_id", "") or "")
        instance = instances.get(war_id)
        if (
            not war_id
            or not isinstance(instance, dict)
            or instance.get("ended_turn") is not None
            or len(instance.get("active_diplo_keys") or []) <= 1
            or str(row.get("status", "")) != "war"
        ):
            passthrough.append(row)
            continue
        by_war_id.setdefault(war_id, []).append(row)

    collapsed: List[Dict[str, Any]] = list(passthrough)
    for war_id, rows in by_war_id.items():
        if len(rows) <= 1:
            collapsed.extend(rows)
            continue

        instance = instances.get(war_id) or {}
        side_by_nation = instance.get("side_by_nation") or {}
        france_side = side_by_nation.get(france)
        enemy_side = "defenders" if france_side == "attackers" else "attackers"
        leader_key = "defender_leader" if enemy_side == "defenders" else "attacker_leader"
        enemy_leader = str(instance.get(leader_key, "") or "")
        # ── PT-B2 ────────────────────────────────────────────────────────
        # The war HUD used to outlive the peace. `side_by_nation` is war
        # MEMBERSHIP, not belligerency: `side_by_nation.pop` fires only
        # when a nation has no remaining active pair ANYWHERE, so a court
        # that signs with France but stays at war with somebody else keeps
        # its entry forever. Measured: the notification read "France and
        # Hesse have signed a Peace Treaty", `France|Hesse` was gone from
        # `active_diplo_keys`, and the SAME payload's `opponent_display`
        # read "Britain + Austria + Hesse + Russia". It stayed wrong for
        # twelve consecutive responses, to the end of the campaign.
        #
        # The score two lines below already solved this — the [A-F5]
        # comment names the armistice-suspended member explicitly — but it
        # fixed only the number and left the NAMES reading membership. One
        # card, two belligerent sets. They read the same one now.
        #
        # `rows` is the live-WAR set by construction (`:482` admits only
        # `status == "war"` rows), so it is the predicate, not a copy of it.
        # ─────────────────────────────────────────────────────────────────
        live_opponents = {str(row.get("opponent", "")) for row in rows
                          if row.get("opponent")}
        enemy_participants = [
            nation for nation, side in side_by_nation.items()
            if side == enemy_side and nation != france
            and nation in live_opponents
        ]
        if not enemy_participants:
            enemy_participants = [str(row.get("opponent", "")) for row in rows]

        ordered_opponents = _leader_first(enemy_participants, enemy_leader)
        representative = next(
            (row for row in rows if row.get("opponent") == enemy_leader),
            rows[0],
        )
        combined = dict(representative)
        # FA-N75 (slice 11): the CA8-D2 collapse folded three bilateral rows
        # into one and the coalition CARD went blind. Every block on it
        # iterates `wars` — the strength bars, the member lines, the Target
        # buttons — and after the collapse there is one row where there were
        # three. Measured on the 1805 boot: one bar, one member line, ZERO
        # Target buttons, `coordination: []`, `weak_link: None`; with the
        # collapse disabled, three bars, three coordination pairs, weak link
        # Austria and Targets for Austria and Russia.
        #
        # The pair rows are not wrong, they are merely folded away. Carry
        # them: every key the card reads (`opponent`, `war_score`,
        # `war_exhaustion`, `army_strength`, `is_coalition_leader`,
        # `in_coalition`) is already on a pair row. The metadata block below
        # and the client read these instead of re-deriving from a row that
        # no longer represents anybody in particular.
        # Review round: the first cut carried WHOLE rows — 32 keys each,
        # where the card reads six — and measured 3,578 -> 13,630 bytes
        # of `active_wars` on every single HTTP response. Carry what the
        # card reads. Each member keeps its OWN fogged `war_exhaustion`
        # and `army_strength`, which is the point: the collapsed row's
        # were the leader's.
        combined["coalition_member_rows"] = [
            {key: row.get(key) for key in COALITION_MEMBER_ROW_KEYS}
            for row in _leader_first_rows(rows, enemy_leader)
        ]
        combined["opponents"] = ordered_opponents
        combined["opponent"] = (
            ordered_opponents[0] if ordered_opponents else representative.get("opponent", "")
        )
        # NA-6 §11.8-3: the war HUD is always on screen — a formed
        # nation must never sit in it under its dead name.
        combined["opponent_display"] = " + ".join(
            formed_display_name(world, nation) for nation in ordered_opponents
        )
        # PC-R7 (i): the collapsed row's title reads the whole war (its
        # roster is every court on the card, not the representative's pair).
        combined.update(_title_block(world, war_id))
        combined["held_line"] = _held_line(world, france, ordered_opponents)
        combined["is_multi_participant_war"] = True

        # ── CA8-D2 / CA8-24 (close-out gate 10.1) ────────────────────────
        # The collapsed row used to keep the LEADER-PAIR's score, battles
        # and duration wholesale — so France crushing Austria read "+0, 0
        # battles across 0 turns" against a Britain-led coalition while
        # "What stirred Europe" listed the victories one line below. The
        # war row now reports the WAR: same keys, honest values, no `.gd`
        # change. Single source: `calculate_side_war_score` (pair-reducing
        # by construction, so bilateral rows are untouched).
        # Close-out review [A-F5]: aggregate over the SAME belligerent set
        # as the rows being collapsed — an armistice-suspended member stays
        # in `side_by_nation` but has no WAR row and no stored pair score,
        # so counting its territory/capital here would show the player a
        # war total no score-consuming seam agrees with.
        from backend.game_logic.diplomacy import calculate_side_war_score
        row_opponents = [str(r.get("opponent", "")) for r in rows
                         if r.get("opponent")]
        side_components = calculate_side_war_score(
            france, row_opponents, world, return_components=True)
        combined["war_score"] = int(side_components["total"])
        # PC-R6: the fill is the WAR's too (the representative's was the
        # leader pair's); the trend glyph follows the combined trend.
        from backend.game_logic.diplomacy import war_score_fill, war_score_fill_lines
        combined["breakdown_fill"] = war_score_fill(side_components)
        combined["breakdown_fill_lines"] = war_score_fill_lines(side_components)
        combined["breakdown"] = {
            "territory": int(side_components["territory"]),
            "battles": int(side_components["battles"]),
            "decisive": int(side_components["decisive"]),
            "capital": int(side_components["capital"]),
            "campaign": int(side_components.get("campaign", 0)),
            "blood": int(side_components.get("blood", 0)),
            # HC-1: sustained naval denial (shown = applied).
            "blockade": int(side_components.get("blockade", 0)),
            # NP-4: the Captive Eagle (shown = applied).
            "captive": int(side_components.get("captive", 0)),
            "ticking": int(side_components["ticking"]),
        }
        combined["battles_fought"] = int(
            sum(int(r.get("battles_fought", 0)) for r in rows))
        combined["decisive_won"] = int(
            sum(int(r.get("decisive_won", 0)) for r in rows))
        merged_battles = [b for r in rows
                          for b in (r.get("recent_battles") or [])]
        merged_battles.sort(key=lambda b: int(b.get("turn", 0)), reverse=True)
        combined["recent_battles"] = merged_battles[:5]
        # The war is as old as its oldest front.
        combined["duration"] = int(
            max(int(r.get("duration", 0)) for r in rows))
        # Close-out review [A-F3]: two score-DERIVED keys on the same row
        # still told the leader-pair story — the settlement-tier verdict
        # word ("White Peace" beside a +50 war score) and `started_turn`
        # (the detail popup prints "Duration: N turns (since Turn X)", so
        # the pair's start beside the oldest front's duration was
        # self-contradicting arithmetic on one line).
        from backend.game_logic.diplomacy import (
            SETTLEMENT_TIER_DISPLAY, get_settlement_tier,
        )
        side_tier = get_settlement_tier(int(combined["war_score"]))
        combined["settlement_tier"] = side_tier
        combined["settlement_tier_display"] = SETTLEMENT_TIER_DISPLAY.get(
            side_tier, side_tier)
        # IQ-2: the side follows the WAR-level score the tier now reads —
        # `dict(representative)` would otherwise carry the leader pair's.
        combined["settlement_tier_side"] = _tier_side(
            int(combined["war_score"]))
        combined["started_turn"] = int(
            int(world.current_turn) - combined["duration"])
        # Trend on the same ±2 rule the pair rows use, over the SUM of
        # oriented pair scores (previous_war_scores stores the pair view).
        prev_scores = getattr(world, "previous_war_scores", {}) or {}
        prev_sum = 0
        for opponent in row_opponents:
            diplo_key = world._make_diplo_key(france, opponent)
            prev = int(prev_scores.get(diplo_key, 0) or 0)
            if france != diplo_key.split("|")[0]:
                prev = -prev
            prev_sum += prev
        now_sum = int(sum(int(r.get("war_score", 0)) for r in rows))
        if now_sum > prev_sum + 2:
            combined["trend"] = "rising"
        elif now_sum < prev_sum - 2:
            combined["trend"] = "falling"
        else:
            combined["trend"] = "stable"
        collapsed.append(combined)

    return collapsed


def _leader_first(nations: List[str], leader: str) -> List[str]:
    ordered = sorted({str(nation) for nation in nations if nation})
    if leader in ordered:
        ordered.remove(leader)
        return [leader] + ordered
    return ordered


# FA-D2 (slice 17, Phase 2) flip lever: the coalition row's objective is
# read across every opponent pair the score already sums. False = the
# leader pair only (the prior row).


def _objective_hint(objective_info, opponent: str, world=None) -> str:
    """FA-D4: what the popup says under (or instead of) the objective block —
    the verb that names a purpose, and that a defensive one is only the
    default a declaration hands out.

    IQ-2: with no province of the homeland left, the defensive purpose has
    nothing to hold and the invitation is dropped. Deliberately NOT replaced
    by a promise either way: the executor (`_set_war_purpose_inner`) still
    accepts a named Conquest / Forced Alliance / Subjugation, but each ticks
    only while France holds the enemy's capital, and the defense objective
    keeps ticking as the claim on soil this pair's court holds — so the
    hint states the one fact that is true on every such board and invites
    nothing it cannot keep."""
    if (world is not None and (not objective_info
                 or str(objective_info.get("type") or "") == "defense")):
        from backend.models.authority import _homeland_held_fraction
        held, total = _homeland_held_fraction(
            world, getattr(world, "player_nation", "France"))
        if total > 0 and held == 0:
            if not objective_info:
                return ("No war purpose set — and the homeland is lost, so "
                        "no defensive purpose has anything left to hold.")
            return ("The homeland is lost — the defensive purpose has "
                    "nothing left to hold.")
    if not objective_info:
        return (f"No war purpose set — 'set war purpose against {opponent}' names one, and "
                f"the war's articles; until then the war ticks toward nothing.")
    if str(objective_info.get("type") or "") == "defense":
        return (f"A defensive purpose only (hold the homeland) — 'set war purpose against "
                f"{opponent}' names a purpose of your own, and the war's articles.")
    return ""


def _pick_war_objective(world, france: str, leader: str, coalition_members,
                        leader_obj, side: str):
    """FA-D2 + FA-D4: the objective a coalition row shows for one side —
    `side == "france"` reads France's purpose against each court, `"enemy"`
    each court's purpose against France. Leader first; a NAMED purpose (any
    type but the declaration's default `defense`) outranks a default one;
    the first live objective when nothing is named. Returns
    ``(objective, court)``; ``(leader_obj, leader)`` when nothing is live."""
    live = []
    for court in _war_opponents_for_objectives(world, france, leader, coalition_members):
        pair = getattr(world, 'war_objectives', {}).get(world._make_diplo_key(france, court), {})
        cand = pair.get(france if side == "france" else court, {})
        if cand and cand.get("concluded_turn") is None:
            live.append((cand, court))
    for cand, court in live:
        if str(cand.get("type") or "") != "defense":
            return cand, court
    if live:
        return live[0]
    return leader_obj, leader


def _war_opponents_for_objectives(world, france: str, leader: str, coalition_members) -> list:
    """The courts whose pair with France may carry the war's objective:
    the leader first, then every coalition member France is at war with."""
    courts = [leader]
    for member in coalition_members or []:
        if member == france or member in courts:
            continue
        if world.diplomatic_states.get(world._make_diplo_key(france, member)) == "WAR":
            courts.append(member)
    return courts


def _resolve_contribution_share(world, france: str, opponent: str) -> Dict[str, Any]:
    """Find the active war_instance covering the France/opponent pair and
    build top-N contribution share rows for it.

    Returns ``{rows, overflow_count, war_id, standing_status}``. Empty
    rows include a humanized status so Godot does not need to show a blank
    standing area or raw fallback identifiers.
    """
    from backend.game_logic.settlement_presentation import (
        build_contribution_share_rows,
    )
    war_id = _find_active_war_instance_id(world, france, opponent)
    if not war_id:
        return {
            "rows": [],
            "overflow_count": 0,
            "war_id": "",
            "standing_status": "no_war_instance",
            "standing_status_display": (
                "Standing appears once this war is opened as a settlement."
            ),
        }
    contribution = build_contribution_share_rows(world, war_id)
    contribution["war_id"] = war_id
    if contribution.get("rows"):
        contribution["standing_status"] = "available"
        contribution["standing_status_display"] = "Standing available."
    else:
        contribution["standing_status"] = "no_contribution_rows"
        contribution["standing_status_display"] = (
            "No participant standing has been recorded yet."
        )
    return contribution


def _find_active_war_instance_id(
    world, nation_a: str, nation_b: str,
) -> Optional[str]:
    """Return the active war_instance id covering both nations, or None."""
    instances = getattr(world, "war_instances", None) or {}
    if not instances:
        return None
    # Prefer the by-participant index when available.
    index_getter = getattr(world, "get_war_instances_by_participant", None)
    candidate_ids: List[str] = []
    if callable(index_getter):
        a_ids = list(index_getter(nation_a) or [])
        b_ids = set(index_getter(nation_b) or [])
        candidate_ids = [wid for wid in a_ids if wid in b_ids]
    else:
        candidate_ids = list(instances.keys())
    for war_id in candidate_ids:
        instance = instances.get(war_id)
        if not isinstance(instance, dict):
            continue
        if instance.get("ended_turn") is not None:
            continue
        attackers = set(instance.get("attackers") or [])
        defenders = set(instance.get("defenders") or [])
        if (
            (nation_a in attackers and nation_b in defenders)
            or (nation_a in defenders and nation_b in attackers)
        ):
            return war_id
    return None


def _is_common_settlement_worth_showing(world, war_id: str) -> bool:
    """Return True when common peace adds value over bilateral peace."""
    if not war_id:
        return False
    instance = (getattr(world, "war_instances", None) or {}).get(war_id)
    if not instance or instance.get("ended_turn") is not None:
        return False
    from backend.game_logic.settlement_validation import (
        is_common_settlement_worth_showing,
    )

    return is_common_settlement_worth_showing(instance)


def _war_has_kept_settlement_draft(world, war_id: str) -> bool:
    """PF-2 / D4 + UX-1: does a same-turn scoped settlement draft exist?

    True iff the SC-5R scoped draft store holds a non-empty entry for this
    war (`settlement_draft:{war_id}:` key prefix). The store is cleared at
    turn end, so existence implies same-turn; the badge appears iff a
    reopen would actually restore something.
    """
    if not war_id:
        return False
    drafts = getattr(world, "pending_settlement_drafts_by_key", None)
    if not isinstance(drafts, dict):
        return False
    prefix = f"settlement_draft:{war_id}:"
    return any(
        isinstance(key, str) and key.startswith(prefix) and entry
        for key, entry in drafts.items()
    )


def _evaluate_settlement_eligibility(world, war_id: str) -> Dict[str, Any]:
    """SC-10: Use active hostile-pair eligibility, not just unique-nation count."""
    from backend.display_names import settlement_disabled_reason_display

    def _blocked(code: str, **extra: Any) -> Dict[str, Any]:
        display = settlement_disabled_reason_display(code)
        return {
            "available": False,
            "error": code,
            "error_display": display,
            "disabled_reason_display": display,
            "display_reason": display,
            **extra,
        }

    if not war_id:
        return _blocked("invalid_war_id", war_id=war_id)
    try:
        from backend.game_logic.settlement_validation import (
            evaluate_open_settlement_eligibility,
        )
        eligibility = evaluate_open_settlement_eligibility(
            world, war_id=war_id,
            actor_nation=getattr(world, "player_nation", "France"),
            ignore_active_dialogue=True,
        )
        return dict(eligibility)
    except Exception as exc:
        report(exc, "war_status._evaluate_settlement_eligibility: import backend.game_logic.settlement_validation")
        return _blocked("settlement_eligibility_unavailable", war_id=war_id)


def _evaluate_settlement_available(world, war_id: str) -> bool:
    return bool(_evaluate_settlement_eligibility(world, war_id).get("available"))


def _evaluate_war_detail_actionability(
    world,
    war_id: str,
    selected_target_nation: str,
    covered_enemy_participants: List[str],
) -> Dict[str, Any]:
    """Return SC-10b recovery metadata for the War Detail row."""
    try:
        from backend.game_logic.settlement_routes import (
            evaluate_war_detail_actionability,
        )
        return dict(evaluate_war_detail_actionability(
            world,
            war_id=war_id,
            selected_target_nation=selected_target_nation,
            covered_enemy_participants=covered_enemy_participants,
        ))
    except Exception as exc:
        report(exc, "war_status._evaluate_war_detail_actionability: import backend.game_logic.settlement_routes")
        return {
            "actionable": False,
            "war_id": str(war_id or ""),
            "selected_target_nation": str(selected_target_nation or ""),
            "refusal_code": "no_peace_seeking_control",
            "refusal_code_display": "War detail recovery is unavailable.",
            "peace_seeking_controls": [],
        }


def _evaluate_request_terms_state(world: Any, war_id: str) -> Dict[str, Any]:
    """SC-30 / Slice G1 — the per-war Request Terms block for the HUD/detail.

    Merges the affordance (available / disabled-with-clock / absent) with
    the lifecycle's observable state so the War Detail popup can render the
    button AND the pending/answered status line.
    """
    try:
        from backend.game_logic.settlement_routes import (
            evaluate_request_terms_affordance,
        )
        affordance = evaluate_request_terms_affordance(world, war_id)
    except Exception as exc:
        report(exc, "war_status._evaluate_request_terms_state: import backend.game_logic.settlement_routes")
        affordance = {"state": "absent", "reason": "request_terms_ineligible"}
    entry = (getattr(world, "settlement_terms_requests", None) or {}).get(
        str(war_id or "")
    )
    block: Dict[str, Any] = {
        "state": str(affordance.get("state") or "absent"),
        "reason": str(affordance.get("reason") or ""),
        "reason_display": str(affordance.get("reason_display") or ""),
        "status": "",
        "requested_turn": 0,
        "resolved_turn": 0,
        "resolve_reason": "",
    }
    if isinstance(entry, dict):
        block["status"] = str(entry.get("status") or "")
        block["requested_turn"] = int(entry.get("requested_turn") or 0)
        block["resolved_turn"] = int(entry.get("resolved_turn") or 0)
        block["resolve_reason"] = str(entry.get("resolve_reason") or "")
    return block
