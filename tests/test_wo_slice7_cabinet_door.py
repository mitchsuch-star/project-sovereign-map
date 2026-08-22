"""WO-D2 "The Cabinet Is The Only Door" — Weird-Outcomes slice 7 (G1).

Build contract: `docs/WEIRD_OUTCOMES_SPEC.md` §3 slice 7 (authoritative);
§6 never-do 14 (do not intercept the chip pipelines) and 15 (verb heads
only, fail-open — a false-positive interception is worse than the
backdoor it closes) bind this slice directly.

THE RULING (WO-D2/G1): matters of state are conducted through the
Cabinet. A typed diplomatic order is redirected in character on the
terminal input path — it costs nothing and SENDS nothing — and the
wizard becomes complete enough to BE the only door.

THE DRIFT PIN (contract item 3) is the load-bearing test here, and it
exists because of the CA9 through-line: *the advisory surface and the
executor are separate implementations of one rule and only one is
maintained.* The client's redirect list is a deliberate MIRROR of the
mock parser's own diplomatic funnel, so this file re-executes the
mirror's trivial rules against BOTH sources and reds the moment they
diverge:

  (a) every mock-parser-reachable diplomatic action id is either claimed
      by the client's family lists or sits in the documented exclusion
      set (measured by parsing a real utterance per action id, not by
      reading the lists);
  (b) every golden-corpus utterance whose expected action is family-tier
      is claimed by a listed keyword — and every NON-diplomatic corpus
      utterance is NOT (the false-positive census over all 333 rows,
      which is what never-do 15 actually asks for).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
MAIN_GD = REPO / "godot-client" / "project-sovereign" / "scripts" / "main.gd"
UTILS_GD = REPO / "godot-client" / "project-sovereign" / "scripts" / "utils.gd"
CORPUS = REPO / "tests" / "data" / "parser_golden_corpus.json"

# The actions the ruling claims for the Cabinet (or, for request_terms,
# the war room). Every one of these must be redirected.
FAMILY_ACTIONS = {
    "diplomatic_declare_war",
    "diplomatic_proposal",
    "diplomatic_ultimatum",
    "diplomatic_break",
    "diplomatic_downgrade",
    "diplomatic_mission",
    "make_vassal",
    "invest_vassal",
    "change_autonomy",
    "release_vassal",
    "grant_region_to_vassal",
    "sponsor_design",
    "buy_off_design",
    "guarantee_nation",
    "propose_common_peace",
    "propose_white_peace",
    "request_terms",
}

# Documented exclusions — these reach the backend as they always did,
# each for a reason recorded in the spec's family table.
EXCLUDED_ACTIONS = {
    # No wizard/panel home (§2 G1-11): redirecting them would make them
    # unreachable outright.
    "make_amends",
    "set_war_purpose",
    "repudiate_bargain",
    # Read-only counsel.
    "diplomatic_advisory",
    "diplomatic_feasibility",
    # Not an order at all — the parser's own failure path.
    "diplomatic_error",
    # The reward economy is NOT diplomacy (§4 N-4), and the committed
    # playtest scripts exercise it typed.
    "grant_dotation",
    "grant_pension",
    "revoke_pension",
    "recruit_marshal",
}

# The corpus expresses expectations in more than one way: 156 rows carry
# `expected.action`, but 177 do not — a proposal row asserts
# `expected.type == "diplomatic"` plus a `diplo` sub-dict instead. Keying
# on `action` alone would have declared 43 plainly diplomatic utterances
# "non-diplomatic" and then reported the redirect for stealing them.
# Found by running the census; recorded because the same trap will catch
# the next reader of this corpus.
#
# Three buckets, and the middle one is the honest part: a row is a
# CONCRETE ORDER when it names an action id or a proposal/mission type,
# and READ-ONLY when it is advisory or not diplomacy at all. A handful of
# rows are neither — "Talleyrand, deal with England" is genuinely
# diplomatic but names no instrument, so either verdict is defensible.
# Those are counted rather than asserted, and the count is capped so the
# bucket cannot quietly become a dumping ground.

def _row_class(row: dict) -> str:
    expected = row.get("expected") or {}
    diplo = expected.get("diplo") or {}
    action = expected.get("action") or diplo.get("action")
    if action in EXCLUDED_ACTIONS:
        return "read_only"
    if action in FAMILY_ACTIONS:
        return "order"
    if diplo.get("proposal_type") or diplo.get("mission_type"):
        return "order"
    if expected.get("type") != "diplomatic":
        return "read_only"   # military / econ / naval / meta
    return "underspecified"


# ══════════════════════════════════════════════════════════════════════════
# The mirror, extracted from the client rather than re-implemented
# ══════════════════════════════════════════════════════════════════════════

def _extract_gd_list(name: str, text: str) -> list:
    """Pull a `const NAME = [ "a", "b", ]` list out of the GDScript."""
    match = re.search(
        r"const\s+" + re.escape(name) + r"\s*=\s*\[(.*?)\n\]", text, re.S)
    assert match, f"{name} not found in main.gd — the drift pin is blind"
    items = re.findall(r'"([^"]*)"', match.group(1))
    assert items, f"{name} extracted empty — the pin would pass vacuously"
    return items


@pytest.fixture(scope="module")
def gd() -> str:
    return MAIN_GD.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def lists(gd) -> dict:
    return {
        "no_home": _extract_gd_list("DIPLO_NO_HOME_KEYWORDS", gd),
        "war_room": _extract_gd_list("DIPLO_WAR_ROOM_KEYWORDS", gd),
        "family": _extract_gd_list("DIPLO_FAMILY_KEYWORDS", gd),
        "nation_gated": _extract_gd_list("DIPLO_NATION_GATED_PREFIXES", gd),
        "nation_anywhere": _extract_gd_list(
            "DIPLO_NATION_ANYWHERE_KEYWORDS", gd),
        "address_names": _extract_gd_list("DIPLO_ADDRESS_NAMES", gd),
        "address_exempt": _extract_gd_list(
            "DIPLO_ADDRESS_EXEMPT_WORDS", gd),
        "advisory_starts": _extract_gd_list("DIPLO_ADVISORY_STARTS", gd),
        "negation": _extract_gd_list("DIPLO_NEGATION_MARKERS", gd),
    }


@pytest.fixture(scope="module")
def nation_forms() -> list:
    """The court name forms the client matches against — read from the
    SAME source the client reads (Utils.NATION_COLORS + display names),
    so a scenario roster change cannot silently unpin this file."""
    text = UTILS_GD.read_text(encoding="utf-8")
    block = re.search(r"const NATION_COLORS\s*=\s*\{(.*?)\n\}", text, re.S)
    assert block, "NATION_COLORS not found in utils.gd"
    tags = re.findall(r'"([A-Za-z]+)"\s*:', block.group(1))
    assert len(tags) >= 15, f"only {len(tags)} courts extracted"
    forms = set()
    for tag in tags:
        forms.add(tag.lower())
        # `display_nation_name` splits CamelCase into spaced words.
        spaced = re.sub(r"(?<!^)(?=[A-Z])", " ", tag).lower()
        forms.add(spaced)
    return sorted(forms)


def _redirect_verdict(command: str, lists: dict, forms: list) -> str:
    """Re-execute the client matcher's rules over the EXTRACTED lists.

    Deliberately trivial (substring / prefix / nation-gate) because the
    GDScript matcher is deliberately trivial — this re-runs the mirror,
    it does not invent a third classifier. Returns "cabinet", "war_room"
    or "" (fail-open).
    """
    lower = command.lower().strip()
    if not lower:
        return ""
    if "_" in lower:
        return ""
    # Advisory question guard.
    if lower.endswith("?"):
        return ""
    body = lower
    comma = body.find(",")
    if 0 <= comma <= 24 and "talleyrand" in body[:comma]:
        body = body[comma + 1:].strip()
    words = body.split()
    if words and words[0] in lists["advisory_starts"]:
        return ""
    # PARSE-NEG owns a negated sentence.
    for marker in lists["negation"]:
        if marker in lower:
            return ""
    # No-home verbs first — precedence mirrors the parser's own.
    for keyword in lists["no_home"]:
        if keyword in lower:
            return ""
    for keyword in lists["war_room"]:
        if keyword in lower:
            return "war_room"
    for keyword in lists["family"]:
        if keyword in lower:
            return "cabinet"
    for prefix in lists["nation_gated"]:
        at = lower.find(prefix)
        if at >= 0:
            tail = lower[at + len(prefix):].strip()
            if tail.startswith("the "):
                tail = tail[4:]
            for form in forms:
                if tail == form or tail.startswith(form + " ") \
                        or tail.startswith(form + ","):
                    return "cabinet"
    if any(form in lower for form in forms):
        for keyword in lists["nation_anywhere"]:
            if keyword in lower:
                return "cabinet"
        if ("cede " in lower or "grant " in lower) and any(
                (" to " + form) in lower for form in forms):
            return "cabinet"
    comma = lower.find(",")
    if 0 <= comma <= 30 and any(n in lower[:comma]
                                for n in lists["address_names"]):
        if any(w in lower for w in lists["address_exempt"]):
            return ""
        return "cabinet"
    return ""


# ══════════════════════════════════════════════════════════════════════════
# (b) THE CORPUS CENSUS — both directions
# ══════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def corpus() -> list:
    import json
    return json.loads(CORPUS.read_text(encoding="utf-8"))["entries"]


class TestTheCorpusCensus:

    def test_every_family_utterance_is_claimed(self, corpus, lists,
                                               nation_forms):
        """Contract item 3(b): every corpus utterance whose expected
        action is family-tier must be redirected. A miss here is a
        typed backdoor the ruling says should not exist."""
        misses = []
        seen = 0
        for row in corpus:
            if _row_class(row) != "order":
                continue
            seen += 1
            verdict = _redirect_verdict(row["utterance"], lists, nation_forms)
            if not verdict:
                misses.append(
                    ((row.get("expected") or {}).get("action"),
                     row["utterance"]))
        assert seen >= 80, (
            f"only {seen} order rows detected — the census has gone blind")
        assert misses == [], (
            f"diplomatic orders the Cabinet does not claim: {misses}")

    def test_request_terms_goes_to_the_war_room_not_the_cabinet(
            self, corpus, lists, nation_forms):
        """The one recorded exception in the family table."""
        rows = [r for r in corpus
                if (r.get("expected") or {}).get("action") == "request_terms"]
        assert rows, "corpus lost its request_terms row — pin is blind"
        for row in rows:
            assert _redirect_verdict(
                row["utterance"], lists, nation_forms) == "war_room"

    def test_no_non_diplomatic_utterance_is_intercepted(
            self, corpus, lists, nation_forms):
        """§6 never-do 15, as a census over all 333 rows: a
        false-positive interception is worse than the backdoor it
        closes. Every military / economic / naval / meta / reward
        utterance must reach the backend untouched."""
        stolen = []
        seen = 0
        for row in corpus:
            if _row_class(row) != "read_only":
                continue
            seen += 1
            verdict = _redirect_verdict(row["utterance"], lists, nation_forms)
            if verdict:
                stolen.append(
                    ((row.get("expected") or {}).get("action"),
                     row["utterance"], verdict))
        assert seen >= 180, (
            f"only {seen} read-only rows checked — census gone blind")
        assert stolen == [], (
            f"the redirect stole a command that is not a diplomatic "
            f"order: {stolen}")

    def test_every_underspecified_row_has_an_explicit_verdict(self, corpus,
                                                              lists,
                                                              nation_forms):
        """Eight corpus rows are diplomatic but record no action id and
        no proposal/mission type, so the data cannot classify them. A
        tolerance ("no more than N") would let the bucket become the
        place inconvenient rows go to avoid a verdict — so each is
        enumerated with the verdict it must get, and a NEW row landing
        here reds this test and forces the decision to be made."""
        expected_verdicts = {
            # Orders in everything but the corpus bookkeeping — the
            # utterance names its instrument even where `expected` does
            # not, so the Cabinet claims them.
            "sign treaty with Saxony": "cabinet",
            "send envoy to Austria": "cabinet",
            "send diplomat to Prussia": "cabinet",
            "declare war on the Prussians": "cabinet",
            "declare war on the British": "cabinet",
            # Counsel. The rewritten help still teaches `assess` as a
            # spoken verb, so claiming these would make the help a liar.
            "minister, assess Prussia": "",
            "Talleyrand, assess Britian": "",
            # Genuinely underspecified — diplomatic, addressed to the
            # foreign minister, naming no instrument. The Cabinet is
            # where that sentence gets its instrument, so it claims it.
            "Talleyrand, deal with England": "cabinet",
        }
        actual = {r["utterance"]: _redirect_verdict(
            r["utterance"], lists, nation_forms)
            for r in corpus if _row_class(r) == "underspecified"}
        assert set(actual) == set(expected_verdicts), (
            f"the underspecified set changed — decide the newcomers: "
            f"{sorted(set(actual) ^ set(expected_verdicts))}")
        assert actual == expected_verdicts, (
            f"underspecified rows got the wrong verdict: "
            f"{ {k: v for k, v in actual.items() if expected_verdicts[k] != v} }")

    def test_a_negated_order_reaches_parse_neg(self, corpus, lists,
                                               nation_forms):
        """The census's own find: `don't declare war on Austria` was
        being answered with a Cabinet pointer. Both paths execute
        nothing — so this is not a safety question but a question of
        which voice answers, and PARSE-NEG's clause guards refuse it by
        name. The redirect yields."""
        rows = [r for r in corpus
                if (r.get("expected") or {}).get("not_action")]
        assert rows, "the corpus lost its PARSE-NEG rows — pin is blind"
        for row in rows:
            assert _redirect_verdict(
                row["utterance"], lists, nation_forms) == "", (
                f"a negated order belongs to PARSE-NEG: {row['utterance']!r}")

    def test_the_no_home_verbs_are_never_intercepted(self, corpus, lists,
                                                     nation_forms):
        """§2 G1-11 as a falsifiable negative: make_amends,
        set_war_purpose and repudiate_bargain have NO wizard home, so
        redirecting them would make them unreachable outright. Note
        `set war purpose against Austria` carries the war-declaration
        substring `war against ` — precedence, not luck, is what saves
        it."""
        checked = set()
        for row in corpus:
            action = (row.get("expected") or {}).get("action")
            if action not in {"make_amends", "set_war_purpose",
                              "repudiate_bargain"}:
                continue
            checked.add(action)  # noqa: PERF401
            assert _redirect_verdict(
                row["utterance"], lists, nation_forms) == "", (
                f"{action} has no UI home and must stay typed: "
                f"{row['utterance']!r}")
        assert checked == {"make_amends", "set_war_purpose",
                           "repudiate_bargain"}, (
            f"corpus coverage lost for the no-home verbs: {checked}")

    def test_counsel_stays_spoken(self, corpus, lists, nation_forms):
        """Advisories and feasibility questions are read-only — and one
        of them ("what would it take to get peace with Prussia?")
        carries a family keyword, so only the question guard saves it."""
        seen_family_keyword = False
        for row in corpus:
            action = (row.get("expected") or {}).get("action")
            if action not in {"diplomatic_advisory", "diplomatic_feasibility"}:
                continue
            utterance = row["utterance"]
            assert _redirect_verdict(utterance, lists, nation_forms) == "", (
                f"counsel must reach Talleyrand: {utterance!r}")
            if any(k in utterance.lower() for k in lists["family"]):
                seen_family_keyword = True
        assert seen_family_keyword, (
            "no advisory row carries a family keyword any more — this test "
            "no longer proves the question guard does anything")


# ══════════════════════════════════════════════════════════════════════════
# (a) THE PARSER-REACHABILITY CENSUS — measured, not read
# ══════════════════════════════════════════════════════════════════════════

# A verb is diplomacy-shaped if its id carries one of these. Deliberately
# mechanical: a NEW diplomatic action added to the single source
# (`validation.VALID_ACTIONS`) forces a conscious decision in this file
# rather than silently becoming a typed backdoor the ruling forbids.
DIPLOMATIC_ID_MARKERS = (
    "diplomatic", "vassal", "design", "guarantee", "amends",
    "peace", "terms", "war_purpose", "bargain", "autonomy",
)


class TestEveryDiplomaticVerbIsDisposed:
    """Contract item 3(a), taken at the SINGLE SOURCE rather than by
    sampling: every diplomatic action id in `VALID_ACTIONS` is either
    claimed by the Cabinet or documented as excluded, with its reason."""

    def test_no_diplomatic_action_is_undisposed(self):
        from backend.ai.validation import VALID_ACTIONS

        shaped = {a for a in VALID_ACTIONS
                  if any(m in a for m in DIPLOMATIC_ID_MARKERS)}
        assert len(shaped) >= 20, (
            f"only {len(shaped)} diplomatic-shaped ids found in "
            f"VALID_ACTIONS — the detector has gone blind")
        undisposed = shaped - (FAMILY_ACTIONS | EXCLUDED_ACTIONS)
        assert undisposed == set(), (
            f"diplomatic verbs neither claimed by the Cabinet nor recorded "
            f"as excluded: {sorted(undisposed)} — decide, do not inherit")

    def test_the_disposal_sets_do_not_overlap(self):
        assert FAMILY_ACTIONS & EXCLUDED_ACTIONS == set()

    def test_every_claimed_action_has_a_corpus_witness(self, corpus):
        """A claim with no corpus row is a claim nothing tests. Any
        family action missing here means the census above is silently
        skipping it."""
        witnessed = set()
        for row in corpus:
            action = (row.get("expected") or {}).get("action")
            if action in FAMILY_ACTIONS:
                witnessed.add(action)
        # These four are reachable but have no corpus row of their own;
        # recorded rather than asserted away.
        known_unwitnessed = {"diplomatic_downgrade", "propose_common_peace",
                             "propose_white_peace", "diplomatic_proposal"}
        missing = FAMILY_ACTIONS - witnessed - known_unwitnessed
        assert missing == set(), (
            f"family actions with no corpus witness: {sorted(missing)}")


# ══════════════════════════════════════════════════════════════════════════
# THE STRUCTURAL PINS — the redirect is where the contract says it is
# ══════════════════════════════════════════════════════════════════════════

class TestTheDoorIsWhereItSaysItIs:

    def test_the_interception_lives_in_execute_command(self, gd):
        """Contract item 1: the ONLY path player-typed text travels."""
        body = re.search(
            r"func _execute_command\(\):(.*?)\nfunc ", gd, re.S)
        assert body, "_execute_command not found"
        assert "_redirect_diplomatic_command(command)" in body.group(1)

    def test_it_sits_below_the_redemption_block(self, gd):
        """Placement pin (§2 G1-9) — the underscore tokens are consumed
        before the matcher can ever see them."""
        redemption = gd.find("send_redemption_response")
        redirect = gd.find("if _redirect_diplomatic_command(command):")
        assert 0 < redemption < redirect

    def test_the_redirect_sends_nothing(self, gd):
        """It costs nothing and sends nothing — the whole point."""
        func = re.search(
            r"func _redirect_diplomatic_command\(.*?\n(.*?)\nfunc ", gd, re.S)
        assert func, "_redirect_diplomatic_command not found"
        assert "api_client" not in func.group(1), (
            "the redirect must never reach the backend")

    def test_the_chip_pipelines_bypass_by_construction(self, gd):
        """§6 never-do 14: the wizard / reward / vassal / region-panel
        senders are load-bearing bypasses, not oversights to unify. Each
        must call api_client directly and never route through
        _execute_command."""
        for handler in ("_on_wizard_command_selected", "_on_reward_command",
                        "_on_vassal_command", "_on_region_panel_command"):
            body = re.search(
                r"func " + handler + r"\(.*?\n(.*?)\nfunc ", gd, re.S)
            assert body, f"{handler} not found"
            assert "_execute_command()" not in body.group(1), (
                f"{handler} must not route through the terminal path — it "
                f"would be intercepted by its own redirect")

    def test_the_link_opens_the_cabinet(self, gd):
        """The redirect names a door the player can actually press."""
        assert "[url=cabinet:open]" in gd
        handler = re.search(
            r"func _on_output_meta_clicked\(.*?\n(.*?)\nfunc ", gd, re.S)
        assert handler and 'cabinet:open' in handler.group(1)
        assert "_open_diplomacy_wizard()" in handler.group(1)

    def test_the_tutorial_suggests_nothing_the_cabinet_would_claim(
            self, lists, nation_forms):
        """Contract item 7: the School of War fills the command line and
        the player presses Enter — so a diplomatic suggest chip would be
        intercepted mid-lesson. All fifteen steps are military/econ, and
        this pins it rather than trusting it."""
        overlay = (REPO / "godot-client" / "project-sovereign" / "scripts"
                   / "tutorial_overlay.gd").read_text(encoding="utf-8")
        suggests = re.findall(r'"suggest"\s*:\s*"([^"]*)"', overlay)
        assert len(suggests) >= 10, (
            f"only {len(suggests)} suggest chips found — pin gone blind")
        claimed = [s for s in suggests
                   if s and _redirect_verdict(s, lists, nation_forms)]
        assert claimed == [], (
            f"tutorial chips the Cabinet would steal: {claimed}")


# ══════════════════════════════════════════════════════════════════════════
# THE WIZARD BECOMES COMPLETE ENOUGH TO BE THE ONLY DOOR
# ══════════════════════════════════════════════════════════════════════════

SCENARIO = "godot-client/project-sovereign/assets/maps/europe_1805.json"


@pytest.fixture(scope="module")
def base_world():
    from backend.models.world_state import WorldState
    return WorldState.from_scenario(SCENARIO)


@pytest.fixture
def world(base_world):
    from backend.models.world_state import WorldState
    return WorldState.from_dict(base_world.to_dict())


def _rows(world, nation):
    from backend.game_logic.diplomacy import get_available_diplomatic_actions
    return {r["action"]: r for r in
            get_available_diplomatic_actions(world, nation)}


def _a_french_vassal(world) -> str:
    """A boot vassal of France — the 1805 board ships three, so the
    tests use the real ones rather than minting a fixture."""
    for name, state in (world.vassals or {}).items():
        if state.get("lord") == "France":
            return name
    pytest.fail("the 1805 boot world has no French vassal any more")


class TestTheWizardIsCompleteEnough:

    def test_an_ally_can_be_offered_vassalage(self, world):
        """Contract item 5: ALLIANCE is in VASSAL_MIN_STATES and Bavaria
        and Spain BOOT at ALLIANCE — with the wizard the only door, the
        missing row made vassalizing an ally unreachable while the
        acceptance seam had allowed it all along."""
        from backend.game_logic.diplomacy import set_diplomatic_state
        set_diplomatic_state(world, "France", "Bavaria", "ALLIANCE")
        world.diplomatic_points = 9
        rows = _rows(world, "Bavaria")
        assert "propose_vassal" in rows, (
            "an ally must be offerable vassalage in the wizard")

    def test_boot_allies_exist_so_the_row_is_not_theoretical(self, world):
        allied = [n for n in world.enemy_nations
                  if world.get_diplomatic_state("France", n) == "ALLIANCE"]
        assert allied, (
            "no boot ally on the 1805 board — the G1-3 case has drifted")

    def test_no_vassal_row_renders_where_the_executor_refuses(self, world):
        """Contract item 5 / §2 G1-5+G1-6: the emitter consults the SAME
        single source the acceptance seam enforces, so a VASSAL row can
        never again render available from a state that refuses it."""
        from backend.game_logic.diplomacy import (
            VASSAL_MIN_STATES, set_diplomatic_state,
        )
        world.diplomatic_points = 9
        for state in ("PEACE", "ARMISTICE"):
            set_diplomatic_state(world, "France", "Prussia", state)
            row = _rows(world, "Prussia").get("propose_vassal")
            if row is None:
                continue
            if state not in VASSAL_MIN_STATES:
                assert not row["available"], (
                    f"a VASSAL row rendered available at {state}, which the "
                    f"acceptance seam refuses")
                assert row["disabled_reason"], "and it must say why"

    def test_the_relation_floor_is_the_single_source(self, world):
        """Falsifiable both ways: adding a state to VASSAL_MIN_STATES
        lights the wizard row, removing one darkens it — one constant,
        two seams."""
        from backend.game_logic import diplomacy as D
        D.set_diplomatic_state(world, "France", "Bavaria", "ALLIANCE")
        world.diplomatic_points = 9
        assert _rows(world, "Bavaria")["propose_vassal"]["available"] or \
            _rows(world, "Bavaria")["propose_vassal"]["disabled_reason"] != \
            "Requires war (a dictated peace) or open borders and above"
        original = set(D.VASSAL_MIN_STATES)
        try:
            D.VASSAL_MIN_STATES = original - {"ALLIANCE"}
            row = _rows(world, "Bavaria")["propose_vassal"]
            assert not row["available"]
            assert "war" in row["disabled_reason"].lower()
        finally:
            D.VASSAL_MIN_STATES = original

    def test_a_mission_against_a_later_vassalized_court_keeps_its_cancel(
            self, world):
        """Contract item 8: the vassal branch's early `return` dropped
        the DPF-2 cancel row. Once typing is retired, a mission opened
        before vassalization would have lost its ONLY cancel."""
        vassal = _a_french_vassal(world)
        world.active_diplomatic_mission = {
            "type": "IMPROVE_RELATIONS", "target": vassal,
            "initial_relation": 10, "turns_active": 2,
        }
        rows = _rows(world, vassal)
        assert "cancel_mission" in rows, (
            "a vassalized court's live mission must still be cancellable")

    def test_the_cancel_row_still_reaches_a_non_vassal_court(self, world):
        """Never-do: sharing the row must not lose it on the path that
        always had it."""
        world.active_diplomatic_mission = {
            "type": "IMPROVE_RELATIONS", "target": "Prussia",
            "initial_relation": 10, "turns_active": 2,
        }
        assert "cancel_mission" in _rows(world, "Prussia")

    def test_investing_at_full_loyalty_refuses_and_charges_nothing(
            self, world):
        """Contract item 6: the DEFAULT interaction (two of three boot
        vassals sit at 100) used to charge 1 DP + 200g, clamp the gain to
        zero and report "+10 (100 → 100)"."""
        from backend.game_logic.vassal import LOYALTY_MAX, invest_in_vassal

        vassal = _a_french_vassal(world)
        world.vassals[vassal]["loyalty"] = LOYALTY_MAX
        world.vassal_investment_cooldowns = {}
        world.diplomatic_points = 5
        world.nation_gold["France"] = 5000

        result = invest_in_vassal(world, vassal, actor="France")

        assert not result["success"]
        assert world.diplomatic_points == 5, "no DP may be charged"
        assert world.nation_gold["France"] == 5000, "no gold may be charged"
        assert "full" in result["message"].lower()
        assert world.vassal_investment_cooldowns.get(vassal, 0) == 0, (
            "and it must not burn the cooldown either")

    def test_a_boot_vassal_actually_sits_at_the_ceiling(self, world):
        """The contract calls this the DEFAULT interaction — if no boot
        vassal is at full loyalty any more, the fix has become exotic
        and the claim on the record needs revisiting."""
        from backend.game_logic.vassal import LOYALTY_MAX
        full = [n for n, s in (world.vassals or {}).items()
                if s.get("lord") == "France"
                and int(s.get("loyalty", 0) or 0) >= LOYALTY_MAX]
        assert full, (
            "no boot vassal sits at full loyalty — the 'default "
            "interaction' claim in the landing record has drifted")

    def test_the_row_mirrors_the_refusal(self, world):
        """Shown = applied: the wizard row states the same gate."""
        from backend.game_logic.vassal import LOYALTY_MAX

        vassal = _a_french_vassal(world)
        world.vassals[vassal]["loyalty"] = LOYALTY_MAX
        world.vassal_investment_cooldowns = {}
        world.diplomatic_points = 5
        world.nation_gold["France"] = 5000
        row = _rows(world, vassal)["invest_vassal"]
        assert not row["available"]
        assert "full" in row["disabled_reason"].lower()

    def test_investing_below_the_ceiling_still_works(self, world):
        """Never-do: the ceiling must not break the verb it guards."""
        from backend.game_logic.vassal import invest_in_vassal

        vassal = _a_french_vassal(world)
        world.vassals[vassal]["loyalty"] = 60
        world.vassal_investment_cooldowns = {}
        world.diplomatic_points = 5
        world.nation_gold["France"] = 5000
        result = invest_in_vassal(world, vassal, actor="France")
        assert result["success"], result["message"]
        assert world.vassals[vassal]["loyalty"] > 60


# ══════════════════════════════════════════════════════════════════════════
# THE HELP STOPS TEACHING THE TYPED VERBS
# ══════════════════════════════════════════════════════════════════════════

class TestTheHelpTeachesTheDoor:

    @pytest.fixture(scope="class")
    def help_text(self) -> str:
        source = (REPO / "backend" / "commands"
                  / "meta_executor.py").read_text(encoding="utf-8")
        block = re.search(r"DIPLOMACY(.*?)SCREENS & HOTKEYS", source, re.S)
        assert block, "the help's diplomacy block was not found"
        return block.group(1)

    def test_it_points_at_the_cabinet(self, help_text):
        assert "F1" in help_text
        assert "Cabinet" in help_text

    def test_it_no_longer_teaches_the_typed_orders(self, help_text):
        """Contract item 4 — every taught typed verb becomes a pointer.
        The eval's "seven verbs" undercounted: break treaty and ultimatum
        were taught in the same block."""
        for taught in ('"propose peace with', '"improve relations with',
                       'declare war /', '"invest in Holland"',
                       '"release Holland"', '"cede Tyrol to Holland"',
                       'break treaty', 'ultimatum'):
            assert taught not in help_text, (
                f"the help still teaches a typed diplomatic order: {taught!r}")

    def test_the_stale_trade_promise_is_gone(self, help_text):
        """Contract item 4: `trade` is a proposal type that exists in
        neither PROPOSAL_TYPE_KEYWORDS nor the wizard — the rewrite must
        not preserve it."""
        assert "trade" not in help_text.lower()

    def test_assess_is_still_taught_because_it_stays_typed(self, help_text):
        assert "assess" in help_text
