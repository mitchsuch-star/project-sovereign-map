"""CN-3 — "The Chip Names the Man", the client half (the Command-Road Queue,
slice 3). Build contract: `docs/audits/RECRUIT_ARM_UX_2026_09_20.md` R3 + the
§5 riders; landing record appended there.

CN-1 made the backend quote every recruit chip with the executor's own steps
(`economy_executor.recruit_quote`, drift-pinned against `/command` on every
province). This file pins that the CHIP says what the quote says:

* the row renders where the backend quoted it (`recruit_here`), one chip per
  arm, ENABLED only where the quote says the levy will be made and stating
  its terms — the man, the men, the gold, the pool — otherwise DIMMED beside
  the backend's own reason (the memo's R3 done_when: zero chips enabled and
  refusing, zero enabled and raising the wrong arm; measured before, 69 of 90
  and 14 of 21);
* the ground speaks first: a province's own gates (whose soil, unrest) refuse
  before a man is chosen, because no marshal can remedy them — measured with
  the man first, `recruit artillery in Milan` told the player to commission
  Marmont for 4,500g on soil where no French levy is raised (ruling D5);
* a remedy that names an order names one the game takes — measured, Paris
  told the player "give him the order yourself: 'Massena, recruit infantry'"
  while Massena stood on Milan, where that order is refused;
* the riders: the marshal row names the arm, the ordinance line says its
  multiplier, the commission bench tags every arm and every pool.

The client pins are DRIVEN: `tools/cn3_region_panel_harness.gd` runs the real
`region_panel.gd` and `marshal_management.gd` headless on the live payload,
and every `do:` url the panel rendered is sent through POST /command. They
SKIP when the engine is absent — and a skip is not a pass.
"""

import contextlib
import io
import json
import os
import pathlib
import re
import shutil
import subprocess

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands import economy_executor as EE
from backend.commands.parser import CommandParser
from backend.models.world_state import RECRUIT_ARMS

REPO = pathlib.Path(__file__).resolve().parents[1]
PROJECT = REPO / "godot-client" / "project-sovereign"
HARNESS = REPO / "tools" / "cn3_region_panel_harness.gd"
ARM_WORD = {"infantry": "foot", "cavalry": "horse", "artillery": "guns",
            "emperor": "Guard"}
NOT_OUR_SOIL = "not our soil — our levies are raised on our own ground"

_CANDIDATES = [
    os.environ.get("GODOT_BIN", ""),
    r"C:\Users\User\Downloads\Godot_v4.4.1-stable_win64.exe"
    r"\Godot_v4.4.1-stable_win64.exe",
    "godot",
    "godot4",
]


def _engine():
    for candidate in _CANDIDATES:
        if not candidate:
            continue
        if os.path.sep in candidate or "/" in candidate:
            if pathlib.Path(candidate).is_file():
                return candidate
            continue
        found = shutil.which(candidate)
        if found:
            return found
    return None


# ═══════════════════════════════════════════════════════════════════════════
# Harness
# ═══════════════════════════════════════════════════════════════════════════
def _boot():
    with contextlib.redirect_stdout(io.StringIO()):
        M._reset_world_state()


def _fund(gold=20000):
    M.world.nation_gold["France"] = gold


def _state():
    w = M.world
    return (dict(w.manpower_pools.get("France", {})),
            int(w.nation_gold.get("France", 0)),
            (w.actions_remaining, w.admin_actions_remaining))


def _drive(client, text):
    pools, gold, ap = _state()
    with contextlib.redirect_stdout(io.StringIO()):
        response = client.post("/command", json={"command": text}).json()
    pools2, gold2, ap2 = _state()
    delta = {k: pools2.get(k, 0) - pools.get(k, 0) for k in pools
             if pools2.get(k, 0) != pools.get(k, 0)}
    events = response.get("events") or []
    via = events[0].get("marshal") if events else None
    return {"ok": bool(response.get("success")), "pool": delta,
            "gold": gold - gold2, "ap": (ap, ap2), "via": via,
            "message": response.get("message") or ""}


def _board_env(mp):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        mp.delenv(key, raising=False)
    mp.setenv("LLM_MODE", "mock")
    _boot()
    mp.setattr(M, "parser", CommandParser(use_real_llm=False))
    assert M.parser.llm.use_real_api is False


@pytest.fixture
def board(monkeypatch):
    _board_env(monkeypatch)
    return TestClient(M.app)


def _chip_urls(bbcode):
    return re.findall(r"\[url=do:(recruit [^\]]*)\]", bbcode)


