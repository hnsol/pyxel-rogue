#!/usr/bin/env python3
"""Counts # C: comments and unannotated defs in rogue.py."""
import ast
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "rogue.py"
src = open(path).read()
lines = src.splitlines()

c_refs = sum(1 for l in lines if "# C:" in l)
print(f"# C: references: {c_refs}")

tree = ast.parse(src)
no_hints = []
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        missing = [a for a in node.args.args if a.annotation is None and a.arg != "self"]
        if missing or node.returns is None:
            no_hints.append((node.lineno, node.name))
print(f"Functions without full type hints: {len(no_hints)}")
