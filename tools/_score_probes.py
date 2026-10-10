"""The PROBE items of the Score Finish checklist (SCORE_FINISH_SPEC.md §4.3).

Each probe is a small READ-ONLY measurement `tools/score_run.py check` calls
by name (the `PROBES` map there). A probe reads the run's arms (digests,
jsonl, the saves the arms left) and, where an item needs the game's own
answer, loads a save into this tree's backend in-process and asks it. Nothing
here writes a save the arms read, and nothing here changes the ledgers.

Every probe returns `{"measured": bool, "pass": bool|None, "evidence": str}`.
A probe that cannot measure its item says why and returns `measured: False`,
which the rule reads as UNMEASURED (never a pass, never a fail).

The in-process backend is booted once, with `LLM_MODE=mock` and the save
directory sandboxed under the run dir (`_probe_saves`), so a probe never
touches the developer's saves or the arms' own.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SHRUG_RX = re.compile(
    r"cannot answer that from the dispatches|cannot determine the order|"
    r"instruction is unclear|cannot parse this order|order eludes me|"
    r"cannot make sense of this|I did not understand|Unclear instruction",
    re.I,
)
CMD_ARMS = ("CMD-H", "CMD-A", "CMD-M")
_STATE: dict = {}


def _res(measured, ok=None, evidence=""):
    return {
        "measured": bool(measured),
        "pass": (bool(ok) if measured else None),
        "evidence": str(evidence)[:700],
    }


def _un(reason):
    return _res(False, None, reason)


# ── the in-process backend ─────────────────────────────────────────────────
def _boot(ctx):
    """Import the backend once, sandboxed. Returns the module."""
    if "M" in _STATE:
        return _STATE["M"]
    run_dir = pathlib.Path(ctx["run_dir"])
    saves = run_dir / "_probe_saves"
    saves.mkdir(parents=True, exist_ok=True)
    os.environ["LLM_MODE"] = "mock"
    os.environ["INK_IRON_SAVE_DIR"] = str(saves)
    os.environ.setdefault("PYTHONHASHSEED", "0")
    for key in (
        "SOVEREIGN_SCENARIO",
        "SOVEREIGN_MAP",
        "SOVEREIGN_SMOKE_START",
        "SOVEREIGN_SEED",
    ):
        os.environ.pop(key, None)
    with contextlib.redirect_stdout(io.StringIO()):
        import backend.main as M  # noqa: WPS433
        from fastapi.testclient import TestClient
    _STATE["M"] = M
    _STATE["client"] = TestClient(M.app)
    _STATE["parser"] = M.parser
    _STATE["saves"] = saves
    return M


def _client(ctx):
    _boot(ctx)
    return _STATE["client"]


def _load_world(ctx, save_path: pathlib.Path):
    """A world off a save file, read-only (never adopted unless asked)."""
    _boot(ctx)
    from backend.save_manager import load_game

    with contextlib.redirect_stdout(io.StringIO()):
        res = load_game(pathlib.Path(save_path))
    if not res.get("success") or res.get("world") is None:
        raise RuntimeError(f"could not load {save_path.name}: {res.get('message')}")
    return res["world"]


def _adopt(ctx, world):
    """The TestClient world-swap rule (IQ-10): all three together."""
    M = _boot(ctx)
    M.world = world
    M.game_state["world"] = world
    M.parser = _STATE["parser"]
    return _STATE["client"]


def _fresh(ctx):
    M = _boot(ctx)
    with contextlib.redirect_stdout(io.StringIO()):
        r = _STATE["client"].post("/new_game", json={}).json()
    return M.world, r


def _cmd(ctx, text):
    with contextlib.redirect_stdout(io.StringIO()):
        return _STATE["client"].post("/command", json={"command": text}).json()


def _saves_of(arms, name) -> list[pathlib.Path]:
    a = arms.get(name)
    if not a:
        return []
    d = a.path / "saves"
    return sorted(d.glob(f"{name}_t*.json")) if d.exists() else []


def _save_turn(p: pathlib.Path) -> int:
    m = re.search(r"_t(\d+)\.json$", p.name)
    return int(m.group(1)) if m else 0


def _blocks(arm):
    return arm.blocks()


def _lines(arm, needle):
    out = []
    for t, text in arm.blocks():
        for line in text.split("\n"):
            if needle.lower() in line.lower():
                out.append((t, line.strip()))
    return out


def _groups(arm):
    return arm.by_turn()


def _gold(world, nation="France"):
    if nation == world.player_nation and hasattr(world, "gold"):
        return int(world.gold)
    return int((getattr(world, "nation_gold", {}) or {}).get(nation, 0))


# ═════════════════════════ THE ENDING ═════════════════════════
def ending_c3_alarm_forecast(arms, ctx):
    """RS-16: the alarm line's promised fall against the next tick, ±1."""
    a = arms.get("CONG")
    if not a:
        return _un("CONG did not run")
    leds = a.kind("ledger")
    threats = [int(l.get("threat") or 0) for l in leds]
    quotes = [
        (t, l) for t, l in _lines(a, "falls") if re.search(r"falls (\d+) a turn", l)
    ]
    # RS-16 (built Sept 29, 2026): the road is ONE forecast of the tick —
    # "rising 1 a turn: … against 3 of decay" / "falling 2 a turn" / "holding"
    # — read as a signed net; the pre-RS-16 "it falls N a turn" reads as −N.
    def _promised_net(text):
        m = re.search(r"\b(rising|falling) (\d+) a turn", text)
        if m:
            return int(m.group(2)) * (1 if m.group(1) == "rising" else -1)
        if re.search(r"\bholding\b", text):
            return 0
        m = re.search(r"falls (\d+) a turn", text)
        return -int(m.group(1)) if m else None

    if not quotes:
        # the road is quoted on the Congress table, not the digest: read it off the summoned board
        try:
            w = _load_world(
                ctx,
                ROOT
                / "docs/audits/playtest_digests/rs0928-hand-played/retest_t24_summonable.json",
            )
            client = _adopt(ctx, w)
            _cmd(ctx, "summon the congress")
            body = client.get("/diplomatic_ledger").json()
            body = body.get("ledger") or body
            road = str((body.get("congress") or {}).get("alarm_road") or "")
        except Exception as exc:
            return _un(
                f"no alarm road on the CONG digest and the board could not be asked: {exc}"
            )
        promised = _promised_net(road)
        if promised is None:
            return _un(f"the Congress quotes no per-turn forecast: {road[:120]}")
        if len(threats) < 2:
            return _un("CONG has fewer than two ledger readings")
        # the promise is the QUIET road: a tick that carries a league's dissolution (the halving) or its brewing is not the road quoted
        groups = _groups(a)
        falls = []
        for i in range(1, min(len(groups), len(threats))):
            txt = json.dumps(groups[i], ensure_ascii=False)
            if re.search(
                r"coalition_dissolved|league is spent|halves|coalition_brewing_started|coalition_formed",
                txt,
            ):
                continue
            falls.append(threats[i] - threats[i - 1])
        if not falls:
            return _un(
                "every CONG tick carried a league event; no quiet tick to read the promise against"
            )
        import statistics as _st

        med = _st.median(falls)
        ok = abs(med - promised) <= 1
        return _res(
            True,
            ok,
            f"the table forecasts a net of {promised:+d} a turn ('{road[:70]}…'); the quiet ticks on the CONG arm moved {falls} (median {med:+.1f}); alarm series {threats}",
        )
    t, line = quotes[0]
    promised = _promised_net(line)
    idx = [i for i, g in enumerate(_groups(a)) if g and g[0].get("turn") == t]
    if promised is None or not idx or idx[0] + 1 >= len(threats):
        return _un("no ledger tick after the quoted line")
    actual = threats[idx[0] + 1] - threats[idx[0]]
    return _res(
        True,
        abs(actual - promised) <= 1,
        f"turn {t} promises a fall of {promised}; the next tick fell {actual}: {line[:120]}",
    )


def ending_c6_refuser_prices(arms, ctx):
    """RS-D1: every REFUSES row's price is payable inside the sitting, or the table says it cannot be."""
    try:
        w = _load_world(
            ctx,
            ROOT
            / "docs/audits/playtest_digests/rs0928-hand-played/retest_t24_summonable.json",
        )
        client = _adopt(ctx, w)
        _cmd(ctx, "summon the congress")
        body = client.get("/diplomatic_ledger").json()
        body = body.get("ledger") or body
        courts = (body.get("congress") or {}).get("courts") or []
    except Exception as exc:
        return _un(f"the summoned board could not be read: {exc}")
    refusers = [
        c for c in courts if str(c.get("stance", "")).upper().startswith("REFUSE")
    ]
    if not refusers:
        return _un("no refuser at the table")
    bad = []
    for c in refusers:
        texts = [str(l.get("text", "")) for l in (c.get("levers") or [])] or [
            str(c.get("price", ""))
        ]
        joined = " · ".join(texts)
        if str(c.get("by") or "") == "war" or c.get("score") is None:
            # A refuser AT WAR is priced by the field — the war score, its
            # capital, the peace it would sign — which no calendar can quote;
            # the honest price names that road (RS-D1 built Sept 29, 2026).
            if re.search(r"win the war|take its capital|sign a peace|shut \d+ of", joined, re.I):
                continue
            bad.append(f"{c.get('nation')} (at war): {joined[:150]}")
            continue
        gains = [int(x) for x in re.findall(r"\(\+(\d+)\)", joined)]
        score = c.get("score")
        threshold = c.get("threshold")
        closes = (
            isinstance(score, (int, float))
            and isinstance(threshold, (int, float))
            and gains
            and score + max(gains) >= threshold
        )
        quoted_turns = bool(
            re.search(r"\b\d+ turns?\b|within the sitting|by turn \d+", joined, re.I)
        )
        says_cannot = bool(
            re.search(r"cannot|not within|out of reach|no road", joined, re.I)
        )
        if not (closes or quoted_turns or says_cannot):
            bad.append(f"{c.get('nation')} ({score} of {threshold}): {joined[:150]}")
    return _res(
        True,
        not bad,
        f"{len(refusers)} refusers; a price that neither closes the gap by its own figures, nor quotes its turns, nor says it cannot: {bad[:3]}"
        if bad
        else f"{len(refusers)} refusers, each price closing the gap, quoting its turns, or declared unpayable",
    )


