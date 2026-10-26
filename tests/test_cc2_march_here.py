"""Row CC, CC-2 "March here" (Pre-Deploy S13c part 1, October 2026).

The province panel offers the click orders a player most often types — march
here, support the corps standing here, attack the enemy seen here — each a
chip that sends the SAME command a typed line would, priced and timed by the
backend's QUOTE (`backend/commands/order_quotes.py`, served read-only by
GET /march_quotes). The quote reads the order's own pure readers: the state
probe every chip dims by, CRT-4's road reader and arrival law, the strategic
price by keyword, the concern evaluators.

The pins:

* THE DRIFT CENSUS — every quote against what POST /command then does on a
  fresh board: taken or refused alike, the refusal in the executor's own
  words, the actions spent, the objection quoted as possible whenever one is
  raised, the first step's contact named whenever the order meets it. The
  full boot census (every marshal × every province, 1,000 cells) read
  1,000 / 1,000 when the slice landed; the pin runs the boot board's
  neighbourhood and a seeded sample, and two state variants.
* FOG — no quote names a corps we cannot see.
* READ-ONLY — the route writes nothing: the world's serialised state, the
  random stream and the popup queues are what they were.
* CC-X8 — a march the game refuses leaves a squared corps in its square.
* The client, DRIVEN (`tools/cc_client_harness.gd`): the panel asks for its
  quotes, renders them as quoted, drops a stale answer, sends a chip's
  command through the chip road and asks again after the reply. SKIPS when
  the engine is absent — and a skip is not a pass.
"""

import collections
import contextlib
import io
import json
import os
import random
import re
import subprocess

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands import executor as executor_mod
from backend.commands import objection_v2 as ov2
from backend.commands import strategic_executor as se_mod
from backend.commands.order_quotes import (
    attack_quote, march_quote, march_quotes_for_region, support_quote,
)
from backend.display_names import humanize_entity_name
from backend.models.intel import FULL, PARTIAL
from tests import _chip_census as C
from tests.test_cc_click_and_command import _pick_board

REPO = C.REPO
PROJECT = C.PROJECT
HARNESS = REPO / "tools" / "cc_client_harness.gd"


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


def _post(client, command):
    with _quiet():
        return client.post("/command", json={"command": command}).json()


@pytest.fixture(scope="module")
def board():
    """A mock-parser 1805 board with the mood variance pinned flat (the ONE
    source of randomness in the objection triggers)."""
    with pytest.MonkeyPatch.context() as mp:
        C.board_env(mp)
        flat = (lambda concern: concern)
        mp.setattr(executor_mod, "apply_mood_variance", flat)
        mp.setattr(se_mod, "apply_mood_variance", flat)
        mp.setattr(ov2, "apply_mood_variance", flat)
        yield TestClient(M.app)


@pytest.fixture
def client(monkeypatch):
    """The same board for ONE test. The suite's conftest pins the bare
    no-scenario world before every test (an autouse function fixture), so a
    test that boots its own board must re-open the 1805 campaign itself; the
    module fixtures above are set up before that pin and keep theirs."""
    C.board_env(monkeypatch)
    flat = (lambda concern: concern)
    monkeypatch.setattr(executor_mod, "apply_mood_variance", flat)
    monkeypatch.setattr(se_mod, "apply_mood_variance", flat)
    monkeypatch.setattr(ov2, "apply_mood_variance", flat)
    return TestClient(M.app)


# ═══ the drift census ═══════════════════════════════════════════════════════

def _unseen_blocker(world, marshal, road) -> bool:
    """An UNSEEN corps on the first step's reach: the executor meets him,
    the quote must not name him (fog) — such cells are counted, not
    compared."""
    reach = max(1, int(marshal.movement_range or 1))
    for region in (road or [])[:reach]:
        if (world.get_enemies_in_region(region, world.player_nation)
                and world.get_region_intel(region).visibility not in (FULL, PARTIAL)):
            return True
    return False


