"""CN-4 — the chip-honesty census (the Command-Road Queue, slice 3's last
part). Build contract: `docs/audits/RECRUIT_ARM_UX_2026_09_20.md` R4; landing
record appended there.

The class: *a chip composes a command naming a parameter the executor
discards* — and its sibling, *a chip offered where the executor refuses*.
CN-3 closed it for the recruit row. This census closes it for every chip the
client composes, and it DRIVES the composed strings, never greps them:

* `TestEveryPanelChipIsHonoured` renders the REAL `region_panel.gd` headless
  (`tools/cn3_region_panel_harness.gd`) on a staged 1805 board — an enemy
  beside two French corps, an ally and a neutral beside a third, a damaged
  market, war damage, a small corps in a dockyard — and sends every rendered
  `do:` / `order:` chip through POST /command on a fresh copy of that board:
  each must act, and act on what it names. Skips without the engine; a skip
  is not a pass.
* The engine-free classes drive every other template the client composes —
  the diplomacy wizard's `_build_command`, the Vassals tab, the reward
  dialog, the Generals screen, the Admiralty's backend-composed chips — each
  template EXTRACTED from the `.gd`, so an edit cannot leave a pin green.
* `TestTheInventoryIsComplete` enumerates every chip url and every command
  template in the client and fails on any row this file has not reviewed.

Reproduced first (HEAD `8b6591b8`), all driven at POST /command: the attack
chip was offered against an ALLY ("Attack Deroy" at Franconia, always
refused); every Drill chip at the 1805 boot was refused (every corps stands
one province from Mack) and so was every fortified marshal's; the
Substitutes chip quoted the national "per 10,000" where a field purchase
delivers 3,000, was gated on a national room flag (Milan: enabled, always
refused) and at Franche-Comte named Murat, a cavalryman it always refuses;
the second keel of a turn and a short treasury left the dockyard chip
enabled and refused; the wizard's cede echo dropped the province the player
picked and its white-peace echo, re-sent from the up-arrow, proposed a
treaty with terms; the attack chip and the FORCES row printed the roster key
("ArchdukeCharles").
"""

import contextlib
import io
import re

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands import economy_executor as EE
from backend.commands.tactical_executor import drill_refusal, fortify_refusal
from backend.display_names import humanize_entity_name
from backend.game_logic import naval
from backend.game_logic.recruitment import build_recruitment_payload
from tests import _chip_census as C

SCRIPTS = C.SCRIPTS

# The land grant needs conquered soil adjoining Holland: Osnabruck is
# Hanover's at boot and borders Holland's Friesland/Gelderland (measured).
CEDE_REGION = "Osnabruck"
BUILD_TYPES = {"depot": "supply_depot", "fort": "fortification",
               "market": "market", "stables": "stables",
               "training ground": "training_ground"}


# ═══════════════════════════════════════════════════════════════════════════
# The staged board
# ═══════════════════════════════════════════════════════════════════════════
def stage(world):
    world.nation_gold["France"] = 20000
    lorraine = world.get_region("Lorraine")
    lorraine.buildings.append({"type": "market", "damaged": True})
    lorraine.war_damage = 0.30
    # An ENEMY beside Ney and Davout; a NEUTRAL beside Bernadotte and Deroy
    # (a Bavarian ally, who already stands at Franconia).
    world.get_marshal("ArchdukeCharles").location = "Rhineland"
    world.get_marshal("Brunswick").location = "Franconia"
    # A small corps in the senior yard: the landing chips.
    yards = naval.controlled_dockyards(world, "France")
    lannes = world.get_marshal("Lannes")
    lannes.strength = 12000
    lannes.location = yards[0]
    C.refresh_view(world)
    return yards


def fresh_staged():
    C.boot()
    stage(M.world)
    return TestClient(M.app)


def snapshot(world):
    return {
        "gold": int(world.nation_gold.get("France", 0)),
        "pools": dict(world.manpower_pools.get("France", {})),
        "marshals": {m.name: {"loc": m.location, "strength": int(m.strength),
                              "fortified": bool(getattr(m, "fortified", False)),
                              "drilling": bool(getattr(m, "drilling", False))}
                     for m in world.marshals.values()},
        "regions": {r: {"damaged": sorted(b["type"] for b in reg.buildings
                                          if b.get("damaged")),
                        "building": (reg.building_under_construction or {}).get("type")
                        if isinstance(reg.building_under_construction, dict) else None,
                        "watchtower": reg.watchtower,
                        "war_damage": float(reg.war_damage)}
                    for r, reg in world.regions.items() if reg.controller == "France"},
    }


def _int(text):
    return int(text.replace(",", ""))