# ═════════════════════════ DIPLOMACY ═════════════════════════
def diplomacy_c1_fresh_peace_holds(arms, ctx):
    """RS-1: a French peace signed at t is not broken by (t, t+5] through another court's cascade."""
    breaks = []
    peaces = 0
    for n in ("CMD-H", "CMD-A", "CMD-M", "PROP-H", "PROP-A", "PROP-M"):
        a = arms.get(n)
        if not a:
            continue
        signed = []
        for t, l in _lines(a, "Treaty signed:") + _lines(a, "RATIFIED"):
            m = re.search(
                r"Treaty signed: [^.]*→ (?:Peace|Armistice) with ([A-Z][A-Za-z ]+)", l
            ) or re.search(r"RATIFIED ([A-Z][A-Za-z ]+?) · (?:PEACE|ARMISTICE)", l)
            if m:
                signed.append((m.group(1).strip(), t))
        peaces += len(signed)
        for court, t in signed:
            for t2, l in _lines(a, court):
                if t < t2 <= t + 5 and re.search(
                    r"declares war on (France|us)|enters the war|joins the war|re-enters|back at war|at war with (France|us) again",
                    l,
                    re.I,
                ):
                    breaks.append(f"{n}: {court} peace t{t} → {l[:90]} (t{t2})")
    if peaces == 0:
        return _un("no French peace signed on the diplomacy arms")
    return _res(
        True,
        not breaks,
        f"{peaces} peaces; broken within 5 turns by a cascade: {breaks[:3]}"
        if breaks
        else f"{peaces} peaces, none re-broken within 5 turns",
    )


def diplomacy_c2_ratification_label(arms, ctx):
    """RS-9: a ratification label names only the covered courts."""
    found = 0
    bad = []
    for n in ("OP", "CMD-H", "CMD-A", "CMD-M"):
        a = arms.get(n)
        if not a:
            continue
        for t, text in a.blocks():
            for line in text.split("\n"):
                if re.search(r"Settlement Ratif|RATIFIED", line):
                    found += 1
                    named = set(
                        re.findall(
                            r"\b(Britain|Austria|Russia|Prussia|Spain|Sweden|Naples|Portugal|Denmark|Bavaria|Saxony|Hanover|Hesse|Ottoman|Sardinia)\b",
                            line,
                        )
                    )
                    still = " ".join(
                        l
                        for l in text.split("\n")
                        if re.search(
                            r"Still at war|dropped|left the table|not covered", l, re.I
                        )
                    )
                    dropped = {c for c in named if c in still}
                    if dropped:
                        bad.append(
                            f"{n} t{t}: names {sorted(dropped)} while '{still[:60]}'"
                        )
    if not found:
        return _un("no ratification on the arms")
    return _res(
        True,
        not bad,
        f"{found} ratification labels; naming a dropped court: {bad[:3]}"
        if bad
        else f"{found} ratification labels, each naming covered courts only (the 'Still at war' line disagrees with none)",
    )


# ═════════════════════════ FIRST CONTACT ═════════════════════════
def first_contact_c1_hold_shrugs(arms, ctx):
    a = arms.get("HOLD")
    if not a:
        return _un("HOLD did not run")
    script = ctx.get("hold_script") or {}
    qs = [x["line"] for x in (script.get("hold") or {}).get("questions", [])]
    cmds = {str(c.get("text", "")).strip().lower(): c for c in a.kind("command")}
    seen = [cmds[q.strip().lower()] for q in qs if q.strip().lower() in cmds]
    if len(seen) < 15:
        return _un(f"only {len(seen)} of the HOLD questions are on the digest")
    shrugs = [
        c["text"][:50]
        for c in seen
        if SHRUG_RX.search(str(c.get("message", "")))
        or c.get("success") is False
        and re.search(
            r"cannot interpret|await clear commands", str(c.get("message", ""))
        )
    ]
    return _res(
        True,
        len(shrugs) <= 2,
        f"{len(seen)} questions; shrugs {len(shrugs)}: {shrugs[:4]}",
    )


def first_contact_c5_today_orders(arms, ctx):
    world, r = _fresh(ctx)
    today = ((r.get("morning_dispatch") or {}).get("today") or {}).get("orders") or []
    if not today:
        return _un("the boot briefing carries no TODAY orders")
    alone = []
    for line in today:
        text = line.split(" — ")[0].strip()
        _fresh(ctx)  # each order on its own boot: the list names orders the board takes
        resp = _cmd(ctx, text)
        ok = resp.get("success") is not False and not SHRUG_RX.search(
            str(resp.get("message", ""))
        )
        alone.append((text, ok, str(resp.get("message", ""))[:70]))
    # and in sequence, as a player who types the list top to bottom would (reported, not scored)
    _fresh(ctx)
    seq = []
    for line in today:
        text = line.split(" — ")[0].strip()
        resp = _cmd(ctx, text)
        seq.append(
            (text, resp.get("success") is not False, str(resp.get("message", ""))[:60])
        )
    seq_fail = [f"{t!r} ✗ {m}" for t, ok, m in seq if not ok]
    return _res(
        True,
        all(ok for _, ok, _ in alone),
        "each on its own boot: "
        + " | ".join(f"{t!r} {'✓' if ok else '✗ ' + m}" for t, ok, m in alone)
        + (
            f" — typed top to bottom on one boot, {len(seq_fail)} fail: {seq_fail}"
            if seq_fail
            else " — and all four in sequence"
        ),
    )


# ═════════════════════════ ECONOMY ═════════════════════════
def economy_f2_britain_net(arms, ctx):
    world, _ = _fresh(ctx)
    from backend.game_logic import ledger as L

    try:
        fr = int(L._build_economy(world, "France").get("net", 0))
        br = int(L._build_economy(world, "Britain").get("net", 0))
    except Exception as exc:
        return _un(f"_build_economy could not price Britain: {exc}")
    return _res(
        True,
        br > fr,
        f"turn-1 Net: Britain {br} vs France {fr} (ledger._build_economy on the boot world)",
    )


def _moved_components(arm):
    """[(turn, key, before, after)] for every economy component moving >= 10% between consecutive turns."""
    out = []
    prev = None
    for g in _groups(arm):
        eco = [r for r in g if r.get("kind") == "economy"]
        if not eco:
            continue
        cur = {
            k: v
            for k, v in eco[0].items()
            if k not in ("kind", "net_residual") and isinstance(v, (int, float))
        }
        if prev is not None:
            for k, v in cur.items():
                b = prev.get(k)
                if b and abs(v - b) >= 0.10 * abs(b):
                    out.append((g[0].get("turn"), k, b, v))
        prev = cur
    return out


def economy_c2_bills_named(arms, ctx):
    """Every Net-line move of 10% or more names its cause — the ledger's own notes, recorded per turn
    by the driver (`bill_notes` on the ledger record, SF-M)."""
    a = arms.get("CMD-H")
    if not a:
        return _un("CMD-H did not run")
    groups = _groups(a)
    notes_by_turn = {}
    for g in groups:
        led = next((r for r in g if r.get("kind") == "ledger"), None)
        if led is not None:
            notes_by_turn[g[0].get("turn")] = " ".join(
                str(v) for v in (led.get("bill_notes") or {}).values()
            )
    if not any(notes_by_turn.values()):
        return _un("the ledger records carry no bill notes (a pre-SF-M archive)")
    moved = _moved_components(a)
    if not moved:
        return _un("no component moved 10% between two turns")
    words = {
        "charges": "charge",
        "upkeep": "upkeep|men under arms",
        "tribute": "tribut",
        "trade": "trade",
        "blockade": "blockade|enemy sail",
        "occupation": "occupation",
        "income": "income",
        "admin": "admin",
        "admiralty": "Admiralty",
        "laws": "law",
        "contributions": "contribution",
        "requisitions": "requisition",
        "overseas": "overseas",
        "rentes": "rente",
        "dotations": "dotation",
        "infrastructure": "infrastructure|structure",
    }
    unnamed = []
    for t, k, b, v in moved:
        notes = notes_by_turn.get(t, "") + " " + notes_by_turn.get(t + 1, "")
        if not re.search(words.get(k, k), notes, re.I):
            unnamed.append(f"t{t} {k} {b}→{v}")
    return _res(
        True,
        not unnamed,
        f"{len(moved)} moves of 10% or more; unnamed by the ledger's notes that turn or the next: {unnamed[:5]}"
        if unnamed
        else f"{len(moved)} moves of 10% or more, each named by a ledger note",
    )


def economy_c3_verdict(rows):
    """The C3 rule on its rows — `(turn, quoted charges, applied, quoted laws,
    applied, materiel)` — kept pure so the rule itself is pinned.

    A turn whose end fought in the enemy phase (the record's `materiel`, the
    Butcher's Bill paid INSIDE the end turn) is EXPLAINED, never a pass by
    itself: those battles land before the income phase draws the bill, so they
    move the chest and the campaign's dead (the pensions term) after the quote
    was read. The item passes only when every battle-free turn bills its quote
    to the gold, and at least one battle-free turn was compared."""
    calm = [r for r in rows if not r[5]]
    fought = [r for r in rows if r[5]]
    bad = [r for r in calm if r[1] != r[2] or r[3] != r[4]]
    explained = [r for r in fought if r[1] != r[2] or r[3] != r[4]]
    tail = ""
    if explained:
        tail += (" — explained by the end turn's own battles (turn, quoted, applied, "
                 "quoted laws, applied, materiel): " + str(explained))
    if bad:
        tail += " — mismatches on battle-free turns " + str(bad)
    if not calm:
        return _un("every compared turn fought in its enemy phase — no battle-free "
                   "turn to hold the quote against" + tail)
    return _res(
        True,
        not bad,
        f"{len(calm)} battle-free turns, quoted == billed on "
        f"{len(calm) - len(bad)}: (turn, quoted charges, applied, quoted laws, applied): "
        + str([r[:5] for r in calm])
        + tail,
    )