def _drive_cell(client, quote_fn, setup=None):
    """Quote on a fresh board, then send the quoted command on another fresh
    board set up the same way; return the verdict."""
    C.boot()
    if setup:
        setup(M.world)
    q, subject_key, other_key = quote_fn(M.world)
    fog = _unseen_blocker(M.world, M.world.get_marshal(subject_key), q["road"])
    C.boot()
    if setup:
        setup(M.world)
    world = M.world
    ap0 = int(world.actions_remaining)
    other_strength = int(world.get_marshal(other_key).strength) if other_key else None
    r = _post(client, q["command"])
    world = M.world
    m = world.get_marshal(subject_key)
    ap_spent = ap0 - int(world.actions_remaining)
    asked = bool(r.get("pending_objection") or r.get("objection") or r.get("requires_input")
                 or r.get("pending_interrupt"))
    objection = bool(r.get("pending_objection") or r.get("objection"))
    fought = (other_key is not None and q["kind"] in ("attack", "march_attack")
              and int(world.get_marshal(other_key).strength) != other_strength)
    acted = (getattr(m, "strategic_order", None) is not None or asked or fought
             or m.location == q["dest"] or (bool(r.get("success")) and ap_spent > 0))
    if fog and q["ok"]:
        return "fog_surprise", q, r
    if q["ok"] and not acted:
        return "quoted_taken_but_refused", q, r
    if not q["ok"] and acted:
        return "quoted_refused_but_taken", q, r
    if q["ok"] and objection and q["objection"] != "possible":
        return "objection_not_quoted", q, r
    if q["ok"] and not asked and ap_spent != q["ap"]:
        return f"actions_differ (quoted {q['ap']}, spent {ap_spent})", q, r
    if q["ok"] and r.get("first_step_interrupt") and not q["contact"]:
        return "contact_not_quoted", q, r
    if not q["ok"]:
        head = q["refusal"].split(" —")[0][:40]
        msg = str(r.get("message", ""))
        # The road's refusals are the executor's own sentences; the state's
        # are the probe's short reasons (the chips' own), so only the road's
        # words are compared.
        if head and ("road" in q["refusal"] or "path" in q["refusal"].lower()) and head not in msg:
            return "refusal_wording_differs", q, r
        return "both_refused", q, r
    return "agree", q, r


def _sample_destinations(world, marshal, rng, n_random):
    regions = sorted(world.regions)
    adjacent = sorted(world.regions[marshal.location].adjacent_regions)
    held = sorted({rg for rg in regions
                   if any(world.get_visible_enemies_in_region(rg, world.player_nation))})
    others = [rg for rg in regions if rg not in adjacent and rg not in held and rg != marshal.location]
    picked = adjacent + held + rng.sample(others, min(n_random, len(others)))
    return [rg for rg in dict.fromkeys(picked) if rg != marshal.location]


def _march_census(client, setup=None, n_random=8, seed=1805):
    C.boot()
    if setup:
        setup(M.world)
    rng = random.Random(seed)
    cells = []
    keys = sorted(m.name for m in M.world.get_player_marshals())
    plan = []
    for key in keys:
        for dest in _sample_destinations(M.world, M.world.get_marshal(key), rng, n_random):
            plan.append((key, dest))
    for key, dest in plan:
        verdict, q, r = _drive_cell(
            client, lambda w, k=key, d=dest: (march_quote(w, w.get_marshal(k), d), k, None), setup)
        cells.append((verdict, q["command"], q["refusal"], str(r.get("message", ""))[:200]))
    return cells


def _one_action_left(world):
    world.actions_remaining = 1


def _first_fortified(world):
    first = sorted(m.name for m in world.get_player_marshals())[0]
    world.get_marshal(first).fortified = True