def judge(region, url, label, tail, before, after, response):
    """"" when the chip acted and acted on what it names; else why not."""
    cmd = C.chip_command(url)
    msg = response.get("message") or ""
    if not response.get("success"):
        return f"refused: {msg[:140]}"
    objection = M.world.pending_objection or {}
    m = re.fullmatch(r"recruit (\w+) in (.+)", cmd)
    if m:
        arm = label.strip().lower()
        spent = {k: before["pools"][k] - after["pools"][k] for k in before["pools"]
                 if before["pools"][k] != after["pools"][k]}
        return "" if list(spent) == [arm] and m.group(1) == arm else f"raised {spent}"
    m = re.fullmatch(r"build (.+) in (.+)", cmd)
    if m:
        kind, where = m.group(1), m.group(2)
        if kind == "watchtower":
            return "" if after["regions"][where]["watchtower"] == "under_construction" else "no tower"
        want = BUILD_TYPES.get(kind)
        got = after["regions"][where]["building"]
        return "" if want and got == want else f"built {got} for {kind}"
    m = re.fullmatch(r"repair buildings in (.+)", cmd)
    if m:
        r0, r1 = before["regions"][m.group(1)], after["regions"][m.group(1)]
        ok = r0["damaged"] and not r1["damaged"] and r1["war_damage"] == r0["war_damage"]
        return "" if ok else f"repaired {r0} -> {r1}"
    m = re.fullmatch(r"repair (.+)", cmd)
    if m:
        r0, r1 = before["regions"][m.group(1)], after["regions"][m.group(1)]
        ok = r1["war_damage"] < r0["war_damage"] and r1["damaged"] == r0["damaged"]
        return "" if ok else f"repaired {r0} -> {r1}"
    if cmd == "build ships":
        yard = region
        m = re.search(r"laid at (\S+) \(the senior yard\)", tail)
        if m:
            yard = m.group(1)
        return "" if f"A keel is laid at {yard}" in msg else f"keel elsewhere: {msg[:80]}"
    m = re.fullmatch(r"buy substitutes for (.+)", cmd)
    if m:
        who = m.group(1)
        t = re.match(r"(?P<man>[\w\- ]+) · (?P<men>[\d,]+) men · (?P<gold>[\d,]+)g", tail)
        if not t or t["man"] != who:
            return f"terms do not name the recipient: {tail!r}"
        grew = after["marshals"][who]["strength"] - before["marshals"][who]["strength"]
        paid = before["gold"] - after["gold"]
        ok = grew == _int(t["men"]) and paid == _int(t["gold"])
        return "" if ok else f"terms {tail!r} but +{grew} men for {paid}g"
    m = re.fullmatch(r"land (.+) in (.+)", cmd)
    if m:
        return "" if m.group(1) in msg and m.group(2) in msg else f"quote names neither: {msg[:80]}"
    m = re.fullmatch(r"(.+), attack (.+)", cmd)
    if m:
        who, enemy = m.group(1), m.group(2)
        order = objection.get("original_order") or objection.get("command") or {}
        target = str(order.get("target") or "")
        named = (enemy in msg or enemy.replace(" ", "") in msg
                 or humanize_entity_name(target) == enemy)
        return "" if named else f"attack did not reach {enemy}: {msg[:80]}"
    m = re.fullmatch(r"(.+), (fortify|unfortify|drill|scout)", cmd)
    if m:
        who, verb = m.group(1), m.group(2)
        asked = objection.get("marshal") == who
        state = after["marshals"][who]
        ok = {"fortify": state["fortified"] or asked,
              "unfortify": not state["fortified"],
              "drill": state["drilling"] or asked,
              "scout": msg.startswith(f"{who} scouts from")}[verb]
        return "" if ok else f"{verb} did not take: {msg[:80]}"
    return f"unreviewed chip shape: {cmd!r}"


@pytest.fixture(scope="module")
def census(tmp_path_factory):
    work = tmp_path_factory.mktemp("cn4")
    with pytest.MonkeyPatch.context() as mp:
        C.board_env(mp)
        stage(M.world)
        gs = C.game_state_now()
        recruitment = build_recruitment_payload(M.world)
        overview = C.overview_now()
        wizard_cases = _wizard_cases()
        first = C.render(gs, sorted(gs["map_data"]), recruitment, work,
                         overview=overview, wizard_cases=wizard_cases)
        # The same board after one keel: the yards at capacity this turn.
        fresh_staged()
        C.post(TestClient(M.app), {"command": "build ships"})
        gs2 = C.game_state_now()
        yards = naval.controlled_dockyards(M.world, "France")
        work2 = tmp_path_factory.mktemp("cn4k")
        second = C.render(gs2, yards, recruitment, work2)
    return {"gs": gs, "rendered": first["regions"], "cards": first["cards"],
            "overview": overview, "after_keel": second["regions"],
            "wizard_cases": wizard_cases, "wizard": first["wizard"],
            "yards": yards, "errors": first["errors"] + second["errors"]}