def _chips(bbcode):
    """(command, label) for every recruit chip url the panel rendered — the
    label is what the player reads, so the effect is judged against it."""
    return re.findall(r"\[url=do:(recruit [^\]]*)\](?:\[color=#[0-9a-fA-F]+\])?"
                      r"([^\[]*)", bbcode)


@pytest.fixture(scope="module")
def driven(tmp_path_factory):
    """One headless run of the real panel on the funded 1805 boot payload."""
    engine = _engine()
    if engine is None:
        pytest.skip("Godot engine not on this machine — the driven pins skip, "
                    "and a skip is not a pass")
    from backend.game_logic.recruitment import build_recruitment_payload
    work = tmp_path_factory.mktemp("cn3")
    with pytest.MonkeyPatch.context() as mp:
        _board_env(mp)
        _fund()
        client = TestClient(M.app)
        with contextlib.redirect_stdout(io.StringIO()):
            game_state = client.get("/test").json()["game_state"]
        recruitment = build_recruitment_payload(M.world)
    out = work / "rendered.json"
    log = work / "godot.log"
    spec = work / "spec.json"
    spec.write_text(json.dumps({
        "game_state": game_state,
        "regions": sorted(game_state["map_data"]),
        "recruitment": recruitment,
        "out": str(out),
    }), encoding="utf-8")
    env = dict(os.environ, CN3_SPEC=str(spec), CN3_OUT=str(out))
    proc = subprocess.run(
        [engine, "--headless", "--path", str(PROJECT), "--log-file", str(log),
         "--script", str(HARNESS)],
        capture_output=True, text=True, timeout=300, env=env,
        cwd=str(PROJECT))
    if not out.is_file():
        pytest.fail("the harness wrote no result\n"
                    f"exit={proc.returncode}\nstderr tail:\n{proc.stderr[-2000:]}")
    result = json.loads(out.read_text(encoding="utf-8"))
    log_text = log.read_text(encoding="utf-8", errors="replace") if log.is_file() else ""
    return {"gs": game_state, "rendered": result.get("regions", {}),
            "bench": result.get("bench", ""), "error": result.get("error"),
            "script_errors": log_text.count("SCRIPT ERROR"),
            "recruitment": recruitment}