@pytest.fixture(scope="module")
def census(board):
    out = {
        "boot": _march_census(board),
        "one_action_left": _march_census(board, _one_action_left, n_random=3, seed=7),
        "fortified": _march_census(board, _first_fortified, n_random=3, seed=11),
    }
    # Support and attack: every pair on the boot board.
    C.boot()
    keys = sorted(m.name for m in M.world.get_player_marshals())
    enemies = []
    for rg in sorted(M.world.regions):
        for row in M.world.get_visible_enemies_in_region(rg, M.world.player_nation):
            name = row.get("name") if isinstance(row, dict) else row.name
            e = M.world.get_marshal(name)
            if e is not None and M.world.is_at_war(M.world.player_nation, e.nation) and name not in enemies:
                enemies.append(name)
    pairs = []
    for key in keys:
        for other in keys + enemies:
            if other == key:
                continue
            pairs.append((key, other))
    rows = []
    for key, other in pairs:
        def quote(w, k=key, o=other):
            subject, target = w.get_marshal(k), w.get_marshal(o)
            if o in keys:
                return support_quote(w, subject, target), k, None
            return attack_quote(w, subject, target), k, o
        verdict, q, r = _drive_cell(board, quote)
        rows.append((verdict, q["kind"], q["command"], q["refusal"], str(r.get("message", ""))[:200]))
    out["support_attack"] = rows
    out["enemies"] = enemies
    return out


class TestTheDriftCensus:

    @pytest.mark.parametrize("variant", ["boot", "one_action_left", "fortified"])
    def test_every_march_quote_is_what_the_order_does(self, census, variant):
        bad = [c for c in census[variant] if c[0] not in ("agree", "both_refused", "fog_surprise")]
        assert bad == [], bad[:5]

    def test_the_census_reads_both_roads(self, census):
        """Sensitive, not vacuous: the sample holds taken AND refused orders
        on every variant, and the state variants refuse what they should."""
        for variant in ("boot", "one_action_left", "fortified"):
            kinds = collections.Counter(c[0] for c in census[variant])
            assert kinds["agree"] >= 10, (variant, kinds)
            assert kinds["both_refused"] >= 10, (variant, kinds)
        assert any("needs 2 actions" in c[2] for c in census["one_action_left"])
        assert any("fortified" in c[2] for c in census["fortified"])

    def test_every_support_and_attack_quote_is_what_the_order_does(self, census):
        bad = [r for r in census["support_attack"] if r[0] not in ("agree", "both_refused", "fog_surprise")]
        assert bad == [], bad[:5]

    def test_the_support_and_attack_census_reads_each_kind(self, census):
        kinds = collections.Counter((r[1], r[0]) for r in census["support_attack"])
        assert kinds[("support", "agree")] >= 20, kinds
        assert kinds[("attack", "agree")] >= 2, kinds
        assert kinds[("march_attack", "agree")] >= 2, kinds
        assert census["enemies"], "the boot board sights no enemy"


# ═══ the quote's own terms ══════════════════════════════════════════════════

class TestTheQuoteSaysItsTerms:

    def test_a_march_is_priced_by_keyword(self, client):
        """`strategic_order_ap("MOVE_TO")` read positionally is `auto_upgrade`
        and prices every march at 1 — an ordinary marshal's march costs 2."""
        C.boot()
        w = M.world
        ordinary = next(m for m in w.get_player_marshals()
                        if m.personality not in ("literal",) and not getattr(m, "is_sovereign", False))
        dest = next(rg for rg in sorted(w.regions[ordinary.location].adjacent_regions)
                    if march_quote(w, ordinary, rg)["ok"])
        assert march_quote(w, ordinary, dest)["ap"] == 2

    def test_a_marchs_contact_is_named(self, client):
        """The first step meets a corps we see — the quote names him and the
        one action charged at once."""
        C.boot()
        w = M.world
        found = []
        for m in w.get_player_marshals():
            for rg in sorted(w.regions):
                q = march_quote(w, m, rg)
                if q["ok"] and q["contact"] and "(1 action now)" in q["contact"]:
                    found.append(q)
        assert found, "the boot board holds no first-step contact"
        assert all(q["ap"] == 1 for q in found)

    def test_a_replaced_order_is_named(self, client):
        C.boot()
        w = M.world
        m = next(m for m in w.get_player_marshals() if not getattr(m, "is_sovereign", False))
        dest = next(rg for rg in sorted(w.regions)
                    if rg != m.location and march_quote(w, m, rg)["ok"] and march_quote(w, m, rg)["turns"] >= 2)
        _post(client, f"{humanize_entity_name(m.name)}, march to {dest}")
        w = M.world
        m = w.get_marshal(m.name)
        assert m.strategic_order is not None
        other = next(rg for rg in sorted(w.regions)
                     if rg not in (dest, m.location) and march_quote(w, m, rg)["ok"])
        q = march_quote(w, m, other)
        assert q["replaces"] == f"his march to {dest}"
        again = march_quote(w, m, dest)
        assert again["already"] is True and again["ap"] == 0


