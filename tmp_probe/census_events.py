import ast, os, sys
sys.stdout.reconfigure(encoding="utf-8")
produced = {}
for root, dirs, files in os.walk("backend"):
    if "__pycache__" in root: continue
    for fn in files:
        if not fn.endswith(".py"): continue
        p = os.path.join(root, fn)
        try:
            tree = ast.parse(open(p, encoding="utf-8").read())
        except SyntaxError:
            continue
        for n in ast.walk(tree):
            # dict literals assigned into an "events" list
            if isinstance(n, ast.Dict):
                keys = [k.value for k in n.keys if isinstance(k, ast.Constant)]
                if "type" in keys and ("marshal" in keys or "region" in keys):
                    for k, v in zip(n.keys, n.values):
                        if isinstance(k, ast.Constant) and k.value == "type" and isinstance(v, ast.Constant):
                            produced.setdefault(v.value, []).append(f"{p}:{n.lineno}")
for t in sorted(produced):
    print(f"{t:28s} {produced[t][:3]}")