# ═══════════════════════════════════════════════════════════════════════════
# Every chip the region panel renders, driven
# ═══════════════════════════════════════════════════════════════════════════
class TestEveryPanelChipIsHonoured:

    def test_the_render_is_clean(self, census):
        assert census["errors"] == 0
        assert len(census["rendered"]) == len(census["gs"]["map_data"])

    def test_every_rendered_chip_acts_and_acts_on_what_it_names(self, census):
        chips = [(region, url, label, tail)
                 for region, bb in sorted(census["rendered"].items())
                 for url, label, tail in C.chips(bb)]
        kinds = {re.sub(r"\b(in|for) .*$|^\w+, (attack) .*|^land .*|^recruit \w+", r"\2",
                        C.chip_command(u)).strip() or C.chip_command(u)
                 for _r, u, _l, _t in chips}
        assert len(chips) > 100 and len(kinds) >= 10, (len(chips), kinds)
        bad = []
        with pytest.MonkeyPatch.context() as mp:
            C.board_env(mp)
            for region, url, label, tail in chips:
                client = fresh_staged()
                before = snapshot(M.world)
                response = C.post(client, {"command": C.chip_command(url)})
                after = snapshot(M.world)
                why = judge(region, url, label, tail, before, after, response)
                if why:
                    bad.append((region, url, why))
        assert bad == [], bad[:6]

    def test_the_attack_chip_is_an_order_not_a_declaration(self, census):
        """Only a court France is at war with: the ally (Deroy) and the
        neutral (Brunswick) beside Bernadotte get no chip; the enemy beside
        Ney and Davout does, by his printed name."""
        franconia = census["rendered"]["Franconia"]
        assert ", attack " not in franconia
        rhine = census["rendered"]["Rhineland"]
        assert "[url=do:Ney, attack Archduke Charles]" in rhine
        assert "[url=do:Davout, attack Archduke Charles]" in rhine

    def test_no_roster_key_reaches_the_panel(self, census):
        keys = [m.name for m in M.world.marshals.values()
                if humanize_entity_name(m.name) != m.name]
        assert keys, "no camelCase roster key on the board — the pin is vacuous"
        leaked = [(r, k) for r, bb in census["rendered"].items()
                  for k in keys if k in bb]
        assert leaked == [], leaked[:5]

    def test_a_dimmed_order_is_refused_for_the_reason_it_states(self, census):
        """Every Drill and Fortify the panel dims: `<M>, <verb>` is refused,
        and the reason beside the chip is the executor's own."""
        refusals = {"Drill": ("drill", drill_refusal),
                    "Fortify": ("fortify", fortify_refusal)}
        dimmed = []
        for region, bb in census["rendered"].items():
            for line in bb.split("\n"):
                for label, shown in re.findall(
                        r"\[color=#6f7480\](Drill|Fortify)\[/color\]  \[/bgcolor\] "
                        r"\[color=#[0-9a-f]+\]([^\[]+)\[/color\]", line):
                    who = re.match(r"\s*\[color=#[0-9a-f]+\]([^\[]+)\[/color\]",
                                   line).group(1)
                    dimmed.append((region, who, label, shown))
        labels = {d[2] for d in dimmed}
        assert labels == {"Drill", "Fortify"} and len(dimmed) >= 8, dimmed
        with pytest.MonkeyPatch.context() as mp:
            C.board_env(mp)
            for region, who, label, shown in dimmed:
                verb, predicate = refusals[label]
                client = fresh_staged()
                sentence, short = predicate(M.world, M.world.get_marshal(who))
                assert short == shown, (who, label, short, shown)
                response = C.post(client, {"command": f"{who}, {verb}"})
                assert not response.get("success"), (who, verb, response.get("message"))
                # The first line is the refusal; a stance refusal carries its
                # suggestion on the next.
                assert (response.get("message") or "").split("\n")[0] == sentence, (who, verb)

    def test_the_real_wizard_says_what_the_census_composes(self, census):
        """The engine-free wizard pins compose each echo from the template
        TEXT; a branch condition is invisible to that (the sweep proved it:
        disabling the cede branch left them green). So the REAL
        `_build_command` and `echo_note` run here, for every arm and both
        branches of the two conditional ones, and must equal what the census
        composes — which is what makes the engine-free pins trustworthy."""
        cases, echoes = census["wizard_cases"], census["wizard"]
        assert len(echoes) == len(cases) >= 27, (len(echoes), len(cases))
        for (action_id, nation, payload), (echo, note) in zip(cases, echoes):
            assert echo == _expected_echo(action_id, nation, payload), (
                action_id, payload, echo)
            assert bool(note) == (action_id == "propose_white_peace"), (action_id, note)
        assert [f"cede {CEDE_REGION} to Holland", ""] in echoes
        assert ["cede territory to Holland", ""] in echoes

    def test_the_generals_cards_offer_only_what_acts(self, census):
        """The Generals screen's own order chips, rendered by its own
        renderer from the real `/marshal_overview`: a card whose payload
        carries a Drill/Fortify reason shows that reason and no chip; every
        chip the cards DO show acts when sent."""
        cards_bb = census["cards"]
        assert cards_bb, "the harness rendered no Generals cards"
        dimmed_seen = 0
        for card in census["overview"]["marshals"]:
            name = card["name"]
            if card.get("captured") or card.get("is_broken") or card.get("is_retreating"):
                continue
            for verb, key, busy in (("drill", "drill_refusal", "is_drilling"),
                                    ("fortify", "fortify_refusal", "is_fortified")):
                why = card.get(key, "")
                url = f"[url=order:{verb}:{name}]"
                if card.get(busy):
                    continue
                if why:
                    assert url not in cards_bb, (name, verb, why)
                    assert why in cards_bb, (name, verb, why)
                    dimmed_seen += 1
                else:
                    assert url in cards_bb, (name, verb)
        assert dimmed_seen >= 4
        bad = []
        with pytest.MonkeyPatch.context() as mp:
            C.board_env(mp)
            for url, label, tail in C.chips(cards_bb):
                client = fresh_staged()
                before = snapshot(M.world)
                response = C.post(client, {"command": C.chip_command(url)})
                after = snapshot(M.world)
                why = judge("", url, label, tail, before, after, response)
                if why:
                    bad.append((url, why))
        assert bad == [], bad

    def test_the_second_keel_dims_the_dockyard_chip(self, census):
        """After one keel the yards are at capacity this turn: the chip is
        dimmed beside the Admiralty's own reason, and the order it would have
        sent is refused for that reason."""
        refusal = census["gs"]["naval_overlay"]["ship_build_refusal"]
        assert refusal == ""
        for yard in census["yards"]:
            bb = census["after_keel"][yard]
            assert "[url=do:build ships]" not in bb, yard
            assert "at capacity this season" in bb, yard
        with pytest.MonkeyPatch.context() as mp:
            C.board_env(mp)
            client = fresh_staged()
            assert C.post(client, {"command": "build ships"})["success"]
            second = C.post(client, {"command": "build ships"})
            assert not second["success"]
            assert second["message"] == naval.build_ships_refusal(M.world, "France")


# ═══════════════════════════════════════════════════════════════════════════
# The Substitutes quote is what the executor does (engine-free drift pin)
# ═══════════════════════════════════════════════════════════════════════════
def _boards():
    """Five boards: funded boot; bled corps (room under the ceiling); an
    empty treasury; no administrative action; the census board."""
    yield "boot", lambda w: w.nation_gold.__setitem__("France", 20000)

    def bled(w):
        w.nation_gold["France"] = 20000
        for name in ("Soult", "Bernadotte", "Massena", "Ney"):
            w.get_marshal(name).strength -= 12000
    yield "bled", bled
    yield "poor", lambda w: w.nation_gold.__setitem__("France", 100)

    def no_admin(w):
        w.nation_gold["France"] = 20000
        w.admin_actions_remaining = 0
    yield "no_admin", no_admin
    yield "census", stage