def economy_c3_quote_equals_applied(arms, ctx):
    """The quoted Charges (and Laws) at a save turn equal what that turn's end BILLED.

    SF-V7 (Score Finish Step 6, October 4, 2026): the bill is the end turn's own
    `applied_bill` record (the `turn_end` event). Until Step 6 this reader held the
    quote against the `economy` record written after the end turn — a `/ledger`
    forward projection, i.e. the NEXT turn's quote — so it compared two forecasts a
    turn apart and read every mismatch as "one tick low". The bill is drawn on the
    same pre-income chest the quote reads (measured: 216 quoted, 216 billed at a
    20,000 chest with no battle in the end turn); the one gap the game owns is the
    enemy phase's battles, which `economy_c3_verdict` names."""
    a = arms.get("CMD-H")
    if not a:
        return _un("CMD-H did not run")
    saves = _saves_of(arms, "CMD-H")
    if not saves:
        return _un("no saves")
    bills = {int(r.get("turn") or 0): r for r in a.kind("applied_bill")}
    if not bills:
        return _un("a pre-SF-V7 archive — the driver did not record the applied bill")
    rows = []
    from backend.game_logic import ledger as L

    for p in saves:
        w = _load_world(ctx, p)
        t = int(w.current_turn)   # the save is taken before this turn's end
        eco = L._build_economy(w, w.player_nation)
        applied = bills.get(t)
        if applied is None:
            continue
        rows.append(
            (
                t,
                int(eco.get("state_charges", 0) or 0),
                int(applied.get("charges", 0) or 0),
                int(eco.get("laws", 0) or 0),
                int(applied.get("laws", 0) or 0),
                int(applied.get("materiel", 0) or 0),
            )
        )
    if not rows:
        return _un("no save turn has a matching applied bill")
    return economy_c3_verdict(rows)


def economy_c4_priced_orders(arms, ctx):
    """Two priced orders on the boot world: the levy (recruit_quote) and a law (restoration_price) charge what they quoted."""
    world, _ = _fresh(ctx)
    from backend.commands import economy_executor as EE
    from backend.game_logic import reforms as RF

    out = []
    ok = True
    # (a) the levy, on the province the boot briefing itself prices
    q = EE.recruit_quote(world, "Rhineland", "infantry")
    if q.get("ok"):
        before = _gold(world)
        resp = _cmd(ctx, "recruit infantry in Rhineland")
        after = _gold(world)
        charged = before - after
        quoted = int(q.get("price") or 0)
        ok = ok and (resp.get("success") is True and charged == quoted)
        out.append(f"levy quoted {quoted}, charged {charged}")
    else:
        out.append(f"levy: no quote ({q.get('kind')})")
    # (b) a gold law — the cheapest in the deck the chest can pay
    deck = [
        r
        for r in RF.deck(world, "France")
        if str(r.get("currency")) == "gold" and not RF.is_in_force(r)
    ]
    deck.sort(
        key=lambda r: int(RF.restoration_price(world, "France", r).get("price", 10**9))
    )
    if deck:
        row = deck[0]
        price = int(RF.restoration_price(world, "France", row).get("price", 0))
        if price <= _gold(world):
            before = _gold(world)
            resp = _cmd(ctx, f"enact {row.get('name')}")
            # the enactment confirm (RF-4a) answers on the clarification channel
            if (
                resp.get("clarification")
                or "confirm" in str(resp.get("message", "")).lower()
            ):
                resp = _cmd(ctx, f"enact {row.get('name')} confirmed")
            after = _gold(world)
            charged = before - after
            ok = ok and (charged == price)
            out.append(f"law {row.get('name')} quoted {price}, charged {charged}")
        else:
            out.append(
                f"law: cheapest gold law {row.get('name')} at {price} exceeds the chest {_gold(world)} — not tried"
            )
    return _res(True, ok, " | ".join(out))


def economy_c6_affordable_purchase(arms, ctx):
    """CMD turns 20–40: 'what can I do' names a purchase the chest can pay (sampled at the 20/30/40 saves)."""
    samples = []
    for n in CMD_ARMS:
        for p in _saves_of(arms, n):
            if _save_turn(p) < 20:
                continue
            w = _load_world(ctx, p)
            _adopt(ctx, w)
            r = _cmd(ctx, "what can I do")
            text = (
                str(r.get("message", ""))
                + " "
                + " ".join(str(x) for x in (r.get("options") or []))
            )
            prices = [
                int(x.replace(",", "")) for x in re.findall(r"(\d[\d,]*)g\b", text)
            ]
            purchase = bool(
                re.search(r"recruit|build|enact|commission|lay down|buy", text, re.I)
            )
            affordable = purchase and (not prices or min(prices) <= _gold(w))
            samples.append(
                (n, _save_turn(p), affordable, text[:60].replace("\n", " / "))
            )
    if not samples:
        return _un("no CMD saves at turn 20 or later")
    rate = sum(1 for s in samples if s[2]) / len(samples)
    return _res(
        True,
        rate >= 0.8,
        f"{sum(1 for s in samples if s[2])}/{len(samples)} samples name an affordable purchase ({rate:.0%}): "
        + "; ".join(f"{n} t{t} {'✓' if ok else '✗'}" for n, t, ok, _ in samples),
    )


# ═════════════════════════ NAVAL ═════════════════════════
def naval_c5_ports_now_zero(arms, ctx):
    hits = []
    for n in ("CONG", "CMD-H", "CMD-A", "CMD-M"):
        a = arms.get(n)
        if not a:
            continue
        hits += [(n, t, l) for t, l in _lines(a, "(now 0)") if "port" in l.lower()]
    if not hits:
        return _un(
            "no '(now 0)' ports lever quoted on the arms (needs a truce with Britain)"
        )
    bad = [
        f"{n} t{t}: {l[:100]}"
        for n, t, l in hits
        if not re.search(r"truce|armistice|at peace|while the peace", l, re.I)
    ]
    return _res(
        True,
        not bad,
        f"{len(hits)} '(now 0)' quotes; unexplained: {bad[:2]}"
        if bad
        else f"{len(hits)} '(now 0)' quotes, each naming the truce",
    )


# ═════════════════════════ LIVING BALANCE ═════════════════════════
# SF7-X39 (Score Finish Step 7b): the frozen item reads "every sponsorship
# against France AND every great power that newly qualifies for a league
# leads or sub-beats the next dispatch, and each quoted keep-out lever flips
# `qualifies_for_coalition(relation_shift=)`". The first probe read the
# headline line alone (the driver kept no sub-beats), never read a newly
# qualifying court, and accepted any keep-out phrase without the flip.
# False = that probe.
THE_PROBE_READS_THE_WHOLE_PAGE = True
# EA-16 (the economy audit, October 5, 2026): the dispatch records no league
# table on a morning the old league still stands (`_coalition_section` skips
# it while `_formed`), but the page's own beat reads the same forecast every
# morning. So on the morning the old league dissolves the beat can name a
# newly free court one page BEFORE the rows first appear (measured: CMD-M,
# "Austria and Prussia would now join a league" on the t12 page, Prussia's
# row first recorded on t13 — "missed" by a reader that only looked at t13).
# The news counts on the previous page only when that morning recorded no
# table at all. False = the page of the rows' first turn only.
THE_C5_READER_KNOWS_A_TABLELESS_MORNING = True
# EG-I1 (the economy gate, October 5, 2026): a campaign-log row the driver
# records LATE — `log_turn` 24 surfacing in turn 34's group on the gate's
# CMD-M arm, its own morning's page having LED with it ("London now pays St
# Petersburg 500 gold a turn against us") — was judged against the wrong
# morning and reported "missed". Each group's log rows are the next
# morning's (group t holds the end turn's response: world turn t+1's page and
# its fresh rows), so a row is judged on the page of ITS OWN morning (group
# `log_turn` − 1) and counted once. False = every row judged on the group it
# surfaced in.
THE_C5_READER_JUDGES_A_ROW_ON_ITS_OWN_MORNING = True
# EG-I2 (the economy gate, October 5, 2026): EA-16's rule looked back ONE
# table-less morning. On the gate's CMD-A arm the old league stood for two
# (groups 8 and 9 record no table), and the page told the news on the first
# of them ("Prussia would now join a league against us … she would march in
# the next"); the reader looked at the second and reported Prussia "missed".
# The news counts on any page of the run of table-less mornings before the
# table — EA-16's rule widened, so it rides on EA-16's lever too. False = the
# one morning EA-16 read.
THE_C5_READER_KNOWS_A_RUN_OF_TABLELESS_MORNINGS = True


def _page_text(dispatch_rec: dict) -> str:
    """The morning's whole page off the driver's record (SF7-X39 fields)."""
    parts = [str(dispatch_rec.get("headline_text") or dispatch_rec.get("headline") or "")]
    parts += [str(b) for b in (dispatch_rec.get("sub_beats") or [])]
    return " ".join(parts)


def _c5_quoted_levers_flip(arms, ctx, peace_turns):
    """Every keep-out lever the league rows quote on a CMD save after the
    peace flips the coalition gate: the relation road's shift (`need`) and a
    buy-off enough alone (+BUYOFF_RELATION_BONUS)."""
    from backend.game_logic import coalition as CO
    from backend.game_logic.instruments import BUYOFF_RELATION_BONUS
    quoted, flips, bad = 0, 0, []
    for n, peace in peace_turns.items():
        for path in _saves_of(arms, n):
            if _save_turn(path) <= peace:
                continue
            w = _load_world(ctx, path)
            fc = CO.league_forecast(w)
            for row in fc.get("courts") or []:
                if row.get("status") != CO.LEAGUE_JOINS:
                    continue
                shifts = []
                if row.get("road") is not None:
                    shifts.append(("road", int(row["need"])))
                if row.get("buyoff") is not None and row.get("buyoff_alone"):
                    shifts.append(("buy-off", int(BUYOFF_RELATION_BONUS)))
                for kind, shift in shifts:
                    quoted += 1
                    if CO.qualifies_for_coalition(row["nation"], w, relation_shift=shift):
                        bad.append(f"{n} t{_save_turn(path)} {row['nation']} {kind} +{shift}")
                    else:
                        flips += 1
    return quoted, flips, bad


