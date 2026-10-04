"""SF-DC-1 "Nothing unnamed" (Score Finish Step 7, October 4, 2026).

The doctrines' T9 drift pin and T10 unnamed-effect census
(`docs/DOCTRINES_SPEC.md` §6) as ONE instrument, installed by
`tools/playtest_driver.py --doctrine-census` on an IN-PROCESS run. Over
`--http` the census cannot read the world and records itself unmeasured.

T9 — no drift. After every POST, every marshal's standing doctrine term
(`Marshal._doctrine_terms`, written by the one writer
`doctrines.refresh_doctrine_terms` and the one setter
`doctrines.set_marshal_nation`) is compared with a fresh
`doctrines.derive_terms(world, marshal.nation)`. A difference is a drift row.

T10 — nothing unnamed. A doctrine effect is captured where the MECHANICS
decide it, never where it is reported, so an effect a surface drops is still
counted:

  arrival   a reinforcement roll the court's bar shift decided — a record
            `CombatExecutor._calculate_reinforcements` returned with
            `doctrine_arrived` and `arrived` (a strength brought him in) or
            reason `doctrine_delayed` (a flaw kept him away), read in its FINAL
            state after the POST (a fumble or a neutral-soil flip after the
            roll is not the doctrine's);
  morale    a lopsided defeat the loser's doctrine scaled — `doctrine_morale`
            on `CombatResolver.resolve_battle`'s result whose
            `doctrines.morale_line` is not empty;
  attack /  a field battle whose modifier snapshot carries a doctrine row
  defense   (`modifier_snapshot` on the resolver's result — the share that
            applied, after the defence cap) — the standing clauses, counted
            beside the spec's four so "no doctrine changes an outcome without
            a line saying so" covers them too;
  supply    a supply bite — `WorldState.process_supply_attrition` re-read with
            the doctrine's supply factor neutralised: a corps that lost more
            men than it would have without the clause. The census's own
            doctrine-on reading must equal the engine's loss to the man, or the
            row is flagged `instrument_drift` (the copy of the loop's
            arithmetic is checked against the engine every time it runs);
  recruit   a draft levy priced by the court's recruit clause — a successful
            `EconomyExecutor._execute_recruit` whose nation carries
            `doctrines.recruit_price_term`.

Each effect is judged against the response of the POST it happened in:

  visible   the player was a party (his marshal, his battle, his levy), or the
            response carries it (the backend's fog filter is the authority for
            a battle or a levy the player did not fight). An arrival also
            needs the reinforcer seen — the battle report's own fog
            (`CombatExecutor._doctrine_lines`), read when the report was built.
  named     its line reaches a CLIENT renderer: the line is in the response
            on a route whose client function reads the key that holds it. The
            renderers are read from the .gd source at census time (function
            bodies, full-line comments stripped — the IQ-5 census idiom), so
            the model cannot drift from the client.

Two-sided: a rendered doctrine line with no captured effect behind it is a
`phantom` row (a line that claims a doctrine decided something it did not).

Pass (T10): 0 unnamed visible effects, 0 phantom lines, at least three
distinct named doctrine moments, and at least one named moment for every
great power that fought where the player could see it.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[1]
GD_DIR = REPO / "godot-client" / "project-sovereign" / "scripts"

GREAT_POWERS = ("France", "Britain", "Russia", "Austria", "Prussia")
MOMENTS_REQUIRED = 3
KINDS = ("arrival", "morale", "attack", "defense", "supply", "recruit")

# ═══════════════════════════ the client's renderers ═══════════════════════════
# A route is where a battle report rides in a response; its ENTRY is the client
# function that receives the container, and the formatter it hands
# `<x>.battle_report` to is read for the key that holds the line.
ROUTES: Dict[str, Tuple[str, str]] = {
    "command": ("main.gd", "_display_result"),
    "jealousy_attack": ("main.gd", "_display_jealousy_attacks"),
    "enemy_phase": ("enemy_phase_dialog.gd", "_format_action"),
    "strategic_report": ("main.gd", "_show_strategic_reports"),
}
# The tactical events (a supply bite's own line) and the morning dispatch.
TACTICAL_ENTRY = ("main.gd", "_on_command_result")
DISPATCH_ENTRY = ("main.gd", "_display_morning_dispatch")
# An AI levy's doctrine note is read off the enemy-phase ACTION entry.
RECRUIT_ENTRY = ("enemy_phase_dialog.gd", "_format_action")

_GD_TOP_LEVEL = re.compile(
    r"^(func |static func |var |const |signal |class |class_name |enum |extends |@)")
_SRC_CACHE: Dict[str, str] = {}


def gd_source(file: str) -> str:
    if file not in _SRC_CACHE:
        _SRC_CACHE[file] = (GD_DIR / file).read_text(encoding="utf-8")
    return _SRC_CACHE[file]


def gd_body(file: str, func: str) -> str:
    """The body of GDScript `func <func>(` with full-line comments dropped;
    the body ends at the next TOP-LEVEL declaration (string literals in these
    files span a raw newline, so column 0 alone does not end a body). "" when
    the function does not exist."""
    lines = gd_source(file).splitlines()
    start = next((i for i, ln in enumerate(lines)
                  if ln.startswith(f"func {func}(")), None)
    if start is None:
        return ""
    body = []
    for ln in lines[start + 1:]:
        if _GD_TOP_LEVEL.match(ln):
            break
        body.append(ln)
    return "\n".join(ln for ln in body if not ln.lstrip().startswith("#"))


def _reads(body: str, key: str) -> bool:
    return f'.get("{key}"' in body


def report_formatters(route: str) -> List[str]:
    """The functions the route's entry hands a battle report to."""
    file, entry = ROUTES[route]
    body = gd_body(file, entry)
    found = re.findall(r"\b(\w+)\(\s*[\w.]+\.battle_report\b", body)
    found += re.findall(r"\b(\w+)\(\s*[\w.]+\.get\(\"battle_report\"", body)
    return sorted({f for f in found if f not in ("has", "get", "str", "is_empty")})