class TestTheSubstituteQuoteIsWhatTheExecutorDoes:

    @pytest.fixture
    def board(self, monkeypatch):
        C.board_env(monkeypatch)
        return TestClient(M.app)

    def test_every_province_every_board(self, board):
        mismatches, acting, kinds = [], 0, set()
        for label, prep in _boards():
            C.boot()
            prep(M.world)
            C.refresh_view(M.world)
            quotes = {r: EE.substitute_quote(M.world, r) for r in sorted(M.world.regions)}
            for region, quote in quotes.items():
                if not quote:
                    continue
                kinds.add(quote["kind"])
                cmd = f"buy substitutes for {quote['recipient']}"
                C.boot()
                prep(M.world)
                C.refresh_view(M.world)
                before = snapshot(M.world)
                response = C.post(TestClient(M.app), {"command": cmd})
                after = snapshot(M.world)
                who = quote["recipient"]
                if not quote["ok"]:
                    if response.get("success") or after != before:
                        mismatches.append((label, region, "quote refused, executor acted"))
                    elif response.get("message") != quote["reason"]:
                        mismatches.append((label, region, quote["reason"][:60],
                                           (response.get("message") or "")[:60]))
                else:
                    acting += 1
                    grew = after["marshals"][who]["strength"] - before["marshals"][who]["strength"]
                    paid = before["gold"] - after["gold"]
                    if not (response.get("success") and grew == quote["men"]
                            and paid == quote["price"]):
                        mismatches.append((label, region, quote["terms"], grew, paid,
                                           (response.get("message") or "")[:80]))
        assert mismatches == [], mismatches[:5]
        assert acting >= 5
        assert {"ok", "wrong_arm", "no_room", "treasury", "no_admin_ap"} <= kinds, kinds

    def test_the_cavalryman_is_not_the_recipient(self, board):
        """Franche-Comte at boot: Lannes (infantry) and Murat (cavalry) — the
        quote names Lannes; alone, Murat is refused with the executor's own
        sentence."""
        _ = board
        quote = EE.substitute_quote(M.world, "Franche-Comte")
        assert quote["recipient"] == "Lannes"
        # The cavalryman FIRST: Murat stands before Bernadotte in the roster,
        # so "the first marshal" and "the first infantryman" differ here (the
        # boot board could not tell them apart — the sweep proved it).
        M.world.get_marshal("Lannes").location = "Lorraine"
        M.world.get_marshal("Bernadotte").location = "Franche-Comte"
        order = [m.name for m in M.world.get_marshals_in_region("Franche-Comte")
                 if m.nation == "France"]
        assert order[0] == "Murat" and "Bernadotte" in order, order
        quote = EE.substitute_quote(M.world, "Franche-Comte")
        assert quote["recipient"] == "Bernadotte" and quote["kind"] != "wrong_arm", quote
        M.world.get_marshal("Bernadotte").location = "Franconia"
        quote = EE.substitute_quote(M.world, "Franche-Comte")
        assert quote["recipient"] == "Murat" and quote["kind"] == "wrong_arm"
        assert quote["reason"] == EE._msg_subs_wrong_arm(M.world.get_marshal("Murat"))

    def test_a_province_with_no_marshal_of_ours_has_no_quote(self, board):
        _ = board
        assert EE.substitute_quote(M.world, "Paris") == {}
        summary = M.world.get_filtered_game_state_summary()["map_data"]
        assert summary["Paris"]["substitute_here"] == {}
        assert summary["Rhineland"]["substitute_here"]["recipient"] == "Ney"