def living_balance_c5_front_page(arms, ctx):
    """Step 7b: after the peace, every sponsorship against France and every great power newly free to join leads or sub-beats the next dispatch, and every quoted keep-out lever flips the gate."""
    seen = 0
    led = 0
    keep = 0
    fresh_seen = 0
    fresh_told = 0
    missed = []
    peace_turns = {}
    for n in CMD_ARMS:
        a = arms.get(n)
        if not a:
            continue
        peace_turn = None
        for t, l in _lines(a, "Treaty signed:"):
            if re.search(
                r"→ (Peace|Armistice) with (Austria|Russia|Britain|Prussia)", l
            ):
                peace_turn = t if peace_turn is None else min(peace_turn, t)
        if peace_turn is None:
            continue
        peace_turns[n] = peace_turn
        prev_majors = None
        prev_page, prev_tableless = "", False
        # EG-I1: every group's page, so a late row is judged on its own morning
        pages_by_group = {}
        for g in _groups(a):
            _d = next((r for r in g if r.get("kind") == "dispatch"), {})
            pages_by_group[g[0].get("turn")] = (
                _page_text(_d) if THE_PROBE_READS_THE_WHOLE_PAGE
                else str(_d.get("headline", "")))
        judged = set()
        tableless_run: list = []   # EG-I2: the pages of the run before a table
        for g in _groups(a):
            t = g[0].get("turn")
            disp = next((r for r in g if r.get("kind") == "dispatch"), {})
            majors = {r["nation"] for r in (disp.get("league_rows") or [])
                      if r.get("major") and r.get("status") in ("joins", "refuses")}
            page = (_page_text(disp) if THE_PROBE_READS_THE_WHOLE_PAGE
                    else str(disp.get("headline", "")))
            # EA-16: a morning with no table at all (no rows, no league line)
            # is one the old league still stood on.
            tableless = ("league_rows" in disp and not disp.get("league_rows")
                         and not str(disp.get("league_line") or "").strip())
            if t is None or t <= peace_turn:
                prev_majors = majors if "league_rows" in disp else prev_majors
                prev_page, prev_tableless = page, tableless
                tableless_run = tableless_run + [page] if tableless else []
                continue
            spons = [
                r
                for r in g
                if r.get("kind") in ("rail", "dispatch_row", "campaign_log")
                and re.search(r"sponsor", str(r.get("text", "")), re.I)
                and re.search(
                    r"against France|aim.*France", str(r.get("text", "")), re.I
                )
            ]
            if spons and THE_C5_READER_JUDGES_A_ROW_ON_ITS_OWN_MORNING:
                for r in spons:
                    key = (str(r.get("text", "")), r.get("log_turn"))
                    if key in judged:
                        continue
                    judged.add(key)
                    own = (int(r["log_turn"]) - 1 if isinstance(r.get("log_turn"), int)
                           else t)
                    if own is None or own <= peace_turn or own not in pages_by_group:
                        continue
                    own_page = pages_by_group[own]
                    seen += 1
                    if THE_PROBE_READS_THE_WHOLE_PAGE:
                        told = bool(re.search(r"pays .* against us|licenses .* against us", own_page))
                    else:
                        told = bool(re.search(r"sponsor|pays|subsid|purse|league", own_page, re.I))
                    if told:
                        led += 1
                    else:
                        missed.append(f"{n} t{own} sponsorship")
            elif spons:
                seen += len(spons)
                if THE_PROBE_READS_THE_WHOLE_PAGE:
                    told = bool(re.search(r"pays .* against us|licenses .* against us", page))
                else:
                    told = bool(re.search(r"sponsor|pays|subsid|purse|league", page, re.I))
                if told:
                    led += len(spons)
                else:
                    missed.append(f"{n} t{t} sponsorship")
            if THE_PROBE_READS_THE_WHOLE_PAGE and "league_rows" in disp:
                if prev_majors is not None:
                    from backend.display_names import display_nation
                    for nation in sorted(majors - prev_majors):
                        fresh_seen += 1
                        said = rf"{re.escape(display_nation(nation))}[^.]*would now join a league"
                        if re.search(said, page) or (
                                THE_C5_READER_KNOWS_A_TABLELESS_MORNING
                                and prev_tableless and re.search(said, prev_page)) or (
                                THE_C5_READER_KNOWS_A_TABLELESS_MORNING
                                and THE_C5_READER_KNOWS_A_RUN_OF_TABLELESS_MORNINGS
                                and any(re.search(said, pg) for pg in tableless_run)):
                            fresh_told += 1
                        else:
                            missed.append(f"{n} t{t} {nation} newly free")
                prev_majors = majors
            prev_page, prev_tableless = page, tableless
            tableless_run = tableless_run + [page] if tableless else []
            if any(
                re.search(
                    r"keep .* out|to keep|buy off|price to",
                    str(r.get("text", "")),
                    re.I,
                )
                for r in g
            ):
                keep += 1
    if not THE_PROBE_READS_THE_WHOLE_PAGE:
        if seen == 0:
            return _un("no sponsorship against France after a peace on the CMD arms")
        return _res(
            True,
            led == seen and keep > 0,
            f"{seen} sponsorships against France after the peace; {led} led or sub-beat the dispatch; keep-out levers quoted {keep}",
        )
    if not peace_turns:
        return _un("no peace with a great power on the CMD arms")
    if not any("league_rows" in r for n in peace_turns for r in arms[n].kind("dispatch")):
        return _un("the dispatch records carry no league rows (a pre-SF7-X39 archive)")
    quoted, flips, bad = _c5_quoted_levers_flip(arms, ctx, peace_turns)
    ok = (led == seen and fresh_told == fresh_seen and quoted > 0 and not bad)
    return _res(
        True,
        ok,
        f"after the peace: {seen} sponsorships against France, {led} on the page; "
        f"{fresh_seen} great powers newly free to join, {fresh_told} on the page; "
        f"{quoted} quoted keep-out levers on the saves, {flips} flip the gate"
        + (f"; missed {missed[:4]}" if missed else "")
        + (f"; not flipping {bad[:3]}" if bad else ""),
    )


# ═════════════════════════ COMBAT LEGIBILITY ═════════════════════════
def combat_c3_capital_garrison(arms, ctx):
    """RS-3: a capital taken after a field battle in the same turn — the garrison fought or is named."""
    caps = set()
    try:
        world, _ = _fresh(ctx)
        caps = {
            r.name for r in world.regions.values() if getattr(r, "is_capital", False)
        }
    except Exception:
        caps = {
            "Vienna",
            "Berlin",
            "London",
            "Madrid",
            "Munich",
            "Dresden",
            "Amsterdam",
            "Milan",
            "Bern",
            "Naples",
            "Rome",
            "Lisbon",
            "Copenhagen",
            "Stockholm",
            "Constantinople",
            "Paris",
            "Turin",
            "Kassel",
            "Hanover",
        }
    cases = []
    bad = []
    for n in ("OP", "FLD", "CMD-H"):
        a = arms.get(n)
        if not a:
            continue
        for t, text in a.blocks():
            for cap in caps:
                if (
                    re.search(
                        rf"capture_choice\[capture\]: {re.escape(cap)},|{re.escape(cap)} has been captured by France|captured {re.escape(cap)}",
                        text,
                    )
                    and "⚔" in text
                ):
                    cases.append(f"{n} t{t} {cap}")
                    if not re.search(r"garrison", text, re.I):
                        bad.append(f"{n} t{t} {cap}")
                elif (
                    re.search(rf"halts before {re.escape(cap)}'s works", text)
                    and "⚔" in text
                ):
                    # RS-3 (Step 3): the field win no longer walks into the
                    # capital — the works halt names the garrison that must
                    # be assaulted. The garrison is NAMED: the item's pass arm.
                    cases.append(f"{n} t{t} {cap} (halted before the works)")
    if not cases:
        return _un("no capital taken after a field battle on the arms")
    return _res(
        True,
        not bad,
        f"{len(cases)} capital captures after a battle; garrison neither fought nor named: {bad[:3]}"
        if bad
        else f"{len(cases)} capital captures, the garrison fought or was named in each",
    )


# ═════════════════════════ MARSHAL DRAMA ═════════════════════════
def drama_f1_flagship_probe(arms, ctx):
    run_dir = pathlib.Path(ctx["run_dir"])
    p = run_dir / "arms" / "FLAG_probe.json"
    if not p.exists():
        return _un("the FLAG probe did not write its record")
    probe = json.loads(p.read_text(encoding="utf-8"))
    silent = len(probe.get("silent") or [])
    a = arms.get("FLAG")
    modals = sum(
        1 for r in (a.kind("popup") if a else []) if r.get("key") == "marshal_petition"
    )
    if a is None:
        return _un("the FLAG digest is missing")
    return _res(
        True,
        modals <= 4 and silent == 0,
        f"petition modals {modals} (≤ 4), silent losses {silent}, petition moments {len(probe.get('rows') or [])}",
    )