class TestFog:

    def test_no_quote_names_a_corps_we_cannot_see(self, client):
        C.boot()
        w = M.world
        seen = {humanize_entity_name(m.name) for m in w.get_visible_enemies(w.player_nation)}
        unseen = {humanize_entity_name(m.name) for m in w.marshals.values()
                  if m.nation != w.player_nation and humanize_entity_name(m.name) not in seen}
        for region in sorted(w.regions):
            payload = march_quotes_for_region(w, region)
            for row in payload["attack"]:
                assert row["enemy_shown"] in seen, (region, row["enemy"])
            texts = [q["note"] + " " + q["contact"] for q in payload["march"]]
            texts += [q["note"] + " " + q["contact"] for row in payload["support"] + payload["attack"]
                      for q in row["quotes"]]
            for text in texts:
                named = [n for n in unseen if re.search(r"\b" + re.escape(n) + r"\b", text)]
                assert named == [], (region, named, text)

    def test_a_corps_hidden_on_the_road_drops_out_of_the_quote(self, client):
        """Sensitive: the same road, its blocker's province fogged — the
        note that named him is gone."""
        C.boot()
        w = M.world
        hit = None
        for m in w.get_player_marshals():
            for rg in sorted(w.regions):
                q = march_quote(w, m, rg)
                if q["ok"] and "stands on the road at" in q["note"]:
                    hit = (m.name, rg, q)
                    break
            if hit:
                break
        assert hit, "the boot board holds no foe on any road"
        key, dest, q = hit
        where = q["note"].split("stands on the road at ")[1].split(" —")[0]
        from backend.models.intel import UNKNOWN
        w.get_region_intel(where).visibility = UNKNOWN
        again = march_quote(w, w.get_marshal(key), dest)
        assert "stands on the road at " + where not in again["note"]


# ═══ the route ══════════════════════════════════════════════════════════════

class TestTheRouteIsReadOnly:

    def test_the_route_answers_in_the_quotes_shape(self, client):
        C.boot()
        region = next(rg for rg in sorted(M.world.regions)
                      if M.world.get_visible_enemies_in_region(rg, M.world.player_nation))
        with _quiet():
            r = client.get("/march_quotes", params={"region": region}).json()
        assert r["success"] is True and r["region"] == region
        assert isinstance(r["ap_left"], int)
        for q in r["march"] + [q for row in r["attack"] for q in row["quotes"]]:
            assert isinstance(q["ap"], int) and isinstance(q["turns"], int)
            assert q["command"].startswith(q["shown"] + ", ")
        assert r["attack"], "a sighted enemy's province offers the attack row"

    def test_an_unknown_province_is_refused(self, client):
        with _quiet():
            r = client.get("/march_quotes", params={"region": "Atlantis"}).json()
        assert r["success"] is False

    def test_the_route_writes_nothing(self, client):
        C.boot()
        before = json.dumps(M.world.to_dict(), sort_keys=True, default=str)
        dm_before = json.dumps(M.world.dialogue_manager.to_dict(), sort_keys=True, default=str)
        state = random.getstate()
        with _quiet():
            for region in sorted(M.world.regions):
                client.get("/march_quotes", params={"region": region})
        assert random.getstate() == state, "a quote rolled the game's dice"
        assert json.dumps(M.world.dialogue_manager.to_dict(), sort_keys=True, default=str) == dm_before
        assert json.dumps(M.world.to_dict(), sort_keys=True, default=str) == before