# ═══════════════════════════════════════════════════════════════════════════
# The Drill refusal is the executor's (engine-free)
# ═══════════════════════════════════════════════════════════════════════════
class TestTheDrillRefusalIsTheExecutors:

    def test_every_french_marshal_on_two_boards(self, monkeypatch):
        C.board_env(monkeypatch)
        checked = 0
        for prep in (lambda w: None, stage):
            C.boot()
            prep(M.world)
            C.refresh_view(M.world)
            names = [m.name for m in M.world.get_player_marshals() if m.strength > 0]
            for name in names:
                C.boot()
                prep(M.world)
                C.refresh_view(M.world)
                marshal = M.world.get_marshal(name)
                sentence, short = drill_refusal(M.world, marshal)
                response = C.post(TestClient(M.app), {"command": f"{name}, drill"})
                if sentence:
                    assert not response.get("success"), name
                    assert response.get("message") == sentence, name
                    assert short
                else:
                    assert response.get("success"), (name, response.get("message"))
                checked += 1
        assert checked >= 16

    def test_a_fortified_marshal_is_told_to_unfortify(self, monkeypatch):
        C.board_env(monkeypatch)
        lannes = M.world.get_marshal("Lannes")
        lannes.location = "Paris"
        lannes.fortified = True
        C.refresh_view(M.world)
        assert drill_refusal(M.world, lannes)[1] == "fortified — unfortify first"

    def test_the_payload_and_the_card_carry_it(self, monkeypatch):
        C.board_env(monkeypatch)
        from backend.game_logic.marshal_overview import build_marshal_overview
        md = M.world.get_filtered_game_state_summary()["map_data"]
        ney = next(m for m in md["Rhineland"]["marshals"] if m["name"] == "Ney")
        assert ney["tactical_state"]["drill_refusal"] == "Mack is at Swabia, one region away"
        card = next(c for c in build_marshal_overview(M.world) if c["name"] == "Ney")
        assert card["drill_refusal"] == "Mack is at Swabia, one region away"

    def test_an_aggressive_stance_refuses_both_orders_in_one_voice(self, monkeypatch):
        """The stance gate the player's road always applied, now the first
        gate of both predicates: the payload says so for both chips, and the
        typed orders are refused in the same words with the same suggestion.
        Before, the battery refused `drill` in aggressive stance while
        `_execute_drill` — the AI's road — had no such gate, and the two roads
        refused `fortify` in two different wordings."""
        from backend.commands.tactical_executor import order_refusal_response
        from backend.models.marshal import Stance
        C.board_env(monkeypatch)
        lannes = M.world.get_marshal("Lannes")
        lannes.location = "Paris"
        lannes.stance = Stance.AGGRESSIVE
        C.refresh_view(M.world)
        md = M.world.get_filtered_game_state_summary()["map_data"]
        row = next(m for m in md["Paris"]["marshals"] if m["name"] == "Lannes")
        for verb, predicate in (("fortify", fortify_refusal), ("drill", drill_refusal)):
            sentence, short = predicate(M.world, lannes)
            assert short == "aggressive stance — change stance first", verb
            assert row["tactical_state"][f"{verb}_refusal"] == short, verb
            response = C.post(TestClient(M.app), {"command": f"Lannes, {verb}"})
            suggestion = "Change stance first: 'Lannes defensive' or 'Lannes neutral'"
            # The endpoint appends the suggestion on its own line.
            assert not response.get("success")
            assert response.get("message") == f"{sentence}\n{suggestion}", verb
        # The executor's road: fortify refuses in the same words (it always
        # had the stance gate). Drill does NOT — that road (the AI's, and the
        # player's strategic/autonomous executions that skip the battery)
        # never had the gate, and giving it one moved BASELINE_SERIES, so
        # this UX slice leaves it and files the asymmetry (CQ-22). Pinned as
        # CURRENT so the fix flips it consciously.
        sentence, _ = fortify_refusal(M.world, lannes)
        assert order_refusal_response(M.world, lannes, "fortify")["message"] == sentence
        assert order_refusal_response(M.world, lannes, "drill", stance_gate=False) is None
        # Driven on the executor itself (the road the battery never sees):
        # he drills — the asymmetry as it stands, until CQ-22's gate.
        from backend.commands.executor import CommandExecutor
        direct = CommandExecutor()._tactical._execute_drill(
            {"marshal": "Lannes", "action": "drill"}, {"world": M.world})
        assert direct.get("success") is True, direct.get("message")

    def test_no_objection_speaks_for_an_order_the_executor_refuses(self, monkeypatch):
        """The pre-objection battery reads the WHOLE gate. The objection roll
        is forced to STRONG, so the pin is deterministic: a refused drill or
        fortify returns the refusal and raises nothing; an order that would
        act draws the forced objection (the control — the patch is live).
        Measured before: `Murat, drill` beside Mack drew "Murat firmly
        objects" on the roll's bad turns."""
        import backend.commands.executor as X
        C.board_env(monkeypatch)
        monkeypatch.setattr(X, "evaluate_situation",
                            lambda *a, **k: X.ConcernLevel.STRONG)
        monkeypatch.setattr(X, "apply_mood_variance", lambda concern: concern)
        client = fresh_staged()
        murat = M.world.get_marshal("Murat")
        sentence, _ = drill_refusal(M.world, murat)
        assert sentence
        response = C.post(client, {"command": "Murat, drill"})
        assert not response.get("success") and response.get("message") == sentence
        assert not M.world.pending_objection
        ney = M.world.get_marshal("Ney")
        sentence, _ = fortify_refusal(M.world, ney)
        assert "engaged with enemy forces" in sentence
        response = C.post(client, {"command": "Ney, fortify"})
        assert not response.get("success") and response.get("message") == sentence
        assert not M.world.pending_objection
        # The control: Lannes (in the senior yard, no enemy near) may drill —
        # the forced roll objects, so the patch is live.
        assert drill_refusal(M.world, M.world.get_marshal("Lannes")) == ("", "")
        C.post(client, {"command": "Lannes, drill"})
        assert (M.world.pending_objection or {}).get("marshal") == "Lannes"

    def test_the_at_war_flag_rides_only_foreign_marshals(self, monkeypatch):
        C.board_env(monkeypatch)
        md = M.world.get_game_state_summary()["map_data"]
        flags = {m["name"]: m.get("at_war_with_player")
                 for v in md.values() if isinstance(v, dict)
                 for m in v.get("marshals", [])}
        assert flags["Mack"] is True and flags["Deroy"] is False
        assert flags["Ney"] is None


# ═══════════════════════════════════════════════════════════════════════════
# The client's other command templates, extracted and driven (engine-free)
# ═══════════════════════════════════════════════════════════════════════════
def _func_body(src, name):
    body = src[src.index("func " + name):]
    nxt = body.find("\nfunc ", 10)
    return body if nxt < 0 else body[:nxt]


def _arms(body):
    return re.findall(r'^\t\t"(\w+)":\n((?:\t\t\t.*\n)+)', body, re.M)


def _compose(expr, **values):
    """Evaluate a GDScript string concatenation with the named variables."""
    out = ""
    for lit, name in re.findall(r'"((?:[^"\\]|\\.)*)"|([A-Za-z_]\w*(?:\([\w.,\s"]*\))?)', expr):
        if lit or (not name):
            out += lit
            continue
        key = re.sub(r"^str\((\w+)\)$", r"\1", name)
        key = re.sub(r"^int\(float\(action_payload\.get\(\"amount\", 200\)\)\)$", "amount", key)
        if key not in values:
            raise KeyError(name)
        out += str(values[key])
    return out