def drama_c2_trust_names_visible(arms, ctx):
    """RS-5: the Trust arm names a man seen before this turn, and a Trust taken does not lose the order."""
    cases = 0
    bad = []
    for n in ("OP", "FLD"):
        a = arms.get(n)
        if not a:
            continue
        seen_before = set()
        for g in _groups(a):
            t = g[0].get("turn")
            for r in g:
                if r.get("kind") != "popup" or r.get("key") != "objection":
                    continue
                m = re.search(
                    r"Trust him and he will attack ([A-Z][A-Za-z ]+?) at ([A-Z][A-Za-z' -]+)",
                    str(r.get("summary", "")),
                )
                if not m:
                    continue
                cases += 1
                who = m.group(1).strip()
                if who not in seen_before:
                    bad.append(f"{n} t{t}: Trust offers {who}, never seen before")
            for r in g:
                txt = json.dumps(r, ensure_ascii=False)
                for name in re.findall(
                    r"\b(Mack|Archduke Charles|Archduke John|Kutuzov|Buxhowden|Bennigsen|Bagration|Moore|Wellesley|Paget|Brunswick|Hohenlohe|Blücher|Deroy|Castanos|Damas)\b",
                    txt,
                ):
                    seen_before.add(name)
    if cases == 0:
        return _un("no Trust alternative naming a man on the arms")
    return _res(
        True,
        not bad,
        f"{cases} Trust alternatives; naming an unseen man: {bad[:3]}"
        if bad
        else f"{cases} Trust alternatives, each a man already in view",
    )


def drama_c3_no_repeated_line(arms, ctx):
    """RS-24: no marshal repeats his voice line within his last three wins (needs the SF-M `voice` field)."""
    seqs: dict = {}
    voiced = 0
    for n in ("OP", "FLD", "CMD-H", "CMD-A", "CMD-M"):
        a = arms.get(n)
        if not a:
            continue
        for r in a.kind("battle"):
            v = r.get("voice")
            if not v:
                continue
            voiced += 1
            m = re.match(
                r"(.+?) \(lost ([\d,]+)[^)]*\) vs (.+?) \(lost ([\d,]+)",
                str(r.get("headline", "")),
            )
            if not m:
                continue
            al, dl = int(m.group(2).replace(",", "")), int(m.group(4).replace(",", ""))
            if al >= dl:
                continue
            line = v.get("line") if isinstance(v, dict) else str(v)
            seqs.setdefault((n, m.group(1).strip()), []).append(str(line)[:80])
    if voiced == 0:
        return _un(
            "no battle record carries a marshal voice line (a pre-SF-M archive, or no voiced battle)"
        )
    rep = []
    for (n, who), lines in seqs.items():
        for i in range(len(lines)):
            if lines[i] in lines[max(0, i - 2) : i]:
                rep.append(f"{n} {who}: {lines[i][:50]!r}")
    return _res(
        True,
        not rep,
        f"{voiced} voiced battles; a line repeated within three wins: {rep[:3]}"
        if rep
        else f"{voiced} voiced battles, no repeat within three wins",
    )


def drama_c5_expectation_before_erosion(arms, ctx):
    """An unmet expectation is announced (the household/claim line) before the escalation that marks erosion."""
    cases = 0
    bad = []
    for n in ("OP", "CMD-H", "CMD-A", "CMD-M"):
        a = arms.get(n)
        if not a:
            continue
        first_notice: dict = {}
        first_erosion: dict = {}
        for t, l in _lines(a, "Marshal"):
            m = re.search(
                r"Marshal ([A-Z][a-z]+)'s (household goes unpaid|claim|patience)", l
            )
            # SR-7d exit (October 3, 2026): the "N turns without settlement on
            # Marshal X" line IS the first notice of an unmet claim (the SR-6a
            # standing class) and the reader had not counted it — CMD-H's
            # Bernadotte was announced at t13 and escalated at t15, and the
            # item read "first notice None". One more notice form.
            m2 = re.search(r"turns without settlement on Marshal ([A-Z][a-z]+)", l)
            if m2 and m2.group(1) not in first_notice:
                first_notice[m2.group(1)] = t
            if m:
                who = m.group(1)
                if (
                    re.search(r"goes unpaid|erodes with his purse|expects", l)
                    and who not in first_notice
                ):
                    first_notice[who] = t
                if (
                    re.search(r"question of the army|in arrears", l)
                    and who not in first_erosion
                ):
                    first_erosion[who] = t
        for who, te in first_erosion.items():
            cases += 1
            tn = first_notice.get(who)
            if tn is None or tn > te:
                bad.append(f"{n} {who}: escalation t{te}, first notice {tn}")
    if cases == 0:
        return _un("no marshal's expectation eroded on the arms")
    return _res(
        True,
        not bad,
        f"{cases} eroding claims; unannounced before the escalation: {bad[:3]}"
        if bad
        else f"{cases} eroding claims, each announced first",
    )


# ═════════════════════════ VASSALS ═════════════════════════
def _tag_key(name) -> str:
    return re.sub(r"[^a-z]", "", str(name or "").lower().replace("the ", "", 1))


def vassals_c2_petition_quote(arms, ctx):
    """A petition's quoted loyalty equals the ledger's reading the same turn (the −2 drift and the bond allowed).

    Step 5's exit (instrument correction): where the digest carries the
    satellite's end-turn `loyalty` row (`playtest_driver.loyalty_tick`), the
    quote is read against the loyalty the tick STARTED from — exact — not
    against the ledger, which also carries the turn's battles ("the lord's
    defeats", −2 a loss, the same for every satellite). Measured on CMD-A
    t7: Switzerland granted to 93, the tick started at 93 and closed at 86
    after four French defeats; the band read a false miss. The row read is
    the FIRST one for the satellite AFTER the grant in the record order — a
    petition answered in the end turn's drain comes after that turn's tick,
    and its ledger already reads the quote. No row after the grant (a quiet
    tick, a drain grant, or an archive from before the correction): the
    band, unchanged."""
    rows = []
    bad = []
    for n in CMD_ARMS:
        a = arms.get(n)
        if not a:
            continue
        for g in _groups(a):
            led = next((r for r in g if r.get("kind") == "ledger"), None)
            for i, r in enumerate(g):
                if r.get("kind") != "popup" or r.get("key") != "proposal_result":
                    continue
                m = re.search(
                    r"^(?:The )?([A-Z][A-Za-z ]+?)'s tribute is remitted.*?Loyalty ([+-]\d+) \((\d+) → (\d+)\)",
                    str(r.get("summary", "")),
                )
                if not m or not led:
                    continue
                who = m.group(1).replace("The ", "")
                quoted = int(m.group(4))
                vass = led.get("vassals") or {}
                key = next(
                    (k for k in vass if k.replace("The ", "") == who or who in k), None
                )
                if key is None:
                    continue
                actual = int(vass[key])
                rows.append((n, g[0].get("turn"), who, quoted, actual))
                tick = next((t for t in g[i + 1:] if t.get("kind") == "loyalty"
                             and _tag_key(t.get("vassal")) == _tag_key(who)), None)
                if tick is not None and tick.get("old") is not None:
                    if int(tick["old"]) != quoted:
                        bad.append(
                            f"{n} t{g[0].get('turn')} {who}: quoted {quoted}, the tick started at {tick['old']}"
                        )
                elif not (quoted - 3 <= actual <= quoted + 2):
                    bad.append(
                        f"{n} t{g[0].get('turn')} {who}: quoted {quoted}, ledger {actual}"
                    )
    if not rows:
        return _un("no priced petition with a ledger reading on the CMD arms")
    return _res(
        True,
        not bad,
        f"{len(rows)} petitions; quote ≠ applied (beyond the −2 drift): {bad[:3]}"
        if bad
        else f"{len(rows)} petitions, quote = applied within the turn's drift",
    )


def vassals_c3_client_not_left_at_war(arms, ctx):
    """SR-1b on the saves: France at peace with X ⇒ no French client at war with X."""
    checked = 0
    bad = []
    for n in CMD_ARMS:
        for p in _saves_of(arms, n):
            w = _load_world(ctx, p)
            checked += 1
            player = w.player_nation
            clients = [
                v
                for v, row in (getattr(w, "vassals", {}) or {}).items()
                if isinstance(row, dict) and row.get("lord") == player
            ]
            for x in w.get_active_nations():
                if x == player or x in clients:
                    continue
                if w.get_diplomatic_state(player, x) == "WAR":
                    continue
                for v in clients:
                    if (
                        v in w.get_active_nations()
                        and w.get_diplomatic_state(v, x) == "WAR"
                    ):
                        bad.append(
                            f"{n} t{_save_turn(p)}: {v} at war with {x} while France is at {w.get_diplomatic_state(player, x)}"
                        )
    if checked == 0:
        return _un("no CMD saves")
    return _res(
        True,
        not bad,
        f"{checked} saves; a client left at war: {bad[:3]}"
        if bad
        else f"{checked} saves, no client left at war after a French peace",
    )


def vassals_c5_client_capital_contested(arms, ctx):
    """VD-C: a client capital taken by an enemy is contested within 2 turns (a French or client attack there)."""
    cases = 0
    bad = []
    caps = {"Milan": "Kingdom of Italy", "Amsterdam": "Holland", "Bern": "Switzerland"}
    for n in CMD_ARMS:
        a = arms.get(n)
        if not a:
            continue
        blocks = a.blocks()
        for i, (t, text) in enumerate(blocks):
            for cap in caps:
                if re.search(
                    rf"{cap} has been captured by (Austria|Russia|Britain|Prussia|Sweden|Naples|Spain)",
                    text,
                ):
                    cases += 1
                    later = " ".join(x for _, x in blocks[i + 1 : i + 3])
                    if not re.search(
                        rf"⚔[^\n]*{cap}|attack[^\n]*{cap}|{cap} has been captured by (France|KingdomOfItaly|Holland|Switzerland)",
                        later,
                    ):
                        bad.append(f"{n} t{t} {cap}")
    if cases == 0:
        return _un("no client capital fell to an enemy on the CMD arms")
    return _res(
        True,
        not bad,
        f"{cases} client capitals taken; uncontested within 2 turns: {bad[:3]}"
        if bad
        else f"{cases} client capitals taken, each contested within 2 turns",
    )


