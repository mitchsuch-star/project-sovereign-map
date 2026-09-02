import ast, sys
sys.stdout.reconfigure(encoding="utf-8")
src = open("backend/ai/enemy_ai.py", encoding="utf-8").read()
tree = ast.parse(src)
lines = src.splitlines()
names = ["_evaluate_marshal","_get_counter_punch_action","_find_attack_opportunity",
         "_find_homeland_defense","_find_liberation_target","_find_undefended_capture",
         "_find_garrison_attack","_find_ally_support_opportunity","_get_stagnation_action",
         "_get_default_action"]
for f in ast.walk(tree):
    if isinstance(f, ast.FunctionDef) and f.name in names:
        body = "\n".join(lines[f.lineno-1:f.end_lineno])
        has_thresh = "threshold" in body
        has_ratio_gate = ">= threshold" in body or "> threshold" in body
        print(f"{f.name:35s} threshold-word={has_thresh!s:5s}  ratio-gate={has_ratio_gate!s:5s}  "
              f"field-sum={'_defending_strength_in_region' in body}")
