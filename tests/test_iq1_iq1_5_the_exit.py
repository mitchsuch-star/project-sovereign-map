"""IQ-1 IQ1-5 — "The Exit": the row's four completion items, made falsifiable.

Landing record = `docs/IMPROVEMENT_QUEUE_SPEC.md` §0.6b. IQ1-5 ships **zero
production code** by definition; what it ships is a grade, and a grade written
in prose is not a measurement. These pins are the grade, so that the day any of
it stops being true something goes red instead of a document going stale.

⚠ **THE TRAP THIS FILE EXISTS AROUND.** `WorldState.advance_turn` calls
`process_income_phase` internally. A probe that calls BOTH charges the nation
twice and then reads its own double charge as an unnamed residual — measured
growing 590 -> 1,061 gold/turn, and entirely fictional. Two of the exit's own
probes did exactly that before the third one traced the call sites. Every test
here that advances time advances it **once**, through `advance_turn` alone, and
reads the applied figures out of `world._income_phase_results`.

What is pinned:

* **(i)** a treasury fall whose LARGEST single term is a player-initiated spend,
  with provinces non-decreasing across that turn — counted over the committed
  archives, which is the only place the three arms exist side by side.
* **(ii)** the item the row could NOT close: a beaten France out-earns a whole
  one, and it is a ratchet rather than a handicap. Pinned as a live measurement
  with a direction, so that when question (c)'s design gate builds its answer
  this file reds and says which half moved. **RULED September 28, 2026
  (SR-5a): keep the rules, make them legible** — the pins now record the
  ruled board's shape and that the ledger says why each bill moved.
* **(iii)** the purse census: exactly FOUR production sites move France's gold
  in a real turn, and exactly ONE of them is invisible to Net.
* **IQ1-5-1** the new finding: the Charges of Empire are quoted one war-effort
  tick stale. A characterization pin — it asserts the defect, names its cause,
  and is written so that FIXING it reds this file.

Item (iv) is not re-pinned here; it lives in
`tests/test_iq1_iq1_3_the_granary.py::TestCompletionItemFour`, with its negative
control, and is mutation-proven there.
"""

from tests._ledgers import doc_text  # CODE-4: the ledger plus its archives
import contextlib
import io
import json
import pathlib
import traceback

import pytest

from backend.game_logic import ledger as L
from backend.game_logic import instruments as INST
from backend.game_logic.ledger import NET_GOLD_COMPONENTS
from backend.models.world_state import (
    CHARGES_HOARD_FLOOR,
    WAR_EFFORT_DIVISOR,
    WorldState,
)

SCENARIO = "godot-client/project-sovereign/assets/maps/europe_1805.json"
DIGESTS = (pathlib.Path(__file__).resolve().parents[1]
           / "docs" / "audits" / "playtest_digests")

SPENDER = "iq13-spender-cmd-historical"
CONTROL = "iq13-control-cmd-historical"
AMBIENT = "iq1-ambient-baseline-historical"


def _quiet(fn, *a, **kw):
    """The engine narrates to stdout; the measurement is the return value."""
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **kw)


def _boot(gold=40_000, seed="historical"):
    world = _quiet(WorldState.from_scenario, SCENARIO, seed=seed)
    world.nation_gold["France"] = gold
    return world


# ---------------------------------------------------------------------------
# item (i) — the treasury falls, and it falls because the player SPENT
# ---------------------------------------------------------------------------

def _arm_turns(name):
    """Per-turn rows from a committed archive's jsonl, in order."""
    path = DIGESTS / name / "digest.jsonl"
    if not path.exists():
        pytest.skip(f"archive {name} carries no jsonl")
    rows = [json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]
    out, cur = [], None
    for row in rows:
        kind = row.get("kind")
        if kind == "turn":
            if cur:
                out.append(cur)
            cur = {"turn": row.get("turn"), "spent": 0}
        elif cur is None:
            continue
        elif kind == "turn_spend":
            cur["spent"] = int(row.get("spent", 0) or 0)
        elif kind == "ledger":
            cur.update(treasury=row.get("treasury"),
                       provinces=row.get("provinces"))
    if cur:
        out.append(cur)
    return [t for t in out if t.get("treasury") is not None]