# ═════════════════════════ COMMAND ═════════════════════════
# ═══ THE ONE JUDGE of a reply to a typed line (SF-CMD-1, October 3, 2026) ═══
# Read by `command_c3_hold_orders` (the HOLD arm) and by
# tools/unrehearsed_census.py (the 300-line held-out census) — never a second
# copy. Every regex here names a SHAPE of reply, not a game rule.
#
# ACTION_WORDS: the words a reply uses when it did the intended family.
ACTION_WORDS = {
    "attack": r"MUSTER|attack|pursu|⚔|marches on|falls upon|engag",
    "move": r"moves? (to|from)|begins march|march|Route:|road to|bars the way|reaches the approach",
    "hold": r"hold|defend|DEFENSIVE|stands? fast",
    "defend": r"hold|defend|DEFENSIVE|stands? fast",
    "scout": r"scout",
    "fortify": r"fortif",
    "unfortify": r"unfortif|breaks? camp|abandons? (the )?works",
    "drill": r"drill",
    "retreat": r"retreat|falls? back|withdraw|begins march|moves? (?:to|from)",
    "recruit": r"recruit|levy|raises|substitut",
    "substitutes": r"substitut",
    "build": r"build|construct|laid|depot|training ground|fort",
    "repair": r"repair",
    "garrison": r"garrison|detach",
    "invest": r"invest",
    "reward": r"estate|rente|pension|endow|duchy|duke|reward",
    "enact": r"enact|law|Staff|ordinance|Quartier",
    "repeal": r"repeal",
    "commission": r"commission|joins|Marshalate|takes up",
    "naval_build": r"keel|ships?|yard|sail",
    "naval_posture": r"fleet|posture|blockade|guard home|sortie|Admiralty",
    "naval_land": r"transport|land|expedition|lift|descent|ashore|ports",
    "naval_diversion": r"diversion",
    "diplomacy": r"Talleyrand|proposal|mission|envoy|guarantee|sponsor|departs|relations|court|state of Europe|conduct diplomacy|"
                 r"Sire,.*(peace|alliance|terms|tribute|design)",
    "declare_war": r"declar|war",
    "break_treaty": r"break|treaty|tears? up",
    "vassal": r"vassal|autonomy",
    "cede": r"cede|grant|ceded",
    "form_square": r"square",
    "end_turn": r"Turn \d+ ended|begins",
    "support": r"support|march|moves? to",
    "pursue": r"pursu|attack|MUSTER",
}
_ACTION_WORDS = ACTION_WORDS  # the HOLD reader's older name
# BOARD_GATE_RX: the BOARD refused a line it read right, and said why.
BOARD_GATE_RX = re.compile(
    r"No administrative actions|Not enough actions|actions remaining|treasury cannot|cannot support this|out of range|"
    r"enemy forces (nearby|present)|is a prisoner|not at war|cannot (drill|fortify|move|attack) (with|while|into)|"
    r"already (fortified|in|lies|have|met|full)|costs [\d,]+ gold|the treasury holds|is not in force|not currently fortified|"
    r"has not opened her ports|No damaged|No war damage|needs one victory|is a nation, not a province|only conquered land|"
    r"no eligible province|loyalty is already full|we do not court a belligerent|at WAR with|no treaty with|"
    r"not found\. Did you mean|supply lines cannot|blocks the path|destination blocked|runs through enemy country|"
    r"No intelligence on|No marshal of artillery can reach|cannot reach|not controlled by France|We do not hold|"
    r"still stands|No province is eligible|I am a diplomat, not a general|"
    # SF-CMD-1 (ii), the fresh census (Oct 3, 2026): the board's own refusals
    # the first judge could not read — a foreign commander, a court that is no
    # vassal, a name on no bench, an inland shore, a garrison left where the
    # corps stands, an enemy named as a friend, an unknown target.
    r"does not answer to us|commands for \w+, Sire|is not a vassal|Unknown target|No candidate named|"
    r"has no shore|is left where the corps stands|is an enemy! Use|cannot bombard|is already a dockyard|"
    r"no corps of ours can|The order rested on|commands no guns|"
    # Chunk 3b (Oct 3, 2026): "Lannes, follow Ney in and back him up" now
    # reads as the SUPPORT it means, and the board answers with the march
    # law's own state refusal — the engaged arm of `march_state_refusal`.
    r"cannot begin a strategic march|"
    # Step 7 slice 5b (CX-BEHAV-1, Oct 4, 2026): the help census, re-keyed to
    # this judge, found three of the board's own refusals it did not know —
    # a rente revoked from a man who holds none, a bombard with no gun corps
    # in reach, the Congress short of its titled provinces. None appears in a
    # committed census record (grepped `docs/audits/unrehearsed/` and the
    # score-run archives first).
    r"holds no rente|No artillery marshals available|cannot be summoned on|summon the Congress first|"
    # SF7-X44 (Step 7's exit, Oct 5, 2026): the HOLD arm re-read on the final
    # tree (SF-V9's closing note left the reading to "the session exit") —
    # four of the board's own refusals this judge could not read: the levy a
    # named marshal raises where he stands (§6 row 19), the town that holds no
    # building, a retreat for a marshal in no danger, and the design a
    # sponsorship would arm aimed at another court (SF7-X43 routes the idiom
    # to the verb). Grepped `docs/audits/unrehearsed/` first: the fresh record
    # holds one "rural regions don't support buildings" (row 107, read
    # `as_meant`), so the town refusal is matched by its own words and that
    # record re-reads unchanged.
    r"raises its levy where it stands|town regions don't support buildings|is not in danger|"
    r"We can only arm the grievance|"
    # DD0-8 (October 10, 2026): the third blind set's board refusals this
    # judge could not read — the Admiralty's rule, a court that cannot be
    # vassalized, a province we do not control, a corps that is not cavalry,
    # a marshal of our own named as the foe. Grepped against the three
    # committed census records first (none appears) and the score archive's
    # HOLD arm re-read identical after.
    r"takes its orders from the Emperor|Cannot vassalize|We do not control|is not cavalry|"
    r"will not attack our own",
    re.I,
)
# ASKED_RX: the game asked before acting (a clarification, an objection).
ASKED_RX = re.compile(
    r"Which marshal|which marshal should act|Name the marshal|Whom did you intend|Did you mean|How shall I proceed|"
    r"Your orders\?|raises concerns|firmly objects|objects:|Shall I|One order at a time|"
    r"Whose household|Where shall|Which province|Name the province|"
    # DD0-8 (October 10, 2026): an objection's "challenges the order", the
    # bare attack's "shall we engage", "whom shall … engage", the cabinet's
    # "which nation", "Attack whom" and "Which is it to be".
    r"challenges the order|shall we engage|whom shall \w+ engage|which nation|Attack whom|"
    r"Which is it to be",
    re.I,
)
# REFUSED_RX: the game could not read the line and said so (spending nothing).
REFUSED_RX = re.compile(
    r"cannot interpret|await clear|Cannot find|not found|eludes me|cannot parse|instruction is unclear|"
    r"in the order of battle|await your instructions|could not make out a destination|contingency, not an order|"
    r"I do not find|cannot determine|cannot make sense|then no order goes out|relayed nothing|appears in no roster|"
    # DD0-8 (October 10, 2026): "Charge requires a marshal", "I need a marshal and an action".
    r"requires a marshal|I need a marshal and an action|"
    # S3b: the live model's own words — "I must confess myself quite bewildered"
    r"confess myself",
    re.I,
)
MISREAD_RX = REFUSED_RX  # the HOLD reader's older name


def command_c3_hold_orders(arms, ctx):
    a = arms.get("HOLD")
    if not a:
        return _un("HOLD did not run")
    script = ctx.get("hold_script") or {}
    orders = (script.get("hold") or {}).get("orders", [])
    cmds = {str(c.get("text", "")).strip().lower(): c for c in a.kind("command")}
    good = 0
    seen = 0
    misses = []
    for o in orders:
        c = cmds.get(o["line"].strip().lower())
        if not c:
            continue
        seen += 1
        intended = o.get("intended") or {}
        action = str(intended.get("action", ""))
        who = str(intended.get("marshal", ""))
        msg = str(c.get("message", ""))
        # a refusal that names the board's own reason (out of reach, engaged, no gold) counts as "read as meant" only if it names the intended marshal
        # SF-CMD-1 (October 3, 2026): the ONE judge's regexes (module constants
        # above), shared with tools/unrehearsed_census.py.
        names_action = bool(re.search(ACTION_WORDS.get(action, action), msg, re.I))
        board_gate = bool(BOARD_GATE_RX.search(msg))
        misread = bool(REFUSED_RX.search(msg))
        read_ok = (not misread) and (
            c.get("success") is True
            and names_action
            or board_gate
            and (who in ("state", "") or who.split()[-1] in msg)
        )
        if read_ok:
            good += 1
        else:
            misses.append(f"{o['line'][:40]!r} → {msg[:60]}")
    if seen < 15:
        return _un(f"only {seen} HOLD orders on the digest")
    return _res(
        True,
        good >= 18,
        f"{good}/{seen} orders executed as meant; misses: {misses[:4]}",
    )


# ═════════════════════════ NARRATION ═════════════════════════
def narration_c3_near_miss_headline(arms, ctx):
    """RS-17: when a road comes within 5 of the summons (or reaches it), the dispatch says so."""
    reached = []
    for n in ("CMD-H", "CMD-A", "CMD-M", "REACH-AAR", "REACH-GEVB"):
        a = arms.get(n)
        if not a:
            continue
        rows = [
            r
            for r in (a.titled.get("rows") or [])
            if isinstance(r, dict) and "titled" in r
        ]
        for r in rows:
            if int(r["titled"]) >= 40:
                t = int(r.get("turn", 0))
                heads = [
                    str(x.get("headline", ""))
                    for g in _groups(a)
                    if g and g[0].get("turn") in (t - 1, t, t + 1)
                    for x in g
                    if x.get("kind") == "dispatch"
                ]
                reached.append(
                    (
                        n,
                        t,
                        int(r["titled"]),
                        any(re.search(r"Congress", h) for h in heads),
                    )
                )
    if not reached:
        return _un("no road came within 5 of the summons on the arms")
    ok = all(x[3] for x in reached)
    return _res(
        True,
        ok,
        f"near-miss/summonable readings (arm, turn, titled, Congress headline): {reached[:4]}",
    )