# ═══ CC-X8 — a refused march leaves the square standing ═════════════════════

class TestARefusedMarchLeavesTheSquare:

    def _refused_on_the_road(self, w, m):
        for rg in sorted(w.regions):
            q = march_quote(w, m, rg)
            if not q["ok"] and ("road" in q["refusal"] or "path" in q["refusal"].lower()):
                return rg
        return None

    def test_a_march_refused_on_the_road_keeps_the_square(self, client):
        C.boot()
        w = M.world
        m = next(m for m in w.get_player_marshals() if not getattr(m, "is_sovereign", False))
        dest = self._refused_on_the_road(w, m)
        assert dest is not None
        m.square_formation = True
        r = _post(client, f"{humanize_entity_name(m.name)}, march to {dest}")
        assert not r.get("success") or M.world.get_marshal(m.name).strategic_order is None
        assert M.world.get_marshal(m.name).square_formation is True

    def test_the_refusal_is_reached_after_the_old_break(self, client, monkeypatch):
        """Sensitivity: with the break put back at stage 2 (the old order) the
        same refused march DOES break the square — the refusal is one the old
        code reached with the square already broken."""
        original = se_mod.StrategicExecutor._strategic_square_and_engagement

        def old_order(self, ctx):
            self._executor._auto_break_square(ctx.marshal, ctx.strategic_type or "strategic order")
            return original(self, ctx)
        monkeypatch.setattr(se_mod.StrategicExecutor, "_strategic_square_and_engagement", old_order)
        C.boot()
        w = M.world
        m = next(m for m in w.get_player_marshals() if not getattr(m, "is_sovereign", False))
        dest = self._refused_on_the_road(w, m)
        m.square_formation = True
        _post(client, f"{humanize_entity_name(m.name)}, march to {dest}")
        assert M.world.get_marshal(m.name).square_formation is False

    def test_a_march_taken_still_breaks_the_square(self, client):
        C.boot()
        w = M.world
        m = next(m for m in w.get_player_marshals() if not getattr(m, "is_sovereign", False))
        dest = next(rg for rg in sorted(w.regions)
                    if march_quote(w, m, rg)["ok"] and not march_quote(w, m, rg)["contact"]
                    and march_quote(w, m, rg)["objection"] == "none")
        m.square_formation = True
        _post(client, f"{humanize_entity_name(m.name)}, march to {dest}")
        m = M.world.get_marshal(m.name)
        assert m.strategic_order is not None or m.location == dest
        assert m.square_formation is False


# ═══ the desk reads the same scan ═══════════════════════════════════════════

class TestTheDeskReadsTheSameScan:

    def test_the_reach_answer_names_the_quotes_foe(self, client):
        C.boot()
        w = M.world
        for m in w.get_player_marshals():
            for rg in sorted(w.regions):
                q = march_quote(w, m, rg)
                if q["ok"] and "stands on the road at" in q["note"] and not q["contact"]:
                    r = _post(client, f"can {humanize_entity_name(m.name)} reach {rg}")
                    foe = q["note"].split(" stands on the road at ")[0]
                    assert f"{foe} stands on the road at" in str(r.get("message", "")), r.get("message")
                    return
        pytest.fail("the boot board holds no foe on a road")