def sink_driven_falls(turns):
    """Completion item (i), re-stated (§0.7).

    A treasury fall counts ONLY when the player's own recorded spend outweighs
    everything else that moved the chest that turn AND the board did not shrink
    across it. The province clause is what stops a collapse scoring as a sink —
    which is the whole reason §0.6 forbids grading the exit on the spender
    script's end state.
    """
    qualifying = []
    for before, after in zip(turns, turns[1:]):
        delta = after["treasury"] - before["treasury"]
        if delta >= 0:
            continue
        spend = after["spent"]
        residual = abs(delta) - spend
        if spend > 0 and spend > residual and after["provinces"] >= before["provinces"]:
            qualifying.append(after["turn"])
    return qualifying


def all_falls(turns):
    return [b["turn"] for a, b in zip(turns, turns[1:])
            if b["treasury"] < a["treasury"]]


class TestCompletionItemOne:
    """The sink is visible in the treasury, and only on the arm that uses it."""

    def test_the_spender_arm_falls_because_it_spent(self):
        turns = _arm_turns(SPENDER)
        assert sink_driven_falls(turns) == [6, 12, 15, 18, 21, 24, 27, 30, 36, 39]

    def test_the_predicate_rejects_the_turns_the_board_shrank(self):
        """⚠ The load-bearing half. The spender arm HAS two falls driven by a
        large spend on a turn it lost a province (turn 9: 29 -> 28, turn 33:
        29 -> 27). Item (i) must not count them, or the row would be scoring
        its own collapse as absorption."""
        turns = _arm_turns(SPENDER)
        by_turn = {t["turn"]: t for t in turns}
        qualifying = set(sink_driven_falls(turns))
        for lost, prev in ((9, 8), (33, 32)):
            assert by_turn[lost]["provinces"] < by_turn[prev]["provinces"]
            assert by_turn[lost]["spent"] > 3_000, "these ARE big-spend turns"
            assert lost not in qualifying

    def test_a_fall_the_player_did_not_cause_does_not_count(self):
        """⚠ WRITTEN BECAUSE A MUTATION CAME BACK INERT. Dropping the
        `spend > residual` clause changed no arm's answer — every big-spend
        turn on the spender arm happens to be spend-dominated — so the clause
        that makes item (i) mean anything was unpinned. Here is the case it
        exists for: a turn where the player spent, and lost far more to
        everything else."""
        turns = [
            {"turn": 1, "treasury": 10_000, "provinces": 20, "spent": 0},
            {"turn": 2, "treasury": 4_000, "provinces": 20, "spent": 500},
        ]
        assert sink_driven_falls(turns) == []
        turns[1]["spent"] = 5_500          # now the spend IS the largest term
        assert sink_driven_falls(turns) == [2]

    def test_the_control_arm_never_falls_at_all(self):
        """The disease, stated as a measurement: forty turns, no fall."""
        turns = _arm_turns(CONTROL)
        assert all_falls(turns) == []
        assert sink_driven_falls(turns) == []

    def test_the_collapsing_arm_falls_constantly_and_qualifies_never(self):
        turns = _arm_turns(AMBIENT)
        assert len(all_falls(turns)) > 20
        assert sink_driven_falls(turns) == []


# ---------------------------------------------------------------------------
# item (ii) — the one the row could not close
# ---------------------------------------------------------------------------

def _french_army(world):
    return sum(m.strength for m in world.marshals.values()
               if m.nation == "France" and m.strength > 0)


def _french_corps(world):
    return sorted(n for n, m in world.marshals.items()
                  if m.nation == "France" and m.strength > 0)


def _beaten(world):
    """Halve the army, lose five provinces, mark the rest with the war."""
    for marshal in world.marshals.values():
        if marshal.nation == "France":
            marshal.strength = int(marshal.strength * 0.5)
            marshal.morale = 40
    held = [r for r in world.regions.values() if r.controller == "France"]
    for region in held[:5]:
        region.controller = "Austria"
    for region in held[5:]:
        region.war_damage = min(0.5, region.war_damage + 0.35)
        region.stability = max(10, region.stability - 45)
    return world


def _hold_at_peace(world):
    from backend.game_logic.diplomacy import set_diplomatic_state
    for other in list(world.get_nations_at_war_with("France")):
        _quiet(set_diplomatic_state, world, "France", other, "PEACE")