def narration_c4_intel_row(arms, ctx):
    """AAR-5: every intelligence row in the stored dispatch places its marshal where the intel store last saw him."""
    checked = 0
    bad = []
    stale_after_refresh = []
    for n in CMD_ARMS:
        for p in _saves_of(arms, n):
            w = _load_world(ctx, p)
            rows = (getattr(w, "last_morning_dispatch", None) or {}).get(
                "intelligence"
            ) or []
            for row in rows:
                if row.get("kind") == "garrison":
                    continue   # SR-6a: a garrison row is a province, not a man
                checked += 1
                shown = str(row.get("name", ""))
                candidates = [str(row.get("roster_name") or ""), shown, shown.replace(" ", "")] + [
                    k
                    for k in w.marshals
                    if k.replace(" ", "").lower() == shown.replace(" ", "").lower()
                ]
                candidates = [c for c in candidates if c]
                lk = next(
                    (
                        w.get_last_known_location(c)
                        for c in candidates
                        if w.get_last_known_location(c)
                    ),
                    None,
                )
                # AAR-5 (Step 2): a LIVE row places the man where he STANDS in a
                # province in full view this morning — the store's last sighting
                # may be a turn older (it is written before the enemy phase).
                live_ok = False
                if row.get("source") == "live":
                    from backend.models.intel import FULL as _FULL
                    _m = next((w.marshals.get(c) for c in candidates if w.marshals.get(c)), None)
                    _intel = w.intel.get(str(row.get("location") or ""))
                    live_ok = bool(_m is not None and _m.location == row.get("location")
                                   and _intel is not None and _intel.visibility == _FULL)
                # SF-CL-1 exit (October 3, 2026): the dispatch is the MORNING's
                # and the save is the evening's. A frozen snapshot row whose
                # province the store RE-READ after the row's own turn (its
                # `last_updated_turn` is later than the row's `intel_turn`)
                # was true when written — measured CMD-A turn 10: Brunswick's
                # turn-2 Berlin snapshot rode the morning rows, then Berlin
                # was read again that turn (partial, empty: he had marched to
                # Hanover's war) and the region-keyed store forgot him. The
                # row said what the store last said; the store moved on.
                refreshed_after = False
                if row.get("source") == "snapshot" and not live_ok:
                    _region = w.intel.get(str(row.get("location") or ""))
                    try:
                        refreshed_after = (
                            _region is not None
                            and int(getattr(_region, "last_updated_turn", 0) or 0)
                            > int(row.get("intel_turn") or 0))
                    except (TypeError, ValueError):
                        refreshed_after = False
                if refreshed_after:
                    stale_after_refresh.append(
                        f"{n} t{_save_turn(p)}: {shown} at {row.get('location')} (row t{row.get('intel_turn')}, "
                        f"province re-read t{getattr(w.intel.get(str(row.get('location') or '')), 'last_updated_turn', '?')})")
                elif not live_ok and (not lk or lk[0] != row.get("location")):
                    bad.append(
                        f"{n} t{_save_turn(p)}: {shown} shown at {row.get('location')}, store says {lk[0] if lk else None}"
                    )
    if checked == 0:
        return _un("no intelligence rows on the saves")
    note = (f"; {len(stale_after_refresh)} morning rows whose province the store re-read later that turn: "
            f"{stale_after_refresh[:2]}" if stale_after_refresh else "")
    return _res(
        True,
        not bad,
        (f"{checked} intel rows; disagreeing with the store: {bad[:3]}" if bad
         else f"{checked} intel rows, each where the store last saw the man or where he stands in full view")
        + note,
    )


def narration_c5_moniteur(arms, ctx):
    out = []
    ok = True
    for n in CMD_ARMS:
        saves = [p for p in _saves_of(arms, n) if _save_turn(p) >= 40]
        if not saves:
            continue
        w = _load_world(ctx, saves[-1])
        turns = sorted(int(i.get("turn", 0)) for i in (w.gazette_issues or []))
        specials = [
            int(i.get("turn", 0)) for i in (w.gazette_issues or []) if i.get("special")
        ]
        # the cadence: an issue at least every 5 turns over the window the store still holds (a special may reset the clock)
        series = turns + [int(w.current_turn)]
        gaps = [b - a for a, b in zip(series, series[1:])]
        longest = max(gaps) if gaps else None
        ok = (
            ok
            and bool(turns)
            and longest is not None
            and longest <= 5
            and bool(specials)
        )
        out.append(
            f"{n}: {len(turns)} issues at {turns}, specials {specials}, longest silence {longest} turns"
        )
    if not out:
        return _un("no turn-40 save")
    return _res(True, ok, " | ".join(out))


# ═════════════════════════ AI ALIVENESS ═════════════════════════
def ai_c4_garrison_grind(arms, ctx):
    triples = []
    assaults = 0
    for n in CMD_ARMS:
        a = arms.get(n)
        if not a:
            continue
        streak: dict = {}
        for g in _groups(a):
            t = g[0].get("turn")
            this_turn = set()
            for r in g:
                if r.get("kind") != "enemy_phase":
                    continue
                for act in r.get("actions") or []:
                    m = re.search(
                        r"([A-Za-z]+) assaults the ([A-Za-z' -]+?) garrison",
                        str(act.get("message", "")),
                    )
                    if m:
                        assaults += 1
                        key = (m.group(1), m.group(2))
                        this_turn.add(key)
            for key in this_turn:
                streak[key] = streak.get(key, 0) + 1
                if streak[key] >= 3:
                    triples.append(f"{n} t{t}: {key[0]} at {key[1]} ×{streak[key]}")
            for key in list(streak):
                if key not in this_turn:
                    streak[key] = 0
    if assaults == 0:
        return _un("no garrison assault on the CMD arms")
    return _res(
        True,
        not triples,
        f"{assaults} garrison assaults; three running on one garrison: {triples[:3]}"
        if triples
        else f"{assaults} garrison assaults, none three turns running",
    )


def ai_c5_fortify_dither(arms, ctx):
    dithers = []
    acts = 0
    for n in CMD_ARMS:
        a = arms.get(n)
        if not a:
            continue
        hist: dict = {}
        for g in _groups(a):
            t = g[0].get("turn")
            for r in g:
                if r.get("kind") != "enemy_phase":
                    continue
                for act in r.get("actions") or []:
                    verb = str(act.get("action", ""))
                    who = str(act.get("marshal", ""))
                    if verb in ("fortify", "unfortify"):
                        acts += 1
                        hist.setdefault(who, []).append((t, verb))
        for who, seq in hist.items():
            for i in range(len(seq) - 2):
                (t1, v1), (t2, v2), (t3, v3) = seq[i], seq[i + 1], seq[i + 2]
                if (v1, v2, v3) == ("fortify", "unfortify", "fortify") and t3 - t1 <= 3:
                    dithers.append(f"{n} {who} t{t1}–t{t3}")
    if acts == 0:
        return _un("no AI fortify/unfortify on the CMD arms")
    return _res(
        True,
        not dithers,
        f"{acts} fortify/unfortify acts; fortify→unfortify→fortify within 3 turns: {dithers[:3]}"
        if dithers
        else f"{acts} acts, no dither",
    )


# ═════════════════════════ AGENDAS ═════════════════════════
def _formables(ctx, world):
    from backend.game_logic import formations as F

    return F.build_formables_payload(world)


def agendas_f2_formables_on_saves(arms, ctx):
    checked = 0
    bad = []
    for n in CMD_ARMS:
        for p in _saves_of(arms, n):
            w = _load_world(ctx, p)
            payload = _formables(ctx, w)
            rows = (
                payload.get("rows")
                or payload.get("templates")
                or payload.get("formables")
                or (payload if isinstance(payload, list) else [])
            )
            if not rows:
                bad.append(f"{n} t{_save_turn(p)}: no rows")
                continue
            for row in rows:
                checked += 1
                terms = row.get("gate_terms")
                if (
                    not isinstance(terms, list)
                    or not terms
                    or not all(
                        isinstance(x, dict) and "text" in x and "met" in x
                        for x in terms
                    )
                ):
                    bad.append(
                        f"{n} t{_save_turn(p)} {row.get('tag') or row.get('id')}: gate_terms {str(terms)[:40]}"
                    )
    if checked == 0 and not bad:
        return _un("no CMD saves")
    return _res(
        True,
        not bad,
        f"{checked} formable rows on the saves; without honest gate terms: {bad[:3]}"
        if bad
        else f"{checked} rows, each with its gate terms",
    )


def _gate_term_key(text) -> str:
    """Step 5 instrument correction (SF-AGD-1): a province-held gate term
    carries its holder while UNMET — "Posen held at the settlement table
    (currently Prussia-held)" — and drops it when met, so a reader keyed on
    the raw text could never see that term flip. The key is the text
    without its "(currently …)" tail."""
    return re.sub(r"\s*\(currently [^)]*\)\s*$", "", str(text or ""))


def agendas_c3_gate_flips(arms, ctx):
    flips = []
    seen = 0
    for n in ("CMD-H", "CMD-A", "CMD-M", "CMD-ULM"):
        saves = _saves_of(arms, n)
        prev = None
        for p in saves:
            w = _load_world(ctx, p)
            payload = _formables(ctx, w)
            rows = (
                payload.get("rows")
                or payload.get("templates")
                or payload.get("formables")
                or []
            )
            cur = {}
            for row in rows:
                for term in row.get("gate_terms") or []:
                    cur[(row.get("tag") or row.get("id"),
                         _gate_term_key(term.get("text")))] = bool(term.get("met"))
                    seen += 1
            if prev is not None:
                for k, v in cur.items():
                    if v and prev.get(k) is False:
                        flips.append(f"{n} t{_save_turn(p)}: {k[0]} — {str(k[1])[:50]}")
            prev = cur
    if seen == 0:
        return _un("no gate terms on the saves")
    return _res(
        True,
        bool(flips),
        f"gate terms flipping to met between saves: {flips[:4]}"
        if flips
        else f"{seen} gate-term readings, none flipped to met between the saves",
    )