# ═══════════════════════════════════════════════════════════════════════════
# The chip, driven (the memo's R3 done_when)
# ═══════════════════════════════════════════════════════════════════════════
class TestTheChipTellsTheTruth:

    def test_the_harness_ran_clean(self, driven):
        assert driven["error"] is None, driven["error"]
        assert driven["script_errors"] == 0
        assert len(driven["rendered"]) == len(driven["gs"]["map_data"])

    def test_the_harness_is_in_the_parse_check_list(self):
        """Engine-free: a driven harness that stops parsing fails its pins
        with no output; the committed parse check names the line."""
        check = (REPO / "tools" / "godot_parse_check.gd").read_text(encoding="utf-8")
        assert '"res://../../tools/cn3_region_panel_harness.gd"' in check

    def test_every_enabled_chip_acts_and_raises_its_arm(self, driven):
        """Every `do:recruit` url the REAL panel rendered, sent through POST
        /command on a fresh funded board: it must act, and raise the arm its
        label names. Measured before CN: 69 of 90 refused, and 14 of the 21
        that acted raised another arm."""
        enabled = [(region, cmd, label)
                   for region, bb in driven["rendered"].items()
                   for cmd, label in _chips(bb)]
        quoted = [(r, a) for r, v in driven["gs"]["map_data"].items()
                  for a, q in (v.get("recruit_here") or {}).items() if q["ok"]]
        assert len(enabled) == len(quoted) >= 12, (len(enabled), len(quoted))
        bad = []
        with pytest.MonkeyPatch.context() as mp:
            _board_env(mp)
            for region, cmd, label in enabled:
                arm = label.strip().lower()
                assert arm in RECRUIT_ARMS and cmd.endswith(f" in {region}"), (
                    cmd, label)
                _boot()
                _fund()
                res = _drive(TestClient(M.app), cmd)
                if not (res["ok"] and list(res["pool"]) == [arm]):
                    bad.append((label, cmd, res["via"], res["pool"],
                                res["message"][:90]))
        assert bad == [], bad

    def test_a_dimmed_chip_carries_the_backends_reason(self, driven):
        """Where the quote refuses, no url is rendered for that arm and the
        backend's own `short` stands beside the dimmed chip; a province the
        backend did not quote renders no recruit chip at all."""
        missing = []
        for region, data in driven["gs"]["map_data"].items():
            bb = driven["rendered"][region]
            rh = data.get("recruit_here") or {}
            if not rh:
                assert _chip_urls(bb) == [], region
                assert "Recruit:" not in bb, region
                continue
            for arm, q in rh.items():
                url = f"[url=do:recruit {arm} in {region}]"
                if q["ok"]:
                    assert bb.count(url) == 1, (region, arm)
                    assert q["terms"] and q["terms"] in bb, (region, arm)
                else:
                    assert url not in bb, (region, arm)
                    if not q["short"] or q["short"] not in bb:
                        missing.append((region, arm, q["short"]))
        assert missing == [], missing[:5]

    def test_ally_soil_renders_one_dimmed_reason(self, driven):
        """Ruling D5 — recruiting does not open on ally soil. Milan and
        Franconia render the row (a French corps stands on each) as three
        dimmed chips beside ONE reason, the ground's."""
        for region in ("Milan", "Franconia"):
            bb = driven["rendered"][region]
            assert "Recruit:" in bb
            assert _chip_urls(bb) == []
            assert bb.count(NOT_OUR_SOIL) == 1, region

    def test_the_marshal_row_names_the_arm(self, driven):
        """Rider 1: the payload's `arm` on every marshal the row lists — the
        cavalryman and the infantryman in one province are told apart."""
        seen = set()
        for region, data in driven["gs"]["map_data"].items():
            for m in data.get("marshals") or []:
                if int(m.get("strength", 0)) <= 0 or not m.get("arm"):
                    continue
                label = f"({int(m['strength']):,} {ARM_WORD[m['arm']]})"
                assert label in driven["rendered"][region], (region, m["name"], label)
                seen.add(m["arm"])
        assert {"infantry", "cavalry", "emperor"} <= seen, seen

    def test_the_ordinance_says_its_price(self, driven):
        """Rider 4: over the force limit the ordinance is a PRICE — the line
        says the multiplier the pricer applies instead of a bare warning."""
        levy = driven["gs"]["levy"]
        assert levy["over_by"] > 0 and levy["ordinance_mult_pct"] > 100
        line = (f"{levy['over_by']:,} over the ordinance — every levy costs "
                f"×{levy['ordinance_mult_pct'] / 100:.2f}")
        assert line in driven["rendered"]["Rhineland"]
        assert "foot here" not in driven["rendered"]["Rhineland"]

    def test_the_bench_names_every_arm_and_every_pool(self, driven):
        """Rider 2: France's two gun marshals rendered untagged under an
        "Infantry pool" header promising them a 5,000 corps."""
        bench = driven["bench"]
        pools = driven["recruitment"]["pools"]
        assert (f"Pools: {pools['infantry']:,} foot · {pools['cavalry']:,} horse"
                f" · {pools['artillery']:,} guns") in bench
        gunners = [c for c in driven["recruitment"]["candidates"]
                   if c["arm"] == "artillery"]
        assert {c["name"] for c in gunners} >= {"Marmont", "Senarmont"}
        assert bench.count("[Artillery]") == len(gunners)
        assert f"a corps of {gunners[0]['corps']:,} guns" in bench
        infantry = [c for c in driven["recruitment"]["candidates"]
                    if c["arm"] == "infantry"]
        assert bench.count("[Infantry]") == len(infantry)


