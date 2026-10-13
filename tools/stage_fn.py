"""CODE-2b: split a monster function into named stages (generalised from
S8b's stage_attack.py).

Pure extract-method. Stages are cut at top-level statement boundaries of a
CONTAINER: the function body ("body" mode) or the body of the function's one
trailing top-level `try` ("try" mode, whose prelude becomes stage 0, called by
the driver BEFORE the `try`, and whose handlers stay in the driver verbatim).

"elif" mode (CODE-2c, `_process_dialogue_choice`): the body past its head is
ONE `if … elif …` chain, which no top-level cut can split. Each stage is a
run of its arms (the run's first `elif` becomes `if`) with a synthetic
`else: return _NEXT_STAGE`; the last stage keeps the chain's own `else`.
Every arm body moves untouched. A matched arm that falls off its end falls
off its stage and answers `None`, as it fell off the old chain. Only the
parameters and what the head binds may cross a stage: the mode refuses a name
an arm reads that only another arm binds, because that read raised
`UnboundLocalError` in the old function and a ctx field or a repeated import
would quietly mend the crash.

A name used in more than one stage (or a parameter) moves onto a slots
context with no default (an unassigned read raises like the local did); a
name used in one stage stays a plain local there. A non-final stage that
falls off its end returns `_NEXT_STAGE`; every early `return` is kept.

New against S8b's tool: `nonlocal` in a nested def (the resolver treats the
name as the outer local; the statement is dropped when the name rides ctx),
a dedent for try-body stages that never touches a multi-line string's
interior (bar nested docstrings), refusals for the shapes a rename cannot
carry (a shared except-as name, a shared walrus target, a shared name in an
f-string `{x=}`, `global`, `locals()`), and a per-stage AST-equality proof.

    .venv/Scripts/python.exe tools/stage_fn.py <target>              # dry run: the report + tools/stage_fn_out/<target>_staged.py
    .venv/Scripts/python.exe tools/stage_fn.py <target> --apply      # write the source
    .venv/Scripts/python.exe tools/stage_fn.py <target> --no-confine # compare against slice 1's rule

Moved here from the S10 session's scratchpad (October 13, 2026) so S10b
(CODE-2c) inherits it; the slice records are `docs/CODE_HEALTH_PLAN.md`
§CODE-2b and §CODE-2c. `pin_scan.py` (test literals a cut loses) and
`oneliner_sweep.py` (slice 2's before/after sweep, a model) came with it;
`dialogue_choice_sweep.py` is CODE-2c slice 2's.
"""
from __future__ import annotations

import ast
import copy
import io
import re
import sys
import symtable
import textwrap
import tokenize
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / "stage_fn_out"   # gitignored