class TestCompletionItemTwo:
    """MEASURED FALSE. Pinned so the (c) gate's answer reds this file.

    ── RULED September 28, 2026 — SR-5a "The chest", question (c) ──────────
    The user kept the rules and asked for them to be legible: the army is
    paid for the men under arms (the July 14 reversal of EC-U1 — the fallen
    draw no pay) and the Charges of Empire are a share of the chest (EB-1 — a
    fuller chest pays more). Nothing about either rule moved; the ledger now
    names why each bill moved since the last turn it charged
    (`ledger.why_the_bills_moved`, `TestTheLedgerSaysWhy` below).

    The same session's ruled balance package ("Britain up, France trimmed":
    every French homeland province at three-quarters of its registry yield)
    changes the SHAPE these pins measure, and they are rewritten to it rather
    than deleted: the whole France's homeland no longer pays for its whole
    189,000-man army (its income phase nets -26 at tick 0, the satellites'
    tribute carrying it), so the beaten France out-earns it from the FIRST
    tick (+257) instead of from the bleed, and the internment widens the gap
    at a stroke (+373 -> +941). The ratchet stands, by ruling.

    Both boards are held at PEACE before every tick, so what is measured is the
    upkeep asymmetry and not a difference in war rate — without that the gap is
    partly a cascade re-declaring on one board and not the other.

    ⚠ **A CLAIM OF THE EXIT'S OWN WAS STRUCK HERE, BY THIS PIN.** The first
    measurement built the beaten board by making peace BEFORE applying the
    losses and reported the loser ahead by **+534 on turn 0**. That does not
    reproduce: making peace first runs the war-end cleanup, which hands
    occupied territory back, so France keeps a RICHER 23 provinces (gross
    income 2,056 against 1,256) and the turn-0 reading is an artefact of
    construction order — under the other order the whole France leads by 266.
    So this class builds the board the **less flattering** way (beat, then
    make peace) and asserts only the half that reproduces identically under
    both orders: the INVERSION and its widening, which agree to within ten
    gold a turn either way.
    """

    TICKS = 9
    BLEED_TICK = 5     # where the beaten army takes its further 25,000

    @pytest.fixture(scope="class")
    def series(self):
        whole = _boot(5_000)
        _hold_at_peace(whole)
        beaten = _beaten(_boot(5_000))      # losses FIRST...
        _hold_at_peace(beaten)              # ...then the peace
        out = []
        for _ in range(self.TICKS):
            _hold_at_peace(whole)
            _hold_at_peace(beaten)
            a = _quiet(whole.process_income_phase, "France")
            b = _quiet(beaten.process_income_phase, "France")
            out.append((int(a["net"]), int(b["net"]),
                        _french_army(beaten), _french_corps(beaten)))
            _quiet(whole.advance_turn)
            _quiet(beaten.advance_turn)
        return out

    def test_the_beaten_france_out_earns_the_whole_one(self, series):
        """Losing pays — RULED to stand (SR-5a, question (c)). On the ruled
        balance board it pays from the first tick, under the less flattering
        construction too (beat, then make peace)."""
        ahead = [i for i, (w, b, _, _c) in enumerate(series) if b > w]
        assert ahead == list(range(self.TICKS)), (
            f"the beaten France should lead on every tick: {series}")

    def test_it_is_a_ratchet_not_a_fixed_handicap(self, series):
        """The correction the exit made to the row's own contract: the gap does
        not settle at a handicap, it widens every turn, and the further bleed
        widens it at a stroke. On the ruled board (SR-5a) it no longer
        INVERTS — the beaten France leads from the first tick — so the pin
        asserts the widening and the step, which is the ratchet itself."""
        gaps = [b - w for w, b, _, _c in series]
        early, late = gaps[:self.BLEED_TICK], gaps[self.BLEED_TICK:]
        assert all(g > 0 for g in gaps), gaps
        assert min(late) > max(early), (
            f"the further bleed must widen the gap at a stroke: {gaps}")
        assert early == sorted(early) and late == sorted(late), (
            f"the gap must be WIDENING, not converging: {gaps}")

    def test_the_inversion_is_caused_by_losing_more(self, series):
        """Why it is a ratchet and not a one-off: the turn the gap flips is the
        turn the beaten France loses MORE, which cuts its upkeep again.

        ⚠ NAMED, NOT ASSUMED. The first sweep mutation for this guessed supply
        attrition and came back INERT; the mechanism is **internment**. The
        peace ceded the ground Ney and Davout were standing on (both at
        Rhineland, 12,000 + 13,000 = the whole 25,000), and when their corridor
        window expired both corps were interned. Losing territory therefore
        cuts the loser's upkeep TWICE — once for the men lost in the fighting,
        and again for the corps left standing on the ground it gave away.
        """
        armies = [a for _, _, a, _c in series]
        corps = [c for _, _, _a, c in series]
        before, after = armies[self.BLEED_TICK - 1], armies[self.BLEED_TICK]
        assert after < before, (
            f"expected the beaten army to fall at tick {self.BLEED_TICK}: "
            f"{armies}")
        lost = set(corps[self.BLEED_TICK - 1]) - set(corps[self.BLEED_TICK])
        assert lost == {"Davout", "Ney"}, (
            f"the fall is whole CORPS being removed, not attrition: {lost}")
        assert before - after == 25_000
        gaps = [b - w for w, b, _, _c in series]
        # SR-5a: on the ruled board the gap is already positive before the
        # bleed; what the internment does is DOUBLE it at a stroke.
        assert gaps[self.BLEED_TICK] > 2 * gaps[self.BLEED_TICK - 1] > 0, gaps

    def test_the_engine_names_the_mechanism_internment(self):
        """⚠ WRITTEN BECAUSE A MUTATION CAME BACK INERT. The pins above INFER
        internment from two corps disappearing; renaming the internment event
        left them all green, which means the record's named mechanism was not
        actually observed anywhere. Observe it: three `evacuation_lapsing`
        warnings counting down, then `marshal_destroyed` carrying the engine's
        own `cause`."""
        world = _boot(5_000)
        _beaten(world)
        _hold_at_peace(world)
        seen = len(getattr(world, "event_log", []) or [])
        interned, warnings = [], 0
        for _ in range(self.TICKS):
            _hold_at_peace(world)
            _quiet(world.advance_turn)
            log = getattr(world, "event_log", []) or []
            for event in log[seen:]:
                if event.get("type") == "evacuation_lapsing":
                    warnings += 1
                if (event.get("type") == "marshal_destroyed"
                        and event.get("cause") == "interned"):
                    interned.append((event.get("marshal"), event.get("victor")))
            seen = len(log)
        assert sorted(interned) == [("Davout", "Austria"), ("Ney", "Austria")]
        assert warnings >= 6, (
            "each interned corps is warned before it is lost; the row's whole "
            f"point is that this is a consequence, not a surprise: {warnings}")

    def test_the_interned_corps_were_standing_on_ceded_soil(self):
        """The mechanism's precondition, pinned so the pin above cannot be
        satisfied by some other removal path."""
        world = _boot(5_000)
        held = [r for r in world.regions.values() if r.controller == "France"]
        ceded = {r.name for r in held[:5]}
        for name in ("Ney", "Davout"):
            assert world.marshals[name].location in ceded

    def test_the_whole_france_decays_while_the_beaten_one_recovers(self, series):
        """The shape underneath the ratchet, and the reason it never closes."""
        whole = [w for w, _, _, _c in series]
        beaten = [b for _, b, _, _c in series]
        assert whole[-1] < whole[0], f"the victor's Net decays: {whole}"
        assert beaten[-1] > beaten[0], f"the loser's Net grows: {beaten}"