def route_reads(route: str, key: str) -> bool:
    """True when the client renders `key` of a battle report on `route`."""
    if route not in ROUTES:
        return False
    file, _entry = ROUTES[route]
    return any(_reads(gd_body(file, f), key) for f in report_formatters(route))


def tactical_messages_rendered() -> bool:
    body = gd_body(*TACTICAL_ENTRY)
    return "response.tactical_events" in body and _reads(body, "message")


def dispatch_headline_rendered() -> bool:
    body = gd_body(*DISPATCH_ENTRY)
    return _reads(body, "headline") and _reads(body, "text")


def recruit_note_rendered() -> bool:
    """The enemy-phase dialog reads `doctrine_note` off the ACTION entry (the
    executor's result, where the backend puts it) — never off `ai_action`,
    the AI's decision dict, which does not carry it."""
    body = gd_body(*RECRUIT_ENTRY)
    return re.search(r'(?<![\w.])action\.get\("doctrine_note"', body) is not None


def client_model() -> Dict[str, object]:
    """The renderers the census judged against, for the record."""
    return {
        "routes": {r: {"entry": f"{f}::{e}", "formatters": report_formatters(r),
                       "reads": {k: route_reads(r, k) for k in
                                 ("doctrine_lines", "morale_line", "modifier_breakdown")}}
                   for r, (f, e) in ROUTES.items()},
        "tactical_messages": tactical_messages_rendered(),
        "dispatch_headline": dispatch_headline_rendered(),
        "recruit_note_on_the_action": recruit_note_rendered(),
    }


# ═══════════════════════════ reading a response ═══════════════════════════════

def route_reports(response) -> List[Tuple[str, dict]]:
    """Every battle report a response carries, with the route it rides."""
    out: List[Tuple[str, dict]] = []
    if not isinstance(response, dict):
        return out
    br = response.get("battle_report")
    if isinstance(br, dict):
        out.append(("command", br))
    for a in response.get("jealousy_attacks") or []:
        if isinstance(a, dict) and isinstance(a.get("battle_report"), dict):
            out.append(("jealousy_attack", a["battle_report"]))
    for r in response.get("strategic_reports") or []:
        if isinstance(r, dict) and isinstance(r.get("battle_report"), dict):
            out.append(("strategic_report", r["battle_report"]))
    ep = response.get("enemy_phase")
    if isinstance(ep, dict):
        for nd in (ep.get("nations") or {}).values():
            for a in (nd or {}).get("actions") or []:
                if isinstance(a, dict) and isinstance(a.get("battle_report"), dict):
                    out.append(("enemy_phase", a["battle_report"]))
    known = {id(rep) for _, rep in out}
    for path, rep in _walk_reports(response, ""):
        if id(rep) not in known:
            out.append((f"other:{path}", rep))
            known.add(id(rep))
    return out