TARGETS = {
    "execute_command": dict(
        src="backend/main.py", cls=None, func="execute_command",
        params=["request"], prefix="_command_", ctx_class="CommandContext",
        mode="try", slice_name="CODE-2b",
        prelude=("open",
                 "Run before the `try`, where the prelude always ran: the relay's "
                 "one-command stash popped, the DD-0 trace opened, the CR-7-9 "
                 "let-go, `_relay_question` (CR-7-3 rule 5)."),
        stages=[
            ("guards", "# GAME-OVER GUARD — No actions after the war ends",
             "The war is over, a blank line, the typed `why` (DD-0 S3)."),
            ("clarification_answer", "# CR-2: PENDING COMMAND CLARIFICATION — one question, one answer.",
             "CR-2: a typed answer to the pending clarification resolves, or the question is let go."),
            ("interrupt_answer", "# PENDING STRATEGIC INTERRUPT CHECK (Phase 5.2-D)",
             "Phase 5.2-D: a typed answer to a marshal's pending interrupt (SF5-X1/X2, PC15-2)."),
            ("pending_answers", "# W6-0 (BUG-CA-1): PENDING-QUESTION ROUTER — when the game itself",
             "W6-0: the objection's words (CA9-N5), the capture answer, a dialogue's own option."),
            ("carryover_and_lost_name", "# CR-4: CONTEXT CARRYOVER — resolve shorthand references (\"again\",",
             "CR-4 shorthand resolved against the history; PC15-4 the fallen or captured name refused."),
            ("parse", "        # Parse command",
             "SF-CMD-1 W2 the premise, the parse, FA-39 provenance, the request's own fields."),
            ("history", "# COMMAND HISTORY: Track parsed commands for LLM repetition detection",
             "The command history (CR-4), never for a line a dialogue consumed."),
            ("delegation", "# CR-5: PERSONALITY-BIASED DISAMBIGUATION (COMMAND_ROBUSTNESS_SPEC §6).",
             "CR-5: a delegation verb routed by the marshal's character — cautious, aggressive or ask."),
            ("dialogue_routing", "# DIPLOMATIC DIALOGUE RESPONSE ROUTING (Audit fix)",
             "A pending dialogue takes the line only when it claims it (CA9, PT-A3, WO-7, IQ-7)."),
            ("ordinary_road", "        if not _dialogue_took_the_line:",
             "The ordinary road: dialogue-only words, WO-1, CR-2 did-you-mean, PARSE-NEG, "
             "Berthier's parse recovery, then the executor."),
            ("riders", "# CR-2: parser warnings (sequential-order drop note, non-standard",
             "What rides the result: parser warnings and the typo note, the CR-7-3 relay, "
             "CR-5's notes and first-use hint."),
            ("executor_recovery", "# BERTHIER EXECUTOR RECOVERY: Catch \"Marshal 'None' not found\"",
             "No marshal named: the CR-4 focus reissue, CX3-X2, the CR-2 marshal choice, Berthier."),
            ("question_returns", "# CHECK FOR OBJECTION: If awaiting player choice, return full result",
             "A result carrying a question or a popup returns whole."),
            ("respond", "# FEEDBACK GENERATION (Phase 5): Generate immersive feedback",
             "Live-mode feedback (Phase 5) and the response."),
        ],
    ),
    "format_event_oneliner": dict(
        src="backend/campaign_log.py", cls=None, func="format_event_oneliner",
        params=["event", "player_nation", "world"], prefix="_oneliner_",
        ctx_class="OnelinerContext", mode="body", slice_name="CODE-2b", confine=True,
        stages=[
            ("head", 'event_type = event.get("type", "")',
             "The type read; a commitments notice goes to its own formatter; a war "
             "that shatters a treaty names it."),
            ("the_field", 'if event_type == "battle":',
             "Battles, bombardments, escalades, retreats, the broken and the "
             "recovered, a province captured."),
            ("purse_and_court", 'if event_type == "recruitment":',
             "Levies, works, bankruptcy and desertion; jealousy and glory; petitions, "
             "rentes, commissions, substitutes; voided orders, agendas, new nations; "
             "dotations and estates."),
            ("orders_and_fates", 'if event_type == "objection":',
             "Objections, the campaign's end, the congress, literal fidelity; a "
             "marshal captured, evacuated, wounded, destroyed, standing last or "
             "released; standing orders and defiance."),
            ("diplomacy", "# ── Diplomacy events (Session 8D) ──",
             "Treaties, war aims, settlements, the ally's entry, AI-AI treaties and "
             "the D5 counter-instruments, crises and designs (Session 8D)."),
            ("laws", '# ── SR-5r "The Laws"',
             "A law enacted, repealed or lapsed (SR-5r)."),
            ("the_sea", "# ── DEF-5 naval (NV-0..NV-3)",
             "Fleets, blockades, the Continental System, the straits, the Descent and "
             "the expeditions (DEF-5); the flip in play."),
            ("allegiance", "# DD-1 S8 Step 3 — the verbs (October 12, 2026)",
             "The allegiance bid, a province returned, the auction resolved (DD-1)."),
            ("cascades_and_coalitions", "# Deep audit fix: new event types",
             "A war declared, the cascades, a coalition declared or dissolved."),
            ("the_fallen_and_the_clients", "# V3 Session 8: new event types",
             "A nation eliminated; vassals joining, refusing, transferred, defecting; "
             "the client's petition; a member leaving the coalition."),
            ("proposals_and_ultimatums",
             "# ── R8 Session 6: format strings for 16 previously-silent types ──",
             "AI proposals and ultimatums, the brewing coalition, counter-offers, "
             "missions, the proposal queue, garrisons, relationships, the peace "
             "ratified (R8, PL-14, PL-27, BPH)."),
            ("unknown", 'return f"Event: {event_type}"',
             "The fall-through: an unknown type is named, never dropped."),
        ],
    ),
    "_execute_strategic_command": dict(
        src="backend/commands/strategic_executor.py", cls="StrategicExecutor",
        func="_execute_strategic_command",
        params=["parsed_command", "command", "game_state"], prefix="_strategic_",
        ctx_class="StrategicCommandContext", mode="body", slice_name="CODE-2b",
        confine=True,
        stages=[
            ("open", "from backend.models.marshal import StrategicOrder, StrategicCondition",
             "The world and the marshal found; the broken and the routed refuse "
             "(7A-1, FA-9); the state speaks first (CRT-9); an identical order "
             "already carried is a no-op (F10)."),
            ("square_and_engagement", "Auto-break square formation (Session 67",
             "The square breaks; guns cannot chase; no order while engaged; a "
             "marshal never targets himself."),
            ("generic_target", "Resolve generic/vague targets for ALL strategic types",
             "A bare march asks where (CX3-R2); a generic target resolved."),
            ("validate_target", "# ── Validate target",
             "SUPPORT names a friendly marshal; PURSUE an enemy one, at war and "
             "sighted."),
            ("hold", "HOLD: default target to current location (Bug #7)",
             "HOLD defaults to where he stands (CRT-2 remembers the game placed "
             "it); a redundant HOLD refused."),
            ("path", "Build path for movement orders",
             "The road for MOVE_TO, PURSUE, SUPPORT and HOLD, from where our scouts "
             "saw the quarry (FA-S17-9)."),
            ("objection", "Strategic objection check (V2a)",
             "The V2a objection check, before any order exists."),
            ("create_order", "# ── Build condition",
             "The condition, the `StrategicOrder`, the old order cancelled, the "
             "event logged."),
            ("first_step", "Execute first step immediately",
             "The first step at once: PURSUE in the same province, the march's "
             "first leg, SUPPORT already beside its friend."),
            ("response", "# ── Build response",
             "The reply's road, the grounding note (FA-54), the MOVE_TO lines."),
            ("cost_and_reply", "CR-7-4 item 6 — THE ECHO",
             "The condition echoed (CR-7-4), the order priced (SR-2e), the "
             "acknowledgement, the reply."),
        ],
    ),
    "_ratify_treaty": dict(
        src="backend/models/world_state.py", cls="WorldState", func="_ratify_treaty",
        params=["proposal"], prefix="_ratify_", ctx_class="RatifyTreatyContext",
        mode="body", slice_name="CODE-2c", confine=True,
        stages=[
            ("open", "# Extract nations from proposal",
             "The two courts, the target state, and the one verdict "
             "(`treaty.can_sign`, DD-1 S7 Slice B) — a refused letter stops here."),
            ("snapshot_and_vassal", "# Build treaty clauses before vassalage validation",
             "The clauses built; the war's data snapshotted before anything "
             "clears it (BPH-D, GE-1); a VASSAL treaty creates its vassal first."),
            ("transition_and_record", "# Apply state transition (R2: centralized setter)",
             "The state transition (R2), the armistice cooldown (R5b), open "
             "borders, the treaty stored and remembered for harshness."),
            ("one_time_clauses", "# Apply one-time clauses (shared)",
             "Every one-time clause applied, cessions and payments first among "
             "them."),
            ("alliances_and_carves", "WPS-C: Forced alliance + liberation clause handling",
             "WPS-C's forced alliance and liberation clauses, the client carved "
             "(NA-6c), the Tilsit clause, the war bargains' commitments (WB-A)."),
            ("titles_and_elimination", "a bilateral treaty that strips a court leaves",
             "The punitive record (AI-5b(i)), the titles and the Humbled Peace "
             "(GE-1), a court eliminated by its cessions (R81)."),
            ("war_end", "# War-end cleanup (shared",
             "The war's end cleaned up (WPS-A, WB-B), the clients follow (SR-1b), "
             "the forced alliance set (WPS-C §9.2), the corridor (WIN-D3), the "
             "volte-face (AI-5b(ii))."),
            ("player_events", "Player-specific events",
             "France's own treaty: its events, notices and reply."),
            ("ai_ai_events", "AI-AI-specific events",
             "Two other courts: relations, the dispatch, the log, the pair's "
             "cooldown (R43), the result."),
        ],
    ),
    "_process_dialogue_choice": dict(
        src="backend/commands/diplomatic_executor.py", cls="DiplomaticExecutor",
        func="_process_dialogue_choice",
        params=["action", "selected", "dialogue", "world"], prefix="_choice_",
        ctx_class="DialogueChoiceContext", mode="elif", slice_name="CODE-2c",
        confine=True,
        stages=[
            ("desk_settlement_and_war", 'if action == "dismiss":',
             "The letter set aside or reconsidered; the settlement's table, offers "
             "and petitions; the ally's entry; a war bargain repudiated; a war "
             "objective or purpose chosen; a war forced or a treaty broken."),
            ("proposal", 'elif action in ("execute_proposal", "send"):',
             "The proposal sent as drafted, or hardened (`modify_harsh`)."),
            ("ultimatum", 'elif action == "execute_ultimatum":',
             "The ultimatum delivered, and its wizard: gold, territory, "
             "manpower, start over."),
            ("generous_and_suggestions", 'elif action == "modify_generous":',
             "The proposal softened, the options expanded, a suggestion taken, "
             "the terms adjusted."),
            ("terms_wizard", 'elif action == "territory_yes":',
             "The terms wizard: provinces offered or skipped, gold, actions."),
            ("missions_and_ai_letters", 'elif action == "start_mission":',
             "A mission started or recalled; an AI court's proposal or ultimatum "
             "accepted, rejected or countered; a letter expanded to a proposal."),
            ("counsel", "# GAP-1: ELABORATE / REVIEW_COUNTER / ACCEPT_WITH_CONFLICT",
             "Talleyrand's counsel: elaborate, review a counter, accept a "
             "conflict (GAP-1); sabotage confronted (R37); the drafting "
             "pushback (PL-23); the pre-proposal objection overridden (R42)."),
            ("counters_and_rebellion", "# R2: COUNTER-OFFER RESPONSE HANDLERS",
             "A counter-offer accepted or rejected (R2); a vassal's rebellion "
             "answered with gold, a garrison, or acceptance (R74)."),
            ("alliance_paradox", "# R12: ALLIANCE PARADOX HANDLERS",
             "The alliance paradox: honour the defender or break with him "
             "(R12); an unknown action is refused."),
        ],
    ),
}