class TestTheLedgerSaysWhy:
    """SR-5a question (c), RULED "keep the rules, make it legible": the two
    boards of the ratchet, advanced through the REAL turn (once, through
    `advance_turn` alone — this file's own trap), each read the sentence the
    ledger now prints beside the bill that moved.

    Killed by: `ledger.THE_BILLS_SAY_WHY_THEY_MOVED` down, a note that no
    longer compares with the charged turn, or a charges note that blames the
    chest for a rate the realm raised."""

    def _advance(self, world):
        _hold_at_peace(world)
        _quiet(world.advance_turn)

    def test_the_victors_chest_is_named_when_the_charges_rise(self):
        from backend.game_logic.ledger import _build_economy
        whole = _boot(5_000)
        _hold_at_peace(whole)
        self._advance(whole)
        econ = _quiet(_build_economy, whole, "France")
        assert "the chest is fuller" in econ["state_charges_delta_note"], econ[
            "state_charges_delta_note"]
        assert "fuller chest pays more" in econ["state_charges_rate_note"]
        assert "the fallen draw no pay" in econ["upkeep_note"]

    def test_the_losers_upkeep_is_named_when_the_army_falls(self):
        from backend.game_logic.ledger import _build_economy
        beaten = _beaten(_boot(5_000))
        _hold_at_peace(beaten)
        army_before = _french_army(beaten)
        self._advance(beaten)
        # the fallen are taken off the rolls between the charged turn and
        # the next one (the half-army board, with 20,000 more lost)
        for m in beaten.marshals.values():
            if m.nation == "France" and m.name == "Ney":
                m.strength = max(0, m.strength - 10_000)
        econ = _quiet(_build_economy, beaten, "France")
        note = econ["upkeep_note"]
        assert "less than last turn's bill" in note, note
        assert "men smaller" in note, note
        assert _french_army(beaten) < army_before

    def test_lever_down_says_only_what_it_said_before(self, monkeypatch):
        from backend.game_logic import ledger as LG
        monkeypatch.setattr(LG, "THE_BILLS_SAY_WHY_THEY_MOVED", False)
        whole = _boot(5_000)
        _hold_at_peace(whole)
        self._advance(whole)
        econ = _quiet(LG._build_economy, whole, "France")
        assert econ["upkeep_note"] == "" and econ["state_charges_delta_note"] == ""
        assert "fuller chest" not in econ["state_charges_rate_note"]