def _walk_reports(node, path):
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "battle_report" and isinstance(v, dict):
                yield (path or "<top>"), v
            else:
                yield from _walk_reports(v, f"{path}.{k}" if path else str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _walk_reports(v, f"{path}[{i}]")


def _enemy_actions(response) -> List[dict]:
    ep = response.get("enemy_phase") if isinstance(response, dict) else None
    out = []
    if isinstance(ep, dict):
        for nd in (ep.get("nations") or {}).values():
            out.extend(a for a in (nd or {}).get("actions") or [] if isinstance(a, dict))
    return out


def _dispatch_texts(response) -> List[str]:
    d = response.get("morning_dispatch") if isinstance(response, dict) else None
    if not isinstance(d, dict):
        return []
    head = d.get("headline")
    texts = []
    if isinstance(head, dict):
        texts.append(str(head.get("text") or ""))
        for sb in head.get("sub_beats") or []:
            texts.append(str(sb.get("text") if isinstance(sb, dict) else sb))
    return texts


# ═══════════════════════════ the census ═══════════════════════════════════════

class DoctrineCensus:
    """T9 + T10 as a `Transport` observer (see the module docstring)."""

    def __init__(self, digest=None, backend_main=None):
        self.d = digest
        self.backend_main = backend_main
        self.pending: List[dict] = []
        self.report_fog: Dict[int, bool] = {}
        self.posts = 0
        self.marshal_checks = 0
        self.drift: List[dict] = []
        self.judged: List[dict] = []
        self.phantoms: List[dict] = []
        self.instrument_drift: List[dict] = []
        self.battles_seen: List[dict] = []
        # run-wide: a rendered line is a phantom only when NO effect of the
        # run produced it (a response may re-carry an earlier report)
        self.known_lines: set = set()
        self.known_standing: set = set()
        self._saved: List[Tuple[object, str, object]] = []
        self.installed = False

    # ── installation ────────────────────────────────────────────────────────
    def install(self):
        from backend.commands import combat_executor as ce
        from backend.commands import economy_executor as ee
        from backend.game_logic import combat as cb
        from backend.models import world_state as ws
        census = self

        def _patch(owner, name, wrapper):
            self._saved.append((owner, name, owner.__dict__[name]))
            setattr(owner, name, wrapper)

        orig_reinf = ce.CombatExecutor._calculate_reinforcements

        def reinf(self_ce, primary, defender, battle_region, nation, world):
            rows = orig_reinf(self_ce, primary, defender, battle_region, nation, world)
            try:
                census._capture_rows(world, primary, defender, battle_region, rows)
            except Exception as exc:          # an instrument never stops a run
                census._note_error("arrival", exc)
            return rows

        orig_lines = ce.CombatExecutor._doctrine_lines

        def lines(self_ce, world, marshal, enemy_marshal, att_r, def_r):
            try:
                census._capture_report_fog(world, att_r, def_r)
            except Exception as exc:
                census._note_error("report_fog", exc)
            return orig_lines(self_ce, world, marshal, enemy_marshal, att_r, def_r)

        orig_resolve = cb.CombatResolver.resolve_battle

        def resolve(self_cr, attacker, defender, *args, **kwargs):
            sides = census._sides(attacker, defender)
            result = orig_resolve(self_cr, attacker, defender, *args, **kwargs)
            try:
                census._capture_battle(sides, result)
            except Exception as exc:
                census._note_error("battle", exc)
            return result

        orig_attrition = ws.WorldState.process_supply_attrition

        def attrition(world):
            try:
                readings = census._supply_readings(world)
            except Exception as exc:
                census._note_error("supply_reading", exc)
                readings = {}
            events = orig_attrition(world)
            try:
                census._capture_supply(world, readings, events)
            except Exception as exc:
                census._note_error("supply", exc)
            return events

        orig_recruit = ee.EconomyExecutor._execute_recruit

        def recruit(self_ex, command, game_state, *args, **kwargs):
            result = orig_recruit(self_ex, command, game_state, *args, **kwargs)
            try:
                census._capture_recruit(game_state, result)
            except Exception as exc:
                census._note_error("recruit", exc)
            return result

        _patch(ce.CombatExecutor, "_calculate_reinforcements", reinf)
        _patch(ce.CombatExecutor, "_doctrine_lines", lines)
        _patch(cb.CombatResolver, "resolve_battle", resolve)
        _patch(ws.WorldState, "process_supply_attrition", attrition)
        _patch(ee.EconomyExecutor, "_execute_recruit", recruit)
        self.installed = True
        return self

    def uninstall(self):
        while self._saved:
            owner, name, original = self._saved.pop()
            setattr(owner, name, original)
        self.installed = False

    def _note_error(self, where, exc):
        self.instrument_drift.append({"where": where, "error": repr(exc)[:200]})

    # ── capture ─────────────────────────────────────────────────────────────
    @staticmethod
    def _player(world) -> str:
        return str(getattr(world, "player_nation", "France") or "France")

    def _world(self):
        bm = self.backend_main
        return getattr(bm, "world", None) if bm is not None else None

    @staticmethod
    def _sides(attacker, defender) -> dict:
        return {"attacker": str(getattr(attacker, "name", "")),
                "attacker_nation": str(getattr(attacker, "nation", "") or ""),
                "defender": str(getattr(defender, "name", "")),
                "defender_nation": str(getattr(defender, "nation", "") or "")}

    def _capture_rows(self, world, primary, other, region, rows):
        if not rows:
            return
        player = self._player(world)
        for row in rows:
            if not isinstance(row, dict) or not row.get("doctrine"):
                continue
            who = world.marshals.get(row.get("marshal")) if hasattr(world, "marshals") else None
            court = str(getattr(who, "nation", "") or "")
            party = player in (court, str(getattr(primary, "nation", "") or ""),
                               str(getattr(other, "nation", "") or ""))
            self.pending.append({
                "kind": "arrival", "row": row, "court": court,
                "doctrine": str(row.get("doctrine") or ""),
                "marshal": str(row.get("marshal") or ""),
                "a": str(getattr(primary, "name", "")), "b": str(getattr(other, "name", "")),
                "region": str(region or ""), "party": party,
                "reinforcer_is_player": court == player,
            })

    def _capture_report_fog(self, world, att_r, def_r):
        player = self._player(world)
        visible = set()
        if hasattr(world, "get_visible_enemies"):
            visible = {m.name for m in world.get_visible_enemies(player)}
        for rows in (att_r or [], def_r or []):
            for row in rows:
                if not isinstance(row, dict):
                    continue
                who = world.marshals.get(row.get("marshal"))
                self.report_fog[id(row)] = bool(
                    who is not None and (who.nation == player or who.name in visible))

    def _capture_battle(self, sides, result):
        if not isinstance(result, dict):
            return
        player = self._battle_player()
        party = player in (sides["attacker_nation"], sides["defender_nation"])
        self.battles_seen.append(dict(sides, party=party, judged=False, visible=None,
                                      post=self.posts + 1))
        from backend.game_logic.doctrines import morale_line
        rec = result.get("doctrine_morale")
        line = morale_line(rec or {}) if rec else ""
        if line:
            self.pending.append({
                "kind": "morale", "court": str(rec.get("nation") or ""),
                "doctrine": str(rec.get("name") or ""), "marshal": str(rec.get("marshal") or ""),
                "a": sides["attacker"], "b": sides["defender"], "party": party,
                "line": line, "record": dict(rec),
            })
        snap = result.get("modifier_snapshot") or {}
        for side, kind in (("attacker", "attack"), ("defender", "defense")):
            for row in snap.get(side) or []:
                if isinstance(row, dict) and row.get("doctrine"):
                    self.pending.append({
                        "kind": kind, "side": side,
                        "court": sides[f"{side}_nation"],
                        "doctrine": str(row.get("label") or ""),
                        "marshal": sides[side], "a": sides["attacker"], "b": sides["defender"],
                        "party": party, "value": int(row.get("value", 0) or 0),
                    })

    def _battle_player(self) -> str:
        w = self._world()
        return self._player(w) if w is not None else "France"

    def _supply_readings(self, world) -> Dict[str, dict]:
        """The engine's loop arithmetic, read twice — with the doctrine's
        supply factor and with it neutralised — for every corps the clause
        bites on today. Pure: nothing is written."""
        from backend.game_logic import doctrines
        if not getattr(world, "doctrines", None):
            return {}
        by_loc: Dict[str, list] = {}
        for m in world.marshals.values():
            if int(getattr(m, "strength", 0) or 0) > 0 and getattr(m, "location", None):
                by_loc.setdefault(m.location, []).append(m)
        out: Dict[str, dict] = {}
        for loc, here in by_loc.items():
            region = world.regions.get(loc)
            if region is None or not region.controller:
                continue
            total = sum(m.strength for m in here)
            num, free = world.crowding_press(region, here)
            for m in here:
                factor, name = doctrines.supply_factor(world, m.nation, region, forecast=False)
                if factor == 1.0:
                    continue
                cap_on = world.get_effective_supply_cap(m.nation, region, forecast=False)
                saved = doctrines.supply_factor
                doctrines.supply_factor = lambda *a, **k: (1.0, "")
                try:
                    cap_off = world.get_effective_supply_cap(m.nation, region, forecast=False)
                finally:
                    doctrines.supply_factor = saved
                r_on = world.supply_attrition_rate(total, cap_on, num, free_corps=free)
                r_off = world.supply_attrition_rate(total, cap_off, num, free_corps=free)
                out[m.name] = {"region": loc, "nation": m.nation, "doctrine": name,
                               "factor": factor, "strength": int(m.strength),
                               "on": int(m.strength * r_on), "off": int(m.strength * r_off)}
        return out

    def _capture_supply(self, world, readings, events):
        player = self._player(world)
        for ev in events or []:
            if not isinstance(ev, dict) or ev.get("type") != "supply_attrition":
                continue
            r = readings.get(ev.get("marshal"))
            if not r:
                continue
            actual = int(ev.get("losses", 0) or 0)
            if r["on"] != actual:
                self.instrument_drift.append({
                    "where": "supply", "marshal": ev.get("marshal"), "region": r["region"],
                    "census_on": r["on"], "engine": actual})
            if actual > r["off"]:
                self.pending.append({
                    "kind": "supply", "court": r["nation"], "doctrine": r["doctrine"],
                    "marshal": str(ev.get("marshal") or ""), "region": r["region"],
                    "party": r["nation"] == player, "losses": actual,
                    "extra": actual - r["off"], "factor": r["factor"],
                })

    def _capture_recruit(self, game_state, result):
        if not isinstance(result, dict) or not result.get("success"):
            return
        world = game_state.get("world") if isinstance(game_state, dict) else None
        if world is None:
            return
        evs = result.get("events") or []
        ev = evs[0] if evs and isinstance(evs[0], dict) else {}
        recipient = ev.get("marshal")
        m = world.marshals.get(recipient) if recipient else None
        nation = str(getattr(m, "nation", "") or self._player(world))
        from backend.game_logic.doctrines import recruit_price_term
        term = recruit_price_term(world, nation)
        if not term:
            return
        self.pending.append({
            "kind": "recruit", "court": nation, "doctrine": term[0], "mult": term[1],
            "marshal": str(recipient or ""), "region": str(ev.get("location") or ""),
            "party": nation == self._player(world),
            "note": f"{term[0]}, ×{term[1]:g}", "term": f"×{term[1]:g} {term[0]}",
            "result": result,
        })

    # ── the observer ────────────────────────────────────────────────────────
    def observe(self, path, payload, response):
        """The Transport swallows an observer's exception (an instrument never
        stops a run) — so the census catches its own and RECORDS it: a census
        that failed silently would read as a pass."""
        try:
            self._observe(path, payload, response)
        except Exception as exc:
            self._note_error(f"observe {path}", exc)

    def _observe(self, path, payload, response):
        self.posts += 1
        world = self._world()
        if world is not None:
            self._t9(world, path, response)
        effects, self.pending = self.pending, []
        if not isinstance(response, dict):
            response = {}
        routes = route_reports(response)
        turn = self._turn(response, world)
        for eff in effects:
            verdict = self._judge(eff, routes, response, world)
            row = {k: v for k, v in eff.items() if k not in ("row", "record", "result")}
            row.update(verdict, turn=turn, path=path)
            self.judged.append(row)
            if self.d is not None:
                # `kind` is the jsonl row's own key — the effect's class rides
                # as `effect`
                self.d.record("doctrine_effect",
                              **{("effect" if k == "kind" else k): v for k, v in row.items()})
        for b in self.battles_seen:
            if not b["judged"]:
                b["judged"] = True
                names = {_hum(b["attacker"]), _hum(b["defender"])}
                b["visible"] = bool(b["party"] or any(
                    _report_pair(rep) == names for _r, rep in routes))
        self._phantoms(routes, effects, turn, path)

    @staticmethod
    def _turn(response, world):
        summary = response.get("action_summary") if isinstance(response, dict) else None
        if isinstance(summary, dict) and isinstance(summary.get("turn"), int):
            return summary["turn"]
        return int(getattr(world, "current_turn", 0) or 0) if world is not None else None

    def _t9(self, world, path, response):
        from backend.game_logic.doctrines import derive_terms, terms_of
        cache: Dict[str, dict] = {}
        for m in (getattr(world, "marshals", None) or {}).values():
            nation = str(getattr(m, "nation", "") or "")
            if nation not in cache:
                cache[nation] = derive_terms(world, nation)
            stored = dict(terms_of(m))
            self.marshal_checks += 1
            if stored != cache[nation]:
                row = {"path": path, "turn": self._turn(response, world),
                       "marshal": m.name, "nation": nation,
                       "stored": stored, "derived": dict(cache[nation])}
                self.drift.append(row)
                if self.d is not None:
                    self.d.record("doctrine_drift", **row)

    # ── judging ─────────────────────────────────────────────────────────────
    def _judge(self, eff, routes, response, world) -> dict:
        kind = eff["kind"]
        if kind in ("arrival", "morale", "attack", "defense"):
            return self._judge_battle(eff, routes)
        if kind == "supply":
            return self._judge_supply(eff, response)
        return self._judge_recruit(eff, response)

    def _judge_battle(self, eff, routes) -> dict:
        kind = eff["kind"]
        if kind == "arrival":
            row = eff["row"]
            decided = bool((row.get("arrived") and row.get("doctrine_arrived"))
                           or row.get("reason") == "doctrine_delayed")
            if not decided:
                return {"verdict": "no_effect"}
            from backend.game_logic.doctrines import arrival_copy
            eff["line"] = arrival_copy(row, eff["a"])
        names = {_hum(eff["a"]), _hum(eff["b"])}
        hits = [(r, rep) for r, rep in routes if _report_pair(rep) == names]
        visible = bool(eff["party"] or hits)
        if kind == "arrival" and visible:
            seen = self.report_fog.get(id(eff["row"]))
            if seen is None:
                seen = eff["reinforcer_is_player"]
            visible = bool(seen)
        if not visible:
            return {"verdict": "fogged", "line": eff.get("line", "")}
        key = {"arrival": "doctrine_lines", "morale": "morale_line",
               "attack": "modifier_breakdown", "defense": "modifier_breakdown"}[kind]

        def present(rep):
            if kind == "arrival":
                return eff["line"] in (rep.get("doctrine_lines") or [])
            if kind == "morale":
                return rep.get("morale_line") == eff["line"]
            rows = ((rep.get("modifier_breakdown") or {}).get(eff["side"]) or [])
            return any(isinstance(x, dict) and x.get("doctrine")
                       and str(x.get("label")) == eff["doctrine"] for x in rows)

        carried = [r for r, rep in hits if present(rep)]
        named = [r for r in carried if route_reads(r, key)]
        out = {"line": eff.get("line", eff.get("doctrine", "")),
               "routes": [r for r, _ in hits], "carried_on": carried, "named_on": named}
        if named:
            out["verdict"] = "named"
        elif not hits:
            out.update(verdict="unnamed", reason="the battle reached no client route")
        elif not carried:
            out.update(verdict="unnamed",
                       reason=f"the line is absent from the report on {', '.join(r for r, _ in hits)}")
        else:
            out.update(verdict="unnamed",
                       reason=f"the client's {', '.join(carried)} renderer does not read {key}")
        return out

    def _judge_supply(self, eff, response) -> dict:
        if not eff["party"]:
            mine = [e for e in response.get("tactical_events") or []
                    if isinstance(e, dict) and e.get("marshal") == eff["marshal"]
                    and e.get("type") == "supply_attrition"]
            if not mine:
                return {"verdict": "fogged"}
        name = eff["doctrine"].lower()
        msgs = [str(e.get("message") or "") for e in response.get("tactical_events") or []
                if isinstance(e, dict) and e.get("type") == "supply_attrition"
                and e.get("marshal") == eff["marshal"]]
        on_event = any(name in m.lower() for m in msgs)
        on_dispatch = any(name in t.lower() and eff["region"].lower() in t.lower()
                          for t in _dispatch_texts(response))
        named = []
        if on_event and tactical_messages_rendered():
            named.append("tactical_event")
        if on_dispatch and dispatch_headline_rendered():
            named.append("dispatch")
        out = {"line": eff["doctrine"], "named_on": named,
               "routes": (["tactical_event"] if msgs else [])}
        if named:
            out["verdict"] = "named"
        elif not msgs:
            out.update(verdict="unnamed", reason="no attrition line reached the response")
        else:
            out.update(verdict="unnamed",
                       reason="the attrition line does not name the clause")
        return out

    def _judge_recruit(self, eff, response) -> dict:
        if eff["party"]:
            msg = str(response.get("message") or "")
            if eff["term"] in msg:
                return {"verdict": "named", "line": eff["term"], "named_on": ["command"]}
            return {"verdict": "unnamed", "line": eff["term"],
                    "reason": "the levy's message does not carry the clause's term"}
        mine = [a for a in _enemy_actions(response)
                if str((a.get("ai_action") or {}).get("action") or "") == "recruit"
                and any(isinstance(e, dict) and e.get("marshal") == eff["marshal"]
                        for e in a.get("events") or [])]
        if not mine:
            return {"verdict": "fogged", "line": eff["note"]}
        carried = [a for a in mine if a.get("doctrine_note") == eff["note"]]
        if carried and recruit_note_rendered():
            return {"verdict": "named", "line": eff["note"], "named_on": ["enemy_phase"]}
        if not carried:
            return {"verdict": "unnamed", "line": eff["note"],
                    "reason": "the enemy-phase action does not carry the clause's note"}
        return {"verdict": "unnamed", "line": eff["note"],
                "reason": "the client's enemy-phase dialog does not read the action's doctrine_note"}

    def _phantoms(self, routes, effects, turn, path):
        """A rendered doctrine line with no captured effect behind it (run-wide:
        an earlier POST's effect may ride a later response's report)."""
        self.known_lines |= {e.get("line") for e in effects
                             if e["kind"] in ("arrival", "morale") and e.get("line")}
        self.known_standing |= {(e["kind"], _hum(e["marshal"]), e["doctrine"])
                                for e in effects if e["kind"] in ("attack", "defense")}
        lines, standing = self.known_lines, self.known_standing
        for route, rep in routes:
            for dl in rep.get("doctrine_lines") or []:
                dl = str(dl)
                # the arrival copy's two shapes (`doctrines.arrival_copy`);
                # Berthier's "marched apart and arrived together" is an
                # observation over the arrivals, not one effect
                if (dl.endswith(" in.") or dl.endswith(" too late.")) and dl not in lines:
                    self._phantom(route, dl, turn, path)
            ml = str(rep.get("morale_line") or "")
            if ml and ml not in lines:
                self._phantom(route, ml, turn, path)
            cs = rep.get("casualty_summary") or {}
            for side, kind, who in (("attacker", "attack", cs.get("attacker_name")),
                                    ("defender", "defense", cs.get("defender_name"))):
                for x in ((rep.get("modifier_breakdown") or {}).get(side) or []):
                    if isinstance(x, dict) and x.get("doctrine"):
                        if (kind, _hum(who or ""), str(x.get("label"))) not in standing:
                            self._phantom(route, f"{x.get('label')} ({who})", turn, path)

    def _phantom(self, route, line, turn, path):
        row = {"route": route, "line": line, "turn": turn, "path": path}
        self.phantoms.append(row)
        if self.d is not None:
            self.d.record("doctrine_phantom", **row)

    # ── the result ──────────────────────────────────────────────────────────
    def summary(self) -> dict:
        per_kind = {k: {"total": 0, "visible": 0, "named": 0, "unnamed": 0, "fogged": 0}
                    for k in KINDS}
        moments, unnamed = set(), []
        for row in self.judged:
            v = row.get("verdict")
            if v == "no_effect":
                continue
            k = per_kind.setdefault(row["kind"], {"total": 0, "visible": 0, "named": 0,
                                                  "unnamed": 0, "fogged": 0})
            k["total"] += 1
            if v == "fogged":
                k["fogged"] += 1
                continue
            k["visible"] += 1
            if v == "named":
                k["named"] += 1
                moments.add((row.get("court") or "", row.get("doctrine") or ""))
            else:
                k["unnamed"] += 1
                unnamed.append(row)
        fought = sorted({n for b in self.battles_seen if b.get("visible")
                         for n in (b["attacker_nation"], b["defender_nation"])
                         if n in GREAT_POWERS})
        covered = {c for c, _ in moments}
        uncovered = [c for c in fought if c not in covered]
        t9_pass = bool(self.posts) and not self.drift
        t10_pass = (not unnamed and not self.phantoms and len(moments) >= MOMENTS_REQUIRED
                    and not uncovered)
        return {
            "measured": True,
            "t9": {"posts": self.posts, "marshal_checks": self.marshal_checks,
                   "drift": len(self.drift), "first_drift": self.drift[:5],
                   "pass": t9_pass},
            "t10": {"effects": per_kind,
                    "unnamed": [{k: r.get(k) for k in ("kind", "court", "doctrine", "marshal",
                                                       "turn", "line", "reason", "routes")}
                                for r in unnamed[:40]],
                    "unnamed_count": len(unnamed),
                    "phantoms": self.phantoms[:20], "phantom_count": len(self.phantoms),
                    "moments": [f"{c}: {d}" for c, d in sorted(moments)],
                    "courts_fought": fought, "uncovered": uncovered,
                    "pass": t10_pass},
            "instrument_drift": self.instrument_drift[:20],
            "client_model": client_model(),
        }

    def digest_lines(self) -> List[str]:
        s = self.summary()
        t9, t10 = s["t9"], s["t10"]
        out = ["", "## Doctrine census (SF-DC-1)",
               f"- T9 drift: {t9['drift']} of {t9['marshal_checks']} marshal checks over "
               f"{t9['posts']} POSTs — {'PASS' if t9['pass'] else 'MISS'}"]
        for k in KINDS:
            c = t10["effects"].get(k) or {}
            if c.get("total"):
                out.append(f"- {k}: {c['total']} effects · {c['visible']} visible · "
                           f"{c['named']} named · {c['unnamed']} unnamed · {c['fogged']} fogged")
        out.append(f"- moments ({len(t10['moments'])}): {', '.join(t10['moments']) or 'none'}")
        out.append(f"- courts that fought in sight: {', '.join(t10['courts_fought']) or 'none'}"
                   + (f" · uncovered: {', '.join(t10['uncovered'])}" if t10["uncovered"] else ""))
        out.append(f"- phantom lines: {t10['phantom_count']}")
        out.append(f"- T10: {'PASS' if t10['pass'] else 'MISS'}")
        for r in t10["unnamed"]:
            out.append(f"  - UNNAMED t{r.get('turn')} {r.get('kind')} {r.get('court')} "
                       f"«{r.get('doctrine')}» ({r.get('marshal')}): {r.get('reason')}")
        if s["instrument_drift"]:
            out.append(f"- ⚠ instrument drift: {s['instrument_drift'][:3]}")
        return out


def _hum(name: str) -> str:
    from backend.display_names import humanize_entity_name
    return humanize_entity_name(str(name or ""))


def _report_pair(rep: dict) -> set:
    cs = rep.get("casualty_summary") if isinstance(rep, dict) else None
    if not isinstance(cs, dict):
        return set()
    return {str(cs.get("attacker_name") or ""), str(cs.get("defender_name") or "")}


def unmeasured(reason: str) -> dict:
    return {"measured": False, "reason": reason}