def _duchy_gate_terms(ctx, world) -> dict:
    payload = _formables(ctx, world)
    rows = payload.get("rows") or payload.get("templates") or payload.get("formables") or []
    for row in rows:
        if (row.get("tag") or row.get("id")) == "DuchyOfWarsaw":
            return {_gate_term_key(t.get("text")): bool(t.get("met"))
                    for t in (row.get("gate_terms") or [])}
    return {}


def agd_gate_flip(arm, ctx) -> str:
    """SF-AGD-1's evidence line: the Duchy of Warsaw's formables gate terms on
    the AGD fixture (Posen still Prussian) against the arm's FIRST save (after
    the turn Posen was taken) — the terms that flipped to met in play."""
    fixture = ROOT / "tests" / "fixtures" / "playtest_saves" / "fixture_agd_tilsit.json"
    saves = sorted((arm.path / "saves").glob("AGD_t*.json")) if (arm.path / "saves").exists() else []
    if not fixture.exists() or not saves:
        return "gate flip unmeasured (no fixture or no save)"
    before = _duchy_gate_terms(ctx, _load_world(ctx, fixture))
    after = _duchy_gate_terms(ctx, _load_world(ctx, saves[0]))
    flipped = [t for t, met in after.items() if met and before.get(t) is False]
    if not flipped:
        return f"no Duchy gate term flipped between the fixture and {saves[0].name}"
    return f"gate flipped to met in play ({saves[0].name}): " + "; ".join(t[:70] for t in flipped)


def agendas_c4_tilsit(arms, ctx):
    """TILSIT (§4.6): the IGR-D fixture — France six turns at war with Prussia, holding Posen — offers the Warsaw
    carve as a separate peace; the game's OWN scorer answers (nothing patched) and, if it accepts, the treaty is
    ratified at the seam the dialogue's accept reaches; `nation_proclamation` fires and DuchyOfWarsaw stands."""
    _boot(ctx)
    try:
        import importlib.util

        path = ROOT / "tests" / "test_igr_d_carve_completable.py"
        spec = importlib.util.spec_from_file_location("_sf_tilsit_fixture", path)
        T = importlib.util.module_from_spec(spec)
        with contextlib.redirect_stdout(io.StringIO()):
            spec.loader.exec_module(T)
            # the DoD's precondition: a court that has actually been BEATEN (its field army gone, Posen/Berlin/Silesia held)
            world = T._beaten_prussia()
            from backend.game_logic.diplomacy import calculate_acceptance

            tried = []
            proposal = None
            # both arms are measured and recorded; only an ACCEPT is a signature (IGR-D: the
            # counter-offer drops the client, so a COUNTER is not the Tilsit road completed)
            for label, sweeteners in (
                ("bare", []),
                ("+6,000g", [{"type": "gold_lump", "value": 6000}]),
            ):
                cand = {
                    "type": "peace",
                    "proposer_nation": "France",
                    "target_nation": "Prussia",
                    "sweeteners": sweeteners,
                    "demands": [T._carve_demand()],
                }
                verdict = calculate_acceptance(cand, world)
                score = verdict.get("score")
                outcome = str(verdict.get("outcome", ""))
                tried.append(f"{label}: {outcome} at {score}")
                if proposal is None and outcome.upper().startswith("ACCEPT"):
                    proposal = cand
            if proposal is None:
                return _res(
                    True,
                    False,
                    "Prussia does not SIGN the Tilsit carve unpatched on the beaten board — a counter is "
                    "not a signature — " + "; ".join(tried),
                )
            world._ratify_treaty(proposal)
            minted = (
                "DuchyOfWarsaw" in world.get_active_nations()
                and world.regions["Posen"].controller == "DuchyOfWarsaw"
            )
            card = world.nation_proclamation_popup
    except Exception as exc:
        return _un(f"the Tilsit road raised {type(exc).__name__}: {str(exc)[:160]}")
    ok = minted and bool(card) and card.get("display_name") == "Duchy of Warsaw"
    return _res(
        True,
        ok,
        f"the scorer answers ({'; '.join(tried)}); DuchyOfWarsaw minted from Posen: {minted}; the Proclamation card: "
        + (
            f"{card.get('display_name')!r}, {card.get('subtitle')!r}"
            if card
            else "none"
        ),
    )


# ═════════════════════════ CHECKLIST v1.1 (October 5, 2026) ═════════════════════════
# `docs/SCORE_CHECKLIST_V1_1.json` re-reads two items under the delegate's rulings
# on SCORE_FINISH_SPEC.md §6 rows 18 and 22 (gate record §6.7). The v1 readers
# above are untouched, so a v1 check of any archive reads what it always read;
# `tools/score_reread.py` re-reads a committed reading beside its v1 record.

_C5_FORTIFY_AT = re.compile(r"fortifies position at (?P<place>[^.\n]+?)\.", re.I)
_C5_STATE_CHANGE = ("attack", "move", "retreat", "naval_expedition")


def ai_c5_fortify_dither_v11(arms, ctx):
    """§6 row 18 (RULED October 5, 2026): SR-7a's own definition of the dither —
    an AI corps digs in, breaks camp and digs in AGAIN IN THE SAME PLACE within
    3 turns, idle between (no attack, move, retreat or landing in the window).
    A corps that broke camp to march or fight and dug in where it arrived is a
    campaign, not a dither; the v1 reader counted it (the final reading's two
    hits: Archduke Charles struck Carniola and Franconia between his works).
    An unreadable place is never excused silently — it counts as the same."""
    dithers, excused, acts = [], [], 0
    for n in CMD_ARMS:
        a = arms.get(n)
        if not a:
            continue
        seq: dict = {}
        for g in _groups(a):
            t = g[0].get("turn")
            for r in g:
                if r.get("kind") != "enemy_phase":
                    continue
                for act in r.get("actions") or []:
                    verb = str(act.get("action", ""))
                    who = str(act.get("marshal", ""))
                    place = None
                    if verb == "fortify":
                        m = _C5_FORTIFY_AT.search(str(act.get("message", "")))
                        place = m.group("place").strip() if m else None
                    if verb in ("fortify", "unfortify"):
                        acts += 1
                    seq.setdefault(who, []).append((t, verb, place))
        for who, s in seq.items():
            fu = [i for i, st in enumerate(s) if st[1] in ("fortify", "unfortify")]
            for k in range(len(fu) - 2):
                i1, i2, i3 = fu[k], fu[k + 1], fu[k + 2]
                (t1, v1, p1), (_t2, v2, _p2), (t3, v3, p3) = s[i1], s[i2], s[i3]
                if (v1, v2, v3) != ("fortify", "unfortify", "fortify") or t3 - t1 > 3:
                    continue
                between = [f"{v}@t{t}" for (t, v, _p) in s[i2 + 1:i3] if v in _C5_STATE_CHANGE]
                same = (p1 is None or p3 is None) or p1 == p3
                if same and not between:
                    dithers.append(f"{n} {who} t{t1}–t{t3} at {p3 or p1 or '?'}")
                else:
                    why = ([f"{p1}→{p3}"] if not same else []) + (
                        ["between: " + ", ".join(between[:4])] if between else [])
                    excused.append(f"{n} {who} t{t1}–t{t3} ({'; '.join(why)})")
    if acts == 0:
        return _un("no AI fortify/unfortify on the CMD arms")
    tail = f"; excused (moved or fought between): {excused[:3]}" if excused else ""
    return _res(
        True,
        not dithers,
        (f"{acts} fortify/unfortify acts; dug in again in place, idle between, "
         f"within 3 turns: {dithers[:3]}" if dithers
         else f"{acts} acts, no dither in place") + tail,
    )


def _longest_consecutive_run(turns) -> int:
    """The longest run of consecutive integers in `turns` (0 when empty)."""
    best = run = 0
    prev = None
    for t in sorted(set(int(x) for x in turns)):
        run = run + 1 if prev is not None and t == prev + 1 else 1
        best = max(best, run)
        prev = t
    return best


def drama_f1_flagship_probe_v11(arms, ctx):
    """§6 row 22 (RULED October 5, 2026): the flagship arm against the bar the
    user CONFIRMED for the petition revisit (PETITION_POPUP_REVISIT_SPEC.md
    §6 Q4 / §8) — at most 9 blocking petition modals in the 24 turns, no run
    of modals on more than 2 consecutive turns, and 0 silent losses. The v1
    item's "≤ 4" was the B5 re-run's own measurement (3) plus one, never the
    bar the user confirmed; the crisis tier's threshold is not the lever
    (raising it to level 3 hides the level-2 card, the one window in which a
    Promise can still stop the spiral)."""
    run_dir = pathlib.Path(ctx["run_dir"])
    p = run_dir / "arms" / "FLAG_probe.json"
    if not p.exists():
        return _un("the FLAG probe did not write its record")
    probe = json.loads(p.read_text(encoding="utf-8"))
    silent = len(probe.get("silent") or [])
    a = arms.get("FLAG")
    if a is None:
        return _un("the FLAG digest is missing")
    modals = 0
    turns = []
    for g in _groups(a):
        here = sum(1 for r in g
                   if r.get("kind") == "popup" and r.get("key") == "marshal_petition")
        if here:
            modals += here
            turns.append(int(g[0].get("turn") or 0))
    longest = _longest_consecutive_run(turns)
    return _res(
        True,
        modals <= 9 and longest <= 2 and silent == 0,
        f"petition modals {modals} (≤ 9) on turns {turns}, the longest run of "
        f"consecutive turns {longest} (≤ 2), silent losses {silent}, petition "
        f"moments {len(probe.get('rows') or [])}",
    )