WIZARD_NATION = {  # a court on which the action is legal on the staged board
    "propose_armistice": "Austria", "propose_peace": "Austria",
    "open_settlement": "Austria", "propose_white_peace": "Austria",
    "send_ultimatum": "Prussia", "invest_vassal": "Holland",
    "increase_autonomy": "Holland", "decrease_autonomy": "Holland",
    "release_vassal": "Holland", "grant_region_to_vassal": "Holland",
}
PROPOSAL_WORD = {  # the treaty the confirm dialogue must name
    "propose_armistice": "Armistice", "propose_peace": "Peace Treaty",
    "propose_open_borders": "Open Borders", "propose_non_aggression": "Non-Aggression",
    "propose_defensive_alliance": "Defensive Alliance", "propose_alliance": "Alliance",
    "propose_vassal": "Vassalage",
}


def _wizard_cases():
    """Every `_build_command` arm with a court on which it is legal, and both
    branches of the two conditional arms."""
    src = (SCRIPTS / "diplomacy_wizard.gd").read_text(encoding="utf-8")
    cases = []
    for action_id, _code in _arms(_func_body(src, "_build_command")):
        nation = WIZARD_NATION.get(action_id, "Prussia")
        payloads = [{}]
        if action_id == "sponsor_design":
            payloads = [{"aim": "Hanover", "amount": 200}, {"amount": 200}]
        if action_id == "grant_region_to_vassal":
            payloads = [{"region": CEDE_REGION}, {}]
        for payload in payloads:
            cases.append([action_id, nation, payload])
    return cases


def _expected_echo(action_id, nation, payload):
    """What the census composes for a case — the branch chosen by the
    payload, as the GDScript chooses it."""
    src = (SCRIPTS / "diplomacy_wizard.gd").read_text(encoding="utf-8")
    rets = re.findall(r"return (.+)", dict(_arms(_func_body(src, "_build_command")))[action_id])
    if action_id == "sponsor_design":
        expr = rets[1] if payload.get("aim") else rets[0]
    elif action_id == "grant_region_to_vassal":
        expr = rets[1] if payload.get("region") else rets[0]
    else:
        assert len(rets) == 1, (action_id, rets)
        expr = rets[0]
    return _compose(expr.strip(), nation=nation, aim=payload.get("aim", ""),
                    amount=payload.get("amount", 200),
                    cede_region=payload.get("region", ""))


def _wizard_board():
    C.boot()
    w = M.world
    w.nation_gold["France"] = 20000
    w.diplomatic_points = max(int(getattr(w, "diplomatic_points", 0) or 0), 20)
    w.regions[CEDE_REGION].controller = "France"
    C.refresh_view(w)
    return TestClient(M.app)


def _names(response, nation):
    from backend.display_names import display_nation
    dlg = response.get("diplomatic_dialogue") or {}
    msg = response.get("message") or ""
    return ((isinstance(dlg, dict) and dlg.get("target_nation") == nation)
            or nation in msg or display_nation(nation) in msg)