# ═══════════════════════════════════════════════════════════════════════════
# The ground speaks first
# ═══════════════════════════════════════════════════════════════════════════
class TestTheGroundSpeaksFirst:

    def test_ally_soil_refuses_every_arm_on_the_ground(self, board):
        _fund()
        for arm in (None,) + RECRUIT_ARMS:
            text = f"recruit {arm} in Milan" if arm else "recruit in Milan"
            res = _drive(board, text)
            assert not res["ok"] and not res["pool"] and res["gold"] == 0, text
            assert res["message"] == EE._msg_not_controlled("Milan"), (
                text, res["message"])

    def test_the_artillery_quote_on_ally_soil_offers_no_commission(self, board):
        quote = EE.recruit_quote(M.world, "Milan", arm="artillery")
        assert quote["kind"] == "not_controlled", quote
        assert quote["short"] == NOT_OUR_SOIL
        assert "commission" not in quote["reason"]

    def test_enemy_soil_says_whose_it_is(self, board):
        """Before: "No marshal is available to receive reinforcements at
        Vienna … March a corps within range" — a remedy that could not work."""
        _fund()
        res = _drive(board, "recruit infantry in Vienna")
        assert not res["ok"] and not res["pool"] and res["gold"] == 0
        assert res["message"] == EE._msg_not_controlled("Vienna")

    def test_unrest_speaks_before_the_selector(self, board):
        """Berry: our soil, nobody within reach at boot. In unrest, the levy
        is refused for the unrest — marching a corps there would not help."""
        _fund()
        berry = M.world.get_region("Berry")
        berry.stability = 40
        res = _drive(board, "recruit in Berry")
        assert not res["ok"] and not res["pool"] and res["gold"] == 0
        assert res["message"] == EE._msg_unrest("Berry", berry)
        quote = EE.recruit_quote(M.world, "Berry", arm="cavalry")
        assert quote["kind"] == "unrest" and "stability 40/100" in quote["short"]

    def test_the_capital_levy_speaks_for_its_ground(self, board):
        """The bare `recruit` (the capital branch): nobody stands within
        reach of Paris at boot. With the capital in unrest the refusal is the
        unrest's, not "no marshal is available" and its march-a-corps advice."""
        _fund()
        paris = M.world.get_region("Paris")
        paris.stability = 40
        for text in ("recruit", "recruit cavalry"):
            res = _drive(board, text)
            assert not res["ok"] and not res["pool"] and res["gold"] == 0, text
            assert res["message"] == EE._msg_unrest("Paris", paris), (
                text, res["message"])

    def test_a_stable_province_with_nobody_in_reach_still_says_so(self, board):
        """Control: the reorder moves only the ground's own refusals."""
        _fund()
        res = _drive(board, "recruit in Berry")
        assert res["message"].startswith(
            "Berthier scans the dispatches. 'No marshal is available to "
            "receive reinforcements at Berry, Sire.'"), res["message"]

    def test_the_named_road_keeps_its_order(self, board):
        _fund()
        res = _drive(board, "Massena, recruit infantry")
        assert not res["ok"] and not res["pool"]
        assert res["message"] == EE._msg_not_controlled("Milan")

    def test_an_unknown_province_is_named_as_unknown(self, board):
        kind, sentence = EE.recruit_ground_refusal(M.world, "Atlantis", "France")
        assert kind == "unknown_region" and sentence == "Unknown region: Atlantis"
        assert EE.recruit_quote(M.world, "Atlantis")["reason"] == sentence


# ═══════════════════════════════════════════════════════════════════════════
# A remedy is an order the game takes
# ═══════════════════════════════════════════════════════════════════════════
class TestTheRemedyIsAnOrderTheGameTakes:

    def test_every_quoted_order_acts(self, board):
        """Every `'<Name>, recruit <arm>'` any refusal on the board quotes,
        sent on a fresh funded board: it must act."""
        orders = set()
        for province in sorted(M.world.regions):
            for arm in RECRUIT_ARMS:
                q = EE.recruit_quote(M.world, province, arm=arm)
                orders.update(re.findall(r"'([A-Z][\w\- ]+, recruit \w+)'",
                                         q["reason"]))
        assert orders, "no refusal quotes an order — the pin is vacuous"
        refused = []
        for order in sorted(orders):
            _boot()
            _fund()
            res = _drive(TestClient(M.app), order)
            if not res["ok"]:
                refused.append((order, res["message"][:100]))
        assert refused == [], refused

    def test_a_man_on_foreign_soil_is_told_to_march_not_ordered(self, board):
        quote = EE.recruit_quote(M.world, "Paris", arm="infantry")
        assert quote["kind"] == "no_arm_in_range"
        assert ("Massena commands our foot at Milan — march him within "
                "reach.") in quote["reason"], quote["reason"]
        assert "'Massena, recruit infantry'" not in quote["reason"]

    def test_a_man_on_our_soil_is_given_the_order(self, board):
        quote = EE.recruit_quote(M.world, "Paris", arm="cavalry")
        assert "'Murat, recruit cavalry'" in quote["reason"], quote["reason"]


# ═══════════════════════════════════════════════════════════════════════════
# The quote speaks for the chip — shown is applied
# ═══════════════════════════════════════════════════════════════════════════
_TERMS = re.compile(r"^(?P<man>[\w\- ]+) · (?P<men>[\d,]+) (?P<noun>foot|horse|guns)"
                    r" · (?P<gold>[\d,]+)g(?P<field> · field levy)?"
                    r" \(pool (?P<pool>[\d,]+)\)$")


