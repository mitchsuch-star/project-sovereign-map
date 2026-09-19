"""CX: the SAME 684 cases under the pre-row arms and the post-row arms.

The row's published "30 executing -> 9" needs both halves measured on one
case set, or it is two numbers from two different grids.
"""
import os
import sys
import io
import contextlib
import itertools
import json
os.environ["LLM_MODE"] = "mock"
sys.path.insert(0, os.getcwd())
from fastapi.testclient import TestClient
from backend.ai.parser_eval import build_world
from backend.commands.parser import CommandParser
from backend.ai import clause_guards as CG
from backend.commands.executor import CommandExecutor
import backend.main as M

OUT = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "sweep_both_arms.out.txt"), "w", encoding="utf-8")
def P(*a): OUT.write(" ".join(str(x) for x in a) + "\n")

@contextlib.contextmanager
def quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield

LEADS = ["why not", "why don't we", "why", "who", "whose men", "whom",
         "what if we", "what about", "how about", "should we", "shall we",
         "can we", "could we", "do we", "will we", "would it be wise to",
         "is it time to", "are we able to", "may we", "might we", "when do we",
         "can Ney", "may Ney", "does Ney", "is Ney", "could Davout",
         "should Soult", "will Ney", "would Davout", "is Mack", "has Ney",
         "did Ney", "are they going to", "is he going to", "how about Ney",
         "what about Ney"]
VERBS = ["attack Mack", "attack", "retreat", "move to Swabia", "fortify",
         "drill", "scout Swabia", "recruit", "declare war on Prussia",
         "build a depot in Paris", "charge", "hold Lorraine", "cancel Ney",
         "endow Ney with Swabia", "blockade the enemy", "buy off Prussia",
         "garrison Rhineland", "end turn"]
EXTRA = ["is Swabia defended", "is Vienna ours", "was the battle won",
         "has Vienna fallen", "did Ney attack", "are the Austrians at Swabia",
         "can Vienna be taken", "attack?", "retreat?", "fortify?", "end turn?",
         "charge?", "drill?", "Ney, attack Mack?", "who holds Swabia",
         "where's Ney", "what's my income", "why not attack Mack",
         "is Ney at Paris", "are we at war with Austria", "can Ney attack Mack",
         "may Ney attack Mack", "does Ney attack Mack", "is Ney attacking Mack",
         "how about Ney attacks Mack", "what about attacking Mack",
         "can Ney reach Vienna", "should Ney attack", "would Davout hold Lorraine",
         "Ney, attack Mack", "when ready then retreat",
         "would you have Ney attack Mack", "can you attack Mack",
         "do attack Mack", "end turn", "Berthier, end turn"]
CASES = [f"{a} {b}" for a, b in itertools.product(LEADS, VERBS)] + EXTRA

CONTROLS = {"Ney, attack Mack", "Ney, attack Mack?", "can you attack Mack",
            "would you have Ney attack Mack", "do attack Mack",
            "end turn", "end turn?", "Berthier, end turn",
            "when ready then retreat"}


def run(label):
    executed = []
    for utt in CASES:
        with quiet():
            w = build_world("1805")
            M.world = w
            M.game_state = {"world": w}
            M.parser = CommandParser(use_real_llm=False)
            client = TestClient(M.app)
        ap0, gold0, turn0 = w.actions_remaining, w.gold, w.current_turn
        adm0 = getattr(w, "admin_actions_remaining", None)
        pos0 = {m.name: (m.location, m.strength) for m in w.get_player_marshals()}
        with quiet():
            r = client.post("/command", json={"command": utt}).json()
        pos1 = {m.name: (m.location, m.strength) for m in w.get_player_marshals()}
        moved = [k for k, v in pos0.items() if pos1.get(k) != v]
        if (moved or w.actions_remaining != ap0 or w.gold != gold0
                or w.current_turn != turn0 or r.get("battle_report")
                or (adm0 is not None
                    and getattr(w, "admin_actions_remaining", None) != adm0)):
            executed.append(utt)
    P(f"\n=== {label} — {len(executed)} of {len(CASES)} executed ===")
    for utt in sorted(executed):
        tag = "CONTROL" if utt in CONTROLS else "DEFECT "
        P(f"  {tag} {utt!r}")
    return executed


CG.A_QUESTION_NEVER_ORDERS = False
CommandExecutor.AN_ADDRESS_NEEDS_NO_COMMA = False
before = run("BEFORE — both row-CX levers OFF")

CG.A_QUESTION_NEVER_ORDERS = True
CommandExecutor.AN_ADDRESS_NEEDS_NO_COMMA = True
after = run("AFTER — both levers ON")

P("\n" + "=" * 60)
P(f"cases            : {len(CASES)}")
P(f"executed BEFORE  : {len(before)}  (of which controls: "
  f"{len([u for u in before if u in CONTROLS])})")
P(f"executed AFTER   : {len(after)}  (of which controls: "
  f"{len([u for u in after if u in CONTROLS])})")
P(f"non-control AFTER: {sorted(set(after) - CONTROLS)}")
OUT.close()
print("done")