# ---------------------------------------------------------------------------
# item (iii) — every gold the player is charged, named
# ---------------------------------------------------------------------------

class _TracedPurse(dict):
    """Records which production function moved France's gold, and by how much."""

    def __init__(self, source, log):
        super().__init__(source)
        self._log = log

    def __setitem__(self, key, value):
        if key == "France":
            old, new = int(super().get(key, 0)), int(value)
            if old != new:
                frames = [f for f in traceback.extract_stack()[:-1]
                          if "/backend/" in f.filename or "\\backend\\" in f.filename]
                self._log.append((new - old, frames[-1].name if frames else "?"))
        super().__setitem__(key, value)


def purse_census(turns=6, with_obligation=False):
    """Every site that moves France's purse across N REAL turns.

    Real turn = `advance_turn` ONLY. See this module's docstring.
    """
    world = _boot()
    if with_obligation:
        _quiet(INST.grant_directed_sponsorship, world, payer="France",
               recipient="Prussia", aim="Austria", amount_per_turn=200)
    log = []
    world.nation_gold = _TracedPurse(world.nation_gold, log)
    for _ in range(turns):
        _quiet(world.advance_turn)
    totals = {}
    for amount, site in log:
        totals[site] = totals.get(site, 0) + amount
    return totals


# The three sites whose every term is a declared Net component.
NAMED_SITES = {"process_income_phase", "process_trade_income",
               "process_vassal_tribute"}


class TestCompletionItemThree:
    """19 of 19 streams named — the nineteenth, IQ1-3a-prime's standing
    obligation, by the economy audit's EA-1 (October 5, 2026)."""

    def test_net_is_the_signed_sum_of_its_declared_components(self):
        """The structural half — also pinned in
        test_economy_ledger_reconciliation.py, asserted here on the shipped
        boot so item (iii) has its own end-to-end evidence."""
        world = _boot()
        econ = _quiet(L._build_economy, world, "France")
        total = sum(sign * int(econ.get(key, 0) or 0)
                    for key, sign in NET_GOLD_COMPONENTS.items())
        assert total == int(econ["net"])

    def test_only_four_production_sites_move_the_purse(self):
        sites = set(purse_census())
        assert sites == NAMED_SITES, (
            f"a new production site moves France's gold: {sites - NAMED_SITES}. "
            "Item (iii) requires every charge to be a named ledger line — "
            "either declare it in NET_GOLD_COMPONENTS or file it as this "
            "row filed process_instruments.")

    def test_the_standing_obligation_is_named_on_the_subsidies_line(self):
        """IQ1-3a-prime, measured at face value: a 200 g/turn sponsorship costs
        200 a turn. REWRITTEN by the economy audit (October 5, 2026; EA-1), as
        the pin itself asked ("if IQ1-3a-prime has landed, rewrite this pin
        rather than deleting it"): the forecast Net now moves by exactly
        -200, on the signed "Subsidies" line; with the lever down the shipped
        invisibility stands (the defect, pinned)."""
        turns = 6
        totals = purse_census(turns=turns, with_obligation=True)
        assert "process_instruments" in totals
        assert totals["process_instruments"] == -200 * turns

        world = _boot()
        before = int(_quiet(L._build_economy, world, "France")["net"])
        _quiet(INST.grant_directed_sponsorship, world, payer="France",
               recipient="Prussia", aim="Austria", amount_per_turn=200)
        econ = _quiet(L._build_economy, world, "France")
        assert int(econ["net"]) == before - 200
        assert int(econ["subsidies"]) == -200
        INST.THE_SUBSIDIES_ARE_ON_THE_BOOKS = False
        try:
            assert int(_quiet(L._build_economy, world, "France")["net"]) == before
        finally:
            INST.THE_SUBSIDIES_ARE_ON_THE_BOOKS = True

    def test_trade_and_blockade_arrive_as_one_net_write_and_both_are_named(self):
        """Why the census counts three named sites and not five: the trade
        producer delivers `trade_income - blockade` in a single write."""
        world = _boot()
        econ = _quiet(L._build_economy, world, "France")
        expected = int(econ["trade_income"]) - int(econ["blockade"])
        log = []
        world.nation_gold = _TracedPurse(world.nation_gold, log)
        _quiet(world.advance_turn)
        trade = [amt for amt, site in log if site == "process_trade_income"]
        assert trade == [expected]
        for key in ("trade_income", "blockade"):
            assert key in NET_GOLD_COMPONENTS