# ═══ the client, driven ═════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def driven(board, tmp_path_factory):
    exe = C.engine()
    if exe is None:
        pytest.skip("Godot engine not on this machine — the driven pins skip, "
                    "and a skip is not a pass")
    C.boot()
    spec = _pick_board()
    w = M.world
    quotes_province = next(rg for rg in sorted(w.regions)
                           if w.get_visible_enemies_in_region(rg, w.player_nation)
                           and sum(q["ok"] for q in march_quotes_for_region(w, rg)["march"]) > 5)
    refused_province = next(rg for rg in sorted(w.regions)
                            if march_quotes_for_region(w, rg)["march"]
                            and not any(q["ok"] for q in march_quotes_for_region(w, rg)["march"]))
    with _quiet():
        spec["march_quotes"] = board.get("/march_quotes", params={"region": quotes_province}).json()
        spec["refused_quotes"] = board.get("/march_quotes", params={"region": refused_province}).json()
    spec["quotes_province"] = quotes_province
    spec["refused_province"] = refused_province
    work = tmp_path_factory.mktemp("cc2")
    out = work / "out.json"
    log = work / "godot.log"
    spec_path = work / "spec.json"
    spec_path.write_text(json.dumps(dict(spec, out=str(out))), encoding="utf-8")
    env = dict(os.environ, CC_SPEC=str(spec_path))
    proc = subprocess.run(
        [exe, "--headless", "--path", str(PROJECT), "--log-file", str(log),
         "--script", str(HARNESS)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=300, env=env, cwd=str(PROJECT))
    if not out.is_file():
        pytest.fail("the harness wrote no result\n"
                    f"exit={proc.returncode}\nstderr tail:\n{proc.stderr[-2000:]}")
    # UXR3-83 (S15, October 26, 2026): a chip label binds its spaces (U+00A0)
    # in the bbcode; this door reads them as spaces, as the instruments do.
    result = json.loads(out.read_text(encoding="utf-8").replace("\u00a0", " "))
    assert "error" not in result, result.get("error")
    text = log.read_text(encoding="utf-8", errors="replace") if log.is_file() else ""
    result["script_errors"] = text.count("SCRIPT ERROR")
    result["spec"] = spec
    return result


class TestThePanelRendersTheQuotes:

    def test_no_script_errors(self, driven):
        assert driven["script_errors"] == 0

    def test_opening_the_panel_asks_for_its_quotes(self, driven):
        assert driven["p1_panel_open"] is True
        assert driven["p1_requested"] == ["march_quotes:" + driven["spec"]["quotes_province"]]

    def test_every_open_order_shown_is_a_chip_of_its_quoted_command(self, driven):
        text = driven["p1_text"]
        ok = [q for q in driven["spec"]["march_quotes"]["march"] if q["ok"]]
        for q in ok[:5]:
            assert f"[url=do:{q['command']}]" in text, q["command"]
            assert f"{q['shown']} · {q['ap']} AP" in text
        hidden = len(ok) - 5 + sum(not q["ok"] for q in driven["spec"]["march_quotes"]["march"])
        assert f"+{hidden} more…" in text

    def test_the_attack_row_is_there(self, driven):
        for row in driven["spec"]["march_quotes"]["attack"]:
            assert "ATTACK " + row["enemy_shown"].upper() in driven["p1_text"]

    def test_a_stale_answer_is_dropped(self, driven):
        assert driven["p2_text_unchanged"] is True

    def test_a_chip_sends_its_quoted_command(self, driven):
        assert driven["p3_command"]
        assert driven["p3_sent"] == ["send:" + driven["p3_command"]]

    def test_the_reply_asks_again(self, driven):
        assert driven["p4_requested_again"] == ["march_quotes:" + driven["spec"]["quotes_province"]]

    def test_more_opens_every_quote(self, driven):
        for q in driven["spec"]["march_quotes"]["march"]:
            if q["ok"]:
                assert f"[url=do:{q['command']}]" in driven["p5_text_more"], q["command"]

    def test_where_no_corps_can_march_the_reasons_are_the_answer(self, driven):
        text = driven["p6_text"]
        refused = driven["spec"]["refused_quotes"]["march"]
        assert refused and not any(q["ok"] for q in refused)
        assert "[url=do:" not in text.split("MARCH HERE")[1].split("\n\n")[0]
        for reason in {q["refusal"] for q in refused}:
            assert reason in text, reason