SCOPES =(ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef,
          ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)


def die(msg):
    print("REFUSED:", msg)
    sys.exit(2)


def scope_stmts(nodes, kinds):
    """Nodes of `kinds` directly in this scope (not inside a nested scope)."""
    out = []
    stack = list(nodes)
    while stack:
        n = stack.pop()
        if isinstance(n, kinds):
            out.append(n)
        if isinstance(n, SCOPES):
            continue
        stack.extend(ast.iter_child_nodes(n))
    return out


def stored_names(nodes):
    """Names bound directly in a (nested) function scope, not descending into deeper scopes."""
    out = set()
    stack = list(nodes)
    while stack:
        n = stack.pop()
        if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del)):
            out.add(n.id)
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out.add(n.name)
            continue
        elif isinstance(n, ast.alias):
            out.add((n.asname or n.name).split(".")[0])
        elif isinstance(n, ast.ExceptHandler) and n.name:
            out.add(n.name)
        if isinstance(n, SCOPES):
            continue
        stack.extend(ast.iter_child_nodes(n))
    return out


def arg_names(args: ast.arguments):
    a = [x.arg for x in args.posonlyargs + args.args + args.kwonlyargs]
    if args.vararg:
        a.append(args.vararg.arg)
    if args.kwarg:
        a.append(args.kwarg.arg)
    return set(a)


class Resolver:
    """Every ast.Name under a stage that resolves to the outer function's
    scope, and every `nonlocal` in a nested def that names an outer local."""

    def __init__(self, func_locals):
        self.L = func_locals
        self.nonlocals = []     # (Nonlocal node, [outer names])

    def walk(self, node, shadow, out):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for d in node.decorator_list:
                self.walk(d, shadow, out)
            for d in node.args.defaults + [x for x in node.args.kw_defaults if x]:
                self.walk(d, shadow, out)
            nl_stmts = scope_stmts(node.body, ast.Nonlocal)
            gl_stmts = scope_stmts(node.body, ast.Global)
            nonlocal_names = {n for s in nl_stmts for n in s.names}
            global_names = {n for s in gl_stmts for n in s.names}
            for s in nl_stmts:
                outer = [n for n in s.names if n in self.L and n not in shadow]
                if outer:
                    self.nonlocals.append((s, outer))
            inner = (shadow | arg_names(node.args)
                     | (stored_names(node.body) - nonlocal_names) | global_names)
            for st in node.body:
                self.walk(st, inner, out)
            return
        if isinstance(node, ast.ClassDef):
            die(f"a nested class at {node.lineno}")
        if isinstance(node, ast.Lambda):
            for d in node.args.defaults + [x for x in node.args.kw_defaults if x]:
                self.walk(d, shadow, out)
            self.walk(node.body, shadow | arg_names(node.args), out)
            return
        if isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            targets = set()
            for g in node.generators:
                targets |= {n.id for n in ast.walk(g.target) if isinstance(n, ast.Name)}
            inner = shadow | targets
            for i, g in enumerate(node.generators):
                self.walk(g.iter, shadow if i == 0 else inner, out)
                self.walk(g.target, inner, out)
                for c in g.ifs:
                    self.walk(c, inner, out)
            if isinstance(node, ast.DictComp):
                self.walk(node.key, inner, out)
                self.walk(node.value, inner, out)
            else:
                self.walk(node.elt, inner, out)
            return
        if isinstance(node, ast.Name):
            if node.id in self.L and node.id not in shadow:
                out.append(node)
            return
        for ch in ast.iter_child_nodes(node):
            self.walk(ch, shadow, out)


def name_key(n):
    return (n.lineno, n.col_offset, n.end_col_offset, n.id)


def protected_lines(text):
    """Lines whose START lies inside a multi-line string / f-string token."""
    prot = set()
    toks = tokenize.generate_tokens(io.StringIO(text).readline)
    fstack = []
    for tok in toks:
        if tok.type == tokenize.STRING and tok.end[0] > tok.start[0]:
            prot.update(range(tok.start[0] + 1, tok.end[0] + 1))
        elif tok.type == getattr(tokenize, "FSTRING_START", -1):
            fstack.append(tok.start[0])
        elif tok.type == getattr(tokenize, "FSTRING_END", -1):
            start = fstack.pop()
            if tok.end[0] > start:
                prot.update(range(start + 1, tok.end[0] + 1))
    return prot


def docstring_lines(fn):
    """Interior lines of every nested def's docstring under `fn`."""
    out = set()
    for n in ast.walk(fn):
        if n is fn:
            continue
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.body \
                and isinstance(n.body[0], ast.Expr) \
                and isinstance(n.body[0].value, ast.Constant) \
                and isinstance(n.body[0].value.value, str):
            c = n.body[0].value
            out.update(range(c.lineno + 1, c.end_lineno + 1))
    return out


def norm_docstrings(tree):
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            b = n.body
            if b and isinstance(b[0], ast.Expr) and isinstance(b[0].value, ast.Constant) \
                    and isinstance(b[0].value.value, str):
                b[0].value.value = ""
    return tree


class ToCtx(ast.NodeTransformer):
    def __init__(self, keys, shared):
        self.keys = keys
        self.shared = shared

    def visit_Name(self, node):
        if name_key(node) in self.keys:
            return ast.Attribute(value=ast.Name(id="ctx", ctx=ast.Load()),
                                 attr=node.id, ctx=node.ctx)
        return node

    def visit_AnnAssign(self, node):
        # `world: T = v` -> `ctx.world: T = v`: an attribute target is not
        # "simple" (in a function scope neither annotation is evaluated)
        self.generic_visit(node)
        if isinstance(node.target, ast.Attribute):
            node.simple = 0
        return node

    def visit_Nonlocal(self, node):
        keep = [n for n in node.names if n not in self.shared]
        if not keep:
            return None
        node.names = keep
        return node