class TestTheWizardSaysWhatItSends:

    @pytest.fixture
    def env(self, monkeypatch):
        C.board_env(monkeypatch)

    def test_every_build_command_template_reaches_its_court(self, env):
        src = (SCRIPTS / "diplomacy_wizard.gd").read_text(encoding="utf-8")
        arms = _arms(_func_body(src, "_build_command"))
        assert len(arms) >= 25, len(arms)
        bad = []
        for action_id, code in arms:
            nation = WIZARD_NATION.get(action_id, "Prussia")
            for ret in re.findall(r"return (.+)", code):
                text = _compose(ret.strip(), nation=nation, aim="Hanover", amount=200,
                                cede_region=CEDE_REGION)
                client = _wizard_board()
                if action_id == "cancel_mission":
                    # A LIVE mission: "court" opens the confirm; begin it.
                    # (Without this, the cancel answers the pending confirm —
                    # which is how a first reading mistook "Very well, Sire."
                    # for a recall.)
                    opened = C.post(client, {"command": f"court {nation}"})
                    dlg = opened.get("diplomatic_dialogue") or {}
                    with contextlib.redirect_stdout(io.StringIO()):
                        client.post("/respond_to_diplomatic_dialogue",
                                    json={"choice": "Begin mission",
                                          "dialogue_id": dlg.get("dialogue_id")})
                    assert M.world.active_diplomatic_mission, "no mission to cancel"
                response = C.post(client, {"command": text})
                if action_id in PROPOSAL_WORD:
                    dlg = response.get("diplomatic_dialogue") or {}
                    pattern = (r"regarding the [\w\- ]*" + PROPOSAL_WORD[action_id]
                               + r"[\w\- ]* proposal to " + nation)
                    ok = (dlg.get("target_nation") == nation
                          and re.search(pattern, response.get("message") or "") is not None)
                elif action_id == "propose_white_peace":
                    continue    # display-only echo — pinned below
                elif action_id == "cancel_mission":
                    ok = (response.get("success") and _names(response, nation)
                          and not M.world.active_diplomatic_mission)
                else:
                    ok = _names(response, nation)
                if not ok:
                    bad.append((action_id, text, (response.get("message") or "")[:100]))
        assert bad == [], bad[:5]

    def _structured(self, action_id, nation, payload=None):
        """Drive the wizard's structured road and its echo, typed."""
        src = (SCRIPTS / "diplomacy_wizard.gd").read_text(encoding="utf-8")
        code = dict(_arms(_func_body(src, "_build_command")))[action_id]
        rets = re.findall(r"return (.+)", code)
        region = (payload or {}).get("region", "")
        # The cede arm returns its bare form first and the named province
        # last; every other structured arm has one return.
        echo = _compose(rets[-1].strip() if region else rets[0].strip(),
                        nation=nation, cede_region=region)
        data = {"action": {"open_settlement": "propose_common_peace"}.get(action_id, action_id),
                "target_nation": nation}
        data.update(payload or {})
        client = _wizard_board()
        structured = C.post(client, {"command": echo, **data})
        after_structured = snapshot(M.world)
        client = _wizard_board()
        typed = C.post(client, {"command": echo})
        after_typed = snapshot(M.world)
        return echo, structured, typed, after_structured, after_typed

    @staticmethod
    def _same(a, b):
        da = a.get("diplomatic_dialogue") or {}
        db = b.get("diplomatic_dialogue") or {}
        return (bool(a.get("success")) == bool(b.get("success"))
                and (da.get("type") if isinstance(da, dict) else None)
                == (db.get("type") if isinstance(db, dict) else None)
                and (a.get("message") or "") == (b.get("message") or ""))

    def test_an_echo_is_its_own_order_or_says_it_is_not(self, env):
        """Every structured echo, TYPED (as the up-arrow re-sends it), must do
        what the structured road did — unless the wizard lists it as display
        copy, which main.gd then keeps off the up-arrow."""
        src = (SCRIPTS / "diplomacy_wizard.gd").read_text(encoding="utf-8")
        display_only = set(re.findall(r'^\t"(\w+)": "',
                                      src[src.index("const ECHO_IS_DISPLAY_ONLY"):
                                          src.index("func echo_note")], re.M))
        cases = [("open_settlement", "Austria", None),
                 ("propose_white_peace", "Austria", None),
                 ("grant_region_to_vassal", "Holland", {"region": CEDE_REGION}),
                 ("grant_region_to_vassal", "Holland", None)]
        for action_id, nation, payload in cases:
            echo, structured, typed, s_state, t_state = self._structured(
                action_id, nation, payload)
            same = self._same(structured, typed) and s_state == t_state
            if action_id in display_only:
                assert not same, (action_id, "listed as display copy but its echo "
                                  "does the same thing — take it off the list")
            else:
                assert same, (action_id, echo, (structured.get("message") or "")[:80],
                              (typed.get("message") or "")[:80])
        assert display_only == {"propose_white_peace"}

    def test_the_cede_echo_names_the_province(self, env):
        echo, structured, typed, s_state, _t = self._structured(
            "grant_region_to_vassal", "Holland", {"region": CEDE_REGION})
        assert echo == f"cede {CEDE_REGION} to Holland"
        assert structured.get("success") and M.world.regions[CEDE_REGION].controller == "Holland"

    def test_main_keeps_display_copy_off_the_up_arrow(self):
        src = (SCRIPTS / "main.gd").read_text(encoding="utf-8")
        body = _func_body(src, "_on_wizard_structured_command_selected")
        assert 'diplomacy_wizard.echo_note(str(data.get("action", "")))' in body
        gate = body.index('if echo_note == "":')
        assert body.index("_add_to_history(command)") > gate

    def test_the_vassal_and_reward_templates_reach_their_subject(self, env):
        ledger = (SCRIPTS / "diplomatic_ledger.gd").read_text(encoding="utf-8")
        reward = (SCRIPTS / "reward_dialog.gd").read_text(encoding="utf-8")
        templates = [_compose(ret.strip(), nation="Holland")
                     for _a, code in _arms(_func_body(ledger, "_vassal_chip_command"))
                     for ret in re.findall(r"return (.+)", code)]
        assert len(templates) == 4
        for tpl in re.findall(r'("(?:endow|grant|revoke) " \+ m_name[^,\n]*)', reward):
            templates.append(_compose(tpl.strip(), m_name="Ney", region=CEDE_REGION))
        assert len(templates) == 7, templates
        bad = []
        for text in templates:
            client = _wizard_board()
            response = C.post(client, {"command": text})
            subject = "Holland" if "Holland" in text else "Ney"
            if subject not in (response.get("message") or ""):
                bad.append((text, (response.get("message") or "")[:100]))
        assert bad == [], bad

    def test_the_generals_chips_reach_their_man(self, env):
        mm = (SCRIPTS / "marshal_management.gd").read_text(encoding="utf-8")
        verbs = set(re.findall(r'"order:(\w+):"', mm))
        assert verbs == {"fortify", "unfortify", "drill"}
        main = (SCRIPTS / "main.gd").read_text(encoding="utf-8")
        assert '_on_reward_command("commission " + candidate_name)' in main
        client = _wizard_board()
        response = C.post(client, {"command": "commission Marmont"})
        assert response.get("success") and "Marmont" in response["message"]
        assert M.world.get_marshal("Marmont") is not None


# ═══════════════════════════════════════════════════════════════════════════
# The Admiralty's backend-composed chips (engine-free)
# ═══════════════════════════════════════════════════════════════════════════
class TestTheAdmiraltyChipsAreTheirGates:

    def test_every_chip_on_three_boards(self, monkeypatch):
        """Each enabled chip's command acts; each disabled chip's command is
        refused — on the boot board, a poor board and after a keel."""
        C.board_env(monkeypatch)
        from backend.game_logic.ledger import build_strategic_ledger

        def boards():
            yield "boot", lambda w: None
            yield "poor", lambda w: w.nation_gold.__setitem__("France", 100)
            yield "keel", "keel"

        checked = 0
        for label, prep in boards():
            client = TestClient(M.app)
            C.boot()
            M.world.nation_gold["France"] = 20000
            if prep == "keel":
                C.post(client, {"command": "build ships"})
            else:
                prep(M.world)
            admiralty = build_strategic_ledger(M.world).get("admiralty") or {}
            chips = admiralty.get("chips") or []
            assert chips, label
            for chip in chips:
                C.boot()
                M.world.nation_gold["France"] = 20000
                if prep == "keel":
                    C.post(TestClient(M.app), {"command": "build ships"})
                else:
                    prep(M.world)
                response = C.post(TestClient(M.app), {"command": chip["command"]})
                assert bool(response.get("success")) == bool(chip["enabled"]), (
                    label, chip["command"], chip.get("reason"),
                    (response.get("message") or "")[:100])
                checked += 1
        assert checked >= 6