# ---------------------------------------------------------------------------
# IQ1-5-1 — the new finding
# ---------------------------------------------------------------------------

class TestIq151TheStaleQuote:
    """The Charges of Empire were quoted one war-effort tick stale.

    It was a CHARACTERIZATION pin (it asserted the defect so the fix would
    red it). ✅ FIXED September 28, 2026 by SR-5a "The chest", which owns the
    row (PB-7): the forecast prices the war-exhaustion term at the value the
    advance's own tick writes before the income phase levies the charge
    (`coalition.next_war_exhaustion`, the tick's single source;
    `world_state.THE_FORECAST_PRICES_TOMORROWS_WAR`). The pins now assert the
    quote IS the levy, and the lever-down arm reproduces the measured stale
    gap to the gold, so the cause stays named.
    """

    @staticmethod
    def _one_turn(gold=40_000):
        world = _boot(gold=gold)
        quoted = _quiet(L._build_economy, world, "France")
        rate_before = _quiet(world.get_state_charges_rate, "France")["rate"]
        _quiet(world.advance_turn)
        rate_after = _quiet(world.get_state_charges_rate, "France")["rate"]
        applied = (getattr(world, "_income_phase_results", {}) or {}).get("France", {})
        return quoted, applied, rate_before, rate_after

    @pytest.fixture
    def one_turn(self):
        return self._one_turn()

    @pytest.fixture
    def stale(self, monkeypatch):
        from backend.models import world_state as WS
        monkeypatch.setattr(WS, "THE_FORECAST_PRICES_TOMORROWS_WAR", False)
        return self._one_turn()

    def test_every_other_ledger_term_is_exact(self, one_turn):
        """The finding is precise because nothing else moves: if this reds, the
        defect is wider than IQ1-5-1 says and the row needs re-measuring."""
        quoted, applied, _, _ = one_turn
        for key in ("income", "admin_bonus", "admiralty", "occupation",
                    "contributions", "requisitions", "overseas",
                    "dotation_skim", "rente_cost", "infrastructure"):
            assert int(quoted.get(key, 0) or 0) == int(applied.get(key, 0) or 0), key
        upkeep = applied.get("upkeep_data", {})
        assert int(quoted["upkeep_base"]) == int(upkeep.get("base", 0) or 0)
        assert int(quoted["upkeep_surcharge"]) == int(upkeep.get("surcharge", 0) or 0)

    def test_the_charge_quoted_is_the_charge_levied(self, one_turn):
        quoted, applied, _, _ = one_turn
        assert int(quoted["state_charges"]) == int(applied["state_charges"]) == 1337

    def test_lever_down_the_levy_exceeds_the_quote(self, stale):
        quoted, applied, _, _ = stale
        assert int(applied["state_charges"]) > int(quoted["state_charges"])
        assert int(applied["state_charges"]) - int(quoted["state_charges"]) == 121

    def test_the_cause_is_the_war_exhaustion_tick(self, stale):
        """Named, not guessed (lever down): the rate itself moves across the
        advance, and the gap is exactly the chest above the floor times that
        move."""
        quoted, applied, rate_before, rate_after = stale
        assert rate_after > rate_before
        gap = int(applied["state_charges"]) - int(quoted["state_charges"])
        chest_above_floor = 40_000 - CHARGES_HOARD_FLOOR
        predicted = (chest_above_floor * rate_after // WAR_EFFORT_DIVISOR
                     - chest_above_floor * rate_before // WAR_EFFORT_DIVISOR)
        assert gap == predicted

    def test_the_forecast_reads_the_ticks_own_arithmetic(self):
        from backend.game_logic.coalition import next_war_exhaustion
        world = _boot()
        before = int(world.war_exhaustion.get("France", 0) or 0)
        tomorrow = next_war_exhaustion(world, "France")
        _quiet(world.advance_turn)
        assert int(world.war_exhaustion.get("France", 0) or 0) == tomorrow
        assert tomorrow == before + 8   # France boots at war

    def test_the_exhaustion_term_is_what_appears(self, one_turn):
        world = _boot()
        keys_before = {t["key"] for t
                       in _quiet(world.get_state_charges_rate, "France")["terms"]}
        keys_projected = {t["key"] for t in _quiet(
            world.get_state_charges_rate, "France", projected=True)["terms"]}
        _quiet(world.advance_turn)
        keys_after = {t["key"] for t
                      in _quiet(world.get_state_charges_rate, "France")["terms"]}
        assert "war_exhaustion" not in keys_before
        assert "war_exhaustion" in keys_projected
        assert "war_exhaustion" in keys_after

    def test_the_gap_is_closed_at_every_chest(self, monkeypatch):
        """Why it mattered more the richer the player was: at the control arm's
        88,556-gold chest the stale quote was worth more than twice what it
        was at 40,000 (lever down). Fixed, the gap is 0 at both."""
        def gap_at(gold):
            quoted, applied, _, _ = self._one_turn(gold)
            return int(applied["state_charges"]) - int(quoted["state_charges"])

        assert gap_at(40_000) == 0 and gap_at(88_556) == 0
        from backend.models import world_state as WS
        monkeypatch.setattr(WS, "THE_FORECAST_PRICES_TOMORROWS_WAR", False)
        small, large = gap_at(40_000), gap_at(88_556)
        assert large > 2 * small > 0


# ---------------------------------------------------------------------------
# the record itself
# ---------------------------------------------------------------------------

def _exit_record():
    """§0.6b's body ONLY.

    ⚠ Scoped because the first cut of these pins was a bare `in` over the whole
    file and the sweep proved it: `6.0 → 6.5` occurs three times in the spec and
    `war_exhaustion` six times in BUG_FIXES.md, so deleting the sentence under
    test left both green. Same class as the FA dead-name pin whose fixed scrape
    overshot into the next endpoint's body.
    """
    spec = (pathlib.Path(__file__).resolve().parents[1]
            / "docs" / "IMPROVEMENT_QUEUE_SPEC.md").read_text(encoding="utf-8")
    head = "### §0.6b LANDING RECORD — IQ1-5"
    assert spec.count(head) == 1
    return spec.split(head)[1].split("### §0.6 THE REMAINING SLICES")[0]


def _iq_bug_rows():
    """The §Improvement Queue block of BUG_FIXES.md ONLY — see above."""
    bugs = doc_text("BUG_FIXES.md")
    head = "## Improvement Queue (IQ) — filed September 14, 2026"
    assert bugs.count(head) == 1
    return bugs.split(head)[1].split("\n## ")[0]


class TestTheExitIsRecorded:
    """A grade nobody can find is not a grade."""

    def test_the_landing_record_carries_the_score(self):
        record = _exit_record()
        assert "6.0 → 6.5" in record
        assert "FOR USER CONFIRMATION" in record

    def test_the_unclosed_item_names_its_owner(self):
        """GR9: item (ii) is measured-open, so it must name where it went."""
        record = _exit_record()
        assert "measured-open and handed off" in record
        assert "ROUTED OUT" in record

    def test_the_struck_claim_is_on_the_record_not_quietly_dropped(self):
        """The exit withdrew its own turn-0 figure. A withdrawal nobody can
        read is just a deletion."""
        record = _exit_record()
        assert "+534" in record and "does not reproduce" in record

    def test_the_new_finding_is_filed_with_its_cause(self):
        rows = _iq_bug_rows()
        assert "IQ1-5-1" in rows
        assert "war_exhaustion" in rows
        assert "get_state_charges_rate" in rows