class TestTheQuoteSpeaksForTheChip:

    def test_the_terms_are_what_the_levy_does(self, board):
        """Every enabled chip's words, against the executor's effect: the
        man it names receives, the men it names arrive, the gold it names is
        charged, the pool it names is the pool drawn."""
        _fund()
        quotes = []
        for province in sorted(M.world.regions):
            for arm in RECRUIT_ARMS:
                q = EE.recruit_quote(M.world, province, arm=arm)
                if q["ok"]:
                    quotes.append((province, arm, q))
        assert len(quotes) >= 12
        bad = []
        for province, arm, q in quotes:
            m = _TERMS.match(q["terms"])
            assert m, q["terms"]
            _boot()
            _fund()
            pool_before = M.world.manpower_pools["France"][arm]
            res = _drive(TestClient(M.app), f"recruit {arm} in {province}")
            men = -res["pool"].get(arm, 0)
            if not (res["ok"] and res["via"] == m["man"]
                    and men == int(m["men"].replace(",", ""))
                    and res["gold"] == int(m["gold"].replace(",", ""))
                    and pool_before == int(m["pool"].replace(",", ""))
                    and m["noun"] == ARM_WORD[arm]
                    and bool(m["field"]) == q["field_capped"]):
                bad.append((province, arm, q["terms"], res))
        assert bad == [], bad[:3]

    def test_a_short_refusal_names_the_real_figures(self, board):
        world = M.world
        world.nation_gold["France"] = 50
        q = EE.recruit_quote(world, "Rhineland", arm="infantry")
        assert q["kind"] == "treasury"
        assert q["short"] == f"{q['price']:,}g — the treasury holds 50g"
        _fund()
        world.manpower_pools["France"]["cavalry"] = 1200
        q = EE.recruit_quote(world, "Rhineland", arm="cavalry")
        assert q["kind"] == "pool_short"
        assert q["short"] == f"the cavalry pool holds 1,200 of the {q['amount']:,} needed"
        world.admin_actions_remaining = 0
        q = EE.recruit_quote(world, "Rhineland", arm="infantry")
        assert q["short"] == "no administrative action left this turn"

    def test_the_ordinance_multiplier_is_the_pricers(self, board, monkeypatch):
        """`ordinance_mult_pct` is the (1 + overage) `_calculate_recruit_cost`
        applies — measured as the ratio of the price over the limit to the
        price with the limit lifted, not re-derived from the formula."""
        levy = EE.get_levy_status(M.world, "France")
        assert levy["over_by"] > 0
        region = M.world.get_region("Rhineland")
        pricer = EE._levy_pricer()
        over = pricer._calculate_recruit_cost(region, M.world, base_cost=100000,
                                              nation="France")
        monkeypatch.setattr(type(M.world), "get_force_limit",
                            lambda self, nation: 10 ** 9)
        under = pricer._calculate_recruit_cost(region, M.world, base_cost=100000,
                                               nation="France")
        assert abs(over / under * 100 - levy["ordinance_mult_pct"]) <= 0.5, (
            over, under, levy["ordinance_mult_pct"])
        assert EE.get_levy_status(M.world, "France")["ordinance_mult_pct"] == 100

    def test_the_result_names_every_term_the_price_carries(self, board):
        """Rider 5: the result named the capital discount and the Intendance
        and never the ×3 war or the ordinance — together 4.36× of a 741-gold
        charge. The note is the list the pricer priced with."""
        _fund()
        mult = EE.get_levy_status(M.world, "France")["ordinance_mult_pct"] / 100
        res = _drive(board, "recruit infantry in Rhineland")
        assert res["ok"] and res["gold"] == 741, res
        assert (f"Cost: 741 gold (×3 at war) (×{mult:.2f} over the ordinance) "
                f"(Davout's intendance: -15%).") in res["message"], res["message"]

    def test_the_capital_names_its_discount_first(self, board):
        _fund()
        soult = M.world.get_marshal("Soult")
        soult.location = "Paris"
        res = _drive(board, "recruit infantry in Paris")
        assert res["ok"], res["message"]
        assert "gold (capital discount) (×3 at war) (×" in res["message"], (
            res["message"])

    def test_the_legacy_world_names_no_war_price(self):
        """N1: the legacy fixture boots at war and its levy is never priced
        for it — so the note must not claim a ×3 it did not charge."""
        from backend.commands.executor import CommandExecutor
        from backend.models.world_state import WorldState
        with contextlib.redirect_stdout(io.StringIO()):
            legacy = WorldState(player_nation="France")
            region = legacy.get_region("Paris")
            cost, terms = CommandExecutor()._economy._recruit_cost_terms(
                region, legacy, base_cost=200, nation="France")
        assert (cost, terms) == (150, ["capital discount"])

    def test_the_legacy_world_carries_no_multiplier(self):
        from backend.models.world_state import WorldState
        with contextlib.redirect_stdout(io.StringIO()):
            legacy = WorldState(player_nation="France")
        assert EE.get_levy_status(legacy)["ordinance_mult_pct"] == 100