# ═══════════════════════════════════════════════════════════════════════════
# The inventory: every chip and template in the client is reviewed
# ═══════════════════════════════════════════════════════════════════════════
def _chip_urls(src):
    out = []
    for m in re.finditer(r"\b(?:Utils\.bb_button_chip|_button_chip)\(", src):
        i, depth, quote, buf = m.end(), 0, None, []
        while i < len(src):
            ch = src[i]
            if quote:
                buf.append(ch)
                if ch == quote:
                    quote = None
            elif ch in "\"'":
                quote = ch
                buf.append(ch)
            elif ch in "([{":
                depth += 1
                buf.append(ch)
            elif ch in ")]}":
                if depth == 0:
                    break
                depth -= 1
                buf.append(ch)
            elif ch == "," and depth == 0:
                break
            else:
                buf.append(ch)
            i += 1
        out.append(re.sub(r"\s+", " ", "".join(buf).replace("\\\n", " ")).strip())
    return out


# Every chip url in the client, with its verdict. A new chip fails until a
# row names how it is driven — the memo's "0 unreviewed rows".
REVIEWED = {
    # region_panel.gd — DRIVEN by TestEveryPanelChipIsHonoured
    ("region_panel.gd", '"do:recruit " + str(arm) + " in " + _region'): "driven (CN-3 + here)",
    ("region_panel.gd", '"do:buy substitutes for " + str(sub_q.get("recipient", ""))'): "driven; quote drift-pinned",
    ("region_panel.gd", '"do:" + str(def[2]) % _region'): "driven (five buildings)",
    ("region_panel.gd", '"do:build watchtower in " + _region'): "driven",
    ("region_panel.gd", '"do:repair buildings in " + _region'): "driven",
    ("region_panel.gd", '"do:repair " + _region'): "driven",
    ("region_panel.gd", '"do:build ships"'): "driven; nation-scoped, the yard disclosed (NV-12)",
    ("region_panel.gd", '"do:land " + who + " in " + _region'): "driven (the quote step)",
    ("region_panel.gd", '"do:" + m_name + ", attack " + enemy_shown'): "driven; at-war courts only",
    ("region_panel.gd", '"order:unfortify:" + m_name'): "driven",
    ("region_panel.gd", '"order:fortify:" + m_name'): "driven",
    ("region_panel.gd", '"order:drill:" + m_name'): "driven; dimmed with the executor's reason",
    ("region_panel.gd", '"order:scout:" + m_name'): "driven",
    ("region_panel.gd", '"negotiate:" + controller'): "opens the wizard at that court; sends nothing",
    # NUI "The Admiralty on the Map" (Sept 23, 2026): THE SEA block's link
    ("region_panel.gd", '"admiralty"'): "opens THE ADMIRALTY (Ledger book 7) via main.gd; sends nothing",
    # marshal_management.gd
    ("marshal_management.gd", '"order:unfortify:" + chip_name'): "same command as the panel's",
    ("marshal_management.gd", '"order:fortify:" + chip_name'): "same command as the panel's",
    ("marshal_management.gd", '"order:drill:" + chip_name'): "same command; dimmed with the card's reason",
    ("marshal_management.gd", '"commission:" + cname'): "driven: `commission <name>`",
    ("marshal_management.gd", '"commission_open"'): "opens the bench; sends nothing",
    ("marshal_management.gd", '"commission_back"'): "closes the bench; sends nothing",
    ("marshal_management.gd", '"reward:" + str(index)'): "opens the reward dialog; its commands driven",
    ("marshal_management.gd", "url_meta"): "the wrapper's own body",
    ("marshal_management.gd", "url_meta: String"): "the wrapper's signature",
    # diplomatic_ledger.gd
    ("diplomatic_ledger.gd", "meta"): "vassal:<action>:<nation> — driven via _vassal_chip_command; vassal_cede opens the wizard",
    ("diplomatic_ledger.gd", '"talleyrand_assess"'): "sends `Talleyrand, assess our situation` (W6-9)",
    # strategic_ledger.gd — backend-composed
    ("strategic_ledger.gd", '"do:" + str(chip.get("command", ""))'): "driven: the Admiralty's chips",
    # tutorial_overlay.gd
    ("tutorial_overlay.gd", '"suggest:" + str(step["suggest"])'): "fills the line, never sends (T-B1 pins each parse)",
    ("tutorial_overlay.gd", '"skipdone:"'): "concludes the lesson; sends nothing",
    # Sept 23, 2026 (the School of War refresh): the two new chips, both
    # observe-only — neither reaches /command.
    ("tutorial_overlay.gd", '"skipstep:"'): "releases the current card with a word; sends nothing",
    ("tutorial_overlay.gd", '"open:" + str(step["open"])'): "asks main.gd to open the real Cabinet on the named court (open_cabinet); sends nothing",
}


class TestTheInventoryIsComplete:

    def test_every_chip_url_is_reviewed(self):
        found = set()
        for path in sorted(SCRIPTS.glob("*.gd")):
            if path.name == "utils.gd":
                continue
            for expr in _chip_urls(path.read_text(encoding="utf-8")):
                found.add((path.name, expr))
        unreviewed = sorted(found - set(REVIEWED))
        stale = sorted(set(REVIEWED) - found)
        assert unreviewed == [], unreviewed
        assert stale == [], stale

    def test_the_census_sees_a_new_chip(self):
        """Sensitivity: a chip added to a producer is caught."""
        src = (SCRIPTS / "region_panel.gd").read_text(encoding="utf-8")
        planted = src + '\n\tvar x = Utils.bb_button_chip("do:burn " + _region, "Burn", "fff", "000")\n'
        assert '"do:burn " + _region' in _chip_urls(planted)
        assert ("region_panel.gd", '"do:burn " + _region') not in REVIEWED