def main(target: str, apply: bool):
    cfg = dict(TARGETS[target])
    if "--no-confine" in sys.argv:
        cfg["confine"] = False
    SRC = ROOT / cfg["src"]
    FUNC, CLASS, PARAMS = cfg["func"], cfg["cls"], cfg["params"]
    PREFIX, CTXC, MODE = cfg["prefix"], cfg["ctx_class"], cfg["mode"]
    STAGES = cfg["stages"]
    raw = SRC.read_bytes()
    nl = "\r\n" if b"\r\n" in raw else "\n"
    text = raw.decode("utf-8")
    lines = text.split(nl)            # lines[i] is line i+1
    tree = ast.parse(text)
    if CLASS:
        owner = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == CLASS)
        fn = next(n for n in owner.body if isinstance(n, ast.FunctionDef) and n.name == FUNC)
    else:
        owner = None
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == FUNC)
    body = fn.body
    if not (isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant)):
        die("no docstring")
    doc_node = body[0]
    base_ind = fn.col_offset + 4              # the function body's indentation
    meth = lambda s: f"{PREFIX}{s}"

    st = symtable.symtable(text, str(SRC), "exec")

    def find(t):
        for c in t.get_children():
            if c.get_name() == FUNC and c.get_lineno() == fn.lineno:
                return c
            r = find(c)
            if r:
                return r
    ft = find(st)
    syms = ft.get_symbols()
    if any(s.is_declared_global() for s in syms):
        die("the function declares a global")
    L = {s.get_name() for s in syms if s.is_local()} - {"self"}
    if "ctx" in L:
        die("the function already uses `ctx`")
    if any(isinstance(n, ast.Name) and n.id in ("locals", "vars", "eval", "exec")
           for n in ast.walk(fn)):
        die("locals()/vars()/eval/exec in the function")
    for n in scope_stmts(fn.body, (ast.Global, ast.Nonlocal)):
        die(f"global/nonlocal at the function's own scope, line {n.lineno}")

    # ── the container and the stage ranges ─────────────────────────────
    # all_stages: list of (name, doc); ranges: (start, end) line numbers;
    # dedent per stage; the final stage of the loop is the last entry.
    if MODE == "try":
        tr = body[-1]
        if not isinstance(tr, ast.Try) or tr.finalbody or tr.orelse or len(tr.handlers) != 1:
            die("try mode needs a trailing try with exactly one handler")
        prelude_stmts = body[1:-1]
        if any(isinstance(n, ast.Return) for s in prelude_stmts
               for n in scope_stmts([s], ast.Return)):
            die("a return in the prelude")
        container = tr.body
        c_first = tr.lineno + 1
        c_last = tr.handlers[0].lineno - 1
        inner_dedent = 4
    elif MODE == "elif":
        # CODE-2c slice 2: the body past its head is ONE `if … elif …` chain.
        # Each stage is a run of its arms with a synthetic final
        # `else: return _NEXT_STAGE`; the last stage keeps the chain's own
        # `else`. Only one arm runs per call, so a matched arm that falls off
        # its end falls off its stage, which returns `None` as the old
        # function did, and no arm body is touched.
        prelude_stmts = None
        chain = body[-1]
        if not isinstance(chain, ast.If) or len(body) < 2:
            die("elif mode needs the body to end in an if/elif chain")
        head_stmts = body[1:-1]
        arms = []
        node = chain
        while True:
            arms.append(node)
            nxt = node.orelse
            if len(nxt) == 1 and isinstance(nxt[0], ast.If) \
                    and lines[nxt[0].lineno - 1].lstrip().startswith("elif"):
                node = nxt[0]
                continue
            final_else = nxt
            break
        for a in arms:
            if any(isinstance(x, ast.NamedExpr) for x in ast.walk(a.test)):
                die(f"a walrus in the arm's test at {a.lineno}")
        if final_else and not lines[final_else[0].lineno - 2].lstrip().startswith("else"):
            die("the chain's last orelse is not a plain `else:`")
        container = None
        c_first = doc_node.end_lineno + 1
        c_last = fn.end_lineno
        inner_dedent = 0
    else:
        prelude_stmts = None
        container = body[1:]
        c_first = doc_node.end_lineno + 1
        c_last = fn.end_lineno
        inner_dedent = 0
    starts = []
    for name, anchor, _doc in STAGES:
        hits = [i + 1 for i in range(c_first - 1, c_last) if anchor in lines[i]]
        if len(hits) != 1:
            die(f"anchor {anchor!r} hits {hits}")
        ln = hits[0]
        while lines[ln - 2].strip().startswith("#") and ln - 1 >= c_first:
            ln -= 1
        starts.append(ln)
    starts[0] = c_first
    if starts != sorted(starts):
        die(f"stages out of order: {starts}")
    ends = [s - 1 for s in starts[1:]] + [c_last]
    stage_stmts = [[] for _ in STAGES]
    first_arm_line = {}
    if MODE == "elif":
        if any(s.end_lineno >= starts[1] for s in head_stmts):
            die("the head crosses the first cut")
        runs = [[] for _ in STAGES]
        for a in arms:
            idx = max(i for i, st in enumerate(starts) if st <= a.lineno)
            if a.body[-1].end_lineno > ends[idx]:
                die(f"arm {a.lineno} crosses the cut at {ends[idx]}")
            runs[idx].append(a)
        for i, run in enumerate(runs):
            if not run:
                die(f"stage {STAGES[i][0]} holds no arm")
            if i:
                first_arm_line[i] = run[0].lineno
                between = [lines[k - 1].strip() for k in range(starts[i], run[0].lineno)]
                if any(x and not x.startswith("#") for x in between):
                    die(f"code between stage {STAGES[i][0]}'s cut and its first arm")
                if not lines[run[0].lineno - 1].lstrip().startswith("elif "):
                    die(f"stage {STAGES[i][0]} does not open on an `elif`")

        def run_chain(run, tail):
            # an `if`/`elif` chain over the ORIGINAL arm nodes (tests and
            # bodies shared, never copied), ending in `tail`
            nxt = tail
            for a in reversed(run):
                n = ast.If(test=a.test, body=a.body, orelse=nxt)
                ast.copy_location(n, a)
                n.end_lineno = (nxt[-1].end_lineno if nxt else a.body[-1].end_lineno)
                n.end_col_offset = 0
                nxt = [n]
            return nxt[0]
        for i, run in enumerate(runs):
            tail = final_else if i == len(runs) - 1 else []
            stage_stmts[i] = (list(head_stmts) if i == 0 else []) + [run_chain(run, tail)]
    else:
        for s in container:
            idx = max(i for i, a in enumerate(starts) if a <= s.lineno)
            if s.end_lineno > ends[idx]:
                die(f"statement {s.lineno}-{s.end_lineno} crosses the cut at {ends[idx]}")
            stage_stmts[idx].append(s)
        for i, ss in enumerate(stage_stmts):
            if not ss:
                die(f"stage {STAGES[i][0]} is empty")
        if not isinstance(stage_stmts[-1][-1], ast.Return):
            die("the last stage does not end in a return")

    # unify: the prelude (try mode) is stage 0
    all_stages = list(STAGES)
    ranges = list(zip(starts, ends))
    dedents = [inner_dedent] * len(STAGES)
    all_stmts = list(stage_stmts)
    if MODE == "try":
        pname, pdoc = cfg["prelude"]
        all_stages.insert(0, (pname, None, pdoc))
        ranges.insert(0, (doc_node.end_lineno + 1, tr.lineno - 1))
        dedents.insert(0, 0)
        all_stmts.insert(0, prelude_stmts)
        if not prelude_stmts:
            die("empty prelude")
    n_st = len(all_stages)
    first_loop = 1 if MODE == "try" else 0

    # ── references per stage ───────────────────────────────────────────
    res = Resolver(L)
    names_by_stage = []
    used = defaultdict(set)
    import_bind = defaultdict(list)
    def_bind = defaultdict(list)
    nonlocal_by_stage = defaultdict(list)
    for i, ss in enumerate(all_stmts):
        out = []
        before = len(res.nonlocals)
        for s in ss:
            res.walk(s, set(), out)
        nonlocal_by_stage[i] = res.nonlocals[before:]
        names_by_stage.append(out)
        for n in out:
            used[n.id].add(i)
        for s in ss:
            for n in ast.walk(s):
                if isinstance(n, (ast.Import, ast.ImportFrom)):
                    for a in n.names:
                        nm = (a.asname or a.name).split(".")[0]
                        if nm in L:
                            import_bind[nm].append((i, n, a))
                            used[nm].add(i)
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name in L:
                    def_bind[n.name].append((i, n))
                    used[n.name].add(i)
        for (_s, outer) in nonlocal_by_stage[i]:
            for nm in outer:
                used[nm].add(i)

    # ── what goes on ctx ───────────────────────────────────────────────
    import_only = {nm for nm in import_bind
                   if not any(n.id == nm and isinstance(n.ctx, (ast.Store, ast.Del))
                              for ns in names_by_stage for n in ns)
                   and nm not in def_bind}

    # confine (slice 2): a name whose every binding sits inside a branch that
    # always ends in return/raise can never carry a value past the top-level
    # statement that bound it, so it never crosses a stage boundary and stays
    # a plain local in each stage that uses it (an `if event_type == X:` arm's
    # temporaries). Sound: a stage that reads such a name without binding it
    # reads it as a global, which the symtable proof refuses.
    def can_complete(stmts):
        for s in stmts:
            if isinstance(s, (ast.Return, ast.Raise)):
                return False
            if isinstance(s, ast.If) and s.orelse \
                    and not can_complete(s.body) and not can_complete(s.orelse):
                return False
        return True

    def binds(node):
        r = Resolver(L)
        out = []
        r.walk(node, set(), out)
        got = {n.id for n in out if isinstance(n.ctx, (ast.Store, ast.Del))}
        for n in scope_stmts([node], (ast.Import, ast.ImportFrom)):
            got |= {(a.asname or a.name).split(".")[0] for a in n.names} & L
        for n in scope_stmts([node], (ast.FunctionDef, ast.AsyncFunctionDef,
                                      ast.ExceptHandler)):
            if n.name in L:
                got.add(n.name)
        return got

    def escaping(s):
        if isinstance(s, ast.If):
            out = binds(s.test)
            for blk in (s.body, s.orelse):
                if blk and can_complete(blk):
                    for x in blk:
                        out |= escaping(x)
            return out
        return binds(s)

    escapes = set()
    for ss in all_stmts:
        for s in ss:
            escapes |= escaping(s)
    for i in range(len(all_stmts)):
        for (_s, outer) in nonlocal_by_stage[i]:
            escapes |= set(outer)
    # split (slice 3): a name no stage ever reads before that stage itself
    # has bound it on every path (definite assignment, per stage, from
    # nothing) takes no value from any other stage, so each stage keeps its
    # own plain local (`_road`: a module alias in one stage, a string in a
    # later one). Conservative: loops, `with` and `try` add nothing past
    # themselves; a name read inside a nested def or lambda, deleted, named
    # by `nonlocal` or bound by a walrus is never split.
    class Flow:
        def __init__(self):
            self.exposed = set()
            self.unsplittable = set()

        def reads(self, node, B):
            if node is None:
                return
            r = Resolver(L)
            out = []
            r.walk(node, set(), out)
            for n in out:
                if isinstance(n.ctx, ast.Load) and n.id not in B:
                    self.exposed.add(n.id)
            for n in ast.walk(node):
                if isinstance(n, (ast.Lambda, ast.FunctionDef, ast.AsyncFunctionDef)):
                    r2 = Resolver(L)
                    o2 = []
                    r2.walk(n, set(), o2)
                    self.unsplittable |= {x.id for x in o2}
                if isinstance(n, ast.NamedExpr):
                    self.unsplittable |= {x.id for x in ast.walk(n.target)
                                          if isinstance(x, ast.Name)}

        def block(self, stmts, B):
            B = set(B)
            for s in stmts:
                B, term = self.stmt(s, B)
                if term:
                    return B, True
            return B, False

        def stmt(self, s, B):
            if isinstance(s, (ast.Return, ast.Raise, ast.Break, ast.Continue)):
                self.reads(s, B)
                return B, True
            if isinstance(s, (ast.Assign, ast.AnnAssign, ast.Expr, ast.Assert, ast.Pass)):
                if isinstance(s, ast.AnnAssign) and s.value is None:
                    return B, False
                self.reads(s, B)
                return B | binds(s), False
            if isinstance(s, ast.AugAssign):
                if isinstance(s.target, ast.Name) and s.target.id not in B:
                    self.exposed.add(s.target.id)
                self.reads(s, B)
                return B | binds(s), False
            if isinstance(s, ast.If):
                self.reads(s.test, B)
                B |= binds(s.test)
                Bb, tb = self.block(s.body, B)
                Be, te = self.block(s.orelse, B)
                if tb and te:
                    return B, True
                if tb:
                    return Be, False
                if te:
                    return Bb, False
                return Bb & Be, False
            if isinstance(s, (ast.For, ast.AsyncFor)):
                self.reads(s.iter, B)
                self.reads(s.target, B)
                self.block(s.body, B | binds(s.target))
                self.block(s.orelse, B)
                return B, False
            if isinstance(s, ast.While):
                self.reads(s.test, B)
                self.block(s.body, B)
                self.block(s.orelse, B)
                return B, False
            if isinstance(s, (ast.With, ast.AsyncWith)):
                B2 = set(B)
                for it in s.items:
                    self.reads(it.context_expr, B2)
                    if it.optional_vars is not None:
                        self.reads(it.optional_vars, B2)
                        B2 |= binds(it.optional_vars)
                self.block(s.body, B2)
                return B2, False
            if isinstance(s, ast.Try):
                Bb, _ = self.block(s.body, B)
                for h in s.handlers:
                    self.reads(h.type, B)
                    self.block(h.body, B | ({h.name} if h.name else set()))
                self.block(s.orelse, Bb)
                self.block(s.finalbody, B)
                return B, False
            if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.reads(s, B)          # decorators, defaults; the body as closure
                return B | {s.name}, False
            if isinstance(s, (ast.Import, ast.ImportFrom)):
                return B | binds(s), False
            if isinstance(s, ast.Delete):
                self.unsplittable |= binds(s)
                self.reads(s, B)
                return B, False
            die(f"split: no flow rule for {type(s).__name__} at {s.lineno}")

    split = set()
    if cfg.get("confine"):
        flow = Flow()
        exposed_any = set()
        for ss in all_stmts:
            flow.exposed = set()
            flow.block(ss, set())
            exposed_any |= flow.exposed
        for i in range(len(all_stmts)):
            for (_s, outer) in nonlocal_by_stage[i]:
                flow.unsplittable |= set(outer)
    confined = set()
    shared = set(PARAMS)
    for nm, stages in used.items():
        if len(stages) > 1 and nm not in import_only and nm not in PARAMS:
            if cfg.get("confine") and nm not in escapes:
                confined.add(nm)
                continue
            if cfg.get("confine") and nm not in exposed_any \
                    and nm not in flow.unsplittable:
                split.add(nm)
                continue
            shared.add(nm)
    for nm in shared:
        if nm in import_bind:
            die(f"{nm} is bound by an import AND shared by assignment")
    if MODE == "elif":
        # only one arm runs per call, so nothing but the parameters and what
        # the head binds may cross a stage: a name an arm reads that only
        # ANOTHER arm binds raised `UnboundLocalError` in the old function,
        # and a repeated import or a ctx field would quietly mend that crash
        head_bound = set()
        for s in head_stmts:
            head_bound |= binds(s)
        odd = sorted(nm for nm in shared if nm not in PARAMS and nm not in head_bound)
        if odd:
            die(f"elif: names cross the arms: {odd}")
        for nm in sorted(import_only):
            binding = {si for si, _, _ in import_bind[nm]}
            for si in sorted(used[nm] - binding):
                if nm not in head_bound:
                    die(f"elif: stage {si} reads {nm}, imported only by another stage's arm")
    shared_defs = {nm for nm in def_bind if nm in shared}
    for nm in shared_defs:
        for (si, node) in def_bind[nm]:
            if node not in all_stmts[si]:
                die(f"shared nested def {nm} is not at the top of its stage")
    # shapes a rename cannot carry
    for i, ss in enumerate(all_stmts):
        for s in ss:
            for n in ast.walk(s):
                if isinstance(n, ast.ExceptHandler) and n.name in shared:
                    die(f"shared except-as name {n.name} at {n.lineno}")
                if isinstance(n, ast.NamedExpr) and isinstance(n.target, ast.Name) \
                        and n.target.id in shared:
                    die(f"shared walrus target {n.target.id} at {n.lineno}")
                if isinstance(n, (ast.MatchAs, ast.MatchStar, ast.MatchMapping)):
                    die(f"a match pattern at {n.lineno}")
                if isinstance(n, ast.JoinedStr):
                    # the AST cannot tell `{x=}` from literal `x=` + `{x}`
                    # (`path={path}`), so read the f-string's own source
                    seg = ast.get_source_segment(text, n) or ""
                    for x in ast.walk(n):
                        if isinstance(x, ast.Name) and x.id in shared and re.search(
                                r"\{\s*" + re.escape(x.id) + r"\s*=(?!=)", seg):
                            die(f"a shared name in an f-string self-documenting {{x=}} at {n.lineno}")
    if MODE == "try":
        hd = tr.handlers[0]
        hd_names = Resolver(L)
        hout = []
        for s in hd.body:
            hd_names.walk(s, set(), hout)
        bad = {n.id for n in hout} - {hd.name} - stored_names(hd.body)
        if bad:
            die(f"the handler reads old locals {bad}")

    # imports to repeat at a stage's head
    # grouped per ORIGINAL import statement, its names in its own order; each
    # entry is a list of source lines (one statement)
    need = defaultdict(lambda: defaultdict(list))   # stage -> src stmt -> [alias]
    for nm in sorted(import_only):
        binding_stages = {si for si, _, _ in import_bind[nm]}
        src_node, alias = import_bind[nm][0][1], import_bind[nm][0][2]
        for si in sorted(used[nm] - binding_stages):
            need[si][src_node].append(alias)
    head_imports = defaultdict(list)
    for si, by_src in need.items():
        for src_node in sorted(by_src, key=lambda n: (n.lineno, n.col_offset)):
            order = {id(a): k for k, a in enumerate(src_node.names)}
            als = sorted(by_src[src_node], key=lambda a: order[id(a)])
            parts = [a.name + (f" as {a.asname}" if a.asname else "") for a in als]
            if isinstance(src_node, ast.ImportFrom):
                head = f"from {'.' * src_node.level}{src_node.module or ''} import "
                if len(parts) == 1:
                    head_imports[si].append([head + parts[0]])
                else:
                    head_imports[si].append([head + "("] + [f"    {p}," for p in parts] + [")"])
            else:
                for p in parts:
                    head_imports[si].append([f"import {p}"])

    # ── the edits (byte columns on each line) ──────────────────────────
    edits = defaultdict(list)
    shared_keys = set()
    for i, ns in enumerate(names_by_stage):
        for n in ns:
            if n.id in shared:
                edits[n.lineno].append((n.col_offset, n.end_col_offset, "ctx." + n.id))
                shared_keys.add(name_key(n))
    drop_lines = set()
    nonlocal_dropped = []
    for i in range(n_st):
        for (s, outer) in nonlocal_by_stage[i]:
            gone = [nm for nm in outer if nm in shared]
            if not gone:
                continue
            if s.lineno != s.end_lineno:
                die(f"multi-line nonlocal at {s.lineno}")
            keep = [nm for nm in s.names if nm not in shared]
            if keep:
                ln = s.lineno
                b = lines[ln - 1].encode("utf-8")
                edits[ln].append((s.col_offset, s.end_col_offset, "nonlocal " + ", ".join(keep)))
            else:
                if lines[s.lineno - 1].strip() != ast.get_source_segment(text, s):
                    die(f"nonlocal at {s.lineno} shares its line")
                drop_lines.add(s.lineno)
            nonlocal_dropped.append((s.lineno, gone))

    def render(lineno):
        line_b = lines[lineno - 1].encode("utf-8")
        es = sorted(edits.get(lineno, []), reverse=True)
        last = None
        for a, b, rep in es:
            if last is not None and b > last:
                die(f"overlapping edits on line {lineno}")
            line_b = line_b[:a] + rep.encode("utf-8") + line_b[b:]
            last = a
        return line_b.decode("utf-8")

    prot = protected_lines(text)
    dlines = docstring_lines(fn)

    def emit_line(lineno, dedent):
        s = render(lineno)
        if dedent == 0:
            return s
        if not s.strip():
            return ""
        if lineno in prot and lineno not in dlines:
            return s                      # inside a multi-line string: verbatim
        if s.startswith(" " * dedent):
            return s[dedent:]
        if lineno in dlines:
            return s                      # a docstring line with less indent
        die(f"line {lineno} cannot lose {dedent} columns: {s!r}")

    # ── emit ──────────────────────────────────────────────────────────
    first_seen = {}
    for i, ns in enumerate(names_by_stage):
        for n in ns:
            if n.id in shared and n.id not in first_seen:
                first_seen[n.id] = (n.lineno, n.col_offset)
    for nm in shared_defs:
        first_seen.setdefault(nm, (def_bind[nm][0][1].lineno, 0))
    ctx_fields = list(PARAMS) + sorted(
        (nm for nm in shared if nm not in PARAMS), key=lambda k: first_seen.get(k, (0, 0)))

    ind = " " * base_ind
    out_lines = []
    head_start = fn.decorator_list[0].lineno if fn.decorator_list else fn.lineno
    out_lines += lines[head_start - 1:doc_node.lineno - 1]
    doc_lines = lines[doc_node.lineno - 1:doc_node.end_lineno]
    if len(doc_lines) == 1:
        one = doc_lines[0]
        q = one.strip()[:3]
        out_lines.append(one.rstrip()[:-3].rstrip() if one.rstrip().endswith(q) else one)
        closing = ind + q
    else:
        closing = doc_lines[-1]
        if closing.strip() not in ('"""', "'''"):
            die("docstring does not close on its own line")
        out_lines += doc_lines[:-1]
    out_lines.append("")
    if MODE == "try":
        out_lines.append(ind + f"{cfg['slice_name']} (October 2026): a driver of named stages behind one")
        out_lines.append(ind + f"`{CTXC}`. Stage 0 runs before the `try`, where the prelude always")
        out_lines.append(ind + "ran; inside it, a stage returns `_NEXT_STAGE` to continue or the")
        out_lines.append(ind + "response to stop, and the `except` is still the route's one error")
        out_lines.append(ind + "reply. Nothing on the context reaches the wire.")
    elif MODE == "elif":
        out_lines.append(ind + f"{cfg['slice_name']} (October 2026): a driver of named stages behind one")
        out_lines.append(ind + f"`{CTXC}`. Each stage is a run of the old `if action == …`")
        out_lines.append(ind + "chain's arms, tried in the old order: a stage none of whose tests")
        out_lines.append(ind + "holds returns `_NEXT_STAGE`, and a matched arm's return — or its")
        out_lines.append(ind + "`None`, falling off the stage as it fell off the chain — ends the")
        out_lines.append(ind + "call. The last stage keeps the chain's own `else`. Nothing on the")
        out_lines.append(ind + "context reaches the wire.")
    else:
        out_lines.append(ind + f"{cfg['slice_name']} (October 2026): a driver of named stages behind one")
        out_lines.append(ind + f"`{CTXC}`. A stage returns `_NEXT_STAGE` to continue or the")
        out_lines.append(ind + "result to stop; nothing on the context reaches the wire.")
    out_lines.append("")
    for k, (s, _a, d) in enumerate(all_stages, 0 if MODE == "try" else 1):
        out_lines += textwrap.wrap(f"{k:2d}. `{meth(s)}` — {d}", width=79,
                                   initial_indent=ind, subsequent_indent=ind + "    ",
                                   break_on_hyphens=False)
    out_lines.append(closing)
    self_ = "self." if CLASS else ""
    out_lines.append(ind + f"ctx = {CTXC}(")
    for p in PARAMS:
        out_lines.append(ind + f"    {p}={p},")
    out_lines.append(ind + ")")
    loop_ind = ind
    if MODE == "try":
        out_lines.append(ind + f"{self_}{meth(all_stages[0][0])}(ctx)")
        out_lines.append(" " * tr.col_offset + "try:")
        loop_ind = ind + "    "
    out_lines.append(loop_ind + "for stage in (")
    for s, _a, _d in all_stages[first_loop:-1]:
        out_lines.append(loop_ind + f"        {self_}{meth(s)},")
    out_lines.append(loop_ind + "):")
    out_lines.append(loop_ind + "    result = stage(ctx)")
    out_lines.append(loop_ind + "    if result is not _NEXT_STAGE:")
    out_lines.append(loop_ind + "        return result")
    out_lines.append(loop_ind + f"return {self_}{meth(all_stages[-1][0])}(ctx)")
    if MODE == "try":
        out_lines += lines[tr.handlers[0].lineno - 1:tr.end_lineno]

    stage_sizes = {}
    stage_def_ind = " " * fn.col_offset
    sep = ["", ""] if not CLASS else [""]
    sig = "(self, ctx: {})".format(CTXC) if CLASS else "(ctx: {})".format(CTXC)
    for i, (s, _a, d) in enumerate(all_stages):
        out_lines += sep
        start_idx = len(out_lines)
        out_lines.append(stage_def_ind + f"def {meth(s)}{sig}:")
        label = f"Stage {i if MODE == 'try' else i + 1} of `{FUNC}`"
        if MODE == "try" and i == 0:
            label += ", the door"
        doc = textwrap.wrap(f'"""{label}: {d}"""', width=79, initial_indent=ind,
                            subsequent_indent=ind, break_on_hyphens=False)
        out_lines += doc
        for imp in head_imports.get(i, []):
            out_lines += [ind + x for x in imp]
        a, b = ranges[i]
        while b > a and not lines[b - 1].strip():
            b -= 1
        while a < b and not lines[a - 1].strip():
            a += 1
        defs_here = {node.end_lineno: nm for nm in shared_defs
                     for (si, node) in def_bind[nm] if si == i}
        for ln in range(a, b + 1):
            if ln in drop_lines:
                continue
            line_out = emit_line(ln, dedents[i])
            if MODE == "elif" and first_arm_line.get(i) == ln:
                # the run's first arm opens its own chain: `elif` -> `if`
                lead = line_out[:len(line_out) - len(line_out.lstrip())]
                if not line_out.lstrip().startswith("elif "):
                    die(f"line {ln} is not an `elif`")
                line_out = lead + line_out.lstrip()[2:]
            out_lines.append(line_out)
            if ln in defs_here:
                out_lines.append(ind + f"ctx.{defs_here[ln]} = {defs_here[ln]}")
        is_last = i == n_st - 1
        is_door = MODE == "try" and i == 0
        if MODE == "elif":
            if not is_last:
                arm_ind = " " * chain.col_offset
                out_lines.append(arm_ind + "else:")
                out_lines.append(arm_ind + "    return _NEXT_STAGE")
        elif not is_last and not is_door and not isinstance(all_stmts[i][-1], ast.Return):
            out_lines.append(ind + "return _NEXT_STAGE")
        stage_sizes[s] = len(out_lines) - start_idx

    # the context class, inserted above the function (module) or class (method)
    anchor_node = owner if CLASS else fn
    ins = anchor_node.decorator_list[0].lineno if anchor_node.decorator_list else anchor_node.lineno
    ctx_cls = [
        f"# {cfg['slice_name']} (October 2026): what the stages of `{(CLASS + '.') if CLASS else ''}{FUNC}`",
        "# share. Built once at the driver's head, never on the wire. The parameters",
        "# are init fields; every other field is set by the stage that first assigns",
        "# it — `slots` with no default, so a read before any assignment raises as",
        "# the local it replaced did.",
        "_NEXT_STAGE = object()",
        "",
        "",
        "@dataclass(slots=True, repr=False, eq=False)",
        f"class {CTXC}:",
    ]
    for p in PARAMS:
        ctx_cls.append(f"    {p}: Any")
    for nm in ctx_fields[len(PARAMS):]:
        ctx_cls.append(f"    {nm}: Any = field(init=False)")
    ctx_cls += ["", ""]

    new_lines = (lines[:ins - 1] + ctx_cls + lines[ins - 1:head_start - 1]
                 + out_lines + lines[fn.end_lineno:])
    new_text = nl.join(new_lines)

    # imports
    if "from dataclasses import dataclass, field" not in new_text:
        typing_node = None
        for old in ("from typing import Optional", "from typing import Dict, Optional",
                    "from typing import Dict, List, Optional", "from typing import Any, Dict, Optional"):
            if (old + nl) in new_text:
                rep = old.replace("from typing import ", "from typing import Any, ") \
                    if "Any" not in old else old
                new_text = new_text.replace(old + nl, "from dataclasses import dataclass, field"
                                            + nl + rep + nl, 1)
                break
        else:
            typing_node = next((n for n in tree.body if isinstance(n, ast.ImportFrom)
                                and n.module == "typing" and n.lineno == n.end_lineno), None)
        if "from dataclasses import dataclass, field" in new_text:
            pass
        elif typing_node is not None:
            # CODE-2c (world_state.py): any other one-line typing import — the
            # dataclasses line goes above it, `Any` joins it when absent
            line = lines[typing_node.lineno - 1]
            rep = line if any(a.name == "Any" for a in typing_node.names) \
                else line.replace("from typing import ", "from typing import Any, ", 1)
            if (nl + line + nl) not in new_text:
                die("could not add imports")
            new_text = new_text.replace(nl + line + nl, nl + "from dataclasses import dataclass, field"
                                        + nl + rep + nl, 1)
        else:
            # no typing line to extend (campaign_log.py): both imports go
            # after the module's first import statement
            first_imp = next((n for n in tree.body
                              if isinstance(n, (ast.Import, ast.ImportFrom))
                              and not (isinstance(n, ast.ImportFrom)
                                       and n.module == "__future__")), None)
            if first_imp is None or first_imp.lineno != first_imp.end_lineno:
                die("could not add imports")
            line = lines[first_imp.lineno - 1]
            if (nl + line + nl) not in new_text or "from typing import" in new_text:
                die("could not add imports")
            new_text = new_text.replace(
                nl + line + nl,
                nl + line + nl + "from dataclasses import dataclass, field" + nl
                + "from typing import Any" + nl, 1)

    # ── proofs ────────────────────────────────────────────────────────
    compile(new_text, str(SRC), "exec")
    new_tree = ast.parse(new_text)
    new_st = symtable.symtable(new_text, str(SRC), "exec")
    bad = []
    stage_names = {meth(s) for s, _a, _d in all_stages}

    def visit(t):
        for c in t.get_children():
            if c.get_type() == "function" and c.get_name() in stage_names | {FUNC}:
                for sym in c.get_symbols():
                    if sym.is_global() and sym.get_name() in L:
                        bad.append((c.get_name(), sym.get_name()))
            visit(c)
    visit(new_st)
    if bad:
        die(f"a stage reads an old local it never bound: {bad[:20]}")
    fields = set(ctx_fields)
    if CLASS:
        container_new = next(n for n in new_tree.body if isinstance(n, ast.ClassDef) and n.name == CLASS).body
    else:
        container_new = new_tree.body
    fns_new = {m.name: m for m in container_new if isinstance(m, ast.FunctionDef)}
    for nm in stage_names | {FUNC}:
        for n in ast.walk(fns_new[nm]):
            if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == "ctx":
                if n.attr not in fields:
                    die(f"ctx.{n.attr} is not a field (in {nm})")
    # per-stage AST equality: old statements (renamed) == new stage body (minus scaffolding)
    for i, (s, _a, _d) in enumerate(all_stages):
        old = norm_docstrings(ast.Module(body=copy.deepcopy(all_stmts[i]), type_ignores=[]))
        old = ToCtx(shared_keys, shared).visit(old)
        ast.fix_missing_locations(old)
        new_fn = fns_new[meth(s)]
        nb = list(new_fn.body[1:])                       # past the docstring
        k = len(head_imports.get(i, []))
        nb = nb[k:]
        if MODE == "elif":
            # the run's chain, its synthetic `else: return _NEXT_STAGE` taken
            # off (every stage but the last), must equal the old arms' chain
            nb = copy.deepcopy(nb)
            if not nb or not isinstance(nb[-1], ast.If):
                die(f"stage {meth(s)} does not end in its chain")
            if i < n_st - 1:
                n = nb[-1]
                while len(n.orelse) == 1 and isinstance(n.orelse[0], ast.If):
                    n = n.orelse[0]
                tail = n.orelse
                if not (len(tail) == 1 and isinstance(tail[0], ast.Return)
                        and isinstance(tail[0].value, ast.Name)
                        and tail[0].value.id == "_NEXT_STAGE"):
                    die(f"stage {meth(s)} lacks its synthetic else")
                n.orelse = []
        elif nb and isinstance(nb[-1], ast.Return) and isinstance(nb[-1].value, ast.Name) \
                and nb[-1].value.id == "_NEXT_STAGE":
            nb = nb[:-1]
        nb = [x for x in nb if not (
            isinstance(x, ast.Assign) and len(x.targets) == 1
            and isinstance(x.targets[0], ast.Attribute)
            and isinstance(x.targets[0].value, ast.Name) and x.targets[0].value.id == "ctx"
            and isinstance(x.value, ast.Name) and x.value.id == x.targets[0].attr
            and x.value.id in shared_defs)]
        new = norm_docstrings(ast.Module(body=copy.deepcopy(nb), type_ignores=[]))
        if ast.dump(old) != ast.dump(new):
            a_, b_ = ast.dump(old, indent=1).splitlines(), ast.dump(new, indent=1).splitlines()
            j = next((j for j in range(min(len(a_), len(b_))) if a_[j] != b_[j]), None)
            die(f"stage {meth(s)} is not the old body moved: first diff at dump line {j}: "
                f"{a_[j] if j is not None else ''!r} vs {b_[j] if j is not None else ''!r}")
    # the driver's handler (try mode) is the old one, verbatim
    if MODE == "try":
        new_tr = next(x for x in fns_new[FUNC].body if isinstance(x, ast.Try))
        if ast.dump(new_tr.handlers[0]) != ast.dump(tr.handlers[0]):
            die("the handler changed")

    # ── report ────────────────────────────────────────────────────────
    print(f"confined (used in >1 stage, never crossing one): {len(confined)} {sorted(confined)}")
    print(f"split (bound before read in every stage): {len(split)} {sorted(split)}")
    print(f"locals {len(L)}; shared on ctx {len(ctx_fields)} ({len(PARAMS)} params); "
          f"import-only names repeated: {sum(len(v) for v in head_imports.values())}; "
          f"shared defs {sorted(shared_defs)}; nonlocal dropped {nonlocal_dropped}")
    for i, (s, _a, _d) in enumerate(all_stages):
        a, b = ranges[i]
        print(f"  {i:2d} {meth(s):40s} lines {a}-{b}  -> {stage_sizes[s]} lines"
              + (f"  +imports {head_imports[i]}" if head_imports.get(i) else ""))
    print("fields:", ", ".join(ctx_fields))
    # F2 class: a stage-local import binding a module-level name of this file
    mod_names = set()
    for n in tree.body:
        if isinstance(n, (ast.Import, ast.ImportFrom)):
            mod_names |= {(a.asname or a.name).split(".")[0] for a in n.names}
        elif isinstance(n, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
            mod_names.add(n.name)
        elif isinstance(n, ast.Assign):
            mod_names |= {x.id for t in n.targets for x in ast.walk(t) if isinstance(x, ast.Name)}
    f2 = sorted({nm for nm in import_bind if nm in mod_names})
    print("F2 class (local import shadowing a module-level name):", f2)
    big = [s for s, n in stage_sizes.items() if n > 500]
    if big:
        die(f"stages over 500 lines: {big}")
    if apply:
        SRC.write_bytes(new_text.encode("utf-8"))
        print("wrote", SRC)
    else:
        OUT.mkdir(exist_ok=True)
        out = OUT / f"{target}_staged.py"
        out.write_bytes(new_text.encode("utf-8"))
        print("dry run: wrote", out)


if __name__ == "__main__":
    main(sys.argv[1], "--apply" in sys.argv)
